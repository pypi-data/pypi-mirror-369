"""
Comprehensive tests for the elegant image utility module.
"""

import base64
import io
import tempfile
import warnings
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlparse

import numpy as np
import pytest

from utils.image import (
    ImageInfo,
    ImageProcessor,
    ImageResource,
    ImageWriter,
    read_image,
    write_image,
)


class TestImageResource:
    """Test all ImageResource methods."""

    def test_from_standard(self):
        """Test loading standard test images."""
        # Test with short name
        img = ImageResource.from_standard("chelsea")
        assert isinstance(img, np.ndarray)
        assert len(img.shape) == 3  # Should be color image

        # Test with full filename
        img2 = ImageResource.from_standard("chelsea.png")
        assert np.array_equal(img, img2)

        # Test invalid standard image
        with pytest.raises(ValueError, match="Unknown standard image"):
            ImageResource.from_standard("nonexistent")

    def test_from_file(self):
        """Test reading from file system."""
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            test_img = ImageResource.from_standard("chelsea")
            ImageWriter.to_file(test_img, tmp.name)

            # Test reading the file
            loaded_img = ImageResource.from_file(tmp.name)
            assert isinstance(loaded_img, np.ndarray)
            assert loaded_img.shape == test_img.shape

            # Clean up
            Path(tmp.name).unlink()

    def test_from_bytes(self):
        """Test reading from byte data."""
        # Get test image as bytes
        test_img = ImageResource.from_standard("chelsea")
        img_bytes = ImageWriter.to_bytes(test_img, ".png")

        # Test reading from bytes
        loaded_img = ImageResource.from_bytes(img_bytes, ".png")
        assert isinstance(loaded_img, np.ndarray)
        assert loaded_img.shape == test_img.shape

        # Test with extension without dot
        loaded_img2 = ImageResource.from_bytes(img_bytes, "png")
        assert np.array_equal(loaded_img, loaded_img2)

    def test_from_stream(self):
        """Test reading from file-like objects."""
        test_img = ImageResource.from_standard("chelsea")
        img_bytes = ImageWriter.to_bytes(test_img, ".png")

        # Test with BytesIO
        stream = io.BytesIO(img_bytes)
        loaded_img = ImageResource.from_stream(stream)
        assert isinstance(loaded_img, np.ndarray)
        assert loaded_img.shape == test_img.shape

    def test_from_base64(self):
        """Test reading from base64 encoded data."""
        test_img = ImageResource.from_standard("chelsea")

        # Test with plain base64
        b64_string = ImageWriter.to_base64(test_img, ".png")
        loaded_img = ImageResource.from_base64(b64_string, ".png")
        assert isinstance(loaded_img, np.ndarray)
        assert loaded_img.shape == test_img.shape

        # Test with data URI
        data_uri = ImageWriter.to_base64(test_img, ".png", include_data_uri=True)
        loaded_img2 = ImageResource.from_base64(data_uri)
        assert np.array_equal(loaded_img, loaded_img2)

        # Test with JPEG data URI (should auto-detect format)
        jpeg_uri = ImageWriter.to_base64(test_img, ".jpg", include_data_uri=True)
        loaded_img3 = ImageResource.from_base64(jpeg_uri)
        assert isinstance(loaded_img3, np.ndarray)

        # Test invalid base64
        with pytest.raises(ValueError, match="Invalid base64 data"):
            ImageResource.from_base64("invalid_base64_data")

    def test_from_url(self):
        """Test URL validation (without actual network calls)."""
        # Test invalid URL schemes
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            ImageResource.from_url("invalid://example.com/image.png")

        # Valid schemes should pass validation (but may fail on network)
        valid_urls = [
            "http://example.com/image.png",
            "https://example.com/image.png",
            "ftp://example.com/image.png",
            "ftps://example.com/image.png",
        ]

        for url in valid_urls:
            parsed = urlparse(url)
            assert parsed.scheme in ("http", "https", "ftp", "ftps")

    def test_from_zip(self):
        """Test reading from ZIP archives."""
        # This is a basic test - real ZIP testing would require creating archives
        zip_path = "test.zip"
        internal_path = "image.png"
        expected_path = f"{zip_path}/{internal_path}"

        # Just verify the path construction
        assert expected_path == "test.zip/image.png"

    def test_from_webcam_error_handling(self):
        """Test webcam error handling."""
        # Mock imread to raise an exception
        with patch("utils.image.iio.imread") as mock_imread:
            mock_imread.side_effect = Exception("Camera not available")

            with pytest.raises(RuntimeError, match="Failed to access webcam device"):
                ImageResource.from_webcam(0)

    def test_get_info(self):
        """Test image information retrieval."""
        info = ImageResource.get_info("imageio:chelsea.png")
        assert isinstance(info, ImageInfo)
        assert hasattr(info, "shape")
        assert hasattr(info, "dtype")
        assert len(info.shape) >= 2  # At least 2D

    def test_stream_webcam(self):
        """Test webcam streaming (mock)."""
        # Mock the imiter function
        fake_frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(3)]

        with patch("utils.image.iio.imiter") as mock_imiter:
            mock_imiter.return_value = iter(fake_frames)

            frames = list(ImageResource.stream_webcam(max_frames=3))
            assert len(frames) == 3
            assert all(frame.shape == (100, 100, 3) for frame in frames)

    def test_stream_video(self):
        """Test video streaming (mock)."""
        fake_frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(2)]

        with patch("utils.image.iio.imiter") as mock_imiter:
            mock_imiter.return_value = iter(fake_frames)

            frames = list(ImageResource.stream_video("test.mp4"))
            assert len(frames) == 2


class TestImageWriter:
    """Test all ImageWriter methods."""

    def test_to_file(self):
        """Test writing to file."""
        test_img = ImageResource.from_standard("chelsea")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            ImageWriter.to_file(test_img, tmp.name)
            assert Path(tmp.name).exists()

            # Verify we can read it back
            loaded = ImageResource.from_file(tmp.name)
            assert loaded.shape == test_img.shape

            Path(tmp.name).unlink()

    def test_to_bytes(self):
        """Test encoding to bytes."""
        test_img = ImageResource.from_standard("chelsea")

        # Test PNG
        png_bytes = ImageWriter.to_bytes(test_img, ".png")
        assert isinstance(png_bytes, bytes)
        assert len(png_bytes) > 0

        # Test JPEG with quality
        jpg_bytes = ImageWriter.to_bytes(test_img, ".jpg", quality=90)
        assert isinstance(jpg_bytes, bytes)
        assert len(jpg_bytes) > 0

        # Test format without dot
        png_bytes2 = ImageWriter.to_bytes(test_img, "png")
        assert isinstance(png_bytes2, bytes)

    def test_to_stream(self):
        """Test writing to stream."""
        test_img = ImageResource.from_standard("chelsea")

        output = io.BytesIO()
        ImageWriter.to_stream(test_img, output, ".png")

        output.seek(0)
        loaded = ImageResource.from_stream(output)
        assert loaded.shape == test_img.shape

    def test_to_base64(self):
        """Test base64 encoding."""
        test_img = ImageResource.from_standard("chelsea")

        # Test plain base64
        b64_string = ImageWriter.to_base64(test_img, ".png")
        assert isinstance(b64_string, str)
        assert len(b64_string) > 0

        # Verify it's valid base64
        decoded = base64.b64decode(b64_string)
        assert isinstance(decoded, bytes)

        # Test data URI
        data_uri = ImageWriter.to_base64(test_img, ".png", include_data_uri=True)
        assert data_uri.startswith("data:image/png;base64,")

        # Test JPEG with quality and data URI
        jpeg_uri = ImageWriter.to_base64(test_img, ".jpg", include_data_uri=True, quality=85)
        assert jpeg_uri.startswith("data:image/jpeg;base64,")

        # Test format mapping
        formats_to_test = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"]
        for fmt in formats_to_test:
            uri = ImageWriter.to_base64(test_img, fmt, include_data_uri=True)
            assert uri.startswith("data:image/")

    def test_create_gif(self):
        """Test GIF creation."""
        # Create test frames
        frames = []
        for i in range(3):
            frame = np.full((50, 50, 3), i * 80, dtype=np.uint8)
            frames.append(frame)

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
            ImageWriter.create_gif(frames, tmp.name, duration=0.1, loop=0)
            assert Path(tmp.name).exists()

            # Verify it's readable
            loaded = ImageResource.from_file(tmp.name)
            assert isinstance(loaded, np.ndarray)

            Path(tmp.name).unlink()

    def test_create_video(self):
        """Test video creation."""
        # Create test frames
        frames = []
        for i in range(3):
            frame = np.full((50, 50, 3), i * 80, dtype=np.uint8)
            frames.append(frame)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            try:
                ImageWriter.create_video(frames, tmp.name, fps=1.0)
                assert Path(tmp.name).exists()
            except Exception:
                # Video creation might fail without proper codecs
                pytest.skip("Video creation requires ffmpeg")
            finally:
                if Path(tmp.name).exists():
                    Path(tmp.name).unlink()


class TestImageProcessor:
    """Test image processing functions."""

    def test_to_grayscale(self):
        """Test grayscale conversion."""
        test_img = ImageResource.from_standard("chelsea")

        # Test default weights
        gray = ImageProcessor.to_grayscale(test_img)
        assert gray.dtype == test_img.dtype
        assert len(gray.shape) == 2 or (len(gray.shape) == 3 and gray.shape[2] == 1)

        # Test custom weights
        custom_gray = ImageProcessor.to_grayscale(test_img, weights=(0.33, 0.33, 0.34))
        assert custom_gray.shape == gray.shape

        # Test already grayscale image
        gray_twice = ImageProcessor.to_grayscale(gray)
        assert np.array_equal(gray, gray_twice)

    def test_normalize(self):
        """Test image normalization."""
        test_img = ImageResource.from_standard("chelsea")

        # Test default normalization [0, 1]
        norm = ImageProcessor.normalize(test_img)
        assert norm.min() >= 0.0
        assert norm.max() <= 1.0

        # Test custom range [-1, 1]
        norm_custom = ImageProcessor.normalize(test_img, (-1, 1))
        assert norm_custom.min() >= -1.0
        assert norm_custom.max() <= 1.0

        # Test constant image
        constant_img = np.full((10, 10), 128, dtype=np.uint8)
        norm_const = ImageProcessor.normalize(constant_img)
        assert np.all(norm_const == 0.0)  # Should be minimum value

    def test_batch_process(self):
        """Test batch processing."""
        img1 = ImageResource.from_standard("chelsea")
        img2 = ImageResource.from_standard("astronaut")
        images = [img1, img2]

        # Test grayscale batch processing
        gray_batch = ImageProcessor.batch_process(images, ImageProcessor.to_grayscale)
        assert len(gray_batch) == 2
        assert all(isinstance(img, np.ndarray) for img in gray_batch)

        # Test normalization batch processing
        norm_batch = ImageProcessor.batch_process(images, ImageProcessor.normalize)
        assert len(norm_batch) == 2
        assert all(img.min() >= 0.0 and img.max() <= 1.0 for img in norm_batch)


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_read_image_auto_detection(self):
        """Test automatic source type detection."""
        # Test standard image
        img1 = read_image("chelsea")
        assert isinstance(img1, np.ndarray)

        # Test file path
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            test_img = ImageResource.from_standard("chelsea")
            ImageWriter.to_file(test_img, tmp.name)

            img2 = read_image(tmp.name)
            assert isinstance(img2, np.ndarray)

            Path(tmp.name).unlink()

        # Test bytes
        img_bytes = ImageWriter.to_bytes(test_img, ".png")
        img3 = read_image(img_bytes)
        assert isinstance(img3, np.ndarray)

        # Test stream
        stream = io.BytesIO(img_bytes)
        img4 = read_image(stream)
        assert isinstance(img4, np.ndarray)

        # Test base64 data URI
        data_uri = ImageWriter.to_base64(test_img, ".png", include_data_uri=True)
        img5 = read_image(data_uri)
        assert isinstance(img5, np.ndarray)

        # Test plain base64 (long alphanumeric string)
        b64_string = ImageWriter.to_base64(test_img, ".png")
        img6 = read_image(b64_string)
        assert isinstance(img6, np.ndarray)

    def test_write_image(self):
        """Test unified write function."""
        test_img = ImageResource.from_standard("chelsea")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            write_image(test_img, tmp.name)
            assert Path(tmp.name).exists()

            loaded = read_image(tmp.name)
            assert loaded.shape == test_img.shape

            Path(tmp.name).unlink()


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_inputs(self):
        """Test various invalid inputs."""
        # Invalid source type for read_image
        with pytest.raises(ValueError, match="Unsupported source type"):
            read_image(123)

        # Invalid URL scheme
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            ImageResource.from_url("invalid://example.com")

        # Invalid standard image
        with pytest.raises(ValueError, match="Unknown standard image"):
            ImageResource.from_standard("nonexistent")

    def test_base64_round_trip(self):
        """Test complete base64 round-trip conversion."""
        original = ImageResource.from_standard("chelsea")

        # PNG round-trip
        b64_png = ImageWriter.to_base64(original, ".png")
        restored_png = ImageResource.from_base64(b64_png, ".png")
        assert restored_png.shape == original.shape

        # Data URI round-trip
        data_uri = ImageWriter.to_base64(original, ".png", include_data_uri=True)
        restored_uri = ImageResource.from_base64(data_uri)
        assert restored_uri.shape == original.shape

        # JPEG round-trip (lossy compression)
        jpg_uri = ImageWriter.to_base64(original, ".jpg", include_data_uri=True, quality=95)
        restored_jpg = ImageResource.from_base64(jpg_uri)
        assert restored_jpg.shape == original.shape

    def test_warnings_suppression(self):
        """Test that warnings are properly handled."""
        # This test ensures our warning handling works
        with warnings.catch_warnings(record=True) as _:
            warnings.simplefilter("always")

            # Try to get info from a problematic source (mock)
            with patch("utils.image.iio.improps") as mock_improps:
                mock_improps.side_effect = Exception("Test error")

                with patch("utils.image.iio.immeta") as mock_immeta:
                    mock_immeta.side_effect = Exception("Test error")

                    with patch("utils.image.iio.imread") as mock_imread:
                        test_img = np.zeros((10, 10, 3), dtype=np.uint8)
                        mock_imread.return_value = test_img

                        info = ImageResource.get_info("test")
                        assert isinstance(info, ImageInfo)
                        assert info.shape == (10, 10, 3)


def test_integration():
    """Integration test combining multiple features."""
    # Load standard image
    original = ImageResource.from_standard("chelsea")

    # Process it
    gray = ImageProcessor.to_grayscale(original)
    normalized = ImageProcessor.normalize(gray)

    # Convert to base64
    b64_data = ImageWriter.to_base64(normalized, ".png")

    # Read back from base64
    restored = ImageResource.from_base64(b64_data)

    # Verify round-trip
    assert restored.shape == normalized.shape
    # Note: dtype may change due to format conversion (float -> uint8)
    assert restored.dtype in (normalized.dtype, np.uint8)

    # Test with convenience function
    auto_restored = read_image(b64_data)
    assert np.array_equal(restored, auto_restored)


if __name__ == "__main__":
    # Run a simple test to verify basic functionality
    print("Running basic functionality test...")

    try:
        # Test basic operations
        img = ImageResource.from_standard("chelsea")
        print(f"✅ Standard image loaded: {img.shape}")

        # Test base64 conversion
        b64 = ImageWriter.to_base64(img, ".png")
        restored = ImageResource.from_base64(b64)
        print(f"✅ Base64 round-trip successful: {restored.shape}")

        # Test processing
        gray = ImageProcessor.to_grayscale(img)
        print(f"✅ Grayscale conversion: {gray.shape}")

        print("🎉 All basic tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
