#!/usr/bin/env python3
"""
Command Line Interface for QR Vision Service
"""

import argparse
import json
import sys
import os
from pathlib import Path
from .service import create_qr_service


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="QR Vision Service - Comprehensive QR & Barcode Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qr-vision generate "Hello World!" output.png
  qr-vision decode image.png
  qr-vision region image.png 100 100 200 200
  qr-vision info
        """
    )
    
    parser.add_argument("--jar", help="Path to JAR file (optional)")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate QR code")
    gen_parser.add_argument("text", help="Text to encode")
    gen_parser.add_argument("output", help="Output file path")
    gen_parser.add_argument("--width", type=int, default=300, help="Image width")
    gen_parser.add_argument("--height", type=int, default=300, help="Image height")
    gen_parser.add_argument("--format", default="PNG", choices=["PNG", "JPG"],
                           help="Image format")
    
    # Decode command
    dec_parser = subparsers.add_parser("decode", help="Decode QR/barcode")
    dec_parser.add_argument("image", help="Image file path")
    dec_parser.add_argument("--mode", default="all",
                           choices=["all", "qr", "qr-zxing", "qr-boofcv", "barcode"],
                           help="Decoding mode")
    
    # Region command
    region_parser = subparsers.add_parser("region", help="Decode from region")
    region_parser.add_argument("image", help="Image file path")
    region_parser.add_argument("x", type=int, help="X coordinate")
    region_parser.add_argument("y", type=int, help="Y coordinate")
    region_parser.add_argument("width", type=int, help="Width")
    region_parser.add_argument("height", type=int, help="Height")
    region_parser.add_argument("--mode", default="all",
                              choices=["all", "qr", "qr-zxing", "qr-boofcv", "barcode"],
                              help="Decoding mode")
    
    # Grid command
    grid_parser = subparsers.add_parser("grid", help="Grid scan")
    grid_parser.add_argument("image", help="Image file path")
    grid_parser.add_argument("--cols", type=int, default=3, help="Grid columns")
    grid_parser.add_argument("--rows", type=int, default=3, help="Grid rows")
    grid_parser.add_argument("--mode", default="all",
                            choices=["all", "qr", "qr-zxing", "qr-boofcv", "barcode"],
                            help="Decoding mode")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show service info")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Determine JAR path
        jar_path = args.jar
        if not jar_path:
            # Try to find JAR in package directory
            package_dir = Path(__file__).parent
            jar_file = package_dir / "vision.jar"
            if jar_file.exists():
                jar_path = str(jar_file)
            else:
                jar_path = "vision.jar"  # Try current directory
        
        # Create service
        service = create_qr_service(
            jar_path=jar_path,
            log_level=args.log_level
        )
        
        # Execute command
        if args.command == "generate":
            result = service.generate_qr_code(
                args.text, args.output, args.width, args.height, args.format
            )
            print(json.dumps(result, indent=2))
            return 0 if result.get("success") else 1
            
        elif args.command == "decode":
            result = service.decode_image(args.image, args.mode)
            print(json.dumps(result, indent=2))
            return 0 if result.get("success") else 1
            
        elif args.command == "region":
            result = service.decode_region(
                args.image, args.x, args.y, args.width, args.height, args.mode
            )
            print(json.dumps(result, indent=2))
            return 0 if result.get("success") else 1
            
        elif args.command == "grid":
            result = service.decode_with_grid_scan(
                args.image, args.cols, args.rows, args.mode
            )
            print(json.dumps(result, indent=2))
            return 0 if result.get("success") else 1
            
        elif args.command == "info":
            info = service.get_service_info()
            print(json.dumps(info, indent=2))
            return 0
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
