"""Training utilities for signature models.

This module provides training functions for both ResNet Siamese and ViT models,
with support for S3 data loading, automatic model saving, and comprehensive metrics.
"""

import logging
import os
from typing import Any, Dict, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from .config import get_config
from .data import SignatureDataset, SignaturePairDataset, create_dataloader
from .models import ContrastiveLoss, ResNet50Siamese, SignatureViT, create_model
from .utils import create_s3_manager, ensure_dir, get_cache_path

logger = logging.getLogger(__name__)


def train_model(
    model_type: str = None, dataset_path: str = None, save_path: str = None, **kwargs
) -> Tuple[torch.nn.Module, Dict[str, float]]:
    """Main training entry point that delegates to the appropriate training function.

    Args:
        model_type (str, optional): Model type ("resnet" or "vit")
        dataset_path (str, optional): Path to dataset CSV file (local or S3)
        save_path (str, optional): Path to save trained model (local or S3)
        **kwargs: Additional training parameters

    Returns:
        Tuple[torch.nn.Module, Dict[str, float]]: Trained model and metrics
    """
    config = get_config()

    # Use config defaults
    if model_type is None:
        model_type = config.model_type
    if dataset_path is None:
        dataset_path = config.data_s3_path

    if dataset_path is None:
        raise ValueError(
            "Dataset path must be provided either as argument or in config"
        )

    # Download dataset if S3 path
    local_dataset_path = _download_dataset_if_needed(dataset_path)

    # Create model
    model = create_model(model_type=model_type, **kwargs)

    # Train based on model type
    if model_type == "resnet":
        return train_resnet_model(model, local_dataset_path, save_path, **kwargs)
    elif model_type == "vit":
        return train_vit_model(model, local_dataset_path, save_path, **kwargs)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")


def train_resnet_model(
    model: ResNet50Siamese,
    dataset_path: str,
    save_path: str = None,
    batch_size: int = None,
    epochs: int = None,
    learning_rate: float = None,
    weight_decay: float = None,
    margin: float = None,
    **kwargs,
) -> Tuple[ResNet50Siamese, Dict[str, float]]:
    """Train ResNet Siamese model for signature verification.

    Args:
        model (ResNet50Siamese): Model to train
        dataset_path (str): Path to pairs CSV file
        save_path (str, optional): Path to save trained model
        batch_size (int, optional): Batch size for training
        epochs (int, optional): Number of training epochs
        learning_rate (float, optional): Learning rate
        weight_decay (float, optional): Weight decay
        margin (float, optional): Margin for contrastive loss
        **kwargs: Additional parameters

    Returns:
        Tuple[ResNet50Siamese, Dict[str, float]]: Trained model and metrics
    """
    config = get_config()

    # Use config defaults
    batch_size = batch_size or config.batch_size
    epochs = epochs or config.epochs
    learning_rate = learning_rate or config.learning_rate
    weight_decay = weight_decay or config.weight_decay
    margin = margin or config.margin

    logger.info(
        f"Training ResNet model with config: batch_size={batch_size}, "
        f"epochs={epochs}, lr={learning_rate}, margin={margin}"
    )

    # Create data loaders
    train_loader, val_loader, test_loader = create_dataloader(
        dataset_path, dataset_type="pairs", batch_size=batch_size, **kwargs
    )

    # Setup training components
    criterion = ContrastiveLoss(margin=margin)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, patience=5, factor=0.5
    )

    model = model.to(config.torch_device)

    # Training loop
    train_metrics = []
    val_metrics = []
    best_val_acc = 0.0

    logger.info("Starting ResNet training...")

    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_labels = []
        train_preds = []

        for img1, img2, labels in train_loader:
            img1, img2, labels = (
                img1.to(config.torch_device),
                img2.to(config.torch_device),
                labels.to(config.torch_device),
            )

            optimizer.zero_grad()
            embedding1, embedding2 = model(img1, img2)
            loss = criterion(embedding1, embedding2, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

            # Calculate predictions based on distance threshold
            distances = torch.nn.functional.pairwise_distance(
                embedding1, embedding2, p=2
            )
            preds = (distances < 7.0).float()  # Threshold for similarity

            train_labels.extend(labels.cpu().numpy())
            train_preds.extend(preds.cpu().numpy())

        train_acc = accuracy_score(train_labels, train_preds)
        avg_train_loss = train_loss / len(train_loader)

        # Validation phase
        val_loss, val_acc = _evaluate_resnet(
            model, val_loader, criterion, config.torch_device
        )

        # Update scheduler
        scheduler.step(val_loss)

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            if save_path:
                _save_model(model, save_path)

        train_metrics.append(
            {"epoch": epoch + 1, "loss": avg_train_loss, "accuracy": train_acc}
        )
        val_metrics.append({"epoch": epoch + 1, "loss": val_loss, "accuracy": val_acc})

        logger.info(
            f"Epoch {epoch + 1}/{epochs}: "
            f"Train Loss={avg_train_loss:.4f}, Train Acc={train_acc:.4f}, "
            f"Val Loss={val_loss:.4f}, Val Acc={val_acc:.4f}"
        )

    # Final evaluation on test set
    test_loss, test_acc = _evaluate_resnet(
        model, test_loader, criterion, config.torch_device
    )

    logger.info(
        f"Training completed. Best Val Acc: {best_val_acc:.4f}, Test Acc: {test_acc:.4f}"
    )

    metrics = {
        "train_accuracy": train_acc,
        "val_accuracy": best_val_acc,
        "test_accuracy": test_acc,
        "train_metrics": train_metrics,
        "val_metrics": val_metrics,
    }

    return model, metrics


def train_vit_model(
    model: SignatureViT,
    dataset_path: str,
    save_path: str = None,
    batch_size: int = None,
    epochs: int = None,
    learning_rate: float = None,
    weight_decay: float = None,
    **kwargs,
) -> Tuple[SignatureViT, Dict[str, float]]:
    """Train ViT model for signature classification.

    Args:
        model (SignatureViT): Model to train
        dataset_path (str): Path to single-image CSV file
        save_path (str, optional): Path to save trained model
        batch_size (int, optional): Batch size for training
        epochs (int, optional): Number of training epochs
        learning_rate (float, optional): Learning rate
        weight_decay (float, optional): Weight decay
        **kwargs: Additional parameters

    Returns:
        Tuple[SignatureViT, Dict[str, float]]: Trained model and metrics
    """
    config = get_config()

    # Use config defaults
    batch_size = batch_size or config.batch_size
    epochs = epochs or config.epochs
    learning_rate = learning_rate or config.learning_rate
    weight_decay = weight_decay or config.weight_decay

    logger.info(
        f"Training ViT model with config: batch_size={batch_size}, "
        f"epochs={epochs}, lr={learning_rate}"
    )

    # Create data loaders
    train_loader, val_loader, test_loader = create_dataloader(
        dataset_path, dataset_type="single", batch_size=batch_size, **kwargs
    )

    # Setup training components
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, patience=3, factor=0.5
    )

    model = model.to(config.torch_device)

    # Training loop
    train_metrics = []
    val_metrics = []
    best_val_acc = 0.0

    logger.info("Starting ViT training...")

    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(config.torch_device), labels.to(
                config.torch_device
            )

            optimizer.zero_grad()
            logits, _ = model(images, labels)  # Get both logits and embeddings
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

            # Calculate accuracy
            preds = torch.argmax(logits, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        train_acc = correct / total if total > 0 else 0.0
        avg_train_loss = train_loss / len(train_loader)

        # Validation phase
        val_loss, val_acc = _evaluate_vit(
            model, val_loader, criterion, config.torch_device
        )

        # Update scheduler
        scheduler.step(val_loss)

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            if save_path:
                _save_model(model, save_path)

        train_metrics.append(
            {"epoch": epoch + 1, "loss": avg_train_loss, "accuracy": train_acc}
        )
        val_metrics.append({"epoch": epoch + 1, "loss": val_loss, "accuracy": val_acc})

        logger.info(
            f"Epoch {epoch + 1}/{epochs}: "
            f"Train Loss={avg_train_loss:.4f}, Train Acc={train_acc:.4f}, "
            f"Val Loss={val_loss:.4f}, Val Acc={val_acc:.4f}"
        )

    # Final evaluation on test set
    test_loss, test_acc = _evaluate_vit(
        model, test_loader, criterion, config.torch_device
    )

    logger.info(
        f"Training completed. Best Val Acc: {best_val_acc:.4f}, Test Acc: {test_acc:.4f}"
    )

    metrics = {
        "train_accuracy": train_acc,
        "val_accuracy": best_val_acc,
        "test_accuracy": test_acc,
        "train_metrics": train_metrics,
        "val_metrics": val_metrics,
    }

    return model, metrics


def _evaluate_resnet(
    model: ResNet50Siamese,
    data_loader: DataLoader,
    criterion: ContrastiveLoss,
    device: torch.device,
) -> Tuple[float, float]:
    """Evaluate ResNet model on a dataset.

    Args:
        model (ResNet50Siamese): Model to evaluate
        data_loader (DataLoader): Data loader for evaluation
        criterion (ContrastiveLoss): Loss function
        device (torch.device): Device to run evaluation on

    Returns:
        Tuple[float, float]: Average loss and accuracy
    """
    model.eval()
    total_loss = 0.0
    all_labels = []
    all_preds = []

    with torch.no_grad():
        for img1, img2, labels in data_loader:
            img1, img2, labels = img1.to(device), img2.to(device), labels.to(device)

            embedding1, embedding2 = model(img1, img2)
            loss = criterion(embedding1, embedding2, labels)
            total_loss += loss.item()

            # Calculate predictions
            distances = torch.nn.functional.pairwise_distance(
                embedding1, embedding2, p=2
            )
            preds = (distances < 7.0).float()

            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

    avg_loss = total_loss / len(data_loader)
    accuracy = accuracy_score(all_labels, all_preds)

    return avg_loss, accuracy


def _evaluate_vit(
    model: SignatureViT,
    data_loader: DataLoader,
    criterion: nn.CrossEntropyLoss,
    device: torch.device,
) -> Tuple[float, float]:
    """Evaluate ViT model on a dataset.

    Args:
        model (SignatureViT): Model to evaluate
        data_loader (DataLoader): Data loader for evaluation
        criterion (nn.CrossEntropyLoss): Loss function
        device (torch.device): Device to run evaluation on

    Returns:
        Tuple[float, float]: Average loss and accuracy
    """
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in data_loader:
            images, labels = images.to(device), labels.to(device)

            logits, _ = model(images, labels)
            loss = criterion(logits, labels)
            total_loss += loss.item()

            # Calculate accuracy
            preds = torch.argmax(logits, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    avg_loss = total_loss / len(data_loader)
    accuracy = correct / total if total > 0 else 0.0

    return avg_loss, accuracy


def _download_dataset_if_needed(dataset_path: str) -> str:
    """Download dataset from S3 if needed.

    Args:
        dataset_path (str): S3 or local path to dataset

    Returns:
        str: Local path to dataset
    """
    if not dataset_path.startswith("s3://"):
        return dataset_path

    # Download from S3
    filename = os.path.basename(dataset_path)
    local_path = get_cache_path(filename, "datasets")

    # Use cached version if it exists
    if os.path.exists(local_path):
        logger.info(f"Using cached dataset: {local_path}")
        return local_path

    try:
        s3_manager = create_s3_manager()
        s3_manager.download_file(dataset_path, local_path)
        logger.info(f"Downloaded dataset from {dataset_path} to {local_path}")
        return local_path
    except Exception as e:
        logger.error(f"Failed to download dataset: {e}")
        raise


def _save_model(model: torch.nn.Module, save_path: str) -> None:
    """Save model to local path or S3.

    Args:
        model (torch.nn.Module): Model to save
        save_path (str): Local or S3 path to save to
    """
    try:
        if save_path.startswith("s3://"):
            # Save locally first, then upload to S3
            filename = os.path.basename(save_path)
            local_path = get_cache_path(filename, "models")
            torch.save(model.state_dict(), local_path)

            s3_manager = create_s3_manager()
            s3_manager.upload_file(local_path, save_path)
            logger.info(f"Saved model to S3: {save_path}")
        else:
            # Save locally
            ensure_dir(os.path.dirname(save_path))
            torch.save(model.state_dict(), save_path)
            logger.info(f"Saved model locally: {save_path}")

    except Exception as e:
        logger.error(f"Failed to save model: {e}")
        raise


# Convenience functions
def train_resnet(**kwargs) -> Tuple[ResNet50Siamese, Dict[str, float]]:
    """Train a ResNet Siamese model."""
    return train_model(model_type="resnet", **kwargs)


def train_vit(num_classes: int, **kwargs) -> Tuple[SignatureViT, Dict[str, float]]:
    """Train a ViT model."""
    return train_model(model_type="vit", num_classes=num_classes, **kwargs)
