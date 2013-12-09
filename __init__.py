import constant
from transaction import write, read, update, delete, cascade
from domain import Folder, Channel, Key, Factory
from openmetadata import __version__

import logging
import sys

# Initiate logging for main level
log = logging.getLogger('openmetadata')
log.setLevel(logging.WARNING)
# log.setLevel(logging.INFO)
# log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)

# Used in distutils
# Name = 'Open Metadata'