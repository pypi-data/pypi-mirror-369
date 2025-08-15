"""Contrastive loss implementation for Siamese networks."""

import torch
import torch.nn as nn
from torch import clamp
from torch.nn.functional import pairwise_distance


class ContrastiveLoss(nn.Module):
    """Contrastive loss for training Siamese networks.

    This loss function encourages similar pairs to have small distances
    and dissimilar pairs to have large distances (at least margin).

    Attributes:
        margin (float): Margin for negative pairs
    """

    def __init__(self, margin: float = 1.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin

    def forward(
        self, embedding1: torch.Tensor, embedding2: torch.Tensor, label: torch.Tensor
    ) -> torch.Tensor:
        """Compute contrastive loss.

        Args:
            embedding1 (torch.Tensor): First set of embeddings
            embedding2 (torch.Tensor): Second set of embeddings
            label (torch.Tensor): Labels (1 for same person, 0 for different)

        Returns:
            torch.Tensor: Contrastive loss value
        """
        distances = pairwise_distance(embedding1, embedding2, p=2)
        losses = (
            0.5 * label * distances**2
            + 0.5 * (1 - label) * clamp(self.margin - distances, min=0.0) ** 2
        )
        return losses.mean()
