"""Signature verification and classification module.

This module provides tools for:
- Training signature verification models (ResNet Siamese and ViT + ArcFace)
- Running inference on detected signatures
- Managing datasets and data preprocessing
- S3-based model and data management

Main components:
- config: Configuration management with S3 support
- models: Model architectures (ResNet50Siamese, SignatureViT)
- training: Training routines for both model types
- inference: Inference and classification utilities
- data: Dataset and data preprocessing utilities
- utils: Helper functions and utilities
"""

from .config import SignatureConfig, get_config
from .data import (
    SignatureDataset,
    SignaturePairDataset,
    create_dataloader,
    create_dataset_csv,
)
from .inference import classify_signatures, load_model
from .models import (
    ArcFace,
    ContrastiveLoss,
    ResNet50Siamese,
    SignatureViT,
    create_model,
)
from .training import train_model, train_resnet, train_vit
from .utils import (
    S3Manager,
    create_s3_manager,
    extract_deep_features,
    get_fused_features,
)

__version__ = "1.0.0"
__all__ = [
    "SignatureConfig",
    "get_config",
    "ResNet50Siamese",
    "SignatureViT",
    "ArcFace",
    "ContrastiveLoss",
    "create_model",
    "classify_signatures",
    "load_model",
    "train_model",
    "train_resnet",
    "train_vit",
    "SignatureDataset",
    "SignaturePairDataset",
    "create_dataset_csv",
    "create_dataloader",
    "S3Manager",
    "create_s3_manager",
    "get_fused_features",
    "extract_deep_features",
]
