from pathlib import Path

import numpy as np
import torch

from mooney_maker.TEED.loss2 import bdcn_loss2
from mooney_maker.TEED.ted import TED


class Evaluate(TED):
    """Wrapper for TEED, that simplifies inference."""

    def __init__(
        self, path: Path, use_cuda: bool = True, verbose: bool = False
    ) -> None:
        super(Evaluate, self).__init__()
        torch.manual_seed(42)

        # Define what device we are using
        if verbose:
            print("CUDA Available: ", torch.cuda.is_available())
        self.device = torch.device(
            "cuda" if use_cuda and torch.cuda.is_available() else "cpu"
        )
        # Initialize the network
        self.to(self.device)

        # Load the pretrained model
        self.load_state_dict(torch.load(path, map_location=self.device))

        # Set the model in evaluation mode. In this case this is for the Dropout layers
        self.eval()

    def backward_pass(self, data: torch.Tensor, loss: float) -> torch.Tensor:
        """Does a backward pass through the model and returns the
        gradient of the input data.

        Parameters
        ----------
        data:
            Input data.
        loss:
            Loss of the forward pass.

        Returns
        -------
            grad: Gradient of the input data.
        """

        self.zero_grad()
        loss.backward()
        grad = data.grad.data

        return grad

    def extract_important_map(self, tensor: list[torch.tensor]) -> list[float]:
        """Extracts the last map from the list of predictions and scales its values according to TEED source code.

        Parameters
        ----------
        tensor:
            The output tensors in a list.
        image_shape:
            The shape of the original image.

        Returns
        -------
        The dfuse edgemap from the model.
        """

        edgemap = torch.nn.functional.sigmoid(tensor[-1])
        edgemap = edgemap.cpu().detach().numpy().squeeze()

        # Normalize image
        min = np.min(edgemap)
        edgemap = (edgemap - min) / (np.max(edgemap) - min)

        # TEED loads BIPED dataset where edges are white
        # Taken from TEED, make sure that no edge pixels are omitted
        edgemap[edgemap > 0.1] += 0.2
        edgemap = np.clip(edgemap, 0.0, 1.0)

        return edgemap

    def forward_pass(
        self, data: torch.Tensor, target: torch.Tensor
    ) -> list[list[torch.Tensor], float]:
        """Does a forward pass through the model.

        Parameters
        ----------
        data:
            Input data (BxCxHxW).
        target:
            Input target, must be in range [0, 1] (BxHxW).

        Returns
        -------
        output:
            Model's prediction.
        tLoss:
            The combined loss.
        """

        assert data.ndim == 4, "(1x3xHxW required)"
        assert data.shape[:2] == (1, 3), "(1x3xHxW required)"
        assert target.ndim == 4, "(1x1xHxW required)"
        assert target.shape[:2] == (1, 1), "(1x1xHxW required)"

        # These come from the original TEED repository
        bdcn_weights = [1.1, 0.7, 1.1, 1.3]

        # Forward pass the data through the model
        output = self(data)

        # Calculate the BDCN loss on first 3 "raw" outputs
        losses = []
        for preds, l_w in zip(output[:-1], bdcn_weights):
            losses.append(bdcn_loss2(preds, target, l_w))
        loss1 = sum(losses)
        # alternative

        # loss1 = bdcn_loss2(output[-1], target, bdcn_weights)

        # Calculate CATS loss on dfuse output
        # loss2 = cats_loss(output[-1], target, cats_weights[-1], self.device)
        # Add to get TEED loss
        tLoss = loss1  # - loss2

        return output, tLoss

    def prepare_input(self, img: list[list[int, int, int]]) -> torch.Tensor:
        """Prepare the input data (img) to have the right
        shape and dtype for TEED.

        Parameters
        ----------
        img:
            Input image.

        Returns
        -------
        Image that can be used as input for TEED.
        """

        assert (
            img.ndim == 3
        ), f"Image has wrong dimensionality: {img.ndim} but 3 is required."
        assert img.shape[-1] == 3, "Image shape (height, width, 3) is required."

        img = img.transpose((2, 0, 1))
        img = torch.from_numpy(img).float()
        img = img.to(self.device)
        img = img.unsqueeze(0)

        return img

    def prepare_target(self, contour: list[list[int]]) -> torch.Tensor:
        """Prepare the target (contour) to have the right
        shape and dtype for TEED.

        Parameters
        ----------
        contour:
            Target contour.

        Returns
        -------
        Contour that can be used as target for TEED.
        """

        assert (
            contour.ndim == 2
        ), f"Contour has wrong dimensionality: {contour.ndim} but 2 is required."

        contour = torch.from_numpy(contour).float()
        contour = contour.to(self.device)
        contour = contour.unsqueeze(0).unsqueeze(0)

        return contour
