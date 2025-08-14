#!/usr/bin/env python3
"""
QR Code & Barcode Service
A comprehensive Python service for QR code and barcode operations
Provides generation, decoding, and region-based detection capabilities
"""

import subprocess
import json
import os
import sys
from typing import Dict, List, Optional, Union, Tuple
import platform
import logging
from pathlib import Path


class QRCodeService:
    """
    Comprehensive QR Code & Barcode Service
    
    Features:
    - QR code generation with customizable formats
    - Multi-engine QR/barcode decoding (ZXing, BoofCV)
    - Region-based detection for precise scanning
    - Automatic JDK detection and management
    - Full error handling and logging
    """
    
    def __init__(self, jar_path: str = "vision.jar", auto_find_java: bool = True, logger: Optional[logging.Logger] = None):
        """
        Initialize QR Code Service
        
        Args:
            jar_path: Path to the JAR file
            auto_find_java: Whether to automatically find suitable Java installation
            logger: Optional logger instance for debugging
        """
        self.jar_path = jar_path
        self.logger = logger or self._setup_logger()
        
        # Validate JAR file exists
        if not os.path.exists(jar_path):
            raise FileNotFoundError(f"JAR file not found: {jar_path}")
        
        # Setup Java executable
        if auto_find_java:
            self.java_executable = self._find_java_executable()
            if not self.java_executable:
                raise RuntimeError("No suitable Java installation found. Please install JDK 17+")
        else:
            self.java_executable = "java"
        
        self.logger.info(f"QR Service initialized with JAR: {jar_path}")
        self.logger.info(f"Using Java: {self.java_executable}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger"""
        logger = logging.getLogger("QRCodeService")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _find_java_executable(self) -> Optional[str]:
        """
        Find the best Java executable to use
        Priority:
        1. JDK 17+ from known paths
        2. JAVA_HOME environment variable  
        3. System PATH java
        """
        
        # Known JDK installation paths
        if platform.system() == "Windows":
            jdk_paths = [
                r"C:\DevTools\Java\jdk-17_windows-x64_bin\bin\java.exe",
                r"C:\Program Files\Java\jdk-17\bin\java.exe",
                r"C:\Program Files\Java\jdk-21\bin\java.exe",
                r"C:\Program Files\Java\jdk-19\bin\java.exe",
                r"C:\Program Files\Java\jdk-18\bin\java.exe",
                r"C:\Program Files\Oracle\Java\jdk-17\bin\java.exe",
                r"C:\Program Files (x86)\Java\jdk-17\bin\java.exe",
            ]
        else:
            jdk_paths = [
                "/usr/lib/jvm/java-17-openjdk/bin/java",
                "/usr/lib/jvm/java-21-openjdk/bin/java",
                "/usr/lib/jvm/java-19-openjdk/bin/java",
                "/usr/lib/jvm/java-18-openjdk/bin/java",
                "/opt/java/jdk-17/bin/java",
                "/opt/java/jdk-21/bin/java",
            ]
        
        # 1. Try known JDK paths
        for java_path in jdk_paths:
            if os.path.exists(java_path):
                version = self._get_java_version(java_path)
                if version and version >= 17:
                    self.logger.info(f"Found JDK {version} at: {java_path}")
                    return java_path
        
        # 2. Try JAVA_HOME
        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            java_path = os.path.join(java_home, "bin", "java.exe" if platform.system() == "Windows" else "java")
            if os.path.exists(java_path):
                version = self._get_java_version(java_path)
                if version and version >= 17:
                    self.logger.info(f"Found JDK {version} from JAVA_HOME: {java_path}")
                    return java_path
        
        # 3. Try system PATH
        try:
            java_path = "java"
            version = self._get_java_version(java_path)
            if version and version >= 17:
                self.logger.info(f"Found JDK {version} from PATH")
                return java_path
        except:
            pass
        
        # Log error and suggestions
        self.logger.error("No suitable Java installation found!")
        self.logger.error("Requirements: Java 17 or higher")
        self.logger.error("Suggestions:")
        self.logger.error("1. Install JDK 17+ and set JAVA_HOME environment variable")
        self.logger.error("2. Add JDK 17+ bin directory to PATH")
        
        return None
    
    def _get_java_version(self, java_executable: str) -> Optional[int]:
        """Get Java version number"""
        try:
            result = subprocess.run(
                [java_executable, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse version from output
            version_line = result.stderr.split('\n')[0] if result.stderr else ""
            if "version" in version_line:
                # Extract version number (e.g., "17.0.1" from 'openjdk version "17.0.1"')
                import re
                match = re.search(r'"(\d+)\.(\d+)\.(\d+)', version_line)
                if match:
                    major = int(match.group(1))
                    return major
                # Try alternative format
                match = re.search(r'"(\d+)"', version_line)
                if match:
                    return int(match.group(1))
                    
        except Exception as e:
            self.logger.debug(f"Error getting Java version: {e}")
        
        return None
    
    def _execute_command(self, command: List[str], timeout: int = 30) -> Dict:
        """
        Execute JAR command and return JSON result
        
        Args:
            command: Command arguments to pass to JAR
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary containing the result
        """
        try:
            full_command = [self.java_executable, "-jar", self.jar_path] + command
            self.logger.debug(f"Executing: {' '.join(full_command)}")
            
            # Use UTF-8 encoding to handle Unicode properly  
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace invalid chars instead of failing
                timeout=timeout
            )
            
            if result.returncode != 0:
                self.logger.error(f"Command failed with exit code {result.returncode}")
                return {
                    "success": False,
                    "error": f"Command failed with exit code {result.returncode}",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }
            
            # Try to parse JSON output (should be the last line)
            output_lines = result.stdout.strip().split('\n')
            json_line = None
            
            # Look for JSON in the output (starts with { or [)
            for line in reversed(output_lines):
                line = line.strip()
                if line.startswith('{') or line.startswith('['):
                    json_line = line
                    break
            
            if json_line:
                try:
                    return json.loads(json_line)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON output: {e}")
                    return {
                        "success": False,
                        "error": f"Failed to parse JSON output: {e}",
                        "raw_output": result.stdout,
                        "stderr": result.stderr
                    }
            else:
                return {
                    "success": False,
                    "error": "No JSON output found",
                    "raw_output": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out after {timeout} seconds")
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {e}"
            }
    
    # ===========================================
    # QR CODE GENERATION METHODS
    # ===========================================
    
    def generate_qr_code(self, text: str, output_file: str, 
                        width: int = 300, height: int = 300, 
                        format: str = "PNG") -> Dict:
        """
        Generate QR code from text
        
        Args:
            text: Text to encode in QR code
            output_file: Output file path
            width: Image width (default: 300)
            height: Image height (default: 300)
            format: Image format - PNG or JPG (default: PNG)
            
        Returns:
            Dictionary containing the result with success status
        """
        self.logger.info(f"Generating QR code: {text[:50]}...")
        
        command = [
            "generate", 
            text, 
            output_file, 
            str(width), 
            str(height), 
            format
        ]
        
        result = self._execute_command(command)
        
        if result.get("success"):
            self.logger.info(f"QR code generated successfully: {output_file}")
        else:
            self.logger.error(f"Failed to generate QR code: {result.get('error')}")
        
        return result
    
    def generate_qr_codes_batch(self, texts_and_files: List[Tuple[str, str]], 
                               width: int = 300, height: int = 300, 
                               format: str = "PNG") -> Dict:
        """
        Generate multiple QR codes in batch
        
        Args:
            texts_and_files: List of (text, output_file) tuples
            width: Image width (default: 300)
            height: Image height (default: 300)
            format: Image format - PNG or JPG (default: PNG)
            
        Returns:
            Dictionary with batch results
        """
        results = []
        successful = 0
        failed = 0
        
        for text, output_file in texts_and_files:
            result = self.generate_qr_code(text, output_file, width, height, format)
            results.append({
                "text": text,
                "output_file": output_file,
                "result": result
            })
            
            if result.get("success"):
                successful += 1
            else:
                failed += 1
        
        return {
            "success": failed == 0,
            "total": len(texts_and_files),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    # ===========================================
    # QR CODE/BARCODE DECODING METHODS
    # ===========================================
    
    def decode_image(self, image_file: str, mode: str = "all") -> Dict:
        """
        Decode QR code/barcode from image
        
        Args:
            image_file: Path to image file
            mode: Decoding mode - "all", "qr", "qr-zxing", "qr-boofcv", "barcode"
            
        Returns:
            Dictionary containing the decoded results
        """
        if not os.path.exists(image_file):
            self.logger.error(f"Image file not found: {image_file}")
            return {
                "success": False,
                "error": f"Image file not found: {image_file}"
            }
        
        self.logger.info(f"Decoding image: {image_file} (mode: {mode})")
        
        command = ["decode", image_file, mode]
        result = self._execute_command(command)
        
        if result.get("success"):
            detected_codes = result.get("detected_codes", {})
            total_codes = sum(len(codes) for codes in detected_codes.values() if isinstance(codes, list))
            self.logger.info(f"Successfully decoded {total_codes} codes from {image_file}")
        else:
            self.logger.error(f"Failed to decode image: {result.get('error')}")
        
        return result
    
    def decode_qr_code(self, image_file: str, engine: str = "zxing") -> Dict:
        """
        Decode QR code specifically using specified engine
        
        Args:
            image_file: Path to image file
            engine: QR decoding engine - "zxing" or "boofcv"
            
        Returns:
            Dictionary containing the decoded QR code
        """
        mode = f"qr-{engine}"
        return self.decode_image(image_file, mode)
    
    def decode_barcode(self, image_file: str) -> Dict:
        """
        Decode barcode from image
        
        Args:
            image_file: Path to image file
            
        Returns:
            Dictionary containing the decoded barcode
        """
        return self.decode_image(image_file, "barcode")
    
    def decode_images_batch(self, image_files: List[str], mode: str = "all") -> Dict:
        """
        Decode multiple images in batch
        
        Args:
            image_files: List of image file paths
            mode: Decoding mode for all images
            
        Returns:
            Dictionary with batch decode results
        """
        results = []
        successful = 0
        failed = 0
        total_codes = 0
        
        for image_file in image_files:
            result = self.decode_image(image_file, mode)
            results.append({
                "image_file": image_file,
                "result": result
            })
            
            if result.get("success"):
                successful += 1
                detected_codes = result.get("detected_codes", {})
                file_codes = sum(len(codes) for codes in detected_codes.values() if isinstance(codes, list))
                total_codes += file_codes
            else:
                failed += 1
        
        return {
            "success": failed == 0,
            "total_files": len(image_files),
            "successful_files": successful,
            "failed_files": failed,
            "total_codes_detected": total_codes,
            "results": results
        }
    
    # ===========================================
    # REGION-BASED DETECTION METHODS
    # ===========================================
    
    def decode_region(self, image_file: str, x: int, y: int, width: int, height: int, 
                     mode: str = "all") -> Dict:
        """
        Decode QR code/barcode from specific region
        
        Args:
            image_file: Path to image file
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of region
            height: Height of region
            mode: Decoding mode - "all", "qr", "qr-zxing", "qr-boofcv", "barcode"
            
        Returns:
            Dictionary containing the decode results from region
        """
        if not os.path.exists(image_file):
            self.logger.error(f"Image file not found: {image_file}")
            return {
                "success": False,
                "error": f"Image file not found: {image_file}"
            }
        
        self.logger.info(f"Decoding region [{x},{y},{width},{height}] from {image_file}")
        
        command = ["decode-region", image_file, str(x), str(y), str(width), str(height), mode]
        result = self._execute_command(command)
        
        if result.get("success"):
            detected_codes = result.get("detected_codes", {})
            total_codes = sum(len(codes) for codes in detected_codes.values() if isinstance(codes, list))
            self.logger.info(f"Successfully decoded {total_codes} codes from region")
        else:
            self.logger.error(f"Failed to decode region: {result.get('error')}")
        
        return result
    
    def decode_multiple_regions(self, image_file: str, regions: List[Tuple[int, int, int, int]], 
                               mode: str = "all") -> Dict:
        """
        Decode QR codes/barcodes from multiple regions
        
        Args:
            image_file: Path to image file
            regions: List of (x, y, width, height) tuples
            mode: Decoding mode
            
        Returns:
            Dictionary with results from all regions
        """
        results = []
        successful = 0
        failed = 0
        total_codes = 0
        
        for i, (x, y, width, height) in enumerate(regions):
            self.logger.info(f"Processing region {i+1}/{len(regions)}")
            result = self.decode_region(image_file, x, y, width, height, mode)
            
            results.append({
                "region": {"x": x, "y": y, "width": width, "height": height},
                "result": result
            })
            
            if result.get("success"):
                successful += 1
                detected_codes = result.get("detected_codes", {})
                region_codes = sum(len(codes) for codes in detected_codes.values() if isinstance(codes, list))
                total_codes += region_codes
            else:
                failed += 1
        
        return {
            "success": failed == 0,
            "total_regions": len(regions),
            "successful_regions": successful,
            "failed_regions": failed,
            "total_codes_detected": total_codes,
            "results": results
        }
    
    def create_grid_regions(self, image_width: int, image_height: int, 
                           grid_cols: int, grid_rows: int, 
                           overlap_percent: float = 0.1) -> List[Tuple[int, int, int, int]]:
        """
        Create grid regions for systematic scanning
        
        Args:
            image_width: Total image width
            image_height: Total image height
            grid_cols: Number of grid columns
            grid_rows: Number of grid rows
            overlap_percent: Overlap between regions (0.0 to 1.0)
            
        Returns:
            List of (x, y, width, height) tuples for each grid cell
        """
        regions = []
        
        cell_width = image_width // grid_cols
        cell_height = image_height // grid_rows
        
        overlap_x = int(cell_width * overlap_percent)
        overlap_y = int(cell_height * overlap_percent)
        
        for row in range(grid_rows):
            for col in range(grid_cols):
                x = max(0, col * cell_width - overlap_x)
                y = max(0, row * cell_height - overlap_y)
                
                width = min(cell_width + 2 * overlap_x, image_width - x)
                height = min(cell_height + 2 * overlap_y, image_height - y)
                
                regions.append((x, y, width, height))
        
        self.logger.info(f"Created {len(regions)} grid regions ({grid_cols}x{grid_rows})")
        return regions
    
    def decode_with_grid_scan(self, image_file: str, grid_cols: int = 3, grid_rows: int = 3,
                             mode: str = "all", overlap_percent: float = 0.1) -> Dict:
        """
        Decode using systematic grid scanning
        
        Args:
            image_file: Path to image file
            grid_cols: Number of grid columns
            grid_rows: Number of grid rows
            mode: Decoding mode
            overlap_percent: Overlap between grid cells
            
        Returns:
            Dictionary with grid scan results
        """
        try:
            from PIL import Image
            with Image.open(image_file) as img:
                image_width, image_height = img.size
        except Exception as e:
            return {
                "success": False,
                "error": f"Could not get image dimensions: {e}"
            }
        
        regions = self.create_grid_regions(image_width, image_height, grid_cols, grid_rows, overlap_percent)
        
        result = self.decode_multiple_regions(image_file, regions, mode)
        result["grid_info"] = {
            "image_size": {"width": image_width, "height": image_height},
            "grid_size": {"cols": grid_cols, "rows": grid_rows},
            "overlap_percent": overlap_percent,
            "total_regions": len(regions)
        }
        
        return result
    
    # ===========================================
    # UTILITY AND MANAGEMENT METHODS
    # ===========================================
    
    def get_service_info(self) -> Dict:
        """Get service information and status"""
        java_version = self._get_java_version(self.java_executable)
        
        return {
            "service": "QRCodeService",
            "version": "1.0.0",
            "jar_path": self.jar_path,
            "jar_exists": os.path.exists(self.jar_path),
            "java_executable": self.java_executable,
            "java_version": java_version,
            "supported_formats": ["PNG", "JPG"],
            "supported_modes": ["all", "qr", "qr-zxing", "qr-boofcv", "barcode"],
            "features": [
                "QR code generation",
                "Multi-engine decoding",
                "Region-based detection",
                "Batch processing",
                "Grid scanning",
                "Automatic Java detection"
            ]
        }
    
    def validate_image_file(self, image_file: str) -> bool:
        """Validate if image file exists and is readable"""
        if not os.path.exists(image_file):
            return False
        
        try:
            # Try to open with PIL if available
            from PIL import Image
            with Image.open(image_file) as img:
                img.verify()
            return True
        except ImportError:
            # Fallback to basic file check
            return os.path.isfile(image_file) and os.access(image_file, os.R_OK)
        except Exception:
            return False
    
    def set_log_level(self, level: str):
        """Set logging level (DEBUG, INFO, WARNING, ERROR)"""
        numeric_level = getattr(logging, level.upper(), None)
        if isinstance(numeric_level, int):
            self.logger.setLevel(numeric_level)
        else:
            raise ValueError(f"Invalid log level: {level}")


# Convenience factory function
def create_qr_service(jar_path: str = "vision.jar", 
                     auto_find_java: bool = True,
                     log_level: str = "INFO") -> QRCodeService:
    """
    Factory function to create QRCodeService instance
    
    Args:
        jar_path: Path to JAR file
        auto_find_java: Whether to auto-detect Java
        log_level: Logging level
        
    Returns:
        Configured QRCodeService instance
    """
    service = QRCodeService(jar_path=jar_path, auto_find_java=auto_find_java)
    service.set_log_level(log_level)
    return service


if __name__ == "__main__":
    # Example usage
    service = create_qr_service()
    
    print("=== QR Code Service Demo ===")
    print(json.dumps(service.get_service_info(), indent=2))
    
    # Generate a QR code
    result = service.generate_qr_code("Hello QR Service!", "test_service.png")
    print(f"\nGenerate result: {result.get('success')}")
    
    if result.get("success"):
        # Decode the generated QR code
        decode_result = service.decode_image("test_service.png")
        print(f"Decode result: {decode_result.get('success')}")
        
        if decode_result.get("success"):
            codes = decode_result.get("detected_codes", {})
            for engine, detected in codes.items():
                print(f"  {engine}: {detected}")
