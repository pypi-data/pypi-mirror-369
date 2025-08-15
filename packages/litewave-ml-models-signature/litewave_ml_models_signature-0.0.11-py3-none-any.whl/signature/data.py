"""Data handling utilities for signature models.

This module provides:
- Dataset classes for signature images and pairs
- Data loading utilities with train/val/test splits
- Data preprocessing and augmentation
- CSV generation utilities for dataset creation
"""

import csv
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import torch
import torchvision.transforms as transforms
from PIL import Image
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset

from .config import get_config
from .utils import get_inference_transform, get_training_transform, validate_image_path

logger = logging.getLogger(__name__)


class SignatureDataset(Dataset):
    """Dataset for single signature images with labels (for ViT training).

    This dataset expects a CSV file with two columns:
    - Column 0: image_path (relative or absolute path to image)
    - Column 1: label (person name or class identifier)
    """

    def __init__(
        self,
        csv_file: str,
        transform: Optional[transforms.Compose] = None,
        root_dir: str = "",
    ):
        """Initialize the dataset.

        Args:
            csv_file (str): Path to CSV file with image paths and labels
            transform (Optional[transforms.Compose]): Transform to apply to images
            root_dir (str): Root directory for relative image paths
        """
        self.data = pd.read_csv(csv_file, header=None)
        self.transform = transform or get_inference_transform()
        self.root_dir = root_dir

        # Build label to index mapping
        unique_labels = self.data.iloc[:, 1].unique()
        self.label_to_idx = {
            label: idx for idx, label in enumerate(sorted(unique_labels))
        }
        self.idx_to_label = {idx: label for label, idx in self.label_to_idx.items()}
        self.num_classes = len(unique_labels)

        logger.info(
            f"Loaded dataset with {len(self.data)} samples and {self.num_classes} classes"
        )

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get a single sample.

        Args:
            idx (int): Sample index

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: (image_tensor, label_index)
        """
        img_path = self.data.iloc[idx, 0]
        label_str = self.data.iloc[idx, 1]

        # Handle relative paths
        if self.root_dir and not os.path.isabs(img_path):
            img_path = os.path.join(self.root_dir, img_path)

        # Load and transform image
        try:
            img = Image.open(img_path).convert("L")  # Convert to grayscale
            if self.transform:
                img = self.transform(img)

            # Convert label to index
            label_idx = self.label_to_idx[label_str]

            return img, torch.tensor(label_idx, dtype=torch.long)

        except Exception as e:
            logger.error(f"Error loading image {img_path}: {e}")
            # Return a dummy sample in case of error
            dummy_img = torch.zeros((1, 224, 224))
            return dummy_img, torch.tensor(0, dtype=torch.long)


class SignaturePairDataset(Dataset):
    """Dataset for signature image pairs with similarity labels (for ResNet training).

    This dataset expects a CSV file with three columns:
    - Column 0: image1_path (path to first image)
    - Column 1: image2_path (path to second image)
    - Column 2: label (1 for same person, 0 for different person)
    """

    def __init__(
        self,
        csv_file: str,
        transform: Optional[transforms.Compose] = None,
        root_dir: str = "",
    ):
        """Initialize the dataset.

        Args:
            csv_file (str): Path to CSV file with image pairs and labels
            transform (Optional[transforms.Compose]): Transform to apply to images
            root_dir (str): Root directory for relative image paths
        """
        self.data = pd.read_csv(csv_file, header=None)
        self.transform = transform or get_training_transform(augment=False)
        self.root_dir = root_dir

        logger.info(f"Loaded pair dataset with {len(self.data)} pairs")

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Get a single pair sample.

        Args:
            idx (int): Sample index

        Returns:
            Tuple[torch.Tensor, torch.Tensor, torch.Tensor]: (image1, image2, label)
        """
        img1_path = self.data.iloc[idx, 0]
        img2_path = self.data.iloc[idx, 1]
        label = self.data.iloc[idx, 2]

        # Handle relative paths
        if self.root_dir:
            if not os.path.isabs(img1_path):
                img1_path = os.path.join(self.root_dir, img1_path)
            if not os.path.isabs(img2_path):
                img2_path = os.path.join(self.root_dir, img2_path)

        try:
            # Load and transform images
            img1 = Image.open(img1_path).convert("L")
            img2 = Image.open(img2_path).convert("L")

            if self.transform:
                img1 = self.transform(img1)
                img2 = self.transform(img2)

            return img1, img2, torch.tensor(label, dtype=torch.float32)

        except Exception as e:
            logger.error(f"Error loading images {img1_path}, {img2_path}: {e}")
            # Return dummy samples in case of error
            dummy_img = torch.zeros((1, 150, 220))
            return dummy_img, dummy_img, torch.tensor(0.0, dtype=torch.float32)


def create_dataloader(
    dataset_path: str,
    dataset_type: str = "single",
    batch_size: int = 32,
    test_size: float = 0.2,
    val_size: float = 0.2,
    shuffle: bool = True,
    num_workers: int = 0,
    augment_training: bool = True,
    **kwargs,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Create train, validation, and test data loaders.

    Args:
        dataset_path (str): Path to CSV dataset file
        dataset_type (str): Type of dataset ("single" or "pairs")
        batch_size (int): Batch size for data loaders
        test_size (float): Fraction of data to use for testing
        val_size (float): Fraction of training data to use for validation
        shuffle (bool): Whether to shuffle training data
        num_workers (int): Number of workers for data loading
        augment_training (bool): Whether to apply data augmentation to training set
        **kwargs: Additional arguments

    Returns:
        Tuple[DataLoader, DataLoader, DataLoader]: train, val, test data loaders
    """
    root_dir = kwargs.get("root_dir", "")

    # Create appropriate dataset
    if dataset_type == "single":
        full_dataset = SignatureDataset(dataset_path, root_dir=root_dir)

        # Create train/val/test splits
        indices = np.arange(len(full_dataset))
        train_indices, test_indices = train_test_split(
            indices,
            test_size=test_size,
            random_state=42,
            stratify=full_dataset.data.iloc[:, 1],  # Stratify by label
        )
        train_indices, val_indices = train_test_split(
            train_indices,
            test_size=val_size,
            random_state=42,
            stratify=full_dataset.data.iloc[train_indices, 1],
        )

        # Create datasets with appropriate transforms
        train_transform = (
            get_inference_transform()
        )  # Use same transform for consistency
        val_transform = get_inference_transform()
        test_transform = get_inference_transform()

        if augment_training:
            train_transform = get_training_transform(augment=True)

        train_dataset = torch.utils.data.Subset(
            SignatureDataset(
                dataset_path, transform=train_transform, root_dir=root_dir
            ),
            train_indices,
        )
        val_dataset = torch.utils.data.Subset(
            SignatureDataset(dataset_path, transform=val_transform, root_dir=root_dir),
            val_indices,
        )
        test_dataset = torch.utils.data.Subset(
            SignatureDataset(dataset_path, transform=test_transform, root_dir=root_dir),
            test_indices,
        )

    elif dataset_type == "pairs":
        full_dataset = SignaturePairDataset(dataset_path, root_dir=root_dir)

        # Create train/val/test splits
        indices = np.arange(len(full_dataset))
        train_indices, test_indices = train_test_split(
            indices, test_size=test_size, random_state=42
        )
        train_indices, val_indices = train_test_split(
            train_indices, test_size=val_size, random_state=42
        )

        # Create transforms for pairs
        train_transform = get_training_transform(augment=augment_training)
        val_transform = get_training_transform(augment=False)
        test_transform = get_training_transform(augment=False)

        train_dataset = torch.utils.data.Subset(
            SignaturePairDataset(
                dataset_path, transform=train_transform, root_dir=root_dir
            ),
            train_indices,
        )
        val_dataset = torch.utils.data.Subset(
            SignaturePairDataset(
                dataset_path, transform=val_transform, root_dir=root_dir
            ),
            val_indices,
        )
        test_dataset = torch.utils.data.Subset(
            SignaturePairDataset(
                dataset_path, transform=test_transform, root_dir=root_dir
            ),
            test_indices,
        )

    else:
        raise ValueError(f"Unsupported dataset_type: {dataset_type}")

    # Create data loaders
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers
    )

    logger.info(
        f"Created data loaders - Train: {len(train_loader.dataset)}, "
        f"Val: {len(val_loader.dataset)}, Test: {len(test_loader.dataset)}"
    )

    return train_loader, val_loader, test_loader


def create_single_image_csv(
    image_directory: str, output_csv: str, relative_paths: bool = True
) -> str:
    """Create a CSV file for single image classification from a directory structure.

    Expected directory structure:
    image_directory/
    ├── person1/
    │   ├── sig1.png
    │   ├── sig2.png
    │   └── ...
    ├── person2/
    │   ├── sig1.png
    │   └── ...
    └── ...

    Args:
        image_directory (str): Root directory containing person subdirectories
        output_csv (str): Path to output CSV file
        relative_paths (bool): Whether to use relative paths in CSV

    Returns:
        str: Path to created CSV file
    """
    rows = []

    for person_dir in os.listdir(image_directory):
        person_path = os.path.join(image_directory, person_dir)

        if not os.path.isdir(person_path):
            continue

        for img_file in os.listdir(person_path):
            if img_file.lower().endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(person_path, img_file)

                # Validate image
                if not validate_image_path(img_path):
                    logger.warning(f"Skipping invalid image: {img_path}")
                    continue

                # Use relative path if requested
                if relative_paths:
                    img_path = os.path.relpath(img_path, os.path.dirname(output_csv))

                rows.append([img_path, person_dir])

    # Write CSV
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    logger.info(f"Created single image CSV with {len(rows)} samples: {output_csv}")
    return output_csv


def create_pairs_csv(
    image_directory: str,
    output_csv: str,
    pairs_per_person: int = 50,
    relative_paths: bool = True,
) -> str:
    """Create a CSV file for pair classification from a directory structure.

    Args:
        image_directory (str): Root directory containing person subdirectories
        output_csv (str): Path to output CSV file
        pairs_per_person (int): Number of positive pairs to generate per person
        relative_paths (bool): Whether to use relative paths in CSV

    Returns:
        str: Path to created CSV file
    """
    import itertools
    import random

    # Collect all images by person
    person_images = {}
    for person_dir in os.listdir(image_directory):
        person_path = os.path.join(image_directory, person_dir)

        if not os.path.isdir(person_path):
            continue

        images = []
        for img_file in os.listdir(person_path):
            if img_file.lower().endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(person_path, img_file)

                if validate_image_path(img_path):
                    if relative_paths:
                        img_path = os.path.relpath(
                            img_path, os.path.dirname(output_csv)
                        )
                    images.append(img_path)

        if images:
            person_images[person_dir] = images

    if len(person_images) < 2:
        raise ValueError("Need at least 2 people for pair generation")

    rows = []

    # Generate positive pairs
    for person, images in person_images.items():
        if len(images) < 2:
            logger.warning(
                f"Person {person} has less than 2 images, skipping positive pairs"
            )
            continue

        # Generate all possible pairs for this person
        all_pairs = list(itertools.combinations(images, 2))

        # Sample the requested number of pairs
        if len(all_pairs) <= pairs_per_person:
            selected_pairs = all_pairs
        else:
            selected_pairs = random.sample(all_pairs, pairs_per_person)

        for img1, img2 in selected_pairs:
            rows.append([img1, img2, 1])  # 1 for same person

    # Generate negative pairs (same number as positive pairs)
    num_positive = len(rows)
    people_list = list(person_images.keys())

    for _ in range(num_positive):
        # Select two different people
        person1, person2 = random.sample(people_list, 2)
        img1 = random.choice(person_images[person1])
        img2 = random.choice(person_images[person2])
        rows.append([img1, img2, 0])  # 0 for different people

    # Shuffle the rows
    random.shuffle(rows)

    # Write CSV
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    logger.info(
        f"Created pairs CSV with {len(rows)} pairs ({num_positive} positive, "
        f"{len(rows) - num_positive} negative): {output_csv}"
    )
    return output_csv


def create_dataset_csv(
    image_directory: str, output_csv: str, dataset_type: str = "single", **kwargs
) -> str:
    """Create a dataset CSV file from an image directory.

    Args:
        image_directory (str): Root directory containing images
        output_csv (str): Path to output CSV file
        dataset_type (str): Type of dataset ("single" or "pairs")
        **kwargs: Additional arguments for specific dataset types

    Returns:
        str: Path to created CSV file
    """
    if dataset_type == "single":
        return create_single_image_csv(image_directory, output_csv, **kwargs)
    elif dataset_type == "pairs":
        return create_pairs_csv(image_directory, output_csv, **kwargs)
    else:
        raise ValueError(f"Unsupported dataset_type: {dataset_type}")


def validate_dataset_csv(
    csv_file: str, dataset_type: str = "single", root_dir: str = ""
) -> Dict[str, int]:
    """Validate a dataset CSV file.

    Args:
        csv_file (str): Path to CSV file
        dataset_type (str): Type of dataset ("single" or "pairs")
        root_dir (str): Root directory for relative paths

    Returns:
        Dict[str, int]: Validation statistics
    """
    stats = {
        "total_samples": 0,
        "valid_samples": 0,
        "invalid_samples": 0,
        "missing_files": 0,
    }

    data = pd.read_csv(csv_file, header=None)
    stats["total_samples"] = len(data)

    for idx, row in data.iterrows():
        if dataset_type == "single":
            img_path = row.iloc[0]
            if root_dir and not os.path.isabs(img_path):
                img_path = os.path.join(root_dir, img_path)

            if validate_image_path(img_path):
                stats["valid_samples"] += 1
            else:
                stats["invalid_samples"] += 1
                if not os.path.exists(img_path):
                    stats["missing_files"] += 1

        elif dataset_type == "pairs":
            img1_path = row.iloc[0]
            img2_path = row.iloc[1]

            if root_dir:
                if not os.path.isabs(img1_path):
                    img1_path = os.path.join(root_dir, img1_path)
                if not os.path.isabs(img2_path):
                    img2_path = os.path.join(root_dir, img2_path)

            valid1 = validate_image_path(img1_path)
            valid2 = validate_image_path(img2_path)

            if valid1 and valid2:
                stats["valid_samples"] += 1
            else:
                stats["invalid_samples"] += 1
                if not os.path.exists(img1_path):
                    stats["missing_files"] += 1
                if not os.path.exists(img2_path):
                    stats["missing_files"] += 1

    logger.info(f"Dataset validation results: {stats}")
    return stats


# Convenience aliases
SignatureImageDataset = SignatureDataset  # For backward compatibility
