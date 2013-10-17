"""Convenience module for the end-user

The goal of this module is to provide as high-level utilities
as possible for users who wish to have as little knowledge as
possible about Open Metadata.

Target audience leans towards Technical Directors or
fellow scripters in any DCC.

"""

from __future__ import absolute_import

import os
import logging
import shutil

from openmetadata import lib


log = logging.getLogger('openmetadata.transaction')


def write(root, data):
    """Convenience method for writing metadata"""
    raise NotImplementedError


def update(root, data):
    """Convenience method for updating metadata"""
    raise NotImplementedError


def read(root, hierarchy={}):
    """Convenience method for reading metadata"""
    raise NotImplementedError


def delete(root, max_retries=10):
    assert os.path.exists(root)

    retries = 0
    while True:
        try:
            if os.path.isdir(root):
                shutil.rmtree(root)
            else:
                os.remove(root)
            break
        except WindowsError as e:
            # Sometimes, Dropbox can bother this operation;
            # creating files in the midst of deleting a folder.
            #
            # If this happens, try again in a short while.
            
            retries += 1
            if retries > max_retries:
                log.error(e)
                break

            import time
            time.sleep(0.1)
            log.debug("Retired %i time(s) for %s" % (retries, root))


    log.debug("Removed %s" % root)


if __name__ == '__main__':
    import openmetadata as om

    package = os.getcwd()
    root = os.path.join(package, 'test', 'persist')

    print "Reading: %s " % root
    print om.read(root)
