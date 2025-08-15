from abc import abstractmethod

import cv2
import numpy as np
from skimage import feature, metrics

from .base import MooneyTechnique


class SimpleThresholdBasedTechnique(MooneyTechnique):
    def __init__(self, smoothing_kernel_size: int = 15):
        self.smoothing_kernel_size = smoothing_kernel_size
        super().__init__()

    @abstractmethod
    def compute_threshold(self, grayscale_image: np.ndarray):
        "Compute the threshold for the given image"
        pass

    def process(self, image):
        """Convert the given image to a Mooney image"""
        image = self.scale_down(image)
        grayscale_image = self.grayscale_conversion(image)
        self._last_smoothing_kernel_size = self.smoothing_kernel_size
        smoothed_image = cv2.GaussianBlur(
            grayscale_image, (self.smoothing_kernel_size, self.smoothing_kernel_size), 0
        )
        threshold = self.compute_threshold(grayscale_image)
        self._last_threshold = threshold
        thresholded_image = np.where(smoothed_image > threshold, 1, 0).astype(np.uint8)
        return grayscale_image, smoothed_image, self.scale_up(thresholded_image)


class MeanThresholdTechnique(SimpleThresholdBasedTechnique):
    def compute_threshold(self, grayscale_image):
        return int(np.floor(np.mean(grayscale_image)))


class OtsusThresholdTechnique(SimpleThresholdBasedTechnique):
    def compute_threshold(self, grayscale_image):
        threshold, _ = cv2.threshold(
            grayscale_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return threshold


class CannyEdgeSimilarityThresholdTechnique(SimpleThresholdBasedTechnique):
    """This class implements a thresholding method that tries to maximize the
    edge similarity between the thresholded image and the original image. It was used in Reining and Wallis (2024) but is now replaced by CannyEdgeSimilarityTechnique in `edge_optimization_techniques.py`
    """

    def __init__(self, smoothing_kernel_size=15, canny_std=1):
        super().__init__(smoothing_kernel_size)
        self.canny_std = canny_std

    def compute_threshold(self, grayscale_image):
        threshold = 0
        error = np.inf
        img_edges = feature.canny(grayscale_image, self.canny_std)
        for t in np.unique(grayscale_image.flatten()):
            thresholded = grayscale_image > t
            thresholded_edges = feature.canny(thresholded, self.canny_std)
            # mse not working due to smoothing, if smoothing is disabled, mse
            # works but gives different results
            # new_error = metrics.mean_squared_error(img_edges, thresholded_edges)
            new_error = metrics.hausdorff_distance(img_edges, thresholded_edges)
            if new_error < error:
                threshold = t
                error = new_error
        return threshold


class CannyMaxEdgeThresholdTechnique(SimpleThresholdBasedTechnique):
    """This class implements a thresholding method that tries to maximize the
    number of edges in the thresholded image."""

    def __init__(self, smoothing_kernel_size=15, canny_std=1):
        super().__init__(smoothing_kernel_size)
        self.canny_std = canny_std

    def compute_threshold(self, grayscale_image):
        threshold = 0
        n_edge_pixels = -np.inf
        for t in np.unique(grayscale_image.flatten()):
            thresholded = grayscale_image > t
            thresholded_edges = feature.canny(thresholded, self.canny_std)
            new_n_edge_pixels = thresholded_edges.sum()
            if n_edge_pixels < new_n_edge_pixels:
                threshold = t
                n_edge_pixels = new_n_edge_pixels
        return threshold
