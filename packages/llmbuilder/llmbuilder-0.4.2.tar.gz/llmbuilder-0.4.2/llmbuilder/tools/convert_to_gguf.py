"""
GGUF conversion and quantization pipeline for LLMBuilder.

This module provides automated conversion of trained models to GGUF format
with support for various quantization levels and validation.
"""

import os
import logging
import subprocess
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import time

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of a GGUF conversion operation."""
    success: bool
    output_path: str
    quantization_level: str
    file_size_bytes: int = 0
    conversion_time_seconds: float = 0.0
    validation_passed: bool = False
    error_message: Optional[str] = None


@dataclass
class QuantizationConfig:
    """Configuration for model quantization parameters."""
    level: str = "Q8_0"  # Q8_0, Q4_0, Q4_1, Q5_0, Q5_1
    use_f16: bool = True
    use_f32: bool = False
    
    SUPPORTED_LEVELS = ["Q8_0", "Q4_0", "Q4_1", "Q5_0", "Q5_1", "F16", "F32"]
    
    def __post_init__(self):
        """Validate quantization configuration."""
        if self.level not in self.SUPPORTED_LEVELS:
            raise ValueError(f"Unsupported quantization level: {self.level}. "
                           f"Supported levels: {self.SUPPORTED_LEVELS}")


class ConversionValidator:
    """Validates GGUF conversion results and file integrity."""
    
    def validate_conversion(self, gguf_path: str) -> bool:
        """
        Validate that a GGUF file was created successfully.
        
        Args:
            gguf_path: Path to the GGUF file to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            path = Path(gguf_path)
            
            # Check file exists and has reasonable size
            if not path.exists():
                logger.error(f"GGUF file does not exist: {gguf_path}")
                return False
            
            file_size = path.stat().st_size
            if file_size < 1024:  # Less than 1KB is suspicious
                logger.error(f"GGUF file is too small ({file_size} bytes): {gguf_path}")
                return False
            
            # Check file extension
            if not gguf_path.lower().endswith('.gguf'):
                logger.warning(f"File does not have .gguf extension: {gguf_path}")
            
            # Basic file header validation (GGUF files start with specific magic bytes)
            with open(gguf_path, 'rb') as f:
                header = f.read(4)
                if header != b'GGUF':
                    logger.error(f"Invalid GGUF file header: {gguf_path}")
                    return False
            
            logger.info(f"GGUF validation passed: {gguf_path} ({file_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"GGUF validation failed for {gguf_path}: {e}")
            return False
    
    def get_file_info(self, gguf_path: str) -> Dict[str, Any]:
        """
        Get information about a GGUF file.
        
        Args:
            gguf_path: Path to the GGUF file
            
        Returns:
            Dictionary with file information
        """
        try:
            path = Path(gguf_path)
            if not path.exists():
                return {"error": "File does not exist"}
            
            stat = path.stat()
            return {
                "file_size_bytes": stat.st_size,
                "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "is_valid_gguf": self.validate_conversion(gguf_path)
            }
            
        except Exception as e:
            return {"error": str(e)}


class GGUFConverter:
    """
    Main orchestrator for GGUF model conversion and quantization.
    
    This class handles the conversion of trained models to GGUF format
    with support for multiple quantization levels and validation.
    """
    
    def __init__(self):
        """Initialize the GGUF converter."""
        self.validator = ConversionValidator()
        self.conversion_scripts = self._detect_conversion_scripts()
    
    def _detect_conversion_scripts(self) -> Dict[str, Optional[str]]:
        """
        Detect available conversion scripts on the system.
        
        Returns:
            Dictionary mapping script types to their paths
        """
        scripts = {
            "llama_cpp": None,
            "convert_hf_to_gguf": None
        }
        
        # Look for llama.cpp conversion script
        llama_cpp_paths = [
            "llama.cpp/convert.py",
            "convert.py",
            shutil.which("convert.py")
        ]
        
        for path in llama_cpp_paths:
            if path and Path(path).exists():
                scripts["llama_cpp"] = path
                break
        
        # Look for Hugging Face conversion script
        hf_convert_paths = [
            "convert_hf_to_gguf.py",
            shutil.which("convert_hf_to_gguf.py")
        ]
        
        for path in hf_convert_paths:
            if path and Path(path).exists():
                scripts["convert_hf_to_gguf"] = path
                break
        
        logger.info(f"Detected conversion scripts: {scripts}")
        return scripts
    
    def get_quantization_options(self) -> List[str]:
        """
        Get available quantization options.
        
        Returns:
            List of supported quantization levels
        """
        return QuantizationConfig.SUPPORTED_LEVELS.copy()
    
    def convert_model(self, model_path: str, output_path: str, 
                     quantization: str = "Q8_0") -> ConversionResult:
        """
        Convert a model to GGUF format with specified quantization.
        
        Args:
            model_path: Path to the input model directory
            output_path: Path for the output GGUF file
            quantization: Quantization level (e.g., "Q8_0", "Q4_0")
            
        Returns:
            ConversionResult with conversion details
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not Path(model_path).exists():
                return ConversionResult(
                    success=False,
                    output_path=output_path,
                    quantization_level=quantization,
                    error_message=f"Model path does not exist: {model_path}"
                )
            
            # Create quantization config
            quant_config = QuantizationConfig(level=quantization)
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Attempt conversion with available scripts
            conversion_success = False
            error_messages = []
            
            # Try llama.cpp conversion first
            if self.conversion_scripts["llama_cpp"]:
                try:
                    conversion_success = self._convert_with_llama_cpp(
                        model_path, output_path, quant_config
                    )
                except Exception as e:
                    error_messages.append(f"llama.cpp conversion failed: {e}")
            
            # Fallback to convert_hf_to_gguf.py
            if not conversion_success and self.conversion_scripts["convert_hf_to_gguf"]:
                try:
                    conversion_success = self._convert_with_hf_script(
                        model_path, output_path, quant_config
                    )
                except Exception as e:
                    error_messages.append(f"HF conversion failed: {e}")
            
            if not conversion_success:
                return ConversionResult(
                    success=False,
                    output_path=output_path,
                    quantization_level=quantization,
                    error_message="; ".join(error_messages) if error_messages else "No conversion scripts available"
                )
            
            # Validate the conversion
            validation_passed = self.validator.validate_conversion(output_path)
            
            # Get file size
            file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0
            
            return ConversionResult(
                success=True,
                output_path=output_path,
                quantization_level=quantization,
                file_size_bytes=file_size,
                conversion_time_seconds=time.time() - start_time,
                validation_passed=validation_passed
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                output_path=output_path,
                quantization_level=quantization,
                conversion_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    def _convert_with_llama_cpp(self, model_path: str, output_path: str, 
                               config: QuantizationConfig) -> bool:
        """
        Convert model using llama.cpp conversion script.
        
        Args:
            model_path: Input model path
            output_path: Output GGUF path
            config: Quantization configuration
            
        Returns:
            True if conversion succeeded, False otherwise
        """
        script_path = self.conversion_scripts["llama_cpp"]
        if not script_path:
            raise RuntimeError("llama.cpp conversion script not available")
        
        cmd = [
            "python", script_path,
            model_path,
            "--outfile", output_path,
            "--outtype", config.level
        ]
        
        logger.info(f"Running llama.cpp conversion: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode != 0:
            logger.error(f"llama.cpp conversion failed: {result.stderr}")
            raise RuntimeError(f"Conversion failed with return code {result.returncode}")
        
        return True
    
    def _convert_with_hf_script(self, model_path: str, output_path: str,
                               config: QuantizationConfig) -> bool:
        """
        Convert model using convert_hf_to_gguf.py script.
        
        Args:
            model_path: Input model path
            output_path: Output GGUF path
            config: Quantization configuration
            
        Returns:
            True if conversion succeeded, False otherwise
        """
        script_path = self.conversion_scripts["convert_hf_to_gguf"]
        if not script_path:
            raise RuntimeError("convert_hf_to_gguf.py script not available")
        
        cmd = [
            "python", script_path,
            model_path,
            "--outfile", output_path
        ]
        
        # Add quantization parameters
        if config.level != "F32":
            cmd.extend(["--outtype", config.level])
        
        logger.info(f"Running HF conversion: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode != 0:
            logger.error(f"HF conversion failed: {result.stderr}")
            raise RuntimeError(f"Conversion failed with return code {result.returncode}")
        
        return True
    
    def batch_convert(self, models: List[Dict[str, str]], 
                     quantization_levels: List[str] = None) -> List[ConversionResult]:
        """
        Convert multiple models with different quantization levels.
        
        Args:
            models: List of dicts with 'input_path' and 'output_path' keys
            quantization_levels: List of quantization levels to apply
            
        Returns:
            List of ConversionResult objects
        """
        if quantization_levels is None:
            quantization_levels = ["Q8_0"]
        
        results = []
        
        for model_info in models:
            for quant_level in quantization_levels:
                # Generate output path with quantization suffix
                base_output = Path(model_info["output_path"])
                output_path = base_output.parent / f"{base_output.stem}_{quant_level}.gguf"
                
                result = self.convert_model(
                    model_info["input_path"],
                    str(output_path),
                    quant_level
                )
                results.append(result)
        
        return results