#!/usr/bin/env python3
"""
Logging Management Module
Provides unified logging functionality
"""

import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """Logging Management Class"""
    
    def __init__(self, name: str = "IntelligentSearch", level: int = logging.INFO):
        """Initialize logger"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup log handlers"""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        
        # File handler
        file_handler = logging.FileHandler(
            f'logs/search_system_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical error message"""
        self.logger.critical(message)
    
    def search_start(self, query: str):
        """Log search start"""
        self.info(f"🔍 Starting search: '{query}'")
    
    def search_complete(self, query: str, count: int, duration: float):
        """Log search completion"""
        self.info(f"✅ Search completed: '{query}' - Found {count} products, took {duration:.2f} seconds")
    
    def browser_search_start(self, query: str):
        """Log browser search start"""
        self.info(f"🌐 Browser-use search started: '{query}'")
    
    def browser_search_complete(self, query: str, count: int, duration: float):
        """Log browser search completion"""
        self.info(f"✅ Browser-use search completed: '{query}' - Found {count} products, took {duration:.2f} seconds")
    
    def local_search_start(self, query: str):
        """Log local search start"""
        self.info(f"💾 Local search started: '{query}'")
    
    def local_search_complete(self, query: str, count: int, duration: float):
        """Log local search completion"""
        self.info(f"✅ Local search completed: '{query}' - Found {count} products, took {duration:.2f} seconds")
    
    def recommendation_start(self, query: str):
        """Log recommendation generation start"""
        self.info(f"🤖 Starting recommendation generation: '{query}'")
    
    def recommendation_complete(self, query: str, duration: float):
        """Log recommendation generation completion"""
        self.info(f"✅ Recommendation generation completed: '{query}', took {duration:.2f} seconds")

# Global logger instance
logger = Logger() 