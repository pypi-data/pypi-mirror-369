"""Vision Transformer implementation for signature classification."""

from typing import Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import timm
except ImportError:
    timm = None

from ..losses.arcface import ArcFace


class SignatureViT(nn.Module):
    """Vision Transformer backbone with ArcFace projection for signature classification.

    This model uses a pre-trained Vision Transformer as the backbone and adds
    an ArcFace classification head for signature identity prediction.

    Attributes:
        vit: Vision Transformer backbone
        fc: Linear projection layer
        bn: Batch normalization layer
        arcface: ArcFace classification head
    """

    def __init__(
        self,
        num_classes: int,
        embedding_dim: int = 512,
        model_name: str = "vit_base_patch16_224",
    ):
        super().__init__()

        if timm is None:
            raise ImportError(
                "timm is required for the ViT model. Install via `pip install timm`."
            )

        # Pre-trained ViT (no classifier head)
        self.vit = timm.create_model(model_name, pretrained=True, num_classes=0)

        # Adapt first conv layer for grayscale input
        if hasattr(self.vit, "patch_embed") and hasattr(self.vit.patch_embed, "proj"):
            original_conv = self.vit.patch_embed.proj
            self.vit.patch_embed.proj = nn.Conv2d(
                1,
                original_conv.out_channels,
                kernel_size=original_conv.kernel_size,
                stride=original_conv.stride,
                padding=original_conv.padding,
                bias=original_conv.bias is not None,
            )
            with torch.no_grad():
                # Use average of RGB weights for the single gray channel
                self.vit.patch_embed.proj.weight.copy_(
                    original_conv.weight.mean(dim=1, keepdim=True)
                )

        # Projection to embedding space
        self.fc = nn.Linear(self.vit.num_features, embedding_dim)
        self.bn = nn.BatchNorm1d(embedding_dim)

        # ArcFace classifier
        s = float(np.sqrt(2) * np.log(num_classes - 1)) if num_classes > 1 else 30.0
        self.arcface = ArcFace(embedding_dim, num_classes, s=s, m=0.10)

    def forward(
        self, x: torch.Tensor, label: Optional[torch.Tensor] = None
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Forward pass of the SignatureViT model.

        Args:
            x (torch.Tensor): Input image tensor of shape (batch_size, 1, H, W)
            label (Optional[torch.Tensor]): Ground truth labels for training

        Returns:
            Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
                If label is provided: (logits, embeddings)
                If label is None: embeddings only
        """
        # Ensure correct input size
        if x.shape[-1] != 224 or x.shape[-2] != 224:
            x = F.interpolate(x, size=(224, 224), mode="bilinear", align_corners=False)

        features = self.vit(x)
        embedding = self.fc(features)
        embedding = F.relu(embedding)
        embedding = self.bn(embedding)

        if label is not None:
            logits = self.arcface(embedding, label)
            return logits, embedding
        return embedding
