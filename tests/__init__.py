import logging
import os

LOGGER_NAME = "tests"

log = logging.getLogger(LOGGER_NAME)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())