"""
Logger configuration for SPIKE AI Backend.
Provides structured logging for debugging and monitoring.
"""

import logging
import sys
from datetime import datetime


def setup_logger(name: str = "spike_ai", level: str = "INFO") -> logging.Logger:
    """
    Set up structured logger for the application.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_logger()


def log_request(endpoint: str, params: dict):
    """Log incoming API requests"""
    logger.info(f"Request to {endpoint}: {params}")


def log_agent_call(agent_name: str, query: str, success: bool = True):
    """Log agent execution"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Agent {agent_name} - {status}: {query}")


def log_validation_error(error_type: str, details: str):
    """Log validation errors"""
    logger.warning(f"Validation error ({error_type}): {details}")


def log_llm_call(model: str, tokens_used: int = None):
    """Log LLM API calls"""
    if tokens_used:
        logger.info(f"LLM call to {model} - Tokens: {tokens_used}")
    else:
        logger.info(f"LLM call to {model}")


def log_ga4_query(property_id: str, metrics: list, dimensions: list):
    """Log GA4 API queries"""
    logger.info(f"GA4 query - Property: {property_id}, Metrics: {metrics}, Dimensions: {dimensions}")


def log_error(error: Exception, context: str = ""):
    """Log errors with context"""
    logger.error(f"Error in {context}: {type(error).__name__}: {str(error)}")


def log_performance(operation: str, duration_ms: float):
    """Log performance metrics"""
    logger.info(f"Performance - {operation}: {duration_ms:.2f}ms")