# QR Vision Service

Comprehensive QR Code & Barcode processing library with advanced region detection capabilities.

## 🚀 Features

- **Multi-engine support**: ZXing and BoofCV engines
- **Region-based detection**: Scan specific areas of images
- **Batch processing**: Handle multiple files efficiently  
- **Grid scanning**: Systematic scanning with overlap
- **Auto Java detection**: Automatically finds JDK 17+
- **CLI interface**: Command-line tools included

## 📦 Installation

```bash
pip install qr-vision-service
```

## 🎯 Quick Start

### Python API

```python
from qr_vision_service import create_qr_service

# Create service
service = create_qr_service()

# Generate QR code
result = service.generate_qr_code("Hello World!", "output.png")

# Decode QR code
decode_result = service.decode_image("output.png")

# Region detection
region_result = service.decode_region("image.png", x=100, y=100, width=200, height=200)
```

### Command Line

```bash
# Generate QR code
qr-vision generate "Hello World!" output.png

# Decode image
qr-vision decode image.png

# Region detection
qr-vision region image.png 100 100 200 200

# Grid scanning
qr-vision grid image.png --cols 3 --rows 3
```

## 📋 Requirements

- **Python 3.7+**
- **Java 17+** (automatically detected)
- **Pillow** (for image processing)

## 🔧 Advanced Usage

### Batch Processing

```python
# Generate multiple QR codes
texts_and_files = [
    ("Email: test@example.com", "qr_email.png"),
    ("Phone: +1234567890", "qr_phone.png"),
    ("Website: https://example.com", "qr_web.png")
]

batch_result = service.generate_qr_codes_batch(texts_and_files)
```

### Grid Scanning

```python
# Systematic grid scanning
result = service.decode_with_grid_scan(
    image_file="document.png",
    grid_cols=3, 
    grid_rows=3,
    overlap_percent=0.1
)
```

### Service Configuration

```python
# Custom configuration
service = QRCodeService(
    jar_path="custom_path/vision.jar",
    auto_find_java=True
)

# Set logging level
service.set_log_level("DEBUG")
```

## 🎛️ API Reference

### Core Methods

- `generate_qr_code(text, output_file, width=300, height=300, format="PNG")`
- `decode_image(image_file, mode="all")`
- `decode_region(image_file, x, y, width, height, mode="all")`
- `decode_with_grid_scan(image_file, grid_cols=3, grid_rows=3)`

### Batch Methods

- `generate_qr_codes_batch(texts_and_files, width=300, height=300)`
- `decode_images_batch(image_files, mode="all")`
- `decode_multiple_regions(image_file, regions, mode="all")`

### Modes

- `"all"` - All engines (ZXing + BoofCV)
- `"qr-zxing"` - ZXing QR engine only
- `"qr-boofcv"` - BoofCV QR engine only
- `"barcode"` - Barcode detection only

## 🏢 Integration Examples

### Web Application

```python
from flask import Flask, request, jsonify
from qr_vision_service import create_qr_service

app = Flask(__name__)
qr_service = create_qr_service()

@app.route('/generate', methods=['POST'])
def generate_qr():
    data = request.json
    result = qr_service.generate_qr_code(
        data['text'], 
        f"qr_{data['id']}.png"
    )
    return jsonify(result)
```

### Document Processing

```python
class DocumentProcessor:
    def __init__(self):
        self.qr_service = create_qr_service()
    
    def scan_document(self, image_path):
        return self.qr_service.decode_with_grid_scan(
            image_path, 
            grid_cols=4, 
            grid_rows=3
        )
```

## 🛠️ Development

```bash
# Install development dependencies
pip install qr-vision-service[dev]

# Run tests
pytest

# Code formatting
black qr_vision_service/
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Full API documentation available
- **Examples**: Check the examples directory

## 🔄 Changelog

### v1.0.0
- Initial release
- Multi-engine QR/barcode support
- Region-based detection
- Grid scanning functionality
- CLI interface
- Batch processing capabilities
