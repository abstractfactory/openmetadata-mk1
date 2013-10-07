#!/usr/bin python

from __future__ import absolute_import

import os
from nose.tools import *

import openmetadata as om

cwd = os.getcwd()
root = os.path.join(cwd, 'test')
dynamic = os.path.join(root, 'dynamic')
persist = os.path.join(root, 'persist')


def test_children():
    """Children are returned as appropriate objects"""
    folder1 = om.instance.Folder(persist)


def test_om_read():
    """`om.read()` convenience method"""
    metadata = om.read(persist)
    assert_is_instance(metadata, dict)


def test_om_write():
    """`om.write()` convenience method"""
    om.write(dynamic, 'some text')


# def test_om_update():
#     """`om.read()` convenience method"""
#     existing_file = os.path.join(persist, r'.meta\chan.txt\document.txt')
#     om.update(existing_file, 'updated data!')


def test_om_delete():
    """`om.delete()` convenience method"""
    meta = om.template.Folder(os.path.join(dynamic, om.constant.Meta))
    chan = om.template.Channel('chan.txt', parent=meta)
    file = om.template.File('document.txt', parent=chan)
    
    data = 'some text'

    file.setdata(data)
    file.write()

    om.delete(meta.path)


def test_read_channel():
    """Read channel directly"""
    chan = os.path.join(persist, '.meta', 'chan.txt')

    channel = om.instance.create(chan)

    assert_is_instance(channel, om.instance.Channel)
    assert_is_instance(channel.read(), dict)
    # {'document1.txt': "This is some data here"}


def test_full_template():
    """New metadata from scratch using templates"""

    meta = om.template.Folder(os.path.join(dynamic, om.constant.Meta))
    chan = om.template.Channel('chan.txt', parent=meta)
    file = om.template.File('document.txt', parent=chan)
    
    data = 'some text'

    file.setdata(data)
    file.write()

    # Read it back in
    instance = om.instance.create(file.path)
    assert_equals(instance.read(), data)

    om.delete(meta.path)


def test_append_file_to_existing():
    """Append file to existing channel"""

    meta = om.instance.Folder(os.path.join(persist, om.constant.Meta))
    channel = meta.children[0]
        
    data = "new content"

    file_template = om.template.File('appended.txt', channel)
    file_template.setdata(data)
    file_template.write()

    # Read it back in
    file_instance = om.instance.create(file_template.path)
    assert_is_instance(file_instance, om.instance.File)
    assert_equals(file_instance.read(), data)

    om.delete(file_instance.path)


def test_append_metadata_to_channel():
    """Append metadata to existing channel"""

    meta = om.instance.Folder(os.path.join(persist, om.constant.Meta))
    channel = meta.children[0]

    submeta = om.template.Folder('.meta', parent=channel)
    subchannel = om.template.Channel('subchan.txt', parent=submeta)

    data = 'some text'

    file = om.template.File('text.txt', parent=subchannel)
    file.setdata(data)
    file.write()

    # Read it back in
    file_instance = om.instance.create(file.path)
    assert_is_instance(file_instance, om.instance.File)
    assert_equals(file_instance.read(), data)

    om.delete(file_instance.path)


def test_hardlink_reference():
    """Create metadata using Hardlink reference"""

    meta = om.template.Folder(os.path.join(dynamic, om.constant.Meta))
    chan = om.template.Channel('chan.img', parent=meta)
    file = om.template.File('image1.png', parent=chan)
    
    img = os.path.join(root, 'image1.png')
    data = om.reference.Hardlink(img)

    file.setdata(data)
    file.write()

    # Read it back in
    instance = om.instance.create(file.path)
    assert_equals(instance.read(), file.path)

    om.delete(meta.path)


def test_copy_reference():
    """Create metadata using Copy reference"""

    meta = om.template.Folder(os.path.join(dynamic, om.constant.Meta))
    chan = om.template.Channel('chan.img', parent=meta)
    file = om.template.File('image1.png', parent=chan)
    
    img = os.path.join(root, 'image1.png')
    data = om.reference.Copy(img)

    file.setdata(data)
    file.write()

    # Read it back in
    instance = om.instance.create(file.path)
    assert_equals(instance.read(), file.path)

    om.delete(meta.path)


if __name__ == '__main__':
    # import nose
    # nose.run(defaultTest=__name__)
    # metadata = om.Folder(parent=root)
    # print metadata
    test_children()
    # test_om_read()
    # test_om_write()
    # test_full_template()
    # test_append_file_to_existing()
    # test_append_metadata_to_channel()
    # test_hardlink_reference()
    # test_copy_reference()
