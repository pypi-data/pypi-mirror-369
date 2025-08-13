import logging


def get_logger(logger_name: str, log_level: str | int = "INFO") -> logging.Logger:
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(logger_name)
