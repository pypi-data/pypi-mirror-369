from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

import numpy as np
import torch
from datasets import Dataset, load_dataset
from PIL import Image

__all__ = ["extract_features_to_dataset", "FeatureExtractor", "BatchFeatureExtractor"]

FeatureExtractor = Callable[[Image.Image], np.ndarray]
BatchFeatureExtractor = Callable[[list[Image.Image]], np.ndarray]


def extract_features_to_dataset(
    dataset_name: str,
    extractor: FeatureExtractor | BatchFeatureExtractor,
    *,
    split: str = "train",
    batch_size: int = 128,
    num_proc: int | None = None,
    image_column: str = "image",
    remove_original_images: bool = True,
    output_column: str = "features",
) -> Dataset:
    if num_proc is None:
        num_proc = min(os.cpu_count() or 1, 8)

    ds = load_dataset(dataset_name, split=split)

    def extract_batch_features(batch: dict[str, Any]) -> dict[str, Any]:
        images = []

        try:
            features = extractor(images)  # type: ignore[arg-type]
            if HAS_TORCH and torch is not None and hasattr(features, "detach"):
                features = features.detach().cpu().numpy()  # type: ignore[attr-defined]
            features = np.asarray(features, dtype=np.float32)

            # 确保是 2D [batch, dim]
            if features.ndim == 1:
                raise ValueError("Batch extractor should return [batch, dim], got 1D")

        except Exception:
            # 回退到逐个处理
            feature_list = []
            for img in images:
                feat = extractor(img)  # type: ignore[misc]
                if HAS_TORCH and torch is not None and hasattr(feat, "detach"):
                    feat = feat.detach().cpu().numpy()  # type: ignore[attr-defined]
                feature_list.append(np.asarray(feat, dtype=np.float32))
            features = np.stack(feature_list, axis=0)

        return {output_column: features.tolist()}

    # 使用 datasets 的高效 map - 这是最优方案
    map_kwargs = {
        "batched": True,
        "batch_size": batch_size,
        "remove_columns": [image_column] if remove_original_images else [],
    }

    # 添加可选参数（如果支持）
    if num_proc is not None and num_proc > 1:
        map_kwargs["num_proc"] = num_proc

    result = ds.map(extract_batch_features, **map_kwargs)

    return result  # type: ignore[return-value]


def save_features_optimized(
    dataset: Dataset,
    output_path: str | Path,
    format: Literal["arrow", "parquet", "numpy"] = "arrow",
) -> Path:
    """
    保存特征数据集，使用最优格式。

    - arrow: 最快读写，支持内存映射，推荐用于后续训练
    - parquet: 跨语言兼容，压缩率高
    - numpy: 传统格式，兼容性最好
    """
    output_path = Path(output_path)

    if format == "arrow":
        # Arrow 格式最快，支持零拷贝读取
        dataset.save_to_disk(str(output_path))
        return output_path

    elif format == "parquet":
        # Parquet 压缩率高，跨平台
        output_file = output_path.with_suffix(".parquet")
        dataset.to_parquet(str(output_file))
        return output_file

    elif format == "numpy":
        # 传统 numpy 格式
        features = np.array(dataset["features"], dtype=np.float32)
        labels = np.array(dataset["label"]) if "label" in dataset.column_names else None

        features_file = output_path.with_suffix(".npy")
        np.save(features_file, features)

        if labels is not None:
            labels_file = output_path.with_name(output_path.stem + ".labels.npy")
            np.save(labels_file, labels)

        return features_file

    else:
        raise ValueError(f"Unsupported format: {format}")


def load_features_for_training(
    path: str | Path, format: Literal["arrow", "parquet", "numpy"] = "arrow"
) -> tuple[np.ndarray, np.ndarray | None]:
    """
    加载特征数据用于训练。

    Returns:
        (features, labels) 其中 labels 可能为 None
    """
    path = Path(path)

    if format == "arrow":
        ds = Dataset.load_from_disk(str(path))
        features = np.array(ds["features"], dtype=np.float32)
        labels = (
            np.array(ds["label"]) if hasattr(ds, "features") and "label" in ds.features else None
        )  # type: ignore[misc]
        return features, labels

    elif format == "parquet":
        ds = Dataset.from_parquet(str(path))
        features = np.array(ds["features"], dtype=np.float32)
        labels = (
            np.array(ds["label"]) if hasattr(ds, "features") and "label" in ds.features else None
        )  # type: ignore[misc]
        return features, labels

    elif format == "numpy":
        features = np.load(path, mmap_mode="r")  # 内存映射读取
        labels_file = path.with_name(path.stem + ".labels.npy")
        labels = np.load(labels_file, mmap_mode="r") if labels_file.exists() else None
        return features, labels

    else:
        raise ValueError(f"Unsupported format: {format}")


# 示例用法和最佳实践
if __name__ == "__main__":
    """
    使用示例：

    # 1. 定义特征提取器 (推荐批处理版本)
    import torch
    from transformers import CLIPModel, AutoProcessor

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
    processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")

    @torch.inference_mode()
    def clip_extractor(images: list[Image.Image]) -> np.ndarray:
        inputs = processor(images=images, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        outputs = model.vision_model(pixel_values=inputs["pixel_values"])
        return outputs.pooler_output.cpu().numpy().astype(np.float32)

    # 2. 提取特征 (自动多进程、缓存)
    dataset = extract_features_to_dataset(
        "cifar10",
        clip_extractor,
        split="train",
        batch_size=128,  # 根据 GPU 内存调整
    )

    # 3. 保存 (推荐 arrow 格式最快)
    save_features_optimized(dataset, "cifar10_features", format="arrow")

    # 4. 后续训练时加载
    X, y = load_features_for_training("cifar10_features", format="arrow")

    # 5. 线性探测训练
    from sklearn.linear_model import LogisticRegression
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X, y)
    """
    print("Import this module and use extract_features_to_dataset()")
