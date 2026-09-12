# app/logging/setup.py
import logging
from pythonjsonlogger import jsonlogger
import sys

def setup_logging():
    logger = logging.getLogger("security_gateway")
    
    # JSON formatter for ELK stack
    json_handler = logging.StreamHandler(sys.stdout)
    json_formatter = jsonlogger.JsonFormatter()
    json_handler.setFormatter(json_formatter)
    
    logger.addHandler(json_handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logging()