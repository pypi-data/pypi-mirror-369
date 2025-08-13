"""Main file conversion service using MarkItDown."""

import os
import signal
import sys
import warnings
from contextlib import contextmanager
from pathlib import Path

# Windows compatibility fix: Monkey patch signal module for MarkItDown
if sys.platform == "win32" and not hasattr(signal, "SIGALRM"):
    # MarkItDown tries to use SIGALRM on Windows, so we provide a dummy
    signal.SIGALRM = 14  # Standard SIGALRM signal number on Unix
    signal.alarm = lambda _: None  # No-op function for Windows

from qdrant_loader.core.file_conversion.conversion_config import FileConversionConfig
from qdrant_loader.core.file_conversion.exceptions import (
    ConversionTimeoutError,
    FileAccessError,
    FileSizeExceededError,
    MarkItDownError,
    UnsupportedFileTypeError,
)
from qdrant_loader.core.file_conversion.file_detector import FileDetector
from qdrant_loader.utils.logging import LoggingConfig

logger = LoggingConfig.get_logger(__name__)


@contextmanager
def capture_openpyxl_warnings(logger_instance, file_path: str):
    """Context manager to capture openpyxl warnings and route them through our logging system."""
    captured_warnings = []

    # Custom warning handler
    def warning_handler(message, category, filename, lineno, file=None, line=None):
        # Check if this is an openpyxl warning we want to capture
        if (
            category == UserWarning
            and filename
            and "openpyxl" in filename
            and (
                "Data Validation extension" in str(message)
                or "Conditional Formatting extension" in str(message)
            )
        ):

            # Extract the specific warning type
            warning_type = "Unknown Excel feature"
            if "Data Validation extension" in str(message):
                warning_type = "Data Validation"
            elif "Conditional Formatting extension" in str(message):
                warning_type = "Conditional Formatting"

            # Track captured warning
            captured_warnings.append(warning_type)

            # Log through our system instead of showing the raw warning
            logger_instance.info(
                "Excel feature not fully supported during conversion",
                file_path=file_path,
                feature_type=warning_type,
                source="openpyxl",
            )
        else:
            # For non-openpyxl warnings, use the default behavior
            original_showwarning(message, category, filename, lineno, file, line)

    # Store original warning handler
    original_showwarning = warnings.showwarning

    try:
        # Install our custom warning handler
        warnings.showwarning = warning_handler
        yield

        # Log summary if any warnings were captured
        if captured_warnings:
            logger_instance.info(
                "Excel conversion completed with unsupported features",
                file_path=file_path,
                total_warnings=len(captured_warnings),
                warning_types=list(set(captured_warnings)),
                source="openpyxl",
            )
    finally:
        # Restore original warning handler
        warnings.showwarning = original_showwarning


class TimeoutHandler:
    """Context manager for handling conversion timeouts."""

    def __init__(self, timeout_seconds: int, file_path: str):
        self.timeout_seconds = timeout_seconds
        self.file_path = file_path
        self.old_handler = None
        self.timer = None

    def _timeout_handler(self, _signum=None, _frame=None):
        """Signal handler for timeout."""
        raise ConversionTimeoutError(self.timeout_seconds, self.file_path)

    def _timeout_thread(self):
        """Thread-based timeout for Windows."""
        import time

        time.sleep(self.timeout_seconds)
        self._timeout_handler()

    def __enter__(self):
        """Set up timeout handler (Unix signals or Windows threading)."""
        if sys.platform == "win32":
            # Windows doesn't support SIGALRM, use threading instead
            import threading

            self.timer = threading.Thread(target=self._timeout_thread, daemon=True)
            self.timer.start()
        else:
            # Unix/Linux/macOS: use signal-based timeout
            if hasattr(signal, "SIGALRM"):
                self.old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(self.timeout_seconds)
        return self

    def __exit__(self, exc_type, exc_val, _exc_tb):
        """Clean up timeout handler."""
        if sys.platform == "win32":
            # On Windows, we can't easily cancel the thread, but since it's daemon,
            # it will be cleaned up when the process exits
            # The timeout will simply not trigger if conversion completes first
            pass
        else:
            # Unix/Linux/macOS: clean up signal handler
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)  # Cancel the alarm
                if self.old_handler is not None:
                    signal.signal(signal.SIGALRM, self.old_handler)


class FileConverter:
    """Service for converting files to Markdown using MarkItDown."""

    def __init__(self, config: FileConversionConfig):
        """Initialize the file converter."""
        self.config = config
        self.file_detector = FileDetector()
        self.logger = LoggingConfig.get_logger(__name__)
        self._markitdown = None

    def _get_markitdown(self):
        """Get MarkItDown instance with lazy loading and LLM configuration."""
        if self._markitdown is None:
            try:
                from markitdown import MarkItDown  # type: ignore

                # Configure MarkItDown with LLM settings if enabled
                if self.config.markitdown.enable_llm_descriptions:
                    self.logger.debug(
                        "Initializing MarkItDown with LLM configuration",
                        llm_model=self.config.markitdown.llm_model,
                        llm_endpoint=self.config.markitdown.llm_endpoint,
                    )

                    # Create LLM client based on endpoint
                    llm_client = self._create_llm_client()

                    self._markitdown = MarkItDown(
                        llm_client=llm_client,
                        llm_model=self.config.markitdown.llm_model,
                    )
                    self.logger.debug("MarkItDown initialized with LLM support")
                else:
                    self._markitdown = MarkItDown()
                    self.logger.debug("MarkItDown initialized without LLM support")

            except ImportError as e:
                raise MarkItDownError(
                    Exception("MarkItDown library not available")
                ) from e
        return self._markitdown

    def _create_llm_client(self):
        """Create LLM client based on configuration."""
        try:
            # Get API key from configuration
            api_key = self.config.markitdown.llm_api_key
            if not api_key:
                self.logger.warning(
                    "No LLM API key configured for MarkItDown LLM integration"
                )
                # Fallback to environment variable for backward compatibility
                api_key = os.getenv("OPENAI_API_KEY") or os.getenv(
                    "LLM_API_KEY", "dummy-key"
                )

            # Check if it's an OpenAI-compatible endpoint
            if "openai" in self.config.markitdown.llm_endpoint.lower():
                from openai import OpenAI  # type: ignore

                return OpenAI(
                    base_url=self.config.markitdown.llm_endpoint,
                    api_key=api_key,
                )
            else:
                # For other endpoints, try to create a generic OpenAI-compatible client
                from openai import OpenAI  # type: ignore

                return OpenAI(
                    base_url=self.config.markitdown.llm_endpoint,
                    api_key=api_key,
                )
        except ImportError as e:
            self.logger.warning(
                "OpenAI library not available for LLM integration", error=str(e)
            )
            raise MarkItDownError(
                Exception("OpenAI library required for LLM integration")
            ) from e

    def convert_file(self, file_path: str) -> str:
        """Convert a file to Markdown format with timeout support."""
        # Normalize path for consistent logging (Windows compatibility)
        normalized_path = file_path.replace("\\", "/")
        self.logger.info("Starting file conversion", file_path=normalized_path)

        try:
            self._validate_file(file_path)
            markitdown = self._get_markitdown()

            # Apply timeout wrapper and warning capture for conversion
            with TimeoutHandler(self.config.conversion_timeout, file_path):
                with capture_openpyxl_warnings(self.logger, file_path):
                    result = markitdown.convert(file_path)

            if hasattr(result, "text_content"):
                markdown_content = result.text_content
            else:
                markdown_content = str(result)

            self.logger.info(
                "File conversion completed",
                file_path=normalized_path,
                content_length=len(markdown_content),
                timeout_used=self.config.conversion_timeout,
            )
            return markdown_content

        except ConversionTimeoutError:
            # Re-raise timeout errors as-is
            self.logger.error(
                "File conversion timed out",
                file_path=normalized_path,
                timeout=self.config.conversion_timeout,
            )
            raise
        except Exception as e:
            self.logger.error(
                "File conversion failed", file_path=normalized_path, error=str(e)
            )
            raise MarkItDownError(e, file_path) from e

    def _validate_file(self, file_path: str) -> None:
        """Validate file for conversion."""
        if not os.path.exists(file_path):
            raise FileAccessError(f"File does not exist: {file_path}")

        if not os.access(file_path, os.R_OK):
            raise FileAccessError(f"File is not readable: {file_path}")

        file_size = os.path.getsize(file_path)
        if not self.config.is_file_size_allowed(file_size):
            raise FileSizeExceededError(file_size, self.config.max_file_size, file_path)

        if not self.file_detector.is_supported_for_conversion(file_path):
            file_info = self.file_detector.get_file_type_info(file_path)
            raise UnsupportedFileTypeError(
                file_info.get("normalized_type", "unknown"), file_path
            )

    def create_fallback_document(self, file_path: str, error: Exception) -> str:
        """Create a fallback Markdown document when conversion fails."""
        filename = Path(file_path).name
        file_info = self.file_detector.get_file_type_info(file_path)

        return f"""# {filename}

**File Information:**
- **Type**: {file_info.get("normalized_type", "unknown")}
- **Size**: {file_info.get("file_size", 0):,} bytes
- **Path**: {file_path}

**Conversion Status**: ❌ Failed
**Error**: {str(error)}

*This document was created as a fallback when the original file could not be converted.*
"""
