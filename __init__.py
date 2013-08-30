

from template import MetadataTemplate, ChannelTemplate, DataTemplate
from transaction import create, read, update, delete

import constant
import logging

# Initiate logging for main level
log = logging.getLogger('openmetadata')
log.setLevel(logging.INFO)
# log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)
