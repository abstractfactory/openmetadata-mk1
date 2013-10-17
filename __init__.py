import constant, reference
from transaction import write, read, update, delete
from lib import Folder, Channel, File, Factory

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
