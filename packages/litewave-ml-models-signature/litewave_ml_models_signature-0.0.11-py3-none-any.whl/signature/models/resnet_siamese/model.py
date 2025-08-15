"""ResNet50-based Siamese network implementation."""

from typing import Tuple

import torch
import torch.nn as nn
from torchvision.models import resnet50


class ResNet50Siamese(nn.Module):
    """Siamese ResNet50 model for signature verification using contrastive loss.

    This model takes pairs of signature images and learns to produce similar
    embeddings for signatures from the same person and different embeddings
    for signatures from different people.

    Attributes:
        embedding_dim (int): Dimension of the output embeddings (default: 512)
        resnet: Pre-trained ResNet50 backbone modified for grayscale input
        feature_extractor: Feature extraction layers from ResNet50
        fc: Projection head for embeddings
    """

    def __init__(self, embedding_dim: int = 512):
        super(ResNet50Siamese, self).__init__()
        self.embedding_dim = embedding_dim

        # Load pre-trained ResNet50
        self.resnet = resnet50(pretrained=True)

        # Modify the input layer to handle grayscale images (1 channel)
        self.resnet.conv1 = nn.Conv2d(
            1, 64, kernel_size=7, stride=2, padding=3, bias=False
        )

        # Extract up to the average pooling layer
        self.feature_extractor = nn.Sequential(*list(self.resnet.children())[:-1])

        # Add a projection head for embeddings
        self.fc = nn.Sequential(
            nn.Linear(2048, self.embedding_dim),
            nn.ReLU(),
            nn.BatchNorm1d(self.embedding_dim),
        )

    def forward_once(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for a single image.

        Args:
            x (torch.Tensor): Input image tensor of shape (batch_size, 1, H, W)

        Returns:
            torch.Tensor: Embedding vector of shape (batch_size, embedding_dim)
        """
        # Feature extraction
        x = self.feature_extractor(x)
        x = x.view(x.size(0), -1)
        # Project to embedding space
        x = self.fc(x)
        return x

    def forward(
        self, img1: torch.Tensor, img2: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass for a pair of images.

        Args:
            img1 (torch.Tensor): First image tensor
            img2 (torch.Tensor): Second image tensor

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Embeddings for both images
        """
        embedding1 = self.forward_once(img1)
        embedding2 = self.forward_once(img2)
        return embedding1, embedding2
