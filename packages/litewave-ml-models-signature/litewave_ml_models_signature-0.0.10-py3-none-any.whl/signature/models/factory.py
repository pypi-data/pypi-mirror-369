"""Factory function for creating signature verification models."""

import torch.nn as nn

try:
    from ..config import get_config
except ImportError:
    # Fallback for when running as top-level module
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from config import get_config

from .resnet_siamese.model import ResNet50Siamese
from .vit.model import SignatureViT


def create_model(
    model_type: str = None, num_classes: int = None, **kwargs
) -> nn.Module:
    """Factory function to create signature models.

    Args:
        model_type (str, optional): Type of model ("resnet" or "vit").
                                   Defaults to config value.
        num_classes (int, optional): Number of classes for ViT model.
                                    Defaults to config value.
        **kwargs: Additional arguments passed to model constructor.

    Returns:
        nn.Module: The requested model instance.

    Raises:
        ValueError: If model_type is unsupported or num_classes is missing for ViT.
    """
    config = get_config()

    if model_type is None:
        model_type = config.model_type
    if num_classes is None:
        num_classes = config.num_classes

    model_type = model_type.lower()

    if model_type == "resnet":
        embedding_dim = kwargs.get("embedding_dim", config.embedding_dim)
        return ResNet50Siamese(embedding_dim=embedding_dim)
    elif model_type == "vit":
        if num_classes is None or num_classes <= 0:
            raise ValueError("num_classes must be specified and positive for ViT model")
        embedding_dim = kwargs.get("embedding_dim", config.embedding_dim)
        model_name = kwargs.get("model_name", config.model_name)
        return SignatureViT(
            num_classes=num_classes, embedding_dim=embedding_dim, model_name=model_name
        )
    else:
        raise ValueError(
            f"Unsupported model_type: {model_type}. Must be 'resnet' or 'vit'"
        )
