import logging

def set_log_level(log_level=logging.INFO):
    """Set the log level for the k_lights_interface package.

    Args:
        log_level (optional): set the log level to one of: CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET. Defaults to logging.INFO.
    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )
