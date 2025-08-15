#!/usr/bin/env python3
"""
Example usage of the signature verification module.

This script demonstrates:
1. Configuration setup
2. Dataset creation
3. Model training
4. Inference/classification
"""

import logging
import os
from pathlib import Path

# Import the signature module
import signature
from signature import (
    S3Manager,
    SignatureConfig,
    classify_signatures,
    create_dataset_csv,
    load_model,
    set_config,
    setup_logging,
    train_model,
)

# Setup logging
setup_logging("INFO")
logger = logging.getLogger(__name__)


def example_configuration():
    """Example of setting up configuration."""
    print("=== Configuration Example ===")

    # Method 1: Using environment variables
    os.environ["SIGNATURE_MODEL_TYPE"] = "vit"
    os.environ["SIGNATURE_NUM_CLASSES"] = "10"
    os.environ["SIGNATURE_BATCH_SIZE"] = "16"

    # Method 2: Programmatic configuration
    config = SignatureConfig(
        model_type="vit",
        num_classes=10,
        batch_size=16,
        learning_rate=1e-4,
        epochs=5,
        device="cpu",  # Use CPU for this example
    )

    set_config(config)
    print(
        f"Configuration set: model_type={config.model_type}, num_classes={config.num_classes}"
    )
    return config


def example_dataset_creation():
    """Example of creating dataset CSVs from image directories."""
    print("\n=== Dataset Creation Example ===")

    # Assume we have a directory structure like:
    # signatures/
    # ├── person1/
    # │   ├── sig1.png
    # │   └── sig2.png
    # └── person2/
    #     ├── sig1.png
    #     └── sig2.png

    image_directory = "example_signatures"  # This would be your actual directory

    if not os.path.exists(image_directory):
        print(f"Directory {image_directory} doesn't exist. Skipping dataset creation.")
        return None, None

    # Create dataset for ViT (single image classification)
    vit_csv = "vit_dataset.csv"
    try:
        create_dataset_csv(
            image_directory=image_directory, output_csv=vit_csv, dataset_type="single"
        )
        print(f"Created ViT dataset: {vit_csv}")
    except Exception as e:
        print(f"Failed to create ViT dataset: {e}")
        vit_csv = None

    # Create dataset for ResNet (image pairs)
    resnet_csv = "resnet_dataset.csv"
    try:
        create_dataset_csv(
            image_directory=image_directory,
            output_csv=resnet_csv,
            dataset_type="pairs",
            pairs_per_person=10,
        )
        print(f"Created ResNet dataset: {resnet_csv}")
    except Exception as e:
        print(f"Failed to create ResNet dataset: {e}")
        resnet_csv = None

    return vit_csv, resnet_csv


def example_training():
    """Example of training a model."""
    print("\n=== Training Example ===")

    # For this example, we'll create a dummy dataset if none exists
    dummy_csv = "dummy_dataset.csv"
    if not os.path.exists(dummy_csv):
        # Create a minimal dummy dataset for demonstration
        import pandas as pd

        dummy_data = [
            ["image1.png", "person1"],
            ["image2.png", "person1"],
            ["image3.png", "person2"],
            ["image4.png", "person2"],
        ]
        df = pd.DataFrame(dummy_data)
        df.to_csv(dummy_csv, header=False, index=False)
        print(f"Created dummy dataset: {dummy_csv}")

    try:
        # Train a small ViT model (just for demonstration)
        print("Training ViT model...")
        model, metrics = train_model(
            model_type="vit",
            dataset_path=dummy_csv,
            num_classes=2,
            epochs=1,  # Very short for demo
            batch_size=2,
        )

        print(f"Training completed!")
        print(f"Final training accuracy: {metrics.get('train_accuracy', 'N/A'):.4f}")
        print(f"Test accuracy: {metrics.get('test_accuracy', 'N/A'):.4f}")

        return model

    except Exception as e:
        print(f"Training failed: {e}")
        return None


def example_inference():
    """Example of running inference on signatures."""
    print("\n=== Inference Example ===")

    try:
        # Load a model (or use a dummy one)
        print("Loading model...")
        model = load_model(model_type="vit", num_classes=2)

        # For demonstration, we'll use dummy paths
        reference_path = (
            "reference_signatures"  # This would contain reference signatures
        )
        detected_path = (
            "detected_signatures"  # This would contain signatures to classify
        )

        if not os.path.exists(reference_path) or not os.path.exists(detected_path):
            print("Reference or detected signature directories don't exist.")
            print("In a real scenario, you would have:")
            print(f"  - Reference signatures in: {reference_path}")
            print(f"  - Detected signatures in: {detected_path}")
            return

        # Run classification
        results = classify_signatures(
            model=model, reference_path=reference_path, detected_path=detected_path
        )

        print(f"Classification results:")
        print(f"  Total processed: {results['total_processed']}")
        print(f"  Accepted signatures: {len(results['accepted_signatures'])}")

        for result in results["file_results"]:
            print(f"    {result['filename']}: {result['result']}")
            if "name" in result:
                print(f"      Matched to: {result['name']}")

    except Exception as e:
        print(f"Inference failed: {e}")


def example_s3_integration():
    """Example of S3 integration."""
    print("\n=== S3 Integration Example ===")

    # Note: This requires valid AWS credentials
    try:
        s3_manager = S3Manager()

        print("S3 Manager created successfully")
        print("In a real scenario, you could:")
        print(
            "  - Download models: s3_manager.download_file('s3://bucket/model.pth', 'local_model.pth')"
        )
        print(
            "  - Upload trained models: s3_manager.upload_file('local_model.pth', 's3://bucket/model.pth')"
        )
        print("  - List files: s3_manager.list_files('s3://bucket/models/', ['.pth'])")

    except Exception as e:
        print(f"S3 integration example failed: {e}")
        print("Make sure AWS credentials are configured for S3 operations")


def main():
    """Main example function."""
    print("Signature Verification Module - Example Usage")
    print("=" * 50)

    # 1. Configuration
    config = example_configuration()

    # 2. Dataset creation
    vit_csv, resnet_csv = example_dataset_creation()

    # 3. Model training
    model = example_training()

    # 4. Inference
    example_inference()

    # 5. S3 integration
    example_s3_integration()

    print("\n" + "=" * 50)
    print("Example completed!")
    print("\nNext steps:")
    print("1. Prepare your signature image directories")
    print("2. Configure environment variables or use programmatic config")
    print("3. Create datasets using create_dataset_csv()")
    print("4. Train models using train_model()")
    print("5. Run inference using classify_signatures()")


if __name__ == "__main__":
    main()
