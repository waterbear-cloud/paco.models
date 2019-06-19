import logging

def get_logger():
    log = logging.getLogger("aim.models")
    log.setLevel(logging.DEBUG)
    return log