from pathlib import Path

import imageio.v3 as iio
from PIL import Image


def read_example_image(name: str = "chelsea.png" | "bricks.jpg" | "wood.jpg" |) -> Image.Image:

    return iio.imread(path)
