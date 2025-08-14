"""
QR Vision Service - Comprehensive QR Code & Barcode Processing Library

A powerful Python library for QR code and barcode operations with:
- Multi-engine support (ZXing, BoofCV)
- Region-based detection
- Batch processing
- Grid scanning
- Automatic Java detection
"""

__version__ = "1.0.0"
__author__ = "QR Vision"
__email__ = "qrvision@example.com"

from .service import QRCodeService, create_qr_service

__all__ = [
    "QRCodeService",
    "create_qr_service",
    "__version__"
]
