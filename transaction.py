"""
Input/Output module for Open Folder

    Created: 2013-09-01
    Author: Marcus Ottosson
    Email: marcus@pipi.io

Usage:

    >>> test()

"""

from __future__ import absolute_import

import os
import logging
import shutil

from openmetadata import instance
from openmetadata import template


log = logging.getLogger('openmetadata.transaction')


def write(root, data):
    """Convenience method for writing metadata"""

    if isinstance(data, basestring):
        # String are written as plain-text
        meta = template.Folder(root)

        # New channel
        chan = template.Channel('untitled.txt', meta)
        file = template.File('untitled.txt', chan)
        file.setdata(data)

        return file.write()

    if isinstance(data, dict):
        meta = template.Folder(root)

        # New channel
        chan = template.Channel('untitled.kvs', meta)
        file = template.File('untitled.json', chan)
        file.setdata(data)

        return file.write()

    raise ValueError('Failed to write "%r" to "%s"' % (data, root))


def update(root, data):
    """Convenience method for updating metadata"""


def read(root, hierarchy={}):
    """Convenience method for reading metadata"""

    obj = instance.create(root)
    if not obj.exists():
        return {}

    for child in obj.children:
        hierarchy[child.basename] = {}
        read(child, hierarchy[child.basename])

    return hierarchy


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


# def _hardlink(src, dst):
#     if not ctypes.windll.kernel32.CreateHardLinkA(dst, src, 0): 
#         raise OSError("Could not hardlink '%s' to '%s'" % (src, dst))


# def _softlink(src, dst):
#     return


# def _junction(src, dst):
#     return



if __name__ == '__main__':
    import openmetadata as om

    package = os.getcwd()
    root = os.path.join(package, 'test', 'persist')

    print "Reading: %s " % root
    print om.read(root)
