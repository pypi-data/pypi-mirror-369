"""
Utils - A comprehensive utility library for Python.

This package provides elegant and powerful utilities for common programming tasks,
with a focus on image processing, data manipulation, and developer productivity.

Example usage:
    >>> from utils import load_image, save_image, ImageProcessor
    >>> img = load_image("photo.jpg")
    >>> gray = ImageProcessor.to_grayscale(img)
    >>> save_image(gray, "gray_photo.png")
"""

from .utils import *  # noqa: F403

# Import version info if available
try:
    from importlib.metadata import version

    __version__ = version("utils")
except ImportError:
    __version__ = "unknown"

# Public API - explicitly define what's available for import
__all__ = [
    # Image processing core classes
    "ImageResource",
    "ImageWriter",
    "ImageProcessor",
    "ImageInfo",
    # Convenience functions
    "read_image",
    "write_image",
    "load_image",
    "save_image",
]
