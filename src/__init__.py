import logging
import os

LOGGER_NAME = "sillybaka"

# TODO: The path for the temp folder shouldn't be hardcoded. For now changing the location of helper_stuff.py file needs
#  special attention to change the location of the root folder
TEMP_PATH = os.path.join("..", "temp")
# For topic filtering
KEY_WORDS = []

log = logging.getLogger(LOGGER_NAME)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())