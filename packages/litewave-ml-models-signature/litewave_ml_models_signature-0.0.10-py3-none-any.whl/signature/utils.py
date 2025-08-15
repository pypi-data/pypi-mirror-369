"""Utility functions for the signature module.

This module provides utility functions for:
- S3 operations (download, upload, list files)
- Image processing and transformations
- Feature extraction and fusion
- File and directory operations
"""

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import boto3
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
from skimage import io as imread
from skimage import transform as sk_transform
from skimage.feature import hog

from .config import get_config

# Set up logging
logger = logging.getLogger(__name__)


class S3Manager:
    """Manager class for S3 operations with signature module configuration."""

    def __init__(self, config=None):
        """Initialize S3 manager with configuration.

        Args:
            config: Configuration object. If None, uses global config.
        """
        self.config = config or get_config()
        self._s3_client = None

    @property
    def s3_client(self):
        """Lazy initialization of S3 client."""
        if self._s3_client is None:
            kwargs = {"region_name": self.config.aws_region}

            # Add credentials if provided
            if self.config.aws_access_key_id and self.config.aws_secret_access_key:
                kwargs.update(
                    {
                        "aws_access_key_id": self.config.aws_access_key_id,
                        "aws_secret_access_key": self.config.aws_secret_access_key,
                    }
                )

            self._s3_client = boto3.client("s3", **kwargs)

        return self._s3_client

    def download_file(self, s3_url: str, local_path: str) -> str:
        """Download a file from S3 to local path.

        Args:
            s3_url (str): S3 URL (s3://bucket/key)
            local_path (str): Local file path to save to

        Returns:
            str: Local path of downloaded file
        """
        try:
            s3_url = s3_url.replace("s3://", "")
            bucket_name = s3_url.split("/")[0]
            object_key = "/".join(s3_url.split("/")[1:])

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            logger.info(f"Downloading from S3: {s3_url}")
            self.s3_client.download_file(bucket_name, object_key, local_path)
            logger.info(f"Successfully downloaded to: {local_path}")
            return local_path

        except Exception as e:
            logger.error(f"Failed to download from S3: {str(e)}")
            raise

    def upload_file(self, local_path: str, s3_url: str) -> str:
        """Upload a local file to S3.

        Args:
            local_path (str): Local file path
            s3_url (str): S3 URL to upload to (s3://bucket/key)

        Returns:
            str: S3 URL of uploaded file
        """
        try:
            s3_url = s3_url.replace("s3://", "")
            bucket_name = s3_url.split("/")[0]
            object_key = "/".join(s3_url.split("/")[1:])

            logger.info(f"Uploading to S3: {s3_url}")
            self.s3_client.upload_file(local_path, bucket_name, object_key)
            logger.info(f"Successfully uploaded from: {local_path}")
            return f"s3://{s3_url}"

        except Exception as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise

    def list_files(self, s3_folder: str, extensions: List[str] = None) -> List[str]:
        """List files in an S3 folder.

        Args:
            s3_folder (str): S3 folder path (s3://bucket/prefix/)
            extensions (List[str], optional): File extensions to filter by

        Returns:
            List[str]: List of S3 URLs for files
        """
        s3_folder = s3_folder.replace("s3://", "")
        bucket_name = s3_folder.split("/")[0]
        prefix = "/".join(s3_folder.split("/")[1:])
        if not prefix.endswith("/"):
            prefix += "/"

        files = []
        paginator = self.s3_client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if "Contents" not in page:
                continue

            for obj in page["Contents"]:
                key = obj["Key"]
                if extensions:
                    if any(key.lower().endswith(ext.lower()) for ext in extensions):
                        files.append(f"s3://{bucket_name}/{key}")
                else:
                    files.append(f"s3://{bucket_name}/{key}")

        return files

    def download_folder(
        self, s3_folder: str, local_folder: str, extensions: List[str] = None
    ) -> str:
        """Download all files from an S3 folder.

        Args:
            s3_folder (str): S3 folder path
            local_folder (str): Local directory to download to
            extensions (List[str], optional): File extensions to filter by

        Returns:
            str: Local folder path
        """
        os.makedirs(local_folder, exist_ok=True)
        files = self.list_files(s3_folder, extensions)

        for s3_url in files:
            filename = os.path.basename(s3_url)
            local_path = os.path.join(local_folder, filename)
            self.download_file(s3_url, local_path)

        return local_folder


def create_s3_manager(config=None) -> S3Manager:
    """Create an S3 manager instance.

    Args:
        config: Configuration object. If None, uses global config.

    Returns:
        S3Manager: Configured S3 manager instance
    """
    return S3Manager(config)


def load_image(
    image_path: str,
    as_tensor: bool = False,
    transform: Optional[transforms.Compose] = None,
) -> Union[np.ndarray, torch.Tensor]:
    """Load an image from file.

    Args:
        image_path (str): Path to image file
        as_tensor (bool): If True, return as PyTorch tensor
        transform (Optional[transforms.Compose]): Transform to apply

    Returns:
        Union[np.ndarray, torch.Tensor]: Loaded image
    """
    if as_tensor:
        img = Image.open(image_path).convert("L")
        if transform:
            img = transform(img)
        else:
            # Default transform for tensor
            default_transform = transforms.Compose(
                [transforms.Resize((224, 224)), transforms.ToTensor()]
            )
            img = default_transform(img)
        return img
    else:
        return imread(image_path, as_gray=True)


def preprocess_signature(
    img: np.ndarray, target_size: Tuple[int, int] = (150, 220)
) -> np.ndarray:
    """Pre-process a signature image: resize and normalize.

    Args:
        img (np.ndarray): Input image array
        target_size (Tuple[int, int]): Target size (height, width)

    Returns:
        np.ndarray: Preprocessed image
    """
    resized_img = sk_transform.resize(img, target_size, anti_aliasing=True)
    return resized_img


def compute_hog_features(image_path: str) -> np.ndarray:
    """Compute HOG (Histogram of Oriented Gradients) features for an image.

    Args:
        image_path (str): Path to image file

    Returns:
        np.ndarray: Normalized HOG feature vector
    """
    img = imread(image_path, as_gray=True)
    img_resized = sk_transform.resize(img, (150, 220), anti_aliasing=True)

    hog_feature, _ = hog(
        img_resized,
        orientations=9,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        block_norm="L2-Hys",
        visualize=True,
        feature_vector=True,
    )

    # Normalize the feature vector
    hog_feature = hog_feature / np.linalg.norm(hog_feature)
    return hog_feature


def get_inference_transform() -> transforms.Compose:
    """Get the standard inference transform for signature images.

    Returns:
        transforms.Compose: Transform pipeline for inference
    """
    return transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor()])


def get_training_transform(augment: bool = True) -> transforms.Compose:
    """Get transform pipeline for training.

    Args:
        augment (bool): Whether to include data augmentation

    Returns:
        transforms.Compose: Transform pipeline for training
    """
    if augment:
        return transforms.Compose(
            [
                transforms.Resize((150, 220)),
                transforms.RandomRotation(degrees=10),
                transforms.RandomAffine(
                    degrees=5, translate=(0.1, 0.1), scale=(0.9, 1.1)
                ),
                transforms.ToTensor(),
            ]
        )
    else:
        return transforms.Compose(
            [
                transforms.Resize((150, 220)),
                transforms.ToTensor(),
            ]
        )


def extract_deep_features(
    model: torch.nn.Module, image_path: str, device: torch.device = None
) -> np.ndarray:
    """Extract deep features from an image using a trained model.

    Args:
        model (torch.nn.Module): Trained model for feature extraction
        image_path (str): Path to image file
        device (torch.device, optional): Device to run inference on

    Returns:
        np.ndarray: Normalized deep feature vector
    """
    config = get_config()
    device = device or config.torch_device

    transform = get_inference_transform()
    img = Image.open(image_path).convert("L")
    img_tensor = transform(img).unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        deep_emb = model(img_tensor).cpu().numpy()[0]
        deep_emb = deep_emb / np.linalg.norm(deep_emb)

    return deep_emb


def fuse_features(deep_features: np.ndarray, hog_features: np.ndarray) -> np.ndarray:
    """Fuse deep learning features with HOG features.

    Args:
        deep_features (np.ndarray): Deep learning feature vector
        hog_features (np.ndarray): HOG feature vector

    Returns:
        np.ndarray: Normalized fused feature vector
    """
    fused = np.concatenate([deep_features, hog_features])
    return fused / np.linalg.norm(fused)


def get_fused_features(
    model: torch.nn.Module, image_path: str, device: torch.device = None
) -> np.ndarray:
    """Extract and fuse deep + HOG features for an image.

    Args:
        model (torch.nn.Module): Trained model for deep feature extraction
        image_path (str): Path to image file
        device (torch.device, optional): Device to run inference on

    Returns:
        np.ndarray: Normalized fused feature vector
    """
    deep_features = extract_deep_features(model, image_path, device)
    hog_features = compute_hog_features(image_path)
    return fuse_features(deep_features, hog_features)


def ensure_dir(path: str) -> str:
    """Ensure directory exists, create if it doesn't.

    Args:
        path (str): Directory path

    Returns:
        str: The directory path
    """
    os.makedirs(path, exist_ok=True)
    return path


def get_cache_path(filename: str, subdir: str = "") -> str:
    """Get path in cache directory.

    Args:
        filename (str): Name of file
        subdir (str): Subdirectory within cache

    Returns:
        str: Full cache path
    """
    config = get_config()
    cache_path = os.path.join(config.cache_dir, subdir, filename)
    ensure_dir(os.path.dirname(cache_path))
    return cache_path


def create_temp_dir(prefix: str = "signature_") -> str:
    """Create a temporary directory.

    Args:
        prefix (str): Prefix for temporary directory name

    Returns:
        str: Path to temporary directory
    """
    return tempfile.mkdtemp(prefix=prefix)


def cleanup_temp_dir(temp_dir: str) -> None:
    """Clean up a temporary directory.

    Args:
        temp_dir (str): Path to temporary directory to remove
    """
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def get_image_files(directory: str, extensions: List[str] = None) -> List[str]:
    """Get list of image files in a directory.

    Args:
        directory (str): Directory to search
        extensions (List[str], optional): File extensions to look for

    Returns:
        List[str]: List of image file paths
    """
    if extensions is None:
        extensions = [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]

    image_files = []
    for ext in extensions:
        pattern = f"*{ext}"
        image_files.extend(Path(directory).glob(pattern))
        # Also check uppercase
        pattern = f"*{ext.upper()}"
        image_files.extend(Path(directory).glob(pattern))

    return [str(f) for f in sorted(image_files)]


def validate_image_path(image_path: str) -> bool:
    """Validate that an image path exists and is readable.

    Args:
        image_path (str): Path to image file

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not os.path.exists(image_path):
            return False

        # Try to open the image
        Image.open(image_path)
        return True
    except Exception:
        return False


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration.

    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
