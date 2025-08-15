from abc import ABC, abstractmethod
from typing import Tuple

import cv2
import numpy as np


class MooneyTechnique(ABC):
    """Base class for all Mooney image techniques."""

    _last_smoothing_kernel_size: None
    _last_threshold: None

    def __init__(self):
        self._last_smoothing_kernel_size = None
        self._last_threshold = None

    def grayscale_conversion(self, image: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def scale_down(self, image: np.ndarray) -> np.ndarray:
        """Scale down the image so that no dimension is larger than 1024 pixels."""
        max_dimension = max(image.shape[0], image.shape[1])
        if max_dimension <= 1024:
            self.scale_factor = 1.0
            return image
        self.scale_factor = 1024 / max_dimension
        new_width = int(image.shape[1] * self.scale_factor)
        new_height = int(image.shape[0] * self.scale_factor)
        return cv2.resize(image, (new_width, new_height))

    def scale_up(self, image: np.ndarray) -> np.ndarray:
        """Scale up the image to the original size."""
        new_width = int(image.shape[1] / self.scale_factor)
        new_height = int(image.shape[0] / self.scale_factor)
        return cv2.resize(image, (new_width, new_height))

    @abstractmethod
    def process(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Convert the given image to a Mooney image using the technique."""
        pass
