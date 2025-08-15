"""Loss functions for signature verification models."""

from .arcface import ArcFace
from .contrastive import ContrastiveLoss

__all__ = ["ArcFace", "ContrastiveLoss"]
