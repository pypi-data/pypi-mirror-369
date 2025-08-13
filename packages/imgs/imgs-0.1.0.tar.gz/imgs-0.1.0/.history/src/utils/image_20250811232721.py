"""
Elegant ImageIO Wrapper - A comprehensive and user-friendly interface for ImageIO operations.

This module provides a clean, intuitive API for reading, writing, and processing images
from various sources including files, web servers, streams, and special devices.
"""

import io
import warnings
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import imageio.v3 as iio
import numpy as np


@dataclass
class ImageInfo:
    """Container for image metadata and properties."""

    shape: tuple[int, ...]
    dtype: np.dtype
    mode: str | None = None
    format: str | None = None
    metadata: dict[str, Any] | None = None


class ImageResource:
    """
    Elegant wrapper for ImageIO with support for diverse image resources.

    This class provides a unified interface for reading and writing images from
    various sources including local files, web URLs, byte streams, ZIP archives,
    webcams, screenshots, and clipboard.
    """

    # Curated collection of standard test images
    STANDARD_IMAGES = {
        # Classic 2D images
        "astronaut": "astronaut.png",
        "camera": "camera.png",
        "checkerboard": "checkerboard.png",
        "chelsea": "chelsea.png",
        "clock": "clock.png",
        "coffee": "coffee.png",
        "coins": "coins.png",
        "horse": "horse.png",
        "hubble": "hubble_deep_field.png",
        "immunohistochemistry": "immunohistochemistry.png",
        "moon": "moon.png",
        "page": "page.png",
        "text": "text.png",
        "wikkie": "wikkie.png",
        # Textures
        "bricks": "bricks.jpg",
        "meadow_cube": "meadow_cube.jpg",
        "wood": "wood.jpg",
        # Animated content
        "newtonscradle": "newtonscradle.gif",
        "cockatoo": "cockatoo.mp4",
        "cockatoo_yuv420": "cockatoo_yuv420.mp4",
        # Volumetric data
        "stent": "stent.npz",
        "bacterial_colony": "bacterial_colony.tif",
        # Archive formats
        "chelsea_bsdf": "chelsea.bsdf",
        "chelsea_zip": "chelsea.zip",
    }

    @classmethod
    def from_file(cls, path: str | Path, **kwargs) -> np.ndarray:
        """
        Read image from local file system.

        Args:
            path: File path (relative, absolute, or URI format)
            **kwargs: Additional parameters for imageio.imread

        Returns:
            Image data as numpy array

        Examples:
            >>> img = ImageResource.from_file("image.jpg")
            >>> img = ImageResource.from_file("/absolute/path/image.png")
            >>> img = ImageResource.from_file("file:///path/to/image.jpg")
        """
        return iio.imread(path, **kwargs)

    @classmethod
    def from_standard(cls, name: str, **kwargs) -> np.ndarray:
        """
        Load a standard test image from ImageIO's curated collection.

        Args:
            name: Short name or full filename of standard image
            **kwargs: Additional parameters for imageio.imread

        Returns:
            Image data as numpy array

        Examples:
            >>> cat = ImageResource.from_standard('chelsea')
            >>> astronaut = ImageResource.from_standard('astronaut')
            >>> gif = ImageResource.from_standard('newtonscradle')
        """
        if name in cls.STANDARD_IMAGES:
            filename = cls.STANDARD_IMAGES[name]
        elif any(name == img for img in cls.STANDARD_IMAGES.values()):
            filename = name
        else:
            raise ValueError(
                f"Unknown standard image: {name}. Available: {list(cls.STANDARD_IMAGES.keys())}"
            )

        return iio.imread(f"imageio:{filename}", **kwargs)

    @classmethod
    def from_url(cls, url: str, **kwargs) -> np.ndarray:
        """
        Read image from web server (HTTP/HTTPS) or FTP server.

        Args:
            url: Complete URL to the image resource
            **kwargs: Additional parameters for imageio.imread

        Returns:
            Image data as numpy array

        Examples:
            >>> img = ImageResource.from_url("https://example.com/image.jpg")
            >>> img = ImageResource.from_url("ftp://server.com/path/image.png")
        """
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https", "ftp", "ftps"):
            raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")

        return iio.imread(url, **kwargs)

    @classmethod
    def from_bytes(cls, data: bytes, extension: str = None, **kwargs) -> np.ndarray:
        """
        Read image from byte data.

        Args:
            data: Raw image bytes
            extension: File extension hint for format detection
            **kwargs: Additional parameters for imageio.imread

        Returns:
            Image data as numpy array

        Examples:
            >>> with open("image.jpg", "rb") as f:
            ...     img = ImageResource.from_bytes(f.read(), ".jpg")
        """
        if extension and not extension.startswith("."):
            extension = f".{extension}"

        byte_stream = io.BytesIO(data)
        if extension:
            kwargs.setdefault("extension", extension)

        return iio.imread(byte_stream, **kwargs)

    @classmethod
    def from_stream(cls, stream: io.IOBase, **kwargs) -> np.ndarray:
        """
        Read image from file-like object or byte stream.

        Args:
            stream: File handle, BytesIO, or any object with read() method
            **kwargs: Additional parameters for imageio.imread

        Returns:
            Image data as numpy array

        Examples:
            >>> with open("image.jpg", "rb") as f:
            ...     img = ImageResource.from_stream(f)
            >>>
            >>> stream = io.BytesIO(image_bytes)
            >>> img = ImageResource.from_stream(stream)
        """
        return iio.imread(stream, **kwargs)

    @classmethod
    def from_zip(cls, zip_path: str | Path, internal_path: str, **kwargs) -> np.ndarray:
        """
        Read image directly from ZIP archive without extraction.

        Args:
            zip_path: Path to ZIP file
            internal_path: Path to image inside the ZIP archive
            **kwargs: Additional parameters for imageio.imread

        Returns:
            Image data as numpy array

        Examples:
            >>> img = ImageResource.from_zip("archive.zip", "images/photo.jpg")
        """
        full_path = f"{zip_path}/{internal_path}"
        return iio.imread(full_path, **kwargs)

    @classmethod
    def from_webcam(cls, device_id: int = 0, **kwargs) -> np.ndarray:
        """
        Capture single frame from webcam.

        Note: Requires ffmpeg backend: pip install imageio[ffmpeg]

        Args:
            device_id: Camera device index (0 for primary camera)
            **kwargs: Additional parameters for imageio.imread

        Returns:
            Single frame as numpy array

        Examples:
            >>> frame = ImageResource.from_webcam()  # Primary camera
            >>> frame = ImageResource.from_webcam(1)  # Secondary camera
        """
        return iio.imread(f"<video{device_id}>", **kwargs)

    @classmethod
    def from_screen(cls, **kwargs) -> np.ndarray:
        """
        Capture screenshot (Windows and macOS only).

        Args:
            **kwargs: Additional parameters for imageio.imread

        Returns:
            Screenshot as numpy array

        Examples:
            >>> screenshot = ImageResource.from_screen()
        """
        return iio.imread("<screen>", **kwargs)

    @classmethod
    def from_clipboard(cls, **kwargs) -> np.ndarray:
        """
        Read image from clipboard (Windows only).

        Args:
            **kwargs: Additional parameters for imageio.imread

        Returns:
            Clipboard image as numpy array

        Examples:
            >>> img = ImageResource.from_clipboard()
        """
        return iio.imread("<clipboard>", **kwargs)

    @classmethod
    def stream_webcam(
        cls, device_id: int = 0, max_frames: int | None = None
    ) -> Generator[np.ndarray, None, None]:
        """
        Stream frames from webcam for real-time processing.

        Args:
            device_id: Camera device index
            max_frames: Maximum number of frames to capture (None for infinite)

        Yields:
            Camera frames as numpy arrays

        Examples:
            >>> for frame in ImageResource.stream_webcam():
            ...     process_frame(frame)
            ...     if should_stop():
            ...         break
        """
        frame_count = 0
        for frame in iio.imiter(f"<video{device_id}>"):
            yield frame
            frame_count += 1
            if max_frames and frame_count >= max_frames:
                break

    @classmethod
    def stream_video(
        cls, source: str | Path, plugin: str = "pyav"
    ) -> Generator[np.ndarray, None, None]:
        """
        Stream video frames for memory-efficient processing.

        Args:
            source: Video file path or URL
            plugin: Backend plugin ("pyav" recommended for videos)

        Yields:
            Video frames as numpy arrays

        Examples:
            >>> for frame in ImageResource.stream_video("movie.mp4"):
            ...     processed = apply_filter(frame)
            ...     save_frame(processed)
        """
        for frame in iio.imiter(source, plugin=plugin):
            yield frame

    @staticmethod
    def get_info(source: str | Path, **kwargs) -> ImageInfo:
        """
        Retrieve comprehensive image information without loading pixel data.

        Args:
            source: Image source (path, URL, etc.)
            **kwargs: Additional parameters

        Returns:
            ImageInfo object with metadata and properties

        Examples:
            >>> info = ImageResource.get_info("image.jpg")
            >>> print(f"Shape: {info.shape}, Format: {info.format}")
        """
        try:
            props = iio.improps(source, **kwargs)
            metadata = iio.immeta(source, **kwargs)

            return ImageInfo(
                shape=props.shape,
                dtype=props.dtype,
                mode=metadata.get("mode"),
                format=metadata.get("format"),
                metadata=metadata,
            )
        except Exception as e:
            warnings.warn(f"Could not retrieve complete info: {e}")
            # Fallback to basic info
            temp_img = iio.imread(source, **kwargs)
            return ImageInfo(shape=temp_img.shape, dtype=temp_img.dtype)


class ImageWriter:
    """Elegant interface for writing images to various destinations."""

    @staticmethod
    def to_file(image: np.ndarray, path: str | Path, quality: int | None = None, **kwargs) -> None:
        """
        Save image to file with automatic format detection.

        Args:
            image: Image data as numpy array
            path: Output file path
            quality: Compression quality (1-100 for JPEG)
            **kwargs: Additional parameters for imageio.imwrite

        Examples:
            >>> ImageWriter.to_file(image, "output.jpg", quality=95)
            >>> ImageWriter.to_file(image, "output.png")
        """
        if quality is not None:
            kwargs["quality"] = quality
        iio.imwrite(path, image, **kwargs)

    @staticmethod
    def to_bytes(image: np.ndarray, format_ext: str, quality: int | None = None, **kwargs) -> bytes:
        """
        Encode image to bytes in specified format.

        Args:
            image: Image data as numpy array
            format_ext: Target format extension (e.g., ".jpg", ".png")
            quality: Compression quality for lossy formats
            **kwargs: Additional parameters for imageio.imwrite

        Returns:
            Encoded image as bytes

        Examples:
            >>> jpg_bytes = ImageWriter.to_bytes(image, ".jpg", quality=90)
            >>> png_bytes = ImageWriter.to_bytes(image, ".png")
        """
        if not format_ext.startswith("."):
            format_ext = f".{format_ext}"

        if quality is not None:
            kwargs["quality"] = quality
        kwargs["extension"] = format_ext

        return iio.imwrite("<bytes>", image, **kwargs)

    @staticmethod
    def to_stream(image: np.ndarray, stream: io.IOBase, format_ext: str, **kwargs) -> None:
        """
        Write image to file-like object.

        Args:
            image: Image data as numpy array
            stream: Output stream (BytesIO, file handle, etc.)
            format_ext: Target format extension
            **kwargs: Additional parameters for imageio.imwrite

        Examples:
            >>> output = io.BytesIO()
            >>> ImageWriter.to_stream(image, output, ".png")
        """
        if not format_ext.startswith("."):
            format_ext = f".{format_ext}"
        kwargs["extension"] = format_ext

        iio.imwrite(stream, image, **kwargs)

    @staticmethod
    def create_gif(
        frames: list[np.ndarray],
        output_path: str | Path,
        duration: float = 0.5,
        loop: int = 0,
        auto_resize: bool = True,
        target_size: tuple[int, int] | None = None,
        **kwargs,
    ) -> None:
        """
        Create animated GIF from image sequence.

        Args:
            frames: List of image frames
            output_path: Output GIF file path
            duration: Duration per frame in seconds
            loop: Number of loops (0 for infinite)
            auto_resize: Whether to automatically resize frames to match
            target_size: Target size (height, width). If None, uses first frame's size
            **kwargs: Additional parameters for imageio.imwrite

        Examples:
            >>> frames = [img1, img2, img3]
            >>> ImageWriter.create_gif(frames, "animation.gif", duration=0.3)
            >>> ImageWriter.create_gif(frames, "animation.gif", target_size=(256, 256))
        """
        if auto_resize:
            frames = ImageProcessor.ensure_same_shape(frames, target_size)

        frame_stack = np.stack(frames, axis=0)
        kwargs.update({"duration": duration, "loop": loop})
        iio.imwrite(output_path, frame_stack, **kwargs)

    @staticmethod
    def create_video(
        frames: list[np.ndarray] | np.ndarray,
        output_path: str | Path,
        fps: float = 30.0,
        codec: str = "libx264",
        auto_resize: bool = True,
        target_size: tuple[int, int] | None = None,
        **kwargs,
    ) -> None:
        """
        Create video file from frame sequence.

        Args:
            frames: Frame sequence as list or 4D numpy array
            output_path: Output video file path
            fps: Frames per second
            codec: Video codec (e.g., 'libx264', 'libx265')
            auto_resize: Whether to automatically resize frames to match
            target_size: Target size (height, width). If None, uses first frame's size
            **kwargs: Additional parameters for imageio.imwrite

        Examples:
            >>> ImageWriter.create_video(frames, "output.mp4", fps=24)
            >>> ImageWriter.create_video(frames, "output.webm", codec='libvpx-vp9')
        """
        if isinstance(frames, list):
            if auto_resize:
                frames = ImageProcessor.ensure_same_shape(frames, target_size)
            frames = np.stack(frames, axis=0)

        kwargs.update({"fps": fps, "codec": codec})
        iio.imwrite(output_path, frames, **kwargs)


class ImageProcessor:
    """Collection of elegant image processing utilities."""

    @staticmethod
    def to_grayscale(
        image: np.ndarray, weights: tuple[float, float, float] = (0.299, 0.587, 0.114)
    ) -> np.ndarray:
        """
        Convert color image to grayscale using luminance weights.

        Args:
            image: Input color image
            weights: RGB luminance weights (default: ITU-R BT.601)

        Returns:
            Grayscale image as numpy array

        Examples:
            >>> gray = ImageProcessor.to_grayscale(color_image)
            >>> gray_custom = ImageProcessor.to_grayscale(image, weights=(0.2126, 0.7152, 0.0722))
        """
        if len(image.shape) == 3 and image.shape[2] >= 3:
            luminance = np.dot(image[..., :3], weights)
            # Ensure the output has the same number of channels as input for consistency
            if image.shape[2] == 4:  # RGBA
                gray_rgba = np.zeros_like(image)
                gray_rgba[..., :3] = np.stack([luminance] * 3, axis=-1)
                gray_rgba[..., 3] = image[..., 3]  # Keep alpha channel
                return gray_rgba.astype(image.dtype)
            else:  # RGB
                return np.stack([luminance] * 3, axis=-1).astype(image.dtype)
        return image

    @staticmethod
    def resize(
        image: np.ndarray, target_size: tuple[int, int], method: str = "nearest"
    ) -> np.ndarray:
        """
        Resize image to target dimensions using specified interpolation.

        Args:
            image: Input image
            target_size: Target size as (height, width)
            method: Interpolation method ('nearest', 'bilinear')

        Returns:
            Resized image

        Examples:
            >>> resized = ImageProcessor.resize(image, (256, 256))
            >>> resized = ImageProcessor.resize(image, (512, 512), 'bilinear')
        """
        old_h, old_w = image.shape[:2]
        new_h, new_w = target_size

        if old_h == new_h and old_w == new_w:
            return image.copy()

        # Calculate scaling factors
        h_scale = old_h / new_h
        w_scale = old_w / new_w

        # Create coordinate grids
        y_coords = np.arange(new_h) * h_scale
        x_coords = np.arange(new_w) * w_scale

        if method == "nearest":
            y_coords = np.round(y_coords).astype(int)
            x_coords = np.round(x_coords).astype(int)

            # Clip coordinates to valid range
            y_coords = np.clip(y_coords, 0, old_h - 1)
            x_coords = np.clip(x_coords, 0, old_w - 1)

            # Create new image
            if len(image.shape) == 3:
                new_image = np.zeros((new_h, new_w, image.shape[2]), dtype=image.dtype)
                for i in range(new_h):
                    for j in range(new_w):
                        new_image[i, j] = image[y_coords[i], x_coords[j]]
            else:
                new_image = np.zeros((new_h, new_w), dtype=image.dtype)
                for i in range(new_h):
                    for j in range(new_w):
                        new_image[i, j] = image[y_coords[i], x_coords[j]]

        elif method == "bilinear":
            # Simple bilinear interpolation
            y_floor = np.floor(y_coords).astype(int)
            x_floor = np.floor(x_coords).astype(int)
            y_ceil = np.minimum(y_floor + 1, old_h - 1)
            x_ceil = np.minimum(x_floor + 1, old_w - 1)

            # Weights for interpolation
            y_weight = y_coords - y_floor
            x_weight = x_coords - x_floor

            if len(image.shape) == 3:
                new_image = np.zeros((new_h, new_w, image.shape[2]), dtype=image.dtype)
            else:
                new_image = np.zeros((new_h, new_w), dtype=image.dtype)

            for i in range(new_h):
                for j in range(new_w):
                    # Get the four surrounding pixels
                    top_left = image[y_floor[i], x_floor[j]]
                    top_right = image[y_floor[i], x_ceil[j]]
                    bottom_left = image[y_ceil[i], x_floor[j]]
                    bottom_right = image[y_ceil[i], x_ceil[j]]

                    # Bilinear interpolation
                    top = top_left * (1 - x_weight[j]) + top_right * x_weight[j]
                    bottom = bottom_left * (1 - x_weight[j]) + bottom_right * x_weight[j]
                    new_image[i, j] = top * (1 - y_weight[i]) + bottom * y_weight[i]
        else:
            raise ValueError(f"Unsupported resize method: {method}")

        return new_image.astype(image.dtype)

    @staticmethod
    def ensure_same_shape(
        images: list[np.ndarray],
        target_size: tuple[int, int] | None = None,
        resize_method: str = "nearest",
    ) -> list[np.ndarray]:
        """
        Ensure all images have the same shape for stacking operations.

        Args:
            images: List of input images
            target_size: Target size (height, width). If None, uses the first image's size
            resize_method: Interpolation method for resizing

        Returns:
            List of images with consistent shapes

        Examples:
            >>> consistent_imgs = ImageProcessor.ensure_same_shape(mixed_size_images)
            >>> consistent_imgs = ImageProcessor.ensure_same_shape(images, (256, 256))
        """
        if not images:
            return images

        if target_size is None:
            target_size = images[0].shape[:2]

        result = []
        target_channels = max(img.shape[2] if len(img.shape) == 3 else 1 for img in images)

        for img in images:
            # Resize to target dimensions
            resized = ImageProcessor.resize(img, target_size, resize_method)

            # Ensure consistent channel count
            if len(resized.shape) == 2 and target_channels > 1:
                # Convert grayscale to RGB/RGBA
                if target_channels == 3:
                    resized = np.stack([resized] * 3, axis=-1)
                elif target_channels == 4:
                    rgb = np.stack([resized] * 3, axis=-1)
                    alpha = np.full(resized.shape, 255, dtype=resized.dtype)
                    resized = np.stack([rgb[..., 0], rgb[..., 1], rgb[..., 2], alpha], axis=-1)
            elif len(resized.shape) == 3 and resized.shape[2] < target_channels:
                # Add alpha channel if needed
                if resized.shape[2] == 3 and target_channels == 4:
                    alpha = np.full(resized.shape[:2], 255, dtype=resized.dtype)
                    resized = np.concatenate([resized, alpha[..., np.newaxis]], axis=-1)

            result.append(resized)

        return result

    @staticmethod
    def normalize(image: np.ndarray, target_range: tuple[float, float] = (0.0, 1.0)) -> np.ndarray:
        """
        Normalize image values to specified range.

        Args:
            image: Input image
            target_range: Target value range (min, max)

        Returns:
            Normalized image

        Examples:
            >>> normalized = ImageProcessor.normalize(image)  # [0, 1]
            >>> scaled = ImageProcessor.normalize(image, (-1, 1))  # [-1, 1]
        """
        min_val, max_val = target_range
        img_min, img_max = image.min(), image.max()

        if img_max == img_min:
            return np.full_like(image, min_val)

        normalized = (image - img_min) / (img_max - img_min)
        return normalized * (max_val - min_val) + min_val

    @staticmethod
    def batch_process(
        images: list[np.ndarray], processor_func: callable, *args, **kwargs
    ) -> list[np.ndarray]:
        """
        Apply processing function to batch of images.

        Args:
            images: List of input images
            processor_func: Processing function to apply
            *args, **kwargs: Arguments for processor function

        Returns:
            List of processed images

        Examples:
            >>> grays = ImageProcessor.batch_process(images, ImageProcessor.to_grayscale)
            >>> normalized = ImageProcessor.batch_process(images, ImageProcessor.normalize)
        """
        return [processor_func(img, *args, **kwargs) for img in images]


# Convenience functions for backward compatibility and ease of use
def read_image(source: str | Path | bytes | io.IOBase, **kwargs) -> np.ndarray:
    """Unified image reading function with automatic source detection."""
    if isinstance(source, bytes):
        return ImageResource.from_bytes(source, **kwargs)
    elif hasattr(source, "read"):
        return ImageResource.from_stream(source, **kwargs)
    elif isinstance(source, (str, Path)):
        source_str = str(source)
        if source_str.startswith(("http://", "https://", "ftp://", "ftps://")):
            return ImageResource.from_url(source_str, **kwargs)
        elif source_str in ImageResource.STANDARD_IMAGES:
            return ImageResource.from_standard(source_str, **kwargs)
        else:
            return ImageResource.from_file(source, **kwargs)
    else:
        raise ValueError(f"Unsupported source type: {type(source)}")


def write_image(image: np.ndarray, destination: str | Path, **kwargs) -> None:
    """Unified image writing function."""
    ImageWriter.to_file(image, destination, **kwargs)


# Usage examples and demonstrations
if __name__ == "__main__":
    # Demonstrate elegant usage patterns

    # Load standard test images
    cat = ImageResource.from_standard("chelsea")
    astronaut = ImageResource.from_standard("astronaut")

    # Process images elegantly
    gray_cat = ImageProcessor.to_grayscale(cat)
    normalized_astronaut = ImageProcessor.normalize(astronaut)

    # Create animated content
    frames = [cat, gray_cat, cat]
    ImageWriter.create_gif(frames, "elegant_animation.gif", duration=0.5)

    # Get comprehensive image information
    info = ImageResource.get_info("imageio:chelsea.png")
    print(f"Image info: {info.shape}, {info.dtype}, {info.mode}")

    # Demonstrate batch processing
    images = [cat, astronaut]
    grayscale_batch = ImageProcessor.batch_process(images, ImageProcessor.to_grayscale)

    # Save with different formats and quality
    ImageWriter.to_file(gray_cat, "elegant_gray.jpg", quality=95)
    ImageWriter.to_file(normalized_astronaut, "elegant_normalized.png")

    print("✨ Elegant ImageIO operations completed successfully!")
