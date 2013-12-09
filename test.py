#!/usr/bin python

from __future__ import absolute_import

import os
from nose.tools import *

import openmetadata as om

cwd = os.getcwd()
root = os.path.join(cwd, 'test')
dynamic = os.path.join(root, 'dynamic')
persist = os.path.join(root, 'persist')
stress = os.path.join(root, 'stresstest')


def test_children(root=None):
    """Children are returned as appropriate objects

    Conditions:
        - Children of Folders are always Channel
        - Children of Channel are either Key or Folder
        - Key has no children

    """
    
    root = root or om.Folder(persist)
    if isinstance(root, om.domain.AbstractParent):
        for child in root.children:
            if isinstance(root, om.Folder):
                # Children of Folders are always channels
                assert_is_instance(child, om.Channel)
            if isinstance(root, om.Channel):
                assert isinstance(child, om.Key) or isinstance(child, om.Folder)

            # Recursively test each child
            test_children(child)
    else:
        assert_is_instance(root, om.Key)


def test_relativepath():
    """Children contain relative paths"""
    folder = om.Folder(persist)
    for child in folder:
        om_relpath = child.relativepath
        parent_path = os.path.join(folder.path, om.constant.Meta)
        manual_relpath = os.path.relpath(child.path, parent_path)

        assert_equals(om_relpath, manual_relpath)

    # Manually adding a child
    channel = om.Channel(os.path.join(persist, r'.meta\chan.txt'), folder)
    assert_equals(channel.relativepath, os.path.relpath(channel.path, os.path.join(folder.path, om.constant.Meta)))
    
    channel = om.Channel(os.path.join(dynamic, r'.meta\chan.txt'), folder)
    assert_true(os.path.isabs(channel.relativepath))

def test_extension():
    """Test extension returns extension including dot"""
    folder = om.Folder(persist)
    for channel in folder:
        assert_equals(channel.extension, "." + channel.basename.rsplit(".", 1)[1])
        assert_equals(channel.extension, os.path.splitext(channel.path)[1])


def test_clear_file():
    """Clear individual file"""
    folder = om.Folder(persist)
    
    # Add channel to it
    channel = om.Channel('new_channel.txt', folder)
    file = om.Key('document.txt', channel)
    
    file.data = "This is some data"
    file.write()

    file.clear()

    assert_equals(file.exists, False)

    # Clean up
    channel.clear()


def test_clear_channel():
    """Clear individual channel"""
    folder = om.Folder(persist)
    
    # Add channel to it
    channel = om.Channel('new_channel.txt', folder)
    file = om.Key('document.txt', channel)
    
    file.data = "This is some data"
    file.write()

    channel.clear()

    assert_equals(channel.exists, False)


def test_clear_folder():
    """Remove ALL metadata"""
    folder = om.Folder(dynamic)
    
    # Add channel to it
    channel = om.Channel('new_channel.txt', folder)
    file = om.Key('document.txt', channel)
    
    file.data = "This is some data"
    file.write()

    folder.clear()

    assert_equals(folder.exists, False)


def test_comparison():
    """Separate instances of same path are equal"""
    folder = om.Folder(dynamic)
    
    # Add channel to it
    channel = om.Channel('new_channel.txt', folder)
    file = om.Key('document.txt', channel)

    file_other = om.Key('document.txt', channel)

    assert_equals(file, file_other)


def test_iterator():
    """Iterator (for channel in folder) works"""
    folder = om.Folder(root)

    for channel in folder:
        # Child is indeed a channel
        assert_is_instance(channel, om.Channel)

        # Result of iterator is the same as calling
        # .children manually.
        assert_true(channel in folder.children)

        for file in channel:
            assert_is_instance(file, om.Key)
            assert_true(file in channel.children)


def test_trash():
    """Deleted items end up in trash"""
    pass


def test_revisions():
    """Edited items are backed up in revisions"""
    pass


# def test_om_read():
#     """`om.read()` convenience method"""
#     metadata = om.read(persist)
#     for channel, content in metadata.iteritems():
#         assert isinstance(content, dict) or isinstance(content, basestring)


def test_instancefactory(root=None):
    """Stress-test instance.Factory

    Traverse stresstest folder and ensure only appropriate
    folders get assigned their respective objects.

    The rules are:
        - Any folder with .meta within is a Folder,
            unless it's parent is also a .meta, then it is
            a Channel that may be considered a Folder
        - Any folder within .meta is a channel
            if is has an extension.
        - Any file whose parents parent is a .meta folder
            is a Key object.

    !Todo!
    How:
        - Get all files and folders of root manually
        - Compare and contrast resulting children
        - No objects containing the word "invalid_" should be returned
        - No objects containing the word "no_" should be returned
        - All other objects should be returned
    !Todo!

    """

    root = root or om.Factory.create(stress)
    
    if isinstance(root, om.domain.AbstractParent):
        for child in root.children:
            test_instancefactory(child)

    # Inserting a .meta folder directly
    metafolder = om.Factory.create(os.path.join(persist, om.constant.Meta))
    assert_is_instance(metafolder, om.domain.Folder)

# def test_om_write():
#     """`om.write()` convenience method"""
#     om.write(dynamic, 'some text')


# def test_om_update():
#     """`om.read()` convenience method"""
#     existing_file = os.path.join(persist, r'.meta\chan.txt\document.txt')
#     om.update(existing_file, 'updated data!')


# def test_om_delete():
#     """`om.delete()` convenience method"""
#     meta = om.Folder(os.path.join(dynamic, om.constant.Meta))
#     chan = om.Channel('chan.txt', parent=meta)
#     file = om.Key('document.txt', parent=chan)
    
#     data = 'some text'

#     file.data = data
#     file.write()

#     om.delete(meta.path)


def test_factory_folder():
    """Create Folder via Factory"""
    obj = om.Factory.create(persist)
    assert_is_instance(obj, om.Folder)


def test_factory_channel():
    """Create Channel via Factory"""
    chan = os.path.join(persist, '.meta', 'chan.txt')

    channel = om.Factory.create(chan)
    assert_is_instance(channel, om.Channel)


def test_factory_file():
    """Create Key via Factory"""
    chan = os.path.join(persist, '.meta', 'chan.txt', 'document.txt')

    channel = om.Factory.create(chan)
    assert_is_instance(channel, om.Key)


def test_full_template():
    """New metadata from scratch using templates"""

    folder = om.Folder(dynamic)
    chan = om.Channel('chan.txt', parent=folder)
    file = om.Key('document.txt', parent=chan)
    
    data = 'some text'

    file.data = data
    file.write()

    # Read it back in
    file_instance = om.Factory.create(file.path)
    file_instance.read()

    assert_equals(file_instance.data, data)

    om.delete(folder.path)


def test_append_file_to_existing():
    """Append file to existing channel"""

    folder = om.Folder(persist)
    channel = folder.children[0]
        
    data = "new content"

    file_template = om.Key('appended.txt', channel)
    file_template.data = data
    file_template.write()

    # Read it back in
    file_instance = om.Factory.create(file_template.path)
    file_instance.read()

    assert_is_instance(file_instance, om.Key)
    assert_equals(file_instance.data, data)

    om.delete(file_instance.path)


def test_append_metadata_to_channel():
    """Append metadata to existing channel"""

    meta = om.Folder(persist)
    channel = meta.children[0]

    submeta = om.Folder('.meta', parent=channel)
    subchannel = om.Channel('subchan.txt', parent=submeta)

    data = 'some text'

    file = om.Key('document.txt', parent=subchannel)
    file.data = data
    file.write()

    # Read it back in
    file_instance = om.Factory.create(file.path)
    file_instance.read()

    assert_is_instance(file_instance, om.Key)
    assert_equals(file_instance.data, data)

    om.delete(file_instance.path)

def test_hidden():
    """Special channels works

    Persist has a hidden channel called __hidden__

    """

    folder = om.Folder(persist)

    hidden = None
    for channel in folder:
        if channel.hidden:
            hidden = channel

    assert_true(hidden is not None)


def test_hidden_channels():
    """Hidden channels works

    Pre-conditions:
        "persist" has atleast one hidden folder

    """

    folder = om.Folder(persist)
    hidden = folder.hiddenchildren
    assert_true(hidden is not [])


# def test_unique_channelname():
#     """Channel names must be unique"""
#     folder = om.Folder(persist)

#     # These channels have the same name, even though they
#     # differ in their extensions. This is not valid due to
#     # convenience method om.read() returns channel names 
#     # without extension.
#     channel1 = om.Channel('unique1.txt', folder)
#     channel2 = om.Channel('unique1.kvs', folder)

#     file1 = om.Key('temp.txt', channel1)
#     file2 = om.Key('temp.txt', channel2)

#     # file1.write()
#     assert_raises(1/0, DivisionByZeroException)


def test_read_channel():
    """Read individual channel"""
    folder = om.Folder(persist)

    metadata = {}
    for channel in folder:
        channel.read()
        metadata.update({channel.name: channel.data})

    # print metadata


def test_read_folder():
    """Read full folder"""
    folder = om.Folder(persist)
    folder.read()
    folder.data


def test_cascading_metadata():
    """Cascading metadata behaves appropriately

    The child folder contains overriding properties from
    the parent `persist` folder.

    Namely
        Persist -> par1: {key1: {val1: Original, val2: Original}, key2: {val2: Original}}
        Child   -> par1: {key1: {val1: Changed, val3: Original}, key2: Changed}

    The result should be
        par1: {key1: {val1: Changed, val2: Original, val3: Original}, key2: Changed}

    """

    # persist_obj = om.Folder(persist)
    path = os.path.join(persist, 'child')
    csmetadata = om.transaction.cascade(path, 'cascading')
    
    # A is overriden
    assert_equals(csmetadata['root']['A'], 'Overidden')

    # B is not
    assert_equals(csmetadata['root']['B'], 'Original')

    # more remains
    assert_equals(csmetadata['more'], {'key': 'value'})


def test_channel_set_multiple_times():
    """Set channel data multiple times"""
    folder = om.Factory.create(root)
    channel = om.Channel('testing.kvs', folder)

    channel.data = {u'file1': {u'some data': u'data'}, 'file2': {'some': u'data'}}
    channel.data = {u'file1': {u'some data': u'data'}, 'file2': {'some': u'data'}}
    channel.data = {u'file4': {u'some data': u'data'}, 'file1': {'some': u'data'}}

    print channel.data


def test_defaultfileextension():
    """Default file extensions of Channel works"""
    folder = om.Folder(persist)
    channel = om.Channel('testing_dfe.txt', folder)
    channel.data = {'key': {'hello': 5}}
    # channel.write()
    # channel.read()
    # data = channel.data['key']
    # print "%r(%s)" % (data.__class__, data)
    # channel.write()
    # channel.clear()


def test_individual_channel_convenience():
    """Accessing individual channel via om.read works"""
    data = om.read(path=persist, channel='testing')
    assert_false(data == {})

    # Non-existing channel returns dictionary
    assert_is_instance(om.read(persist, 'NON_EXISTANT'), dict)


def test_individual_file_convenience():
    """Accessing individual file via om.read works"""
    data = om.read(path=persist, channel='testing', key='file1')
    assert_false(data == {})

    data = om.read(persist, 'testing', 'NON_EXISTANT')
    assert_equals(data, None)


def test_om_write():
    channel_data = {'channel1': {'key1': 'data'}}
    key_data = 'data'

    # Write to channel
    # om.write(path=persist, channel='testing', data=channel_data)

    # Write to key
    # om.write(path=persist, channel='testing', key='temp', data=key_data)


if __name__ == '__main__':
    import logging
    log = logging.getLogger('openmetadata')
    log.setLevel(logging.ERROR)

    import nose
    nose.run(defaultTest=__name__)

    # test_cascading_metadata()
    # test_om_write()
    # test_inmemorychildren()
    # test_individual_channel_convenience()
    # test_individual_file_convenience()
    # test_defaultfileextension()
    # test_channel_set_multiple_times()
    # test_cascading_metadata()
    # test_relativepath()
    # print metadata
    # test_clear_file()
    # test_clear_folder()
    # test_relativepath()
    # test_children()
    # test_om_read()
    # test_factory_folder()
    # test_factory_channel()
    # test_instancefactory()
    # test_factory_file()
    # test_om_write()
    # test_full_template()
    # test_append_file_to_existing()
    # test_append_metadata_to_channel()
    # test_hardlink_reference()
    # test_copy_reference()
    # test_read_channel()
    # test_hidden_channels()
    # test_cascading_metadata()
