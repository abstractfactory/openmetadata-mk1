"""
Input/Output module for Open Metadata

    Created: 2013-09-01
    Author: Marcus Ottosson
    Email: marcus@pipi.io

Usage:

    >>> test()

"""


import os
import logging
import shutil

from interface import AbstractTemplate
import template

log = logging.getLogger('openmetadata.transaction')


def write(root):
    """Recursively create all metadata under `root`"""

    assert isinstance(root, AbstractTemplate)
    assert root.parent is not None
    assert os.path.exists( str(root.parent) )

    if root.exists:
        log.warning('"%s" already exists' % root)
        return

    if isinstance(root, template.Data):
        data = root.get()

        if isinstance(data, template.Hardlink):
            src = data.path
            dst = root.path

            try:
                _hardlink(src, dst)
            except (AttributeError, OSError) as e:
                raise OSError("Could not create hardlink %s\n%s" % (src, e))

            log.debug("Linked '%s' to '%s'" % (src, dst))

        elif isinstance(data, template.Softlink):
            src = data.path
            dst = root.path

            try:
                _softlink(src, dst)
            except (AttributeError, OSError) as e:
                raise OSError("Could not create softlink %s\n%s" % (src, e))

            log.debug("Linked '%s' to '%s'" % (src, dst))

        elif isinstance(data, template.Junction):
            src = data.path
            dst = root.path

            try:
                _junction(src, dst)
            except (AttributeError, OSError) as e:
                raise OSError("Could not create junction %s\n%s" % (src, e))

            log.debug("Linked '%s' to '%s'" % (src, dst))


        elif isinstance(data, template.Copy):
            src = data.path
            dst = root.path

            try:
                shutil.copy(src, dst)
            except OSError as e:
                raise e

            log.debug("Copied '%s' to '%s'" % (src, dst))


        else:
            with open(root.path, 'w') as f:
                f.write(data)

            log.debug("Wrote %s" % root)
    else:
        os.mkdir(root.path)

        log.debug("Created %s" % root)

        # Recursively create children
        for child in root.children:
            write(child)
        

def read(root):
    """Return metadata hierarchy as dict"""
    metadata_root = os.path.join(root, '.meta')
    if not os.path.exists(metadata_root):
        log.error("No metadata found under %s" % metadata_root)
        return {}

    return _hierarchy_as_dict(metadata_root)



def update(root):
    print "Updating %r" % root


def delete(root, max_retries=10):
    assert os.path.exists(root)
    assert os.path.isdir(root)

    retries = 0
    while True:
        try:
            shutil.rmtree(root)
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


def _hierarchy_as_dict(root):
    """Return a dict of folders and files under `root`"""
    hier = {}
    root = root.rstrip(os.sep)
    start = root.rfind(os.sep) + 1
    for path, dirs, files in os.walk(root):
        folders = path[start:].split(os.sep)
        subdir = files or {}  # Files are entered as lists
        parent = reduce(dict.get, folders[:-1], hier)
        parent[folders[-1]] = subdir
    return hier

# ------------------------------------


def _hardlink(src, dst):
    import ctypes
    if not ctypes.windll.kernel32.CreateHardLinkA(dst, src, 0): 
        raise OSError("Could not hardlink '%s' to '%s'" % (src, dst))


def _softlink(src, dst):
    return


def _junction(src, dst):
    return


if __name__ == '__main__':
    # import sys
    import openmetadata as om

    package = os.getcwd()
    root = os.path.join(package, 'test')

    print om.read(root)
