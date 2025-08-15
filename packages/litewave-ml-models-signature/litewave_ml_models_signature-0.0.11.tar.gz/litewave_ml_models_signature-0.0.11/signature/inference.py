"""Inference and classification utilities for signature verification.

This module provides:
- Model loading with S3 support
- Signature classification for both ResNet and ViT models
- Reference signature management
- Weibull distribution fitting for thresholds
- Feature fusion and extraction
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import torch
from scipy.stats import weibull_min

from .config import get_config
from .models import ResNet50Siamese, SignatureViT, create_model
from .utils import (
    S3Manager,
    create_s3_manager,
    ensure_dir,
    extract_deep_features,
    get_cache_path,
    get_fused_features,
)

logger = logging.getLogger(__name__)


def load_model(
    model_type: str = None,
    num_classes: int = None,
    weights_path: str = None,
    clean: bool = False,
) -> torch.nn.Module:
    """Load a signature model with optional S3 weights.

    Args:
        model_type (str, optional): Model type ("resnet" or "vit")
        num_classes (int, optional): Number of classes for ViT
        weights_path (str, optional): S3 or local path to model weights
        clean (bool): Force re-download of weights from S3

    Returns:
        torch.nn.Module: Loaded model on the configured device
    """
    config = get_config()

    # Use config defaults if not provided
    if model_type is None:
        model_type = config.model_type
    if num_classes is None:
        num_classes = config.num_classes
    if weights_path is None:
        weights_path = config.model_s3_path

    # Create the model
    model = create_model(model_type=model_type, num_classes=num_classes)
    model = model.to(config.torch_device)

    # Load weights if provided
    if weights_path:
        local_weights_path = _download_weights_if_needed(weights_path, clean)
        if local_weights_path:
            _load_model_weights(model, local_weights_path)
            logger.info(f"Loaded model weights from: {local_weights_path}")

    return model


def _download_weights_if_needed(
    weights_path: str, clean: bool = False
) -> Optional[str]:
    """Download model weights from S3 if needed.

    Args:
        weights_path (str): S3 or local path to weights
        clean (bool): Force re-download

    Returns:
        Optional[str]: Local path to weights file
    """
    # If it's a local path and exists, use it directly
    if not weights_path.startswith("s3://"):
        return weights_path if os.path.exists(weights_path) else None

    # S3 path - download to cache
    filename = os.path.basename(weights_path)
    local_path = get_cache_path(filename, "models")

    # Use cached version if it exists and clean is False
    if os.path.exists(local_path) and not clean:
        logger.info(f"Using cached weights: {local_path}")
        return local_path

    try:
        s3_manager = create_s3_manager()
        s3_manager.download_file(weights_path, local_path)
        return local_path
    except Exception as e:
        logger.error(f"Failed to download weights from {weights_path}: {e}")
        return None


def _load_model_weights(model: torch.nn.Module, weights_path: str) -> None:
    """Load weights into a model.

    Args:
        model (torch.nn.Module): Model to load weights into
        weights_path (str): Path to weights file
    """
    config = get_config()
    try:
        state_dict = torch.load(weights_path, map_location=config.torch_device)
        model.load_state_dict(state_dict)
        logger.info(f"Successfully loaded weights from: {weights_path}")
    except Exception as e:
        logger.error(f"Failed to load weights from {weights_path}: {e}")
        raise


def _build_reference_features(
    model: torch.nn.Module, reference_path: str, model_type: str = None
) -> Dict[str, np.ndarray]:
    """Build reference feature dictionary for all users.

    Args:
        model (torch.nn.Module): Trained model for feature extraction
        reference_path (str): Path to reference signatures directory
        model_type (str, optional): Model type for feature extraction method

    Returns:
        Dict[str, np.ndarray]: Dictionary mapping user names to feature arrays
    """
    config = get_config()
    model_type = model_type or config.model_type

    ref_dict = {}

    for user in os.listdir(reference_path):
        user_path = os.path.join(reference_path, user)
        if not os.path.isdir(user_path):
            continue

        img_files = [
            os.path.join(user_path, f)
            for f in os.listdir(user_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        if not img_files:
            logger.warning(f"No image files found for user: {user}")
            ref_dict[user] = np.empty((0,))
            continue

        # Extract features based on model type
        if model_type == "vit":
            # Use fused features for ViT
            feats = [get_fused_features(model, img_path) for img_path in img_files]
        else:
            # Use deep features only for ResNet
            feats = [extract_deep_features(model, img_path) for img_path in img_files]

        ref_dict[user] = np.stack(feats) if feats else np.empty((0,))
        logger.info(
            f"Built reference features for user '{user}': {len(feats)} signatures"
        )

    return ref_dict


def _fit_weibull_thresholds(
    reference_features: Dict[str, np.ndarray], ppf_value: float = 1e-3
) -> Dict[str, float]:
    """Fit Weibull distribution thresholds for each user.

    Args:
        reference_features (Dict[str, np.ndarray]): Reference feature dictionary
        ppf_value (float): Percentile point function value for threshold

    Returns:
        Dict[str, float]: User-specific thresholds
    """
    thresholds = {}

    for user, feats in reference_features.items():
        if feats.size == 0:
            thresholds[user] = float("inf")
            continue

        # Collect impostor distances
        impostor_dists = []
        for other_user, other_feats in reference_features.items():
            if user == other_user or other_feats.size == 0:
                continue

            # Compute pairwise distances between user and impostor
            dists = np.linalg.norm(feats[:, None] - other_feats, axis=2)
            impostor_dists.extend(dists.flatten())

        if len(impostor_dists) > 10:
            try:
                # Fit Weibull distribution and get threshold
                params = weibull_min.fit(np.array(impostor_dists), floc=0)
                threshold = weibull_min.ppf(ppf_value, *params)
                thresholds[user] = threshold
                logger.debug(f"Weibull threshold for {user}: {threshold:.4f}")
            except Exception as e:
                logger.warning(f"Failed to fit Weibull for {user}: {e}")
                thresholds[user] = float("inf")
        else:
            logger.warning(
                f"Insufficient impostor data for {user}, using infinite threshold"
            )
            thresholds[user] = float("inf")

    return thresholds


def classify_signatures_resnet(
    model: ResNet50Siamese,
    reference_path: str,
    detected_path: str,
    similarity_threshold: float = None,
) -> Dict[str, List]:
    """Classify signatures using ResNet Siamese model.

    Args:
        model (ResNet50Siamese): Trained ResNet model
        reference_path (str): Path to reference signatures
        detected_path (str): Path to detected signatures
        similarity_threshold (float, optional): Distance threshold for classification

    Returns:
        Dict[str, List]: Classification results
    """
    config = get_config()
    if similarity_threshold is None:
        similarity_threshold = config.similarity_threshold

    # Build reference features
    reference_features = _build_reference_features(model, reference_path, "resnet")

    accepted_names = []
    file_results = []

    # Process detected signatures
    for file_path in _get_signature_files(detected_path):
        filename = os.path.basename(file_path)

        try:
            detected_features = extract_deep_features(model, file_path)

            best_match, best_distance = None, float("inf")

            # Compare with all reference signatures
            for user, ref_feats in reference_features.items():
                if ref_feats.size == 0:
                    continue

                # Compute distances to all reference signatures for this user
                distances = np.linalg.norm(ref_feats - detected_features, axis=1)
                min_distance = distances.min()

                if min_distance < best_distance:
                    best_distance = min_distance
                    best_match = user

            # Apply threshold
            if best_match and best_distance <= similarity_threshold:
                accepted_names.append(best_match)
                file_results.append(
                    {
                        "filename": filename,
                        "result": "ACCEPTED",
                        "name": best_match,
                        "distance": float(best_distance),
                    }
                )
                logger.info(
                    f"ACCEPTED: {filename} -> {best_match} (dist: {best_distance:.4f})"
                )
            else:
                file_results.append(
                    {
                        "filename": filename,
                        "result": "REJECTED",
                        "name": best_match,
                        "distance": float(best_distance) if best_match else None,
                        "reason": f"Distance {best_distance:.4f} exceeds threshold {similarity_threshold}",
                    }
                )
                logger.info(f"REJECTED: {filename} (dist: {best_distance:.4f})")

        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            file_results.append(
                {"filename": filename, "result": "ERROR", "reason": str(e)}
            )

    return {
        "accepted_signatures": accepted_names,
        "file_results": file_results,
        "total_processed": len(file_results),
    }


def classify_signatures_vit(
    model: SignatureViT, reference_path: str, detected_path: str, delta: float = None
) -> Dict[str, List]:
    """Classify signatures using ViT model with Weibull thresholds.

    Args:
        model (SignatureViT): Trained ViT model
        reference_path (str): Path to reference signatures
        detected_path (str): Path to detected signatures
        delta (float, optional): Threshold adjustment factor

    Returns:
        Dict[str, List]: Classification results
    """
    config = get_config()
    if delta is None:
        delta = config.classification_threshold

    # Build reference features and thresholds
    reference_features = _build_reference_features(model, reference_path, "vit")
    thresholds = _fit_weibull_thresholds(reference_features)

    accepted_names = []
    file_results = []

    # Process detected signatures
    for file_path in _get_signature_files(detected_path):
        filename = os.path.basename(file_path)

        try:
            detected_features = get_fused_features(model, file_path)

            best_match, best_distance = None, float("inf")

            # Compare with all reference signatures
            for user, ref_feats in reference_features.items():
                if ref_feats.size == 0:
                    continue

                # Compute distances to all reference signatures for this user
                distances = np.linalg.norm(ref_feats - detected_features, axis=1)
                min_distance = distances.min()

                if min_distance < best_distance:
                    best_distance = min_distance
                    best_match = user

            if best_match is None:
                file_results.append(
                    {
                        "filename": filename,
                        "result": "REJECTED",
                        "reason": "No reference signatures available",
                    }
                )
                continue

            # Apply Weibull threshold with delta adjustment
            threshold = thresholds.get(best_match, float("inf")) + delta
            accepted = best_distance < threshold

            if accepted:
                accepted_names.append(best_match)
                file_results.append(
                    {
                        "filename": filename,
                        "result": "ACCEPTED",
                        "name": best_match,
                        "distance": float(best_distance),
                    }
                )
                logger.info(
                    f"ACCEPTED: {filename} -> {best_match} (dist: {best_distance:.4f})"
                )
            else:
                file_results.append(
                    {
                        "filename": filename,
                        "result": "REJECTED",
                        "name": best_match,
                        "distance": float(best_distance),
                        "reason": f"Distance {best_distance:.4f} exceeds threshold {threshold:.4f}",
                    }
                )
                logger.info(f"REJECTED: {filename} (dist: {best_distance:.4f})")

        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            file_results.append(
                {"filename": filename, "result": "ERROR", "reason": str(e)}
            )

    return {
        "accepted_signatures": accepted_names,
        "file_results": file_results,
        "total_processed": len(file_results),
    }


def classify_signatures(
    model: torch.nn.Module,
    reference_path: str,
    detected_path: str,
    model_type: str = None,
    **kwargs,
) -> Dict[str, List]:
    """Main entry point for signature classification.

    Args:
        model (torch.nn.Module): Trained model
        reference_path (str): Path to reference signatures
        detected_path (str): Path to detected signatures
        model_type (str, optional): Model type override
        **kwargs: Additional arguments for specific classifiers

    Returns:
        Dict[str, List]: Classification results
    """
    config = get_config()
    model_type = model_type or config.model_type

    if model_type == "resnet":
        return classify_signatures_resnet(
            model, reference_path, detected_path, **kwargs
        )
    elif model_type == "vit":
        return classify_signatures_vit(model, reference_path, detected_path, **kwargs)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")


def _get_signature_files(directory: str) -> List[str]:
    """Get all signature image files from directory and subdirectories.

    Args:
        directory (str): Directory to search

    Returns:
        List[str]: List of image file paths
    """
    signature_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                signature_files.append(os.path.join(root, file))

    return sorted(signature_files)


# Convenience functions for backward compatibility
def load_resnet_model(**kwargs) -> ResNet50Siamese:
    """Load a ResNet Siamese model."""
    return load_model(model_type="resnet", **kwargs)


def load_vit_model(num_classes: int, **kwargs) -> SignatureViT:
    """Load a ViT model."""
    return load_model(model_type="vit", num_classes=num_classes, **kwargs)
