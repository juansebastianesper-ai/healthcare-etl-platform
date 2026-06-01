import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    log_dir = Path(__file__).resolve().parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    handlers = [
        RotatingFileHandler(
            log_dir / 'healthcare.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        ),
        RotatingFileHandler(
            log_dir / 'errors.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8',
        ),
        logging.StreamHandler(),
    ]

    for handler in handlers:
        handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in handlers:
        root_logger.addHandler(handler)

    error_handler = logging.FileHandler(log_dir / 'errors.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    return root_logger


logger = logging.getLogger('healthcare')
