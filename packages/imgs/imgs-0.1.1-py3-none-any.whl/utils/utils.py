"""
Utilities Package - Collection of useful utility functions and classes.

This module provides convenient access to all utility functionality including
image processing, data manipulation, and more.
"""

# Image utilities - comprehensive image I/O and processing
from .image import (
    ImageInfo,
    ImageProcessor,
    # Core classes
    ImageResource,
    ImageWriter,
    # Convenience functions
    read_image,
    write_image,
)

# Define what gets exported when using "from utils import *"
__all__ = [
    # Image utilities
    "ImageResource",
    "ImageWriter",
    "ImageProcessor",
    "ImageInfo",
    "read_image",
    "write_image",
    # Convenience aliases
    "load_image",
    "save_image",
]

# Convenience aliases for common operations
load_image = read_image  # More intuitive for some users
save_image = write_image  # More intuitive for some users


def main():
    """Main entry point for the utilities package."""
    print("🛠️  Utils Package - Image Processing Utilities")
    print("=" * 50)

    # Demo basic functionality
    try:
        # Load a standard test image
        img = ImageResource.from_standard("chelsea")
        print(f"✅ Loaded test image: {img.shape}, {img.dtype}")

        # Convert to grayscale
        gray = ImageProcessor.to_grayscale(img)
        print(f"✅ Converted to grayscale: {gray.shape}")

        # Convert to base64
        b64 = ImageWriter.to_base64(gray, ".png")
        print(f"✅ Converted to base64: {len(b64)} characters")

        # Round-trip test
        restored = ImageResource.from_base64(b64)
        print(f"✅ Restored from base64: {restored.shape}")

        print("\n🎉 All utilities working correctly!")
        print("\nAvailable functions:")
        print("- ImageResource: Load images from files, URLs, base64, webcam, etc.")
        print("- ImageWriter: Save images to files, base64, bytes, streams, etc.")
        print("- ImageProcessor: Convert, normalize, batch process images")
        print("- read_image/load_image: Universal image loading")
        print("- write_image/save_image: Universal image saving")

    except Exception as e:
        print(f"❌ Error during demo: {e}")


if __name__ == "__main__":
    main()
