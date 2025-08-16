"""
Image Enhancement Presets for Hashub DocApp SDK

OCR kalitesini artırmak için önceden tanımlanmış görüntü geliştirme preset'leri.
enhance_doc.md'deki değerlere göre optimize edilmiştir.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ImageEnhanceOptions:
    """Image enhancement options for OCR preprocessing."""
    grayscale: bool = True
    invert: bool = False
    auto_contrast: bool = True
    brightness: float = 1.0
    contrast: float = 1.0
    sharpness: float = 1.0
    blur_radius: float = 0.0
    threshold: int = 170
    deskew: bool = True


class ImageEnhancePresets:
    """
    SDK özel image enhancement preset'leri.
    
    Her preset, belirli türdeki belgeler için optimize edilmiştir.
    convert_fast fonksiyonunda kullanılır.
    """
    
    @staticmethod
    def document_crisp() -> ImageEnhanceOptions:
        """
        Düz metinli tarama, anlaşılır belge için optimize edilmiş.
        
        Usage:
            client.convert_fast("doc.pdf", enhancement="document_crisp")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=False,
            auto_contrast=True,
            brightness=1.00,
            contrast=1.25,
            sharpness=1.15,
            blur_radius=0.0,
            threshold=170,
            deskew=True
        )
    
    @staticmethod
    def scan_low_dpi() -> ImageEnhanceOptions:
        """
        100–150 DPI zayıf taramalar için optimize edilmiş.
        
        Usage:
            client.convert_fast("scan.pdf", enhancement="scan_low_dpi")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=False,
            auto_contrast=True,
            brightness=1.00,
            contrast=1.30,
            sharpness=1.40,
            blur_radius=0.0,
            threshold=185,
            deskew=True
        )
    
    @staticmethod
    def camera_shadow() -> ImageEnhanceOptions:
        """
        Telefonla çekilmiş gölgeli sayfalar için optimize edilmiş.
        
        Usage:
            client.convert_fast("phone.jpg", enhancement="camera_shadow")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=False,
            auto_contrast=True,
            brightness=1.15,
            contrast=1.15,
            sharpness=1.20,
            blur_radius=0.3,
            threshold=180,
            deskew=True
        )
    
    @staticmethod
    def photocopy_faded() -> ImageEnhanceOptions:
        """
        Soluk fotokopi için optimize edilmiş.
        
        Usage:
            client.convert_fast("photocopy.pdf", enhancement="photocopy_faded")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=False,
            auto_contrast=True,
            brightness=1.30,
            contrast=1.40,
            sharpness=1.10,
            blur_radius=0.0,
            threshold=160,
            deskew=False
        )
    
    @staticmethod
    def inverted_scan() -> ImageEnhanceOptions:
        """
        Ters renkli (beyaz yazı siyah zemin) için optimize edilmiş.
        
        Usage:
            client.convert_fast("inverted.pdf", enhancement="inverted_scan")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=True,
            auto_contrast=True,
            brightness=1.00,
            contrast=1.10,
            sharpness=1.00,
            blur_radius=0.0,
            threshold=200,
            deskew=True
        )
    
    @staticmethod
    def noisy_dots() -> ImageEnhanceOptions:
        """
        Nokta/tuşele parazitli tarama için optimize edilmiş.
        
        Usage:
            client.convert_fast("noisy.pdf", enhancement="noisy_dots")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=False,
            auto_contrast=True,
            brightness=1.00,
            contrast=1.20,
            sharpness=1.00,
            blur_radius=0.8,
            threshold=190,
            deskew=False
        )
    
    @staticmethod
    def tables_fine() -> ImageEnhanceOptions:
        """
        Tablolu PDF/çıktı için optimize edilmiş.
        
        Usage:
            client.convert_fast("table.pdf", enhancement="tables_fine")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=False,
            auto_contrast=True,
            brightness=1.00,
            contrast=1.20,
            sharpness=1.40,
            blur_radius=0.0,
            threshold=190,
            deskew=True
        )
    
    @staticmethod
    def receipt_thermal() -> ImageEnhanceOptions:
        """
        Isı yazıcılı fiş/fatura için optimize edilmiş.
        
        Usage:
            client.convert_fast("receipt.jpg", enhancement="receipt_thermal")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=False,
            auto_contrast=True,
            brightness=1.10,
            contrast=1.30,
            sharpness=1.30,
            blur_radius=0.0,
            threshold=180,
            deskew=True
        )
    
    @staticmethod
    def newspaper_moire() -> ImageEnhanceOptions:
        """
        Gazete/dergi (moire) için optimize edilmiş.
        
        Usage:
            client.convert_fast("newspaper.pdf", enhancement="newspaper_moire")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=False,
            auto_contrast=True,
            brightness=1.00,
            contrast=1.20,
            sharpness=1.00,
            blur_radius=0.4,
            threshold=185,
            deskew=True
        )
    
    @staticmethod
    def fax_low_quality() -> ImageEnhanceOptions:
        """
        Eski faks görüntüleri için optimize edilmiş.
        
        Usage:
            client.convert_fast("fax.pdf", enhancement="fax_low_quality")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=False,
            auto_contrast=True,
            brightness=1.00,
            contrast=1.20,
            sharpness=1.10,
            blur_radius=0.6,
            threshold=190,
            deskew=True
        )
    
    @staticmethod
    def blueprint() -> ImageEnhanceOptions:
        """
        Teknik çizim/mimari plan için optimize edilmiş.
        
        Usage:
            client.convert_fast("blueprint.pdf", enhancement="blueprint")
        """
        return ImageEnhanceOptions(
            grayscale=True,
            invert=False,
            auto_contrast=True,
            brightness=1.00,
            contrast=1.40,
            sharpness=1.60,
            blur_radius=0.0,
            threshold=200,
            deskew=True
        )


def get_enhancement_preset(preset_name: str) -> Optional[ImageEnhanceOptions]:
    """
    Get enhancement preset by name.
    
    Args:
        preset_name: Name of the preset
        
    Returns:
        ImageEnhanceOptions or None if preset not found
    """
    preset_map = {
        "document_crisp": ImageEnhancePresets.document_crisp,
        "scan_low_dpi": ImageEnhancePresets.scan_low_dpi,
        "camera_shadow": ImageEnhancePresets.camera_shadow,
        "photocopy_faded": ImageEnhancePresets.photocopy_faded,
        "inverted_scan": ImageEnhancePresets.inverted_scan,
        "noisy_dots": ImageEnhancePresets.noisy_dots,
        "tables_fine": ImageEnhancePresets.tables_fine,
        "receipt_thermal": ImageEnhancePresets.receipt_thermal,
        "newspaper_moire": ImageEnhancePresets.newspaper_moire,
        "fax_low_quality": ImageEnhancePresets.fax_low_quality,
        "blueprint": ImageEnhancePresets.blueprint,
    }
    
    preset_func = preset_map.get(preset_name)
    return preset_func() if preset_func else None


def get_available_presets() -> Dict[str, str]:
    """
    Get all available enhancement presets with descriptions.
    
    Returns:
        Dictionary mapping preset names to descriptions
    """
    return {
        "document_crisp": "Clean text documents, clear scans",
        "scan_low_dpi": "Low quality scans (100-150 DPI)",
        "camera_shadow": "Phone camera with shadows",
        "photocopy_faded": "Faded photocopies",
        "inverted_scan": "Inverted colors (white text on black)",
        "noisy_dots": "Noisy scans with dots/artifacts",
        "tables_fine": "Documents with tables/columns",
        "receipt_thermal": "Thermal printer receipts/invoices",
        "newspaper_moire": "Newspaper/magazine with moire",
        "fax_low_quality": "Old fax images",
        "blueprint": "Technical drawings/blueprints"
    }


def enhancement_options_to_dict(options: ImageEnhanceOptions) -> Dict[str, Any]:
    """
    Convert ImageEnhanceOptions to dictionary for API.
    
    Args:
        options: Enhancement options
        
    Returns:
        Dictionary representation
    """
    return {
        "grayscale": options.grayscale,
        "invert": options.invert,
        "auto_contrast": options.auto_contrast,
        "brightness": options.brightness,
        "contrast": options.contrast,
        "sharpness": options.sharpness,
        "blur_radius": options.blur_radius,
        "threshold": options.threshold,
        "deskew": options.deskew
    }
