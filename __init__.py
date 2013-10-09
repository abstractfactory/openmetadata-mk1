from template import Folder, Channel, File
from transaction import write, read, update, delete
import constant, instance, format, reference

import logging
import sys

# Initiate logging for main level
log = logging.getLogger('openmetadata')
log.setLevel(logging.INFO)
# log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)
