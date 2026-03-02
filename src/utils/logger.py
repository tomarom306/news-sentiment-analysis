from loguru import logger
import sys
import os

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logger
logger.remove()  # Remove default handler

# Console output
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="INFO"
)

# File output
logger.add(
    "logs/news_sentiment_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # New file at midnight
    retention="7 days",  # Keep logs for 7 days
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
)

def get_logger(name):
    """Get a logger instance"""
    return logger.bind(name=name)