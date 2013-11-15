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
import collections

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

    As opposed to calling Folder.read().data, this method blends
    Files together, disregarding if a channel has multiple files.

    They are blended in an alphabetical order, last one overwrites
    first one.

    This introduces some interesting limitations:
        - Parent channel must not exist twice

        E.g.
            Legal:
                CHAN_1.txt
                CHAN_2.kvs

            Not legal:
                CHAN_1.txt
                CHAN_1.kvs

    """

    folder = lib.Factory.create(root)
    assert isinstance(folder, lib.Folder)
    return folder.read().data


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



def findchannels(folder, term, result=None):
    """Return channels matching `term` up-wards through hierarchy"""
    assert isinstance(folder, lib.Folder)
    result = result or []

    # Note: We can only cascade channels of type .kvs

    current_channel = None
    # Look for `term` within folder
    for _channel in folder:
        if _channel.name == term and _channel.extension == '.kvs':
            result.append(_channel)
            current_channel = _channel

    # Recurse
    parent = folder.parent
    if parent:
        # Before we recurse, ensure this is not a root.
        isroot = False

        # TODO
        # Find a way to optimize this. Channel is being read here
        # to find the isRoot property which is used solely to
        # determine whether or not to continue searching.
        # This is an expensive operation, and whats worse,
        # the channel is being re-read in `cascade`.
        if current_channel:
            data = current_channel.read().data or {}
            if data.get('isRoot') is True:
                isroot = True

        if not isroot:
            return findchannels(parent, term, result)

    return result


def cascade(folder, term):
    """Merge metadata of each channel matching `term` up-wards through hierarchy"""
    hierarchy = findchannels(folder, term)
    hierarchy.reverse()

    # An implementation of the Property-Pattern as discussed here:
    # http://steve-yegge.blogspot.co.uk/2008/10/universal-design-pattern.html
    metadata_hierarchy = []
    for _channel in hierarchy:
        _channel.read()
        _data = _channel.data or {}
        metadata_hierarchy.append(_data)

    # The following algorithm is based on this answer:
    # http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    def update(d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    metadata = {}
    for _metadata in metadata_hierarchy:
        update(metadata, _metadata)

    return metadata


if __name__ == '__main__':
    import openmetadata as om

    package = os.getcwd()
    root = os.path.join(package, 'test', 'persist')
    root = om.Folder(r's:\content\jobs\test\content\shots')

    print cascade(root, 'properties')
