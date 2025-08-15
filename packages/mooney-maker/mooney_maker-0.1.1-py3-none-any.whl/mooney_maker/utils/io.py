from pathlib import Path
from typing import Union

import cv2
import numpy as np


def load_image(image_path: Union[Path, str]) -> np.ndarray:
    """
    Load an image from the specified path.

    Parameters
    ----------
    image_path : Union[Path, str]
        Path to the image file.

    Returns
    -------
    np.ndarray
        Loaded image as a NumPy array with shape (height, width, 3[BGR])
    """
    if isinstance(image_path, str):
        image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to load image from: {image_path}")

    return image
