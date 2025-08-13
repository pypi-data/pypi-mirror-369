import imageio.v3 as iio


def read_image(path: str | Path) -> Image.Image:
    return iio.imread(path)
