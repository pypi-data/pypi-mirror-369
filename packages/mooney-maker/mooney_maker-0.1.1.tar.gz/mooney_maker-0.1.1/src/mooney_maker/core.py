import os
from pathlib import Path
from typing import Dict, List, Tuple, Union

import cv2
import numpy as np
from cv2.typing import MatLike
from matplotlib import pyplot as plt
from tqdm import tqdm

from mooney_maker.techniques import TECHNIQUE_REGISTRY, get_technique
from mooney_maker.techniques.edge_optimization_techniques.optimizers import (
    CannyOptimizer,
    DiffusionEdgeOptimizer,
    MooneyOptimizer,
    TEEDOptimizer,
)
from mooney_maker.utils import visualize_template_and_mooney
from mooney_maker.utils.io import load_image

__all__ = [
    "generate_mooney_image",
    "convert_folder_to_mooney_images",
    "plot_technique_comparison",
    "get_edge_prediction",
]


def generate_mooney_image(
    image_path: Union[Path, str],
    output_path: Union[Path, str, None] = None,
    store_intermediate_images: bool = False,
    visualize: bool = False,
    technique: str = "Mean",
    **technique_params,
) -> Tuple[MatLike, MatLike, MatLike]:
    """Generate a Mooney image from a template image.

    Converts an input image to a two-tone (black and white) Mooney image using
    the specified technique.

    Parameters
    ----------
    image_path : Path
        Path to the input template image. Can be a Path object or a string.
    output_path : Path, optional
        Directory path where the generated images will be saved.
        Required if store_intermediate_images is True. Can be a Path object or a string., by default
        None
    store_intermediate_images : bool, optional
        If True, saves the grayscale and smoothed intermediate images
        in addition to the final Mooney image. Requires output_path
        to be specified, by default False.
    visualize : bool, optional
        If True, displays the original and Mooney images, by default False
    technique : str, optional
        Technique used to generate the Mooney image. Currently available
        options are "Mean", "Otsu", "CannyMaxEdge", "CannyEdgeSimilarity",
        "CannyEdgeDisruption", "TEEDEdgeDisruption", "TEEDEdgeSimilarity",
        "DiffusionEdgeSimilarity", "DiffusionEdgeDisruption", by default "Mean"
    **technique_params
        Additional parameters specific to the chosen technique.

    Returns
    -------
    Tuple[MatLike, MatLike, MatLike]
        A tuple containing the grayscale image, smoothed image, and
        final Mooney image as numpy arrays.
    """
    image_path = Path(image_path) if isinstance(image_path, str) else image_path
    if output_path is not None:
        output_path = Path(output_path) if isinstance(output_path, str) else output_path
    if output_path is None and store_intermediate_images:
        raise ValueError(
            "If store_intermediate_images is True, output_path may not be None."
        )
    img_color = load_image(image_path)
    img_stem = image_path.stem
    technique_instance = get_technique(technique, **technique_params)
    img_grayscale, img_smoothed, img_mooney = technique_instance.process(img_color)

    if output_path is not None:
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        smoothing_kernel_size = technique_instance._last_smoothing_kernel_size
        threshold = technique_instance._last_threshold
        # Save Mooney image - ensure it's properly formatted for cv2.imwrite
        mooney_img_name = f"{img_stem}_{technique}_mooney.png"
        if img_mooney.dtype == bool:
            img_mooney_save = img_mooney.astype(np.uint8) * 255
        elif np.array_equal(np.unique(img_mooney), np.array([0, 1])):
            img_mooney_save = img_mooney.astype(np.uint8) * 255
        else:
            img_mooney_save = img_mooney
        cv2.imwrite(output_path / mooney_img_name, img_mooney_save)
        if store_intermediate_images:
            grayscale_img_name = f"{img_stem}_{technique}_grayscale.png"
            cv2.imwrite(output_path / grayscale_img_name, img_grayscale)
            smoothed_img_name = f"{img_stem}_{technique}_smoothed.png"
            cv2.imwrite(output_path / smoothed_img_name, img_smoothed)
        file_exists = (output_path / "mooney_maker_log.txt").is_file()
        with open(output_path / "mooney_maker_log.txt", "a") as f:
            if not file_exists:
                header = "input_image, smoothing_kernel_size, threshold, mooney_image\n"
                f.write(header)
            f.write(
                f"{image_path.name}, {smoothing_kernel_size}, {threshold}, {mooney_img_name}\n"
            )
    if visualize:
        visualize_template_and_mooney(img_color, img_mooney)

    return (img_grayscale, img_smoothed, img_mooney)


def convert_folder_to_mooney_images(
    input_folder: Union[Path, str],
    output_folder: Union[Path, str],
    technique: str = "Mean",
    store_intermediate_images: bool = False,
    **technique_params,
):
    """Convert all images in a folder to Mooney images using the specified technique.

    Parameters
    ----------
    input_folder : Union[Path, str]
        Path to the input folder containing images to be converted. Images need to be in the following formats:
        .png, .jpg, or .jpeg. Can be a Path object or a string
    output_folder : Union[Path, str]
        Path to the output folder where Mooney images will be saved.
    technique : str, optional, by default "Mean"
        Technique used to generate the Mooney image. Currently available
        options are "Mean", "Otsu", "CannyMaxEdge", "CannyEdgeSimilarity",
        "CannyEdgeDisruption", "TEEDEdgeDisruption", "TEEDEdgeSimilarity",
        "DiffusionEdgeSimilarity", "DiffusionEdgeDisruption", by default "Mean"
    store_intermediate_images : bool, optional
        If True, saves the grayscale and smoothed intermediate images
        in addition to the final Mooney image, by default False.
    **technique_params
        Additional parameters specific to the chosen technique.
    """
    input_folder = Path(input_folder) if isinstance(input_folder, str) else input_folder
    output_folder = (
        Path(output_folder) if isinstance(output_folder, str) else output_folder
    )

    if not input_folder.exists():
        raise FileNotFoundError(f"Input folder not found: {input_folder}")
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)
    if input_folder == output_folder:
        raise ValueError("Input and output folders must be different.")
    images = [
        img
        for img in os.listdir(input_folder)
        if img.endswith((".png", ".jpg", ".jpeg"))
    ]
    for img_path in tqdm(images, desc="Images converted", unit="img"):
        generate_mooney_image(
            input_folder / img_path,
            output_path=output_folder,
            store_intermediate_images=store_intermediate_images,
            technique=technique,
            **technique_params,
        )


def plot_technique_comparison(
    image_path: Union[Path, str],
    techniques: List[str] = None,
    technique_specific_params: Dict = None,
):
    """Creates a grid of Mooney images generated using different techniques.

    Parameters
    ----------
    image_path : Union[Path, str]
        Path to the input image. Can be a Path object or a string.
    techniques : List[str]
        List of techniques to apply for generating Mooney images. If None, all available techniques will be used, by default None
    technique_specific_params : Dict, optional
        Dictionary containing specific parameters for each technique.
        The keys should be technique names and the values should be dictionaries of parameters for that technique.
        If None, default parameters for each technique will be used, by default None
    """
    img_color = load_image(image_path)
    if techniques is None or len(techniques) == 0:
        techniques = TECHNIQUE_REGISTRY.keys()
    mooney_images = {}
    thresholds = {}
    smoothing_kernel_sizes = {}
    pbar = tqdm(techniques, desc="Techniques applied")
    for technique in pbar:
        pbar.set_postfix_str(f"Currently applying: {technique}")
        technique_params = (
            technique_specific_params.get(technique, {})
            if technique_specific_params
            else {}
        )
        technique_instance = get_technique(technique, **technique_params)
        _, _, mooney_images[technique] = technique_instance.process(img_color)
        thresholds[technique] = technique_instance._last_threshold
        smoothing_kernel_sizes[
            technique
        ] = technique_instance._last_smoothing_kernel_size

    n_cols = 3
    n_rows = int(np.ceil(len(mooney_images) / n_cols))
    _, ax = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
    ax = ax.flatten()
    for i, technique in enumerate(techniques):
        ax[i].imshow(mooney_images[technique], cmap="gray")
        ax[i].set_title(
            technique + f"\nThreshold: {thresholds[technique]}\n"
            f"Kernel Size: {smoothing_kernel_sizes[technique]}"
        )
    for i in range(n_cols * n_rows):
        ax[i].axis("off")
    plt.show()


def get_edge_prediction(
    image_path: Union[Path, str],
    technique: str = "Canny",
    **technique_params,
) -> np.ndarray:
    """Get the edge map of an image using the specified technique.

    Parameters
    ----------
    image_path : Union[Path, str]
        Path to the image. Can be a Path object or a string.
    technique : str, optional
        Technique used to generate the edge map. Must be a valid edge detection technique (Canny, TEED or DiffusionEdge) , by default "Canny".
    **technique_params
        Additional parameters specific to the chosen edge detection technique.

    Returns
    -------
    np.ndarray
        The edge map of the image.
    """
    image = load_image(image_path)
    optimizer_lookup = {
        "Canny": CannyOptimizer,
        "TEED": TEEDOptimizer,
        "DiffusionEdge": DiffusionEdgeOptimizer,
    }
    if technique not in optimizer_lookup:
        raise ValueError(
            f"Invalid technique '{technique}'. Available techniques: {list(optimizer_lookup.keys())}"
        )

    optimizer: MooneyOptimizer = optimizer_lookup[technique](**technique_params)
    technique_instance = get_technique("Mean")
    image = technique_instance.scale_down(image)
    edge_map = optimizer.get_edge_prediction(image)
    if edge_map.dtype == bool:
        edge_map = edge_map.astype(np.uint8) * 255
    return technique_instance.scale_up(edge_map)
