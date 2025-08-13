from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable
from typing import Literal

import numpy as np
import numpy.typing as npt
import pyarrow as pa
import pyarrow.parquet as pq
from datasets import ClassLabel, Dataset, Image as HFImage, load_dataset
from PIL import Image

__all__ = [
    "extract_and_save_embeddings",
    "EmbeddingOutputFormat",
    "FeatureExtractor",
    "BatchFeatureExtractor",
    "ExtractionConfig",
]


EmbeddingOutputFormat = Literal["npy", "parquet"]

FeatureExtractor = Callable[[Image.Image], npt.NDArray[np.floating]]
BatchFeatureExtractor = Callable[[list[Image.Image]], npt.NDArray[np.floating]]


@dataclass(slots=True)
class ExtractionConfig:
    dataset_name: str
    split: str = "train"
    image_column: str = "image"
    label_column: str | None = "label"
    batch_size: int = 64
    use_label_names: bool = False
    output_path: Path | str = Path("embeddings.parquet")
    output_format: EmbeddingOutputFormat | None = None
    load_kwargs: dict[str, object] | None = None


def _resolve_output_format(path: Path, explicit: EmbeddingOutputFormat | None) -> EmbeddingOutputFormat:
    if explicit is not None:
        return explicit
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return "parquet"
    if suffix == ".npy":
        return "npy"
    return "parquet"


def _as_pil(image: object) -> Image.Image:
    if isinstance(image, Image.Image):
        return image
    if isinstance(image, dict) and "bytes" in image:
        return HFImage().decode_example(image)  # type: ignore[arg-type]
    return Image.fromarray(np.asarray(image))


def _call_extractor(
    extractor: FeatureExtractor | BatchFeatureExtractor, images: list[Image.Image]
) -> npt.NDArray[np.floating]:
    try:
        embeddings = extractor(images)  # type: ignore[misc]
        arr = np.asarray(embeddings)
        if arr.ndim == 1:
            raise TypeError("Batch extractor returned 1D array; expected [batch, dim]")
        return arr
    except Exception:
        per_item = [np.asarray(extractor(img)) for img in images]  # type: ignore[misc]
        return np.stack(per_item, axis=0)


def _to_float32(a: npt.NDArray[np.floating]) -> npt.NDArray[np.float32]:
    if a.dtype != np.float32:
        return a.astype(np.float32, copy=False)
    return a  # type: ignore[return-value]


def _iter_batches(ds: Dataset, batch_size: int):
    images_batch: list[Image.Image] = []
    labels_batch: list[object] = []
    indices_batch: list[int] = []
    for i, item in enumerate(ds):
        images_batch.append(_as_pil(item["image"]))
        labels_batch.append(item.get("label", None))
        indices_batch.append(i)
        if len(images_batch) == batch_size:
            yield images_batch, labels_batch, indices_batch
            images_batch, labels_batch, indices_batch = [], [], []
    if images_batch:
        yield images_batch, labels_batch, indices_batch


def _coerce_label_ints(labels: list[object]) -> list[int | None]:
    out: list[int | None] = []
    for x in labels:
        if x is None:
            out.append(None)
        elif isinstance(x, (int, np.integer)):
            out.append(int(x))
        else:
            try:
                out.append(int(x))  # pyright: ignore[reportArgumentType]
            except Exception:
                out.append(None)
    return out


def _label_names_from_classlabel(label_feature: ClassLabel, labels: list[object]) -> list[str | None]:
    out: list[str | None] = []
    for x in labels:
        if x is None:
            out.append(None)
        else:
            try:
                out.append(label_feature.int2str(int(x)))
            except Exception:
                out.append(None)
    return out


def extract_and_save_embeddings(
    extractor: FeatureExtractor | BatchFeatureExtractor,
    config: ExtractionConfig,
) -> Path:
    output_path = Path(config.output_path)
    output_format = _resolve_output_format(output_path, config.output_format)

    load_kwargs = dict(config.load_kwargs or {})
    ds: Dataset = load_dataset(config.dataset_name, split=config.split, **load_kwargs)  # type: ignore[arg-type]

    if config.image_column != "image" or (config.label_column and config.label_column != "label"):
        select_cols = [c for c in ds.column_names if c in {config.image_column, config.label_column or ""}]
        ds = ds.select_columns(select_cols)
        rename_map: dict[str, str] = {}
        if config.image_column in ds.column_names and config.image_column != "image":
            rename_map[config.image_column] = "image"
        if config.label_column and config.label_column in ds.column_names and config.label_column != "label":
            rename_map[config.label_column] = "label"
        if rename_map:
            ds = ds.rename_columns(rename_map)

    label_feature = ds.features.get("label") if "label" in ds.column_names else None
    is_class_label = isinstance(label_feature, ClassLabel)

    if output_format == "npy":
        try:
            num_rows = len(ds)
        except TypeError as exc:
            raise ValueError("Format 'npy' requires finite length dataset; use Parquet for streaming.") from exc

        first_images, first_labels, first_indices = next(_iter_batches(ds, config.batch_size))
        first_emb = _to_float32(_call_extractor(extractor, first_images))
        if first_emb.ndim != 2:
            raise ValueError(f"Extractor must return [batch, dim]; got {first_emb.shape}")
        dim = first_emb.shape[1]

        emb_path = output_path if output_path.suffix == ".npy" else output_path.with_suffix(".npy")
        labels_path = emb_path.with_name(emb_path.stem + ".labels.npy") if config.label_column else None

        if config.label_column and is_class_label and config.use_label_names:
            raise ValueError("For NPY outputs, only integer labels are supported. Use Parquet if you need label names.")

        emb_mem = np.memmap(emb_path, dtype=np.float32, mode="w+", shape=(num_rows, dim))
        labels_mem: np.memmap | None = None
        if config.label_column:
            labels_mem = np.memmap(labels_path, dtype=np.int64, mode="w+", shape=(num_rows,))  # type: ignore[arg-type]

        emb_mem[first_indices[0] : first_indices[0] + len(first_indices)] = first_emb
        if labels_mem is not None:
            coerced = _coerce_label_ints(first_labels)
            labels_mem[first_indices[0] : first_indices[0] + len(first_indices)] = [
                (-1 if v is None else v) for v in coerced
            ]

        write_pos = len(first_indices)
        for images, labels, indices in _iter_batches(ds.select(range(write_pos, num_rows)), config.batch_size):
            emb = _to_float32(_call_extractor(extractor, images))
            if emb.shape[1] != dim:
                raise ValueError(f"Inconsistent embedding dim. Expected {dim}, got {emb.shape[1]}")
            start = write_pos
            emb_mem[start : start + len(indices)] = emb
            if labels_mem is not None:
                coerced = _coerce_label_ints(labels)
                labels_mem[start : start + len(indices)] = [
                    (-1 if v is None else v) for v in coerced
                ]
            write_pos += len(indices)

        emb_mem.flush()
        if labels_mem is not None:
            labels_mem.flush()
        return emb_path

    writer: pq.ParquetWriter | None = None
    try:
        for _batch_idx, (images, labels, indices) in enumerate(_iter_batches(ds, config.batch_size)):
            emb = _to_float32(_call_extractor(extractor, images))
            if emb.ndim != 2:
                raise ValueError(f"Extractor must return [batch, dim]; got {emb.shape}")

            columns: dict[str, pa.Array] = {}
            columns["embedding"] = pa.array(emb.tolist(), type=pa.list_(pa.float32()))
            columns["index"] = pa.array(indices, type=pa.int64())
            if config.label_column and labels:
                if is_class_label and config.use_label_names:
                    lbl_vals = [label_feature.int2str(int(x)) if x is not None else None for x in labels]  # type: ignore[union-attr]
                    columns["label"] = pa.array(lbl_vals, type=pa.string())
                else:
                    try:
                        columns["label"] = pa.array([int(x) if x is not None else None for x in labels], type=pa.int64())
                    except Exception:
                        columns["label"] = pa.array([str(x) if x is not None else None for x in labels], type=pa.string())

            table = pa.table(columns)
            if writer is None:
                writer = pq.ParquetWriter(output_path, table.schema)
            assert writer is not None
            writer.write_table(table)

        if writer is None:
            empty_table = pa.table({"embedding": pa.array([], type=pa.list_(pa.float32())), "index": pa.array([], type=pa.int64())})
            pq.write_table(empty_table, output_path)
        else:
            writer.close()
        return output_path
    finally:
        if writer is not None:
            try:
                writer.close()
            except Exception:
                pass


def main() -> None:
    raise SystemExit("Import and call `extract_and_save_embeddings(extractor, config)` instead.")


if __name__ == "__main__":
    main()
