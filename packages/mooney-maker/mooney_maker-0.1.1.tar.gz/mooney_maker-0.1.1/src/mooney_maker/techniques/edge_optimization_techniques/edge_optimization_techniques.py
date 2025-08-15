import cv2
import numpy as np

from mooney_maker.techniques.base import MooneyTechnique
from mooney_maker.techniques.edge_optimization_techniques.optimizers import (
    CannyOptimizer,
    DiffusionEdgeOptimizer,
    MooneyOptimizer,
    TEEDOptimizer,
)


class EdgeOptimizationTechnique(MooneyTechnique):
    optimizer: MooneyOptimizer = None

    def process(self, image):
        image = self.scale_down(image)
        result = self.optimizer.find_extremum(image)
        grayscale_image = self.grayscale_conversion(image)
        smoothed_image = cv2.GaussianBlur(
            grayscale_image, (result["kernel_size"], result["kernel_size"]), 0
        )
        thresholded_image = np.where(smoothed_image > result["threshold"], 1, 0).astype(
            np.uint8
        )
        self._last_smoothing_kernel_size = result["kernel_size"]
        self._last_threshold = result["threshold"]
        return grayscale_image, smoothed_image, self.scale_up(thresholded_image)


class TEEDEdgeDisruptionTechnique(EdgeOptimizationTechnique):
    """TEED-based technique that select the kernel size and threshold
    that maximize the differences between the template images edge map
    and the mooney images edge map."""

    def __init__(self):
        super().__init__()
        self.optimizer = TEEDOptimizer(maximize_loss=True)


class TEEDEdgeSimilarityTechnique(EdgeOptimizationTechnique):
    """TEED-based technique that select the kernel size and threshold
    that minimize the differences between the template images edge map
    and the mooney images edge map."""

    def __init__(self):
        super().__init__()
        self.optimizer = TEEDOptimizer(maximize_loss=False)


class DiffusionEdgeSimilarityTechnique(EdgeOptimizationTechnique):
    """DiffusionEdge-based technique that select the kernel size and threshold
    that minimize the differences between the template images edge map
    and the mooney images edge map."""

    def __init__(self, batch_size: int = 16):
        super().__init__()
        self.optimizer = DiffusionEdgeOptimizer(
            maximize_loss=False, batch_size=batch_size
        )


class DiffusionEdgeDisruptionTechnique(EdgeOptimizationTechnique):
    """DiffusionEdge-based technique that select the kernel size and threshold
    that maximize the differences between the template images edge map
    and the mooney images edge map."""

    def __init__(self, batch_size: int = 16):
        super().__init__()
        self.optimizer = DiffusionEdgeOptimizer(
            maximize_loss=True, batch_size=batch_size
        )


class CannyEdgeDisruptionTechnique(EdgeOptimizationTechnique):
    """CannyEdge-based technique that select the kernel size and threshold
    that maximize the differences between the template images edge map
    and the mooney images edge map."""

    def __init__(self, canny_std: int = 1):
        super().__init__()
        self.optimizer = CannyOptimizer(maximize_loss=True, canny_std=canny_std)


class CannyEdgeSimilarityTechnique(EdgeOptimizationTechnique):
    """CannyEdge-based technique that select the kernel size and threshold
    that minimize the differences between the template images edge map
    and the mooney images edge map."""

    def __init__(self, canny_std: int = 1):
        super().__init__()
        self.optimizer = CannyOptimizer(maximize_loss=False, canny_std=canny_std)
