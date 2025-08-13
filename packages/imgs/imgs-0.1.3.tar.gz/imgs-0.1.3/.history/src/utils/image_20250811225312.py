from pathlib import Path

import imageio.v3 as iio
from PIL import Image


def read_example_image(name: str = "") -> Image.Image:
    """Read an image from a file or URL."""
    return iio.imread(path)
