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
        - Children of Channel are either File or Folder
        - File has no children

    """
    
    root = root or om.instance.Folder(persist)
    if hasattr(root, 'children'):
        for child in root.children:
            if isinstance(root, om.instance.Folder):
                # Children of Folders are always channels
                assert_is_instance(child, om.instance.Channel)
            if isinstance(root, om.instance.Channel):
                assert isinstance(child, om.instance.File) or isinstance(child, om.instance.Folder)

            # Recursively test each child
            test_children(child)
    else:
        assert_is_instance(root, om.instance.File)


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
            is a File object.

    !Todo START!
    How:
        - Get all files and folders of root manually
        - Compare and contrast resulting children
        - No objects containing the word "invalid_" should be returned
        - No objects containing the word "no_" should be returned
        - All other objects should be returned
    !Todo END!

    """

    root = root or om.instance.create(stress)
    
    if hasattr(root, 'children'):
        for child in root.children:
            test_instancefactory(child)

# def test_om_write():
#     """`om.write()` convenience method"""
#     om.write(dynamic, 'some text')


# def test_om_update():
#     """`om.read()` convenience method"""
#     existing_file = os.path.join(persist, r'.meta\chan.txt\document.txt')
#     om.update(existing_file, 'updated data!')


# def test_om_delete():
#     """`om.delete()` convenience method"""
#     meta = om.template.Folder(os.path.join(dynamic, om.constant.Meta))
#     chan = om.template.Channel('chan.txt', parent=meta)
#     file = om.template.File('document.txt', parent=chan)
    
#     data = 'some text'

#     file.setdata(data)
#     file.write()

#     om.delete(meta.path)


def test_factory_folder():
    """Create Folder via Factory"""
    obj = om.instance.create(persist)
    assert_is_instance(obj, om.instance.Folder)


def test_factory_channel():
    """Create Channel via Factory"""
    chan = os.path.join(persist, '.meta', 'chan.txt')

    channel = om.instance.create(chan)
    assert_is_instance(channel, om.instance.Channel)


def test_factory_file():
    """Create File via Factory"""
    chan = os.path.join(persist, '.meta', 'chan.txt', 'document.txt')

    channel = om.instance.create(chan)
    assert_is_instance(channel, om.instance.File)


def test_full_template():
    """New metadata from scratch using templates"""

    folder = om.template.Folder(dynamic)
    chan = om.template.Channel('chan.txt', parent=folder)
    file = om.template.File('document.txt', parent=chan)
    
    data = 'some text'

    file.setdata(data)
    file.write()

    # Read it back in
    file_instance = om.instance.create(file.path)
    file_instance.read()

    assert_equals(file_instance.data, data)

    om.delete(folder.path)


def test_append_file_to_existing():
    """Append file to existing channel"""

    meta = om.instance.Folder(persist)
    channel = meta.children.next()
        
    data = "new content"

    file_template = om.template.File('appended.txt', channel)
    file_template.setdata(data)
    file_template.write()

    # Read it back in
    file_instance = om.instance.create(file_template.path)
    file_instance.read()

    assert_is_instance(file_instance, om.instance.File)
    assert_equals(file_instance.data, data)

    om.delete(file_instance.path)


def test_append_metadata_to_channel():
    """Append metadata to existing channel"""

    meta = om.instance.Folder(persist)
    channel = meta.children.next()

    submeta = om.template.Folder('.meta', parent=channel)
    subchannel = om.template.Channel('subchan.txt', parent=submeta)

    data = 'some text'

    file = om.template.File('text.txt', parent=subchannel)
    file.setdata(data)
    file.write()

    # Read it back in
    file_instance = om.instance.create(file.path)
    file_instance.read()

    assert_is_instance(file_instance, om.instance.File)
    assert_equals(file_instance.data, data)

    om.delete(file_instance.path)


# def test_hardlink_reference():
#     """Create metadata using Hardlink reference"""

#     meta = om.template.Folder(os.path.join(dynamic, om.constant.Meta))
#     chan = om.template.Channel('chan.img', parent=meta)
#     file = om.template.File('image1.png', parent=chan)
    
#     img = os.path.join(root, 'image1.png')
#     data = om.reference.Hardlink(img)

#     file.setdata(data)
#     file.write()

#     # Read it back in
#     instance = om.instance.create(file.path)
#     assert_equals(instance.read(), file.path)

#     om.delete(meta.path)


# def test_copy_reference():
#     """Create metadata using Copy reference"""

#     meta = om.template.Folder(os.path.join(dynamic, om.constant.Meta))
#     chan = om.template.Channel('chan.img', parent=meta)
#     file = om.template.File('image1.png', parent=chan)
    
#     img = os.path.join(root, 'image1.png')
#     data = om.reference.Copy(img)

#     file.setdata(data)
#     file.write()

#     # Read it back in
#     instance = om.instance.create(file.path)
#     assert_equals(instance.read(), file.path)

#     om.delete(meta.path)


if __name__ == '__main__':
    import nose
    nose.run(defaultTest=__name__)
    # print metadata
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
