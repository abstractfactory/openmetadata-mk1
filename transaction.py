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


def read(root):
    """Convenience method for reading metadata

    Returns dict() 
    {'channelname without extension': content}

    Pre-conditions
        - Parent channel name must not exist twice, not
        regarding its extension.

        E.g.
            Legal:
                CHAN_1.txt
                CHAN_2.kvs

            Not legal:
                CHAN_1.txt
                CHAN_1.kvs

        This is otherwise legal in OM, but this convenience 
        method relies on unique naming as it returns channels
        without their extension.

    """

    folder = lib.Factory.create(root)
    assert isinstance(folder, lib.Folder)

    data = {}
    for channel in folder:
        data.update(read_channel(channel))

    return data


def read_channel(channel):
    # basename = os.path.splitext(channel.basename)[0]
    name = channel.name

    data = {}
    for file in channel:
        contents = file.read().data
        if not contents:
            contents = file.path

        if isinstance(contents, dict):
            if not data.get(name):
                data[name] = {}

            data[name].update(contents)

        elif isinstance(contents, basestring):
            if not data.get(name):
                data[name] = ""

            try:
                data[name] += contents + "\n"
            except TypeError:
                log.warning("om.read: Disregarding %r due to format "
                    "not aligning with neighboring files" % file.path)
                continue
        else:
            raise ValueError("Contents of %r has not yet been accounted for in om.read()")

    return data


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
            log.info("Retired %i time(s) for %s" % (retries, root))

    log.info("Removed %s" % root)


if __name__ == '__main__':
    import openmetadata as om

    package = os.getcwd()
    root = os.path.join(package, 'test', 'persist')

    print "Reading: %s " % root
    data = om.read(root)
    for channel in data:
        print channel
        print "\t%s" % data.get(channel),
