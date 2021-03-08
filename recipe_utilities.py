import math
import random
import string
import time

import numpy as np
import PIL
from PIL import ImageEnhance


class Timer:
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print(
                "[%s]" % self.name,
            )
        print("Elapsed: %s" % (time.time() - self.tstart))


def get_random_string(length=10):
    """Generate a random string of letters and digits """
    letters_and_digits = string.ascii_lowercase + string.digits
    return "".join(random.choice(letters_and_digits) for i in range(length))


def _noise_to_image(noise_base, width, height, contrast=1, brightness=1):
    noise_image = PIL.Image.fromarray(noise_base * 255)
    noise_image = noise_image.resize((width, height), PIL.Image.BICUBIC)
    noise_image = noise_image.convert("RGBA")
    noise_image = ImageEnhance.Brightness(noise_image).enhance(brightness)
    noise_image = ImageEnhance.Contrast(noise_image).enhance(contrast)
    return noise_image


def generate_gaussian_noise_image(
    image_size, scale=1, seed=None, strength=1, contrast=1, brightness=1
):
    if seed is not None:
        np.random.seed(seed)

    width, height = image_size

    height_base = math.ceil(height / scale)
    width_base = math.ceil(width / scale)

    noise_base = np.random.randn(height_base, width_base) * strength + 0.5

    noise_image = _noise_to_image(
        noise_base, width, height, contrast, brightness
    )

    return noise_image


def generate_uniform_noise_image(
    image_size, scale=1, seed=None, contrast=1, brightness=1
):
    if seed is not None:
        np.random.seed(seed)

    width, height = image_size

    height_base = math.ceil(height / scale)
    width_base = math.ceil(width / scale)

    noise_base = np.random.rand(height_base, width_base)

    noise_image = _noise_to_image(
        noise_base, width, height, contrast, brightness
    )

    return noise_image


def set_random_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
