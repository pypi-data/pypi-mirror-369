import io
from pathlib import Path

import imageio.v3 as iio
import numpy as np


class ImageIOWrapper:
    STANDARD_IMAGES = [
        "astronaut.png",
        "camera.png",
        "checkerboard.png",
        "chelsea.png",
        "clock.png",
        "coffee.png",
        "coins.png",
        "horse.png",
        "hubble_deep_field.png",
        "immunohistochemistry.png",
        "moon.png",
        "page.png",
        "text.png",
        "wikkie.png",
        "bricks.jpg",
        "meadow_cube.jpg",
        "wood.jpg",
        "newtonscradle.gif",
        "cockatoo.mp4",
        "cockatoo_yuv420.mp4",
        "stent.npz",
        "bacterial_colony.tif",
    ]

    @staticmethod
    def read_image(
        source: str | Path | bytes | io.BytesIO,
        index: int | None = None,
        mode: str | None = None,
        **kwargs,
    ) -> np.ndarray:
        """
        读取图片的通用函数

        Args:
            source: 图片源，可以是文件路径、URL、bytes或BytesIO对象
            index: 对于多帧图片（如GIF），指定读取的帧索引，None表示读取所有帧
            mode: 颜色模式，如 'RGB', 'RGBA', 'L' 等
            **kwargs: 其他参数传递给imageio.imread

        Returns:
            numpy.ndarray: 图片数据
        """
        try:
            # 处理标准测试图片
            if isinstance(source, str) and any(
                source.endswith(img) for img in ImageIOWrapper.STANDARD_IMAGES
            ):
                if not source.startswith("imageio:"):
                    source = f"imageio:{source}"

            # 读取图片
            if mode:
                kwargs["mode"] = mode
            if index is not None:
                kwargs["index"] = index

            image = iio.imread(source, **kwargs)
            return image

        except Exception as e:
            print(f"读取图片失败: {e}")
            raise

    @staticmethod
    def read_gif(source: str | Path, frame_index: int | None = None) -> np.ndarray:
        """
        专门读取GIF文件的函数

        Args:
            source: GIF文件路径
            frame_index: 指定帧索引，None表示读取所有帧

        Returns:
            numpy.ndarray: GIF数据，形状为 (frames, height, width, channels) 或 (height, width, channels)
        """
        return ImageIOWrapper.read_image(source, index=frame_index)

    @staticmethod
    def read_video(
        source: str | Path, frame_index: int | None = None, plugin: str = "pyav"
    ) -> np.ndarray:
        """
        读取视频文件

        Args:
            source: 视频文件路径
            frame_index: 指定帧索引，None表示读取所有帧
            plugin: 使用的插件，默认 "pyav"

        Returns:
            numpy.ndarray: 视频数据
        """
        return ImageIOWrapper.read_image(source, index=frame_index, plugin=plugin)

    @staticmethod
    def iterate_video(source: str | Path, plugin: str = "pyav"):
        """
        迭代读取视频帧（适合大文件）

        Args:
            source: 视频文件路径
            plugin: 使用的插件

        Yields:
            numpy.ndarray: 每一帧的数据
        """
        for frame in iio.imiter(source, plugin=plugin):
            yield frame

    @staticmethod
    def read_folder(
        folder_path: str | Path, extensions: list[str] | None = None
    ) -> list[np.ndarray]:
        """
        读取文件夹中的所有图片

        Args:
            folder_path: 文件夹路径
            extensions: 允许的文件扩展名列表，默认常见图片格式

        Returns:
            List[np.ndarray]: 图片数据列表
        """
        if extensions is None:
            extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif"]

        folder = Path(folder_path)
        images = []

        for file_path in sorted(folder.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                try:
                    img = ImageIOWrapper.read_image(file_path)
                    images.append(img)
                except Exception as e:
                    print(f"跳过文件 {file_path}: {e}")

        return images

    @staticmethod
    def read_from_web(url: str, **kwargs) -> np.ndarray:
        """
        从网络URL读取图片

        Args:
            url: 图片URL
            **kwargs: 其他参数

        Returns:
            numpy.ndarray: 图片数据
        """
        return ImageIOWrapper.read_image(url, **kwargs)

    @staticmethod
    def read_from_bytes(data: bytes, extension: str, **kwargs) -> np.ndarray:
        """
        从字节数据读取图片

        Args:
            data: 图片字节数据
            extension: 文件扩展名（用于格式识别）
            **kwargs: 其他参数

        Returns:
            numpy.ndarray: 图片数据
        """
        byte_stream = io.BytesIO(data)
        return ImageIOWrapper.read_image(byte_stream, **kwargs)

    @staticmethod
    def capture_screen() -> np.ndarray:
        """
        截取屏幕（Windows和macOS支持）

        Returns:
            numpy.ndarray: 屏幕截图数据
        """
        return ImageIOWrapper.read_image("<screen>")

    @staticmethod
    def read_clipboard() -> np.ndarray:
        """
        从剪贴板读取图片（仅Windows支持）

        Returns:
            numpy.ndarray: 剪贴板图片数据
        """
        return ImageIOWrapper.read_image("<clipboard>")

    @staticmethod
    def capture_webcam(device_index: int = 0, num_frames: int = 1):
        """
        从摄像头捕获帧

        Args:
            device_index: 设备索引
            num_frames: 捕获帧数

        Yields:
            numpy.ndarray: 摄像头帧数据
        """
        device_name = f"<video{device_index}>"
        frame_count = 0

        for frame in iio.imiter(device_name):
            yield frame
            frame_count += 1
            if frame_count >= num_frames:
                break

    @staticmethod
    def write_image(
        image: np.ndarray,
        destination: str | Path | io.BytesIO,
        extension: str | None = None,
        quality: int | None = None,
        **kwargs,
    ) -> bytes | None:
        """
        写入图片的通用函数

        Args:
            image: 图片数据
            destination: 目标路径或 "<bytes>" 或 BytesIO对象
            extension: 文件扩展名（当destination为"<bytes>"时必需）
            quality: 图片质量（适用于JPEG等格式）
            **kwargs: 其他参数

        Returns:
            Optional[bytes]: 当destination为"<bytes>"时返回字节数据
        """
        if quality:
            kwargs["quality"] = quality
        if extension:
            kwargs["extension"] = extension

        return iio.imwrite(destination, image, **kwargs)

    @staticmethod
    def write_gif(
        images: list[np.ndarray],
        destination: str | Path,
        fps: float = 5.0,
        duration: float | None = None,
        **kwargs,
    ) -> None:
        """
        创建GIF动画

        Args:
            images: 图片帧列表
            destination: 输出路径
            fps: 帧率
            duration: 每帧持续时间（秒），优先级高于fps
            **kwargs: 其他参数
        """
        frames = np.stack(images, axis=0)
        if duration:
            kwargs["duration"] = duration
        else:
            kwargs["fps"] = fps

        iio.imwrite(destination, frames, **kwargs)

    @staticmethod
    def write_video(
        frames: list[np.ndarray] | np.ndarray,
        destination: str | Path,
        fps: float = 30.0,
        codec: str = "libx264",
        **kwargs,
    ) -> None:
        """
        创建视频文件

        Args:
            frames: 视频帧数据
            destination: 输出路径
            fps: 帧率
            codec: 视频编码器
            **kwargs: 其他参数
        """
        if isinstance(frames, list):
            frames = np.stack(frames, axis=0)

        kwargs["fps"] = fps
        kwargs["codec"] = codec

        iio.imwrite(destination, frames, **kwargs)

    @staticmethod
    def get_metadata(source: str | Path, exclude_applied: bool = True) -> dict:
        """
        获取图片/视频元数据

        Args:
            source: 文件路径
            exclude_applied: 是否排除已应用的变换

        Returns:
            dict: 元数据字典
        """
        return iio.immeta(source, exclude_applied=exclude_applied)

    @staticmethod
    def get_properties(source: str | Path):
        """
        获取标准化的图片属性

        Args:
            source: 文件路径

        Returns:
            ImageProperties: 标准化属性对象
        """
        return iio.improps(source)

    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        将彩色图片转换为灰度图

        Args:
            image: 输入图片

        Returns:
            numpy.ndarray: 灰度图片
        """
        if len(image.shape) == 3 and image.shape[2] == 3:
            # RGB转灰度的标准权重
            gray = np.dot(image, [0.2989, 0.5870, 0.1140])
            return np.round(gray).astype(np.uint8)
        return image

    @staticmethod
    def resize_image(
        image: np.ndarray, new_size: tuple[int, int], interpolation: str = "bilinear"
    ) -> np.ndarray:
        """
        调整图片大小（需要额外的图像处理库如PIL或opencv）
        这里提供一个简单的最近邻插值实现

        Args:
            image: 输入图片
            new_size: 新尺寸 (height, width)
            interpolation: 插值方法

        Returns:
            numpy.ndarray: 调整后的图片
        """
        # 简单的最近邻插值实现
        old_h, old_w = image.shape[:2]
        new_h, new_w = new_size

        # 计算缩放比例
        row_scale = old_h / new_h
        col_scale = old_w / new_w

        # 创建新图片
        if len(image.shape) == 3:
            new_image = np.zeros((new_h, new_w, image.shape[2]), dtype=image.dtype)
        else:
            new_image = np.zeros((new_h, new_w), dtype=image.dtype)

        for i in range(new_h):
            for j in range(new_w):
                old_i = int(i * row_scale)
                old_j = int(j * col_scale)
                new_image[i, j] = image[old_i, old_j]

        return new_image


# 使用示例
if __name__ == "__main__":
    # 创建包装器实例
    img_io = ImageIOWrapper()

    # 读取标准测试图片
    cat_image = img_io.read_image("chelsea.png")
    print(f"猫咪图片形状: {cat_image.shape}")

    # 读取GIF
    gif_frames = img_io.read_gif("newtonscradle.gif")
    print(f"GIF帧数和形状: {gif_frames.shape}")

    # 转换为灰度图
    gray_cat = img_io.convert_to_grayscale(cat_image)

    # 保存图片
    img_io.write_image(gray_cat, "gray_cat.png")

    # 获取元数据
    metadata = img_io.get_metadata("imageio:chelsea.png")
    print(f"图片元数据: {metadata}")

    # 创建简单的GIF
    frames = [cat_image, gray_cat, cat_image]
    img_io.write_gif(frames, "cat_animation.gif", fps=2)

    print("所有示例执行完成！")
