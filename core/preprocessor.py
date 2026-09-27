"""
Digital Heritage Archive - Image Preprocessing Engine
Performs computer vision enhancements on historical documents, manuscripts,
and degraded archival scans using OpenCV, Pillow, and NumPy.
"""

from typing import Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


class ImagePreprocessor:
    """Provides computer vision algorithms tailored for historical manuscript restoration."""

    @staticmethod
    def load_image(image_input) -> Image.Image:
        """Loads an image into a PIL Image object."""
        if isinstance(image_input, (str, bytes)):
            return Image.open(image_input)
        elif isinstance(image_input, Image.Image):
            return image_input.copy()
        elif isinstance(image_input, np.ndarray):
            if len(image_input.shape) == 2:
                return Image.fromarray(image_input)
            elif HAS_OPENCV:
                return Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
            return Image.fromarray(image_input)
        raise ValueError("Unsupported image input format.")

    @staticmethod
    def convert_to_pil(img_input) -> Image.Image:
        """Converts OpenCV numpy array or PIL Image into a standard RGB PIL Image."""
        if isinstance(img_input, Image.Image):
            return img_input
        elif isinstance(img_input, np.ndarray):
            if len(img_input.shape) == 2:
                return Image.fromarray(img_input).convert("RGB")
            elif HAS_OPENCV:
                return Image.fromarray(cv2.cvtColor(img_input, cv2.COLOR_BGR2RGB))
            return Image.fromarray(img_input).convert("RGB")
        raise ValueError("Unsupported image object.")

    @classmethod
    def deskew(cls, pil_img: Image.Image) -> Tuple[Image.Image, float]:
        """
        Detects the skew angle of the historical text and rotates it back to 0 degrees.
        """
        if HAS_OPENCV:
            np_img = np.array(pil_img.convert("RGB"))
            cv_bgr = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            coords = np.column_stack(np.where(thresh > 0))

            if len(coords) < 100:
                return pil_img, 0.0

            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            if abs(angle) < 0.2:
                return pil_img, 0.0

            rotated_pil = pil_img.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))
            return rotated_pil, round(float(angle), 2)
        else:
            # Native PIL deskew fallback (returns upright image)
            return pil_img, 0.0

    @classmethod
    def enhance_contrast(cls, pil_img: Image.Image, factor: float = 1.6) -> Image.Image:
        """
        Applies Contrast Enhancement to recover faded ancient ink.
        Uses CLAHE if OpenCV is present, otherwise high-fidelity PIL Autocontrast.
        """
        if HAS_OPENCV:
            np_img = np.array(pil_img.convert("RGB"))
            lab = cv2.cvtColor(np_img, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            merged = cv2.merge((cl, a, b))
            rgb = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
            return Image.fromarray(rgb)
        else:
            auto_c = ImageOps.autocontrast(pil_img, cutoff=2)
            enhancer = ImageEnhance.Contrast(auto_c)
            return enhancer.enhance(factor)

    @classmethod
    def remove_noise(cls, pil_img: Image.Image) -> Image.Image:
        """Removes background grain and noise while preserving character boundaries."""
        if HAS_OPENCV:
            np_img = np.array(pil_img.convert("RGB"))
            bgr = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
            denoised_bgr = cv2.fastNlMeansDenoisingColored(bgr, None, 10, 10, 7, 21)
            rgb = cv2.cvtColor(denoised_bgr, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb)
        else:
            return pil_img.filter(ImageFilter.MedianFilter(size=3))

    @classmethod
    def adaptive_binarize(cls, pil_img: Image.Image) -> Image.Image:
        """
        Segments historical text from stained or yellowed parchment background.
        """
        gray = pil_img.convert("L")
        if HAS_OPENCV:
            np_gray = np.array(gray)
            binarized = cv2.adaptiveThreshold(
                np_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10
            )
            return Image.fromarray(binarized).convert("RGB")
        else:
            # Otsu-like threshold with NumPy
            np_gray = np.array(gray)
            threshold_val = np.mean(np_gray) - 10
            binarized = (np_gray > threshold_val) * 255
            return Image.fromarray(binarized.astype(np.uint8)).convert("RGB")

    @classmethod
    def process_pipeline(
        cls,
        image_input,
        do_deskew: bool = True,
        do_contrast: bool = True,
        do_denoise: bool = True,
        do_binarize: bool = False,
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Runs the complete or customized image enhancement pipeline.
        Returns the enhanced PIL Image and an audit dictionary of operations applied.
        """
        img = cls.load_image(image_input)
        audit = {"engine": "OpenCV" if HAS_OPENCV else "Pillow/NumPy"}

        if do_deskew:
            img, angle = cls.deskew(img)
            audit["deskew_angle"] = angle

        if do_contrast:
            img = cls.enhance_contrast(img)
            audit["contrast_enhanced"] = True

        if do_denoise:
            img = cls.remove_noise(img)
            audit["denoised"] = True

        if do_binarize:
            img = cls.adaptive_binarize(img)
            audit["binarized"] = True

        return img, audit

    @classmethod
    def full_pipeline(
        cls,
        image_input,
        apply_deskew: bool = True,
        apply_contrast: bool = True,
        apply_denoise: bool = True,
        apply_binarization: bool = False,
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """Alias for process_pipeline supporting apply_* keyword arguments."""
        return cls.process_pipeline(
            image_input=image_input,
            do_deskew=apply_deskew,
            do_contrast=apply_contrast,
            do_denoise=apply_denoise,
            do_binarize=apply_binarization,
        )

