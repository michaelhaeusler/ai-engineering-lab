# rag_logging_config.py
"""
RAG Logging Configuration
Easy-to-use logging setup for RAG applications
"""

import logging
import sys
import os
from datetime import datetime


class RAGLoggingConfig:
    """RAG Logging Configuration - Edit these settings to customize logging"""

    # Enable/disable logging (can be overridden by environment variable)
    ENABLED = os.getenv("RAG_LOGGING_ENABLED", "true").lower() == "true"

    # Output destination: 'file', 'console', or 'both'
    OUTPUT = os.getenv("RAG_LOG_OUTPUT", "file")

    # Logging level
    LEVEL = getattr(logging, os.getenv("RAG_LOG_LEVEL", "INFO").upper())

    # Log message format
    FORMAT = os.getenv(
        "RAG_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File logging settings
    FILENAME_PREFIX = os.getenv("RAG_LOG_FILENAME_PREFIX", "rag_log")
    FILENAME_TIMESTAMP = (
        os.getenv("RAG_LOG_FILENAME_TIMESTAMP", "true").lower() == "true"
    )


def setup_rag_logging(config=None):
    """
    Setup RAG logging based on configuration

    Args:
        config: RAGLoggingConfig instance or None to use default config
    """
    if config is None:
        config = RAGLoggingConfig()

    if config.ENABLED:
        # Clear existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Create formatter
        formatter = logging.Formatter(config.FORMAT)

        # Configure root logger
        logging.root.setLevel(config.LEVEL)

        # Add handlers based on OUTPUT setting
        if config.OUTPUT in ["file", "both"]:
            if config.FILENAME_TIMESTAMP:
                log_filename = f"{config.FILENAME_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            else:
                log_filename = f"{config.FILENAME_PREFIX}.log"

            file_handler = logging.FileHandler(log_filename)
            file_handler.setFormatter(formatter)
            logging.root.addHandler(file_handler)
            print(f"✅ File logging enabled - writing to {log_filename}")

        if config.OUTPUT in ["console", "both"]:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logging.root.addHandler(console_handler)
            print("✅ Console logging enabled")

        if config.OUTPUT not in ["file", "console", "both"]:
            print("⚠️ Invalid OUTPUT setting - logging disabled")
            logging.disable(logging.CRITICAL)
    else:
        logging.disable(logging.CRITICAL)
        print("❌ RAG logging disabled")


def quick_setup(output="console", level=logging.INFO, enabled=True):
    """
    Quick setup function for common configurations

    Args:
        output: 'file', 'console', or 'both'
        level: logging level
        enabled: whether to enable logging
    """
    config = RAGLoggingConfig()
    config.OUTPUT = output
    config.LEVEL = level
    config.ENABLED = enabled
    setup_rag_logging(config)


def get_logger(name):
    """
    Get a logger instance with the configured settings

    Args:
        name: Logger name (usually __name__)
    """
    return logging.getLogger(name)


# Example usage
if __name__ == "__main__":
    # Example: Setup logging for development
    quick_setup(output="console", level=logging.INFO)

    # Test logging
    logger = get_logger("test")
    logger.info("RAG logging is working!")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
