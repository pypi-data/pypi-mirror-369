"""ArcFace loss implementation for signature classification."""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ArcFace(nn.Module):
    """Implementation of the ArcFace classification head.

    ArcFace adds an angular margin to the classification loss, which
    enhances the discriminative power of face recognition models.

    Attributes:
        weight (nn.Parameter): Learnable weight matrix
        s (float): Feature scale
        m (float): Angular margin
    """

    def __init__(
        self, in_features: int, out_features: int, s: float = 30.0, m: float = 0.50
    ):
        super().__init__()
        self.weight = nn.Parameter(torch.FloatTensor(out_features, in_features))
        nn.init.xavier_uniform_(self.weight)
        self.s = s
        self.m = m

    def forward(self, input: torch.Tensor, label: torch.Tensor) -> torch.Tensor:
        """Forward pass of ArcFace layer.

        Args:
            input (torch.Tensor): Input features
            label (torch.Tensor): Ground truth labels

        Returns:
            torch.Tensor: ArcFace logits
        """
        cosine = F.linear(F.normalize(input), F.normalize(self.weight))
        theta = torch.acos(torch.clamp(cosine, -1.0 + 1e-7, 1.0 - 1e-7))
        cosine_margin = torch.cos(theta + self.m)
        one_hot = torch.zeros_like(cosine, device=input.device)
        one_hot.scatter_(1, label.view(-1, 1), 1.0)
        output = self.s * (one_hot * cosine_margin + (1.0 - one_hot) * cosine)
        return output
