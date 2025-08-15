"""Neural network architectures for signature verification.

Available models and components:
- ResNet50Siamese: Siamese network with contrastive loss for signature verification
- SignatureViT: Vision Transformer with ArcFace for signature classification  
- ArcFace: Angular margin loss implementation
- ContrastiveLoss: Contrastive loss for Siamese networks
- create_model: Factory function to create models based on configuration

All models support grayscale signature images and are optimized for signature verification.
"""

from .factory import create_model
from .losses.arcface import ArcFace
from .losses.contrastive import ContrastiveLoss
from .resnet_siamese.model import ResNet50Siamese
from .vit.model import SignatureViT

__all__ = [
    "ResNet50Siamese",
    "SignatureViT",
    "ArcFace",
    "ContrastiveLoss",
    "create_model",
]
