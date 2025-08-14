#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Centralized logging utility for PrecisionDoc.
Provides a common logging configuration and functions for all modules.
"""

import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Base project directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Create logs directory structure
def _setup_log_dirs():
    """Create logs directory structure with date-based folders"""
    today = datetime.now().strftime('%Y-%m-%d')
    logs_dir = PROJECT_ROOT / 'logs'
    daily_logs_dir = logs_dir / today
    
    # Create directories if they don't exist
    logs_dir.mkdir(exist_ok=True)
    daily_logs_dir.mkdir(exist_ok=True)
    
    return daily_logs_dir

# Configure logging singleton
_configured = False
_loggers = {}

def get_logger(name=None, level=None):
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name, typically __name__ of the calling module
        level: Optional logging level override (default: from LOG_LEVEL env var or INFO)
    
    Returns:
        Configured logger instance
    """
    global _configured, _loggers
    
    # Use the provided name or default to root logger
    logger_name = name if name else ''
    
    # Return existing logger if already configured
    if logger_name in _loggers:
        return _loggers[logger_name]
    
    # Configure root logger if not already done
    if not _configured:
        _configure_logging(level)
        _configured = True
    
    # Get logger for the specified name
    logger = logging.getLogger(logger_name)
    _loggers[logger_name] = logger
    
    return logger

def _configure_logging(level=None):
    """
    Configure the root logger with console and file handlers.
    
    Args:
        level: Optional logging level override
    """
    # Determine log level from environment or default to INFO
    log_level = level if level else os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory
    daily_logs_dir = _setup_log_dirs()
    log_file = daily_logs_dir / 'precisiondoc.log'
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates on reconfiguration
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(numeric_level)
    root_logger.addHandler(console_handler)
    
    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(numeric_level)
    root_logger.addHandler(file_handler)

# Convenience function for modules to get their logger
def setup_logger(module_name=None):
    """
    Convenience function to set up a logger for a module.
    
    Args:
        module_name: Module name, typically __name__
        
    Returns:
        Configured logger instance
    """
    return get_logger(module_name)
