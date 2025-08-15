# Tri-Breed Image Dataset Generator

This project aims to create a Python package for generating diverse and enriched image datasets from a small original dataset using three augmentation families:

1.  **Traditional Augmentation**: Flips, rotations, scaling, cropping, color jitter, etc., implemented via Albumentations.
2.  **Neural Style Transfer (NST)**: Applies artistic/domain-specific textures from style images, implemented with PyTorch + pre-trained fast NST models.
3.  **Patch Mixing**: Combines regions from different images (CutMix, MixUp) to boost structural diversity.

## Goals

- Produce lightweight, diverse datasets for small-data training scenarios.
- Allow custom combinations of techniques per batch.

## Features

- **Gradio-based UI**: For interactive usage, allowing users to upload base datasets and optional style images, choose augmentation pipelines and parameters, and preview generated samples in real-time.
- **Python API & CLI**: For batch automation.
- **Export**: To standard dataset formats (COCO, ImageFolder, etc.).
- **Diversity Scoring**: (LPIPS, FID) with visual reports.

## Gradio Workflow Example

1.  User uploads original images.
2.  Selects techniques (checklist) and parameters (sliders for rotation, blend ratio, style strength).
3.  Previews augmented images instantly.
4.  Clicks "Generate & Download" to export the batch.