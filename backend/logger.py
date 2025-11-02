"""
Logging configuration for Meeting Summarizer.
Sets up both console and rotating file handlers.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import config


def setup_logging(name: str = None) -> logging.Logger:
    """
    Configure logging with console and optional file output.
    
    Args:
        name: Logger name (defaults to root logger if None)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if already configured
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
    console_formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional, for production)
    if config.ENABLE_FILE_LOGGING:
        try:
            # Create logs directory if it doesn't exist
            config.LOG_DIR.mkdir(parents=True, exist_ok=True)
            
            log_file_path = config.LOG_DIR / config.LOG_FILE
            
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=config.LOG_MAX_BYTES,
                backupCount=config.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
            file_formatter = logging.Formatter(config.LOG_FORMAT)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            logger.info(f"File logging enabled: {log_file_path}")
        except Exception as e:
            logger.warning(f"Failed to setup file logging: {e}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger
