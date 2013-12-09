"""Convenience module for the end-user

The goal of this module is to provide as high-level utilities
as possible for users who wish to have as little knowledge as
possible about Open Folder.

Target audience leans towards Technical Directors or
fellow scripters in any DCC.

"""

from __future__ import absolute_import

import os
# import sys
import errno
import logging
import shutil
import collections

from openmetadata import domain

log = logging.getLogger('openmetadata.transaction')


def write(path, channel=None, key=None, data=None):
    """Convenience method for writing metadata"""
    container = domain.Folder(path)
    
    if key and not channel:
        raise ValueError("Argument `key` must be specified in "
            "conjunction with `channel`")

    if channel and not key:
        if not isinstance(data, dict):
            raise ValueError("Data passed to object of type "
                "<Channel> must be of type <dict>")

        container = domain.Channel(channel, container)

    if channel and key:
        channel = domain.Channel(channel, container)
        key = domain.Key(key, channel)

        container = key

    container.data = data
    # container.write()
    print "%r = %r" % (container.path, container.data)


def update(path, channel=None, key=None, data=None):
    """Convenience method for updating metadata"""
    raise NotImplementedError


def read(path, channel=None, key=None):
    """Convenience method for reading metadata

    Parameters
        path    (str)   : Path to meta folder
        channel (str)   : (optional) Name of individual channel
        key     (str)   : (optional) Name of individual file


    Returns
        dict()          : {'obj.name': content}
    

    Calling this method with only `path` specified is identical
    to calling Folder.read().data directly.

    """

    if key and not channel:
        raise ValueError("Must supply `channel` with `key` argument")

    if not os.path.exists(path):
        return {}

    try:
        obj = domain.Factory.create(path)
    except WindowsError as e:
        # Temporary fix. An error occurs when trying to
        # read junctions pointing to invalid targets.
        if e.errno == errno.ENOENT:
            print e
            return {}
        raise e

    assert isinstance(obj, domain.Folder)

    if channel:
        obj = obj.child(channel)
        if not obj:
            return {}

        if key:
            obj = obj.child(key)
            if not obj:
                return None

    return obj.read().data


def exists(path, channel=None, key=None):
    pass


def cascade(path, channel, key=None):
    """Merge metadata of each channel matching `term` up-wards through hierarchy"""
    folder = domain.Folder(path)

    hierarchy = _findchannels(folder, channel)
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


def delete(path, channel=None, key=None, max_retries=10):
    assert os.path.exists(path)

    retries = 0
    while True:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
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
            log.info("Retired %i time(s) for %s" % (retries, path))

    log.info("Removed %s" % path)



def _findchannels(folder, term, result=None):
    """Return channels matching `term` up-wards through hierarchy"""
    assert isinstance(folder, domain.Folder)
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
        # Before we recurse, ensure this is not a path.
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
            return _findchannels(parent, term, result)

    return result


# def cascade(folder, term):


if __name__ == '__main__':
    import openmetadata as om

    package = os.getcwd()
    path = os.path.join(package, 'test', 'persist')
    path = om.Folder(r's:\content\jobs\test\content\shots')

    # print cascade(path, 'properties')
