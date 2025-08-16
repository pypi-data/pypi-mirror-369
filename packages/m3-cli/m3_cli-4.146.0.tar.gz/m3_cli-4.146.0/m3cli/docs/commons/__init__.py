import logging
import logging.handlers

# Singleton pattern implementation
_logger_instance = None


def create_logger(level=logging.DEBUG) -> logging.Logger:
    global _logger_instance
    if _logger_instance is not None:
        return _logger_instance

    logger = logging.getLogger('root')
    # Create handlers
    stream_handler = logging.StreamHandler()
    file_handler = logging.handlers.RotatingFileHandler(
        'generate_docs.log',
        maxBytes=1048576,  # 1 MB
        backupCount=30,
    )
    # Create formatter and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    # Set logger level
    logger.setLevel(level)

    _logger_instance = logger
    return logger
