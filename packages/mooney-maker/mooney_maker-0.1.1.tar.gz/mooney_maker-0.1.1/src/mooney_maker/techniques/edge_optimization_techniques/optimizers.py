from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import cv2
import numpy as np
import torch
from skimage import feature, metrics

from mooney_maker.DiffusionEdge.diffedge import get_predictions

from .eval_teed import Evaluate

CURRENT_FOLDER = Path(__file__).parent


class MooneyOptimizer(ABC):
    def __init__(self, maximize_loss: bool = True):
        """Base class for Mooney optimizers.

        Parameters
        ----------
        maximize_loss : bool, optional
            Whether to maximize or minimize the loss, by default True
        """
        self.MAXIMIZE_LOSS = maximize_loss

    def find_extremum(self, image) -> dict:
        """Find kernel size and threshold that maximize/minimize the loss
        for the given image.

        Parameters
        ----------
        image:
            The image to be optimized.

        Returns
        -------
        result:
            Dict of maximum loss with corresponding threshold and kernel size.
        """
        kernels = np.arange(11, 39, step=4, dtype=int)
        threshs = np.arange(20, 190, step=8, dtype=int)
        edge_maps, infos, pixel_ratios = self.iterate_all(image, kernels, threshs)
        template_edge_map, mooney_edge_maps = edge_maps[0], edge_maps[1:]
        losses = self.calculate_loss(template_edge_map, mooney_edge_maps, pixel_ratios)
        opt_loss_index = np.argmax(losses) if self.MAXIMIZE_LOSS else np.argmin(losses)
        kernel_size = infos[opt_loss_index][0]
        threshold = infos[opt_loss_index][1]
        kernel_start = kernel_size - 4
        kernel_end = kernel_size + 4

        if kernel_start < 11:
            kernel_start = 11
        if kernel_end > 39:
            kernel_end = 39

        kernels = np.arange(kernel_start, kernel_end, step=2, dtype=int)
        threshs = np.arange(threshold - 12, threshold + 12, step=1, dtype=int)
        mooney_edge_maps, infos, pixel_ratios = self.iterate_all(
            image, kernels, threshs, compute_template_edge_map=False
        )
        losses = self.calculate_loss(template_edge_map, mooney_edge_maps, pixel_ratios)
        opt_loss_index = np.argmax(losses) if self.MAXIMIZE_LOSS else np.argmin(losses)
        kernel_size = infos[opt_loss_index][0]
        threshold = infos[opt_loss_index][1]
        return {
            "loss": losses[opt_loss_index],
            "kernel_size": kernel_size,
            "threshold": threshold,
        }

    @abstractmethod
    def iterate_all(
        self,
        image: np.ndarray,
        kernels: List[int],
        threshs: List[int],
        compute_template_edge_map: bool = True,
    ) -> tuple[np.ndarray, List[tuple], np.ndarray]:
        """Generate edge maps for all mooney images created by iterating
        through the given kernel sizes and threshold values.

        Parameters
        ----------
        image : np.ndarray
            The image to be optimized.
        kernels : List[int]
            The list of kernel sizes to iterate through.
        threshs : List[int]
            The list of threshold values to iterate through.
        compute_template_edge_map : bool, optional
            Whether to include the template edge map, by default True

        Returns
        -------
        edge_maps : np.ndarray
            The edge maps for each combination of kernel size and threshold.
        infos : List[tuple]
            The kernel size and threshold for each edge map.
        pixel_ratios : np.ndarray
            The pixel ratios for each edge map (ratio of foreground to background pixels).
        """
        pass

    def calculate_loss(
        self,
        template_edge_map: np.ndarray,
        mooney_edge_maps: np.ndarray,
        pixel_ratios: np.ndarray,
    ) -> np.ndarray:
        """Calculate the loss between the template edge map and the mooney edge maps. Per default, the loss is calculated as the modified Hausdorff distance between the edge maps and regularized by the pixel ratios.

        Parameters
        ----------
        template_edge_map: np.ndarray
            The template edge map.
        mooney_edge_maps: np.ndarray
            The edge maps to be compared with the template edge map.
        pixel_ratios: np.ndarray
            The pixel ratios of the mooney images.

        Returns
        -------
        losses: np.ndarray
            The losses for each edge map.
        """
        losses = np.array(
            [
                metrics.hausdorff_distance(
                    template_edge_map,
                    mooney_edge_map,
                    method="modified",
                )
                for mooney_edge_map in mooney_edge_maps
            ]
        )
        np.clip(losses, a_min=0, a_max=100000, out=losses)
        if self.MAXIMIZE_LOSS:
            log_odds = abs(np.log(pixel_ratios + 1e-6))
            c = (losses - losses.min()) / 2
            losses -= c * log_odds
        return losses

    @abstractmethod
    def get_edge_prediction(self, image: np.ndarray) -> np.ndarray:
        """Get the edge map prediction of the image.

        Parameters
        ----------
        image : np.ndarray
            The template image.

        Returns
        -------
        np.ndarray
            The edge map of the template image.
        """
        pass


class CannyOptimizer(MooneyOptimizer):
    def __init__(self, maximize_loss: bool = True, canny_std: int = 1):
        """Performs an optimization routine to select the kernel size and
        threshold that maximize/minimize the differences between the template
        images edge map and the mooney images edge map if the edge maps are created using the Canny edge detector.
        The optimization is done by iterating through all possible kernel sizes and threshold values.

        Parameters
        ----------
        maximize_loss : bool, optional
            Whether to maximize or minimize the differences , by default True
        """
        super().__init__(maximize_loss)
        self.canny_std = canny_std

    def iterate_all(
        self,
        image: np.ndarray,
        kernels: List[int],
        threshs: List[int],
        compute_template_edge_map: bool = True,
    ) -> np.ndarray:
        edge_maps = []
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if compute_template_edge_map:
            edge_maps.append(feature.canny(image_grey, self.canny_std))
        infos = []
        pixel_ratios = []
        for i, kernel_size in enumerate(kernels):
            smoothed_image = cv2.GaussianBlur(image_grey, (kernel_size, kernel_size), 0)

            for j, threshold in enumerate(threshs):
                mooney_img = (
                    np.where(smoothed_image > threshold, 1, 0).astype(np.uint8) * 255
                )
                edge_maps.append(feature.canny(mooney_img, self.canny_std))
                n_foreground = np.sum(mooney_img / 255)
                n_background = len(mooney_img.flatten()) - n_foreground
                if n_foreground == 0 or n_background == 0:
                    pixel_ratios.append(0)
                else:
                    pixel_ratios.append(n_foreground / n_background)
                infos.append((kernel_size, threshold))
        edge_maps = np.array(edge_maps)
        return edge_maps, infos, np.array(pixel_ratios)

    def get_edge_prediction(self, image: np.ndarray) -> np.ndarray:
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return feature.canny(image_grey, self.canny_std)


class TEEDOptimizer(MooneyOptimizer):
    def __init__(self, maximize_loss: bool = True):
        """Performs an optimization routine to select the kernel size and
        threshold that maximize/minimize the differences between the template
        images edge map and the mooney images edge map.
        The optimization is done by iterating through all possible kernel sizes and threshold values.

        Parameters
        ----------
        maximize_loss : bool, optional
            Whether to maximize or minimize the differences , by default True
        """
        self.MAXIMIZE_LOSS = maximize_loss
        self.MODEL = Evaluate(
            CURRENT_FOLDER / ".." / ".." / "TEED" / "checkpoints" / "TEED.pth"
        )

    def iterate_all(
        self,
        image,
        kernels: List[int],
        threshs: List[int],
        compute_template_edge_map: bool = True,
    ) -> dict:
        imgs = []
        img_height, img_width = image.shape[:2]

        while (img_height / 8) % 2 != 0:
            img_height -= 1
        while (img_width / 8) % 2 != 0:
            img_width -= 1
        image = cv2.resize(image, (img_width, img_height))
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if compute_template_edge_map:
            imgs.append(image)
        infos = []
        pixel_ratios = []
        edge_maps = []
        for i, kernel_size in enumerate(kernels):
            blurred_img = cv2.GaussianBlur(image_grey, (kernel_size, kernel_size), 0)

            for j, threshold in enumerate(threshs):
                mooney_img = np.where(blurred_img > threshold, 1, 0).astype(np.uint8)
                n_foreground = np.sum(mooney_img)
                n_background = len(mooney_img.flatten()) - n_foreground
                mooney_img = cv2.cvtColor(mooney_img * 255, cv2.COLOR_GRAY2RGB)
                imgs.append(mooney_img)
                if n_foreground == 0 or n_background == 0:
                    pixel_ratios.append(0)
                else:
                    pixel_ratios.append(n_foreground / n_background)
                infos.append((kernel_size, threshold))
        for img in imgs:
            img = self.MODEL.prepare_input(img)
            edge_map = self.MODEL(img)
            edge_map = self.MODEL.extract_important_map(edge_map)
            edge_maps.append(edge_map)
        return np.array(edge_maps), infos, np.array(pixel_ratios)

    def calculate_loss(
        self,
        template_edge_map: np.ndarray,
        mooney_edge_maps: np.ndarray,
        pixel_ratios: np.ndarray,
    ) -> np.ndarray:
        template_edge_map = template_edge_map > 0.75
        mooney_edge_maps = mooney_edge_maps > 0.75
        return super().calculate_loss(template_edge_map, mooney_edge_maps, pixel_ratios)

    def get_edge_prediction(self, image: np.ndarray) -> np.ndarray:
        image = self.MODEL.prepare_input(image)
        edge_map = self.MODEL(image)
        edge_map = self.MODEL.extract_important_map(edge_map)
        return edge_map > 0.75


class DiffusionEdgeOptimizer(MooneyOptimizer):
    def __init__(self, maximize_loss: bool = True, batch_size: int = 16):
        """Performs an optimization routine to select the kernel size and
        threshold that maximize/minimize the differences between the template
        images edge map and the mooney images edge map if the edge maps are created using the DiffusionEdge model.
        The optimization is done by iterating through all possible kernel sizes and threshold values.

        Parameters
        ----------
        maximize_loss : bool, optional
            Whether to maximize or minimize the differences , by default True
        batch_size : int, optional
            The batch size for the DiffusionEdge model, by default 16
        """
        super().__init__(maximize_loss)
        self.batch_size = batch_size

    def iterate_all(
        self,
        image,
        kernels: List[int],
        threshs: List[int],
        compute_template_edge_map: bool = True,
    ) -> np.ndarray:
        imgs = []
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if compute_template_edge_map:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            imgs.append(image / 255)
        infos = []
        pixel_ratios = []
        for i, kernel_size in enumerate(kernels):
            blurred_img = cv2.GaussianBlur(image_grey, (kernel_size, kernel_size), 0)

            for j, threshold in enumerate(threshs):
                mooney_img = np.where(blurred_img > threshold, 1, 0).astype(np.uint8)
                n_foreground = np.sum(mooney_img)
                n_background = len(mooney_img.flatten()) - n_foreground
                mooney_img = cv2.cvtColor(mooney_img, cv2.COLOR_GRAY2RGB)
                imgs.append(mooney_img)
                if n_foreground == 0 or n_background == 0:
                    pixel_ratios.append(0)
                else:
                    pixel_ratios.append(n_foreground / n_background)
                infos.append((kernel_size, threshold))
        imgs = np.array(imgs).astype(np.float32)
        with torch.no_grad():
            edge_maps = np.array(
                get_predictions(imgs, batch_size=self.batch_size)
            ).squeeze()
        return edge_maps, infos, np.array(pixel_ratios)

    def calculate_loss(
        self,
        template_edge_map: np.ndarray,
        mooney_edge_maps: np.ndarray,
        pixel_ratios: np.ndarray,
    ) -> np.ndarray:
        template_edge_map = template_edge_map > 0.2
        mooney_edge_maps = mooney_edge_maps > 0.2
        return super().calculate_loss(template_edge_map, mooney_edge_maps, pixel_ratios)

    def get_edge_prediction(self, image: np.ndarray) -> np.ndarray:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image.astype(np.float32) / 255
        with torch.no_grad():
            edge_map = get_predictions(np.array([image]), batch_size=self.batch_size)
        return edge_map[0].squeeze().numpy() > 0.2
