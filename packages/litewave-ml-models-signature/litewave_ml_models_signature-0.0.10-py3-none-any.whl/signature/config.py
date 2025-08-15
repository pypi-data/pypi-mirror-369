"""Configuration management for the signature module.

This module provides configuration management with S3 support and environment variable overrides.
It combines the best features from both the original scripts and the inference server.
"""

import os
from pathlib import Path
from typing import Literal, Optional

import torch
from pydantic import BaseModel, Field


class SignatureConfig(BaseModel):
    """Configuration class for signature module with S3 and environment variable support."""

    # Model configuration
    model_type: Literal["resnet", "vit"] = Field(
        default="vit", description="Type of model to use for signature verification"
    )
    num_classes: int = Field(
        default=1000, description="Number of signature classes for classification"
    )
    embedding_dim: int = Field(
        default=512, description="Dimension of the embedding space"
    )
    model_name: str = Field(
        default="vit_base_patch16_224", description="Specific model variant to use"
    )

    # Training configuration
    batch_size: int = Field(default=32, description="Batch size for training/inference")
    learning_rate: float = Field(default=5e-5, description="Learning rate for training")
    weight_decay: float = Field(default=1e-2, description="Weight decay for training")
    epochs: int = Field(default=15, description="Number of training epochs")
    margin: float = Field(
        default=17.5, description="Margin for contrastive loss (ResNet)"
    )

    # Device configuration
    device: str = Field(
        default_factory=lambda: "cuda" if torch.cuda.is_available() else "cpu",
        description="Device to use for computation",
    )

    # S3 and storage configuration
    aws_access_key_id: Optional[str] = Field(
        default=None, description="AWS access key ID"
    )
    aws_secret_access_key: Optional[str] = Field(
        default=None, description="AWS secret access key"
    )
    aws_region: str = Field(default="us-east-2", description="AWS region")

    model_s3_path: Optional[str] = Field(
        default=None, description="S3 path to model weights"
    )
    data_s3_path: Optional[str] = Field(
        default=None, description="S3 path to training data"
    )
    cache_dir: str = Field(default="cache/", description="Local cache directory")

    # Reference signatures configuration
    true_signatures_csv_s3_path: Optional[str] = Field(
        default=None, description="S3 path to CSV with reference signature metadata"
    )

    # Inference configuration
    classification_threshold: float = Field(
        default=0.10, description="Threshold adjustment for classification"
    )
    similarity_threshold: float = Field(
        default=1000.0, description="Similarity threshold for ResNet classification"
    )

    class Config:
        # Allow environment variable overrides
        env_prefix = "SIGNATURE_"
        case_sensitive = False

    @classmethod
    def from_env(cls) -> "SignatureConfig":
        """Create configuration from environment variables."""
        env_values = {}

        # Map environment variables to config fields
        env_mapping = {
            "SIGNATURE_MODEL_TYPE": "model_type",
            "SIGNATURE_NUM_CLASSES": "num_classes",
            "SIGNATURE_EMBEDDING_DIM": "embedding_dim",
            "SIGNATURE_MODEL_NAME": "model_name",
            "SIGNATURE_BATCH_SIZE": "batch_size",
            "SIGNATURE_LEARNING_RATE": "learning_rate",
            "SIGNATURE_WEIGHT_DECAY": "weight_decay",
            "SIGNATURE_EPOCHS": "epochs",
            "SIGNATURE_MARGIN": "margin",
            "SIGNATURE_DEVICE": "device",
            "AWS_ACCESS_KEY_ID": "aws_access_key_id",
            "AWS_SECRET_ACCESS_KEY": "aws_secret_access_key",
            "AWS_DEFAULT_REGION": "aws_region",
            "SIGNATURE_MODEL_S3_PATH": "model_s3_path",
            "SIGNATURE_DATA_S3_PATH": "data_s3_path",
            "SIGNATURE_CACHE_DIR": "cache_dir",
            "SIGNATURE_TRUE_SIGNATURES_CSV_S3_PATH": "true_signatures_csv_s3_path",
            "SIGNATURE_CLASSIFICATION_THRESHOLD": "classification_threshold",
            "SIGNATURE_SIMILARITY_THRESHOLD": "similarity_threshold",
        }

        for env_var, config_field in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert types as needed
                if config_field in [
                    "num_classes",
                    "embedding_dim",
                    "batch_size",
                    "epochs",
                ]:
                    value = int(value)
                elif config_field in [
                    "learning_rate",
                    "weight_decay",
                    "margin",
                    "classification_threshold",
                    "similarity_threshold",
                ]:
                    value = float(value)
                elif config_field == "model_type" and value.lower() not in [
                    "resnet",
                    "vit",
                ]:
                    raise ValueError(
                        f"Invalid model_type: {value}. Must be 'resnet' or 'vit'"
                    )

                env_values[config_field] = value

        return cls(**env_values)

    @property
    def torch_device(self) -> torch.device:
        """Get PyTorch device object."""
        return torch.device(self.device)

    def validate_model_type(self) -> None:
        """Validate model type configuration."""
        if self.model_type not in ["resnet", "vit"]:
            raise ValueError(
                f"Unsupported model_type: {self.model_type}. Must be 'resnet' or 'vit'"
            )

        if self.model_type == "vit" and self.num_classes <= 0:
            raise ValueError("num_classes must be positive for ViT model")


# Global configuration instance
_config: Optional[SignatureConfig] = None


def get_config() -> SignatureConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = SignatureConfig.from_env()
        _config.validate_model_type()
    return _config


def set_config(config: SignatureConfig) -> None:
    """Set the global configuration instance."""
    global _config
    config.validate_model_type()
    _config = config


# Backward compatibility with original config module
MODEL_TYPE = get_config().model_type
DEVICE = get_config().torch_device
