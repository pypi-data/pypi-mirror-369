# Signature Verification Module

A comprehensive Python package for signature verification and classification using deep learning models. This module supports both ResNet Siamese networks for verification and Vision Transformers (ViT) with ArcFace for classification.

## Features

- **Multiple Model Architectures**: 
  - ResNet50 Siamese network with contrastive loss for signature verification
  - Vision Transformer (ViT) with ArcFace loss for signature classification
- **S3 Integration**: Seamless integration with AWS S3 for model weights and dataset storage
- **Flexible Configuration**: Environment variable-based configuration system
- **Complete Pipeline**: From data preprocessing to model training and inference
- **Production Ready**: Optimized for both research and production deployment

## Installation

### Requirements

- Python 3.8+
- PyTorch 1.9+
- torchvision
- timm (for ViT models)
- scikit-image
- scikit-learn
- pandas
- PIL/Pillow
- boto3 (for S3 support)
- pydantic
- scipy

### Install Dependencies

```bash
pip install torch torchvision torchaudio
pip install timm scikit-image scikit-learn pandas pillow boto3 pydantic scipy
```

## Quick Start

### Basic Usage

```python
from signature import SignatureConfig, load_model, classify_signatures

# Configure the module
config = SignatureConfig(
    model_type="vit",
    num_classes=100,
    model_s3_path="s3://my-bucket/models/signature_vit.pth"
)

# Load a trained model
model = load_model()

# Classify signatures
results = classify_signatures(
    model=model,
    reference_path="path/to/reference/signatures",
    detected_path="path/to/detected/signatures"
)

print(f"Accepted signatures: {results['accepted_signatures']}")
```

### Training a Model

```python
from signature import train_model, create_dataset_csv

# Create a dataset CSV from image directory
create_dataset_csv(
    image_directory="path/to/signature/images",
    output_csv="dataset.csv",
    dataset_type="single"  # or "pairs" for ResNet
)

# Train a model
model, metrics = train_model(
    model_type="vit",
    dataset_path="dataset.csv",
    save_path="s3://my-bucket/models/trained_model.pth",
    num_classes=100,
    epochs=20
)

print(f"Test accuracy: {metrics['test_accuracy']:.4f}")
```

## Configuration

The module supports configuration through environment variables or programmatically:

### Environment Variables

```bash
# Model configuration
export SIGNATURE_MODEL_TYPE=vit
export SIGNATURE_NUM_CLASSES=100
export SIGNATURE_MODEL_S3_PATH=s3://my-bucket/models/model.pth

# AWS configuration
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-2

# Training configuration
export SIGNATURE_BATCH_SIZE=32
export SIGNATURE_LEARNING_RATE=5e-5
export SIGNATURE_EPOCHS=15
```

### Programmatic Configuration

```python
from signature import SignatureConfig, set_config

config = SignatureConfig(
    model_type="vit",
    num_classes=100,
    batch_size=32,
    learning_rate=5e-5,
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key"
)

set_config(config)
```

## Model Architectures

### ResNet50 Siamese

Best for signature verification (determining if two signatures are from the same person):

```python
from signature import ResNet50Siamese, train_resnet

# Create model
model = ResNet50Siamese(embedding_dim=512)

# Train model
model, metrics = train_resnet(
    dataset_path="pairs_dataset.csv",
    epochs=25,
    margin=17.5
)
```

### Vision Transformer (ViT)

Best for signature classification (identifying which person signed):

```python
from signature import SignatureViT, train_vit

# Create model
model = SignatureViT(num_classes=100, embedding_dim=512)

# Train model
model, metrics = train_vit(
    num_classes=100,
    dataset_path="single_image_dataset.csv",
    epochs=15
)
```

## Data Preparation

### Directory Structure

Organize your signature images in the following structure:

```
signatures/
├── person1/
│   ├── signature1.png
│   ├── signature2.png
│   └── signature3.png
├── person2/
│   ├── signature1.png
│   └── signature2.png
└── person3/
    ├── signature1.png
    ├── signature2.png
    └── signature4.png
```

### Creating Dataset CSVs

```python
from signature import create_dataset_csv

# For ViT (single image classification)
create_dataset_csv(
    image_directory="signatures/",
    output_csv="vit_dataset.csv",
    dataset_type="single"
)

# For ResNet (image pairs)
create_dataset_csv(
    image_directory="signatures/",
    output_csv="resnet_dataset.csv",
    dataset_type="pairs",
    pairs_per_person=50
)
```

## S3 Integration

The module seamlessly works with S3 for storing models, datasets, and reference signatures:

```python
from signature import S3Manager

# Create S3 manager
s3_manager = S3Manager()

# Download model weights
s3_manager.download_file(
    "s3://my-bucket/models/model.pth", 
    "local_model.pth"
)

# Upload trained model
s3_manager.upload_file(
    "local_model.pth",
    "s3://my-bucket/models/new_model.pth"
)
```

## Advanced Usage

### Custom Feature Extraction

```python
from signature import get_fused_features, extract_deep_features

# Extract fused features (deep + HOG)
features = get_fused_features(model, "signature.png")

# Extract only deep features
deep_features = extract_deep_features(model, "signature.png")
```

### Custom Training Loop

```python
from signature import (
    create_model, ContrastiveLoss, create_dataloader, 
    get_config
)
import torch

config = get_config()

# Create model and loss
model = create_model(model_type="resnet")
criterion = ContrastiveLoss(margin=17.5)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

# Create data loaders
train_loader, val_loader, test_loader = create_dataloader(
    "dataset.csv", 
    dataset_type="pairs",
    batch_size=32
)

# Custom training loop
for epoch in range(10):
    for img1, img2, labels in train_loader:
        optimizer.zero_grad()
        emb1, emb2 = model(img1, img2)
        loss = criterion(emb1, emb2, labels)
        loss.backward()
        optimizer.step()
```

## API Reference

### Core Functions

- `load_model()`: Load a trained model with optional S3 weights
- `classify_signatures()`: Classify detected signatures against references
- `train_model()`: Train a model with automatic type detection
- `create_dataset_csv()`: Create dataset CSV from image directory

### Model Classes

- `ResNet50Siamese`: Siamese ResNet50 for signature verification
- `SignatureViT`: Vision Transformer with ArcFace for classification
- `ContrastiveLoss`: Contrastive loss for Siamese networks
- `ArcFace`: Angular margin loss implementation

### Data Classes

- `SignatureDataset`: Dataset for single signature images
- `SignaturePairDataset`: Dataset for signature image pairs
- `create_dataloader()`: Create train/val/test data loaders

### Utility Classes

- `SignatureConfig`: Configuration management
- `S3Manager`: S3 operations manager

## Performance Tips

1. **Use GPU**: Set `SIGNATURE_DEVICE=cuda` for faster training and inference
2. **Batch Processing**: Use larger batch sizes for better GPU utilization
3. **Data Augmentation**: Enable augmentation for better generalization
4. **Caching**: Models and datasets are automatically cached locally
5. **S3 Optimization**: Use appropriate S3 region for reduced latency

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **S3 Access**: Check AWS credentials and permissions
3. **Memory Issues**: Reduce batch size or use CPU if GPU memory is limited
4. **Image Format**: Ensure images are in supported formats (PNG, JPG, JPEG)

### Debug Mode

Enable detailed logging:

```python
from signature.utils import setup_logging
setup_logging("DEBUG")
```

## Examples

See the `examples/` directory for complete examples:

- `train_vit_example.py`: Training a ViT model
- `train_resnet_example.py`: Training a ResNet Siamese model
- `inference_example.py`: Running inference on new signatures
- `s3_integration_example.py`: Working with S3 storage

## License

This module is part of the LiteWave ML Models repository. 