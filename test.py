import os
import sys
import shutil

from nose.tools import *

pythonpath = 's:/research/beast/openmetadata/api'
if not pythonpath in sys.path:
    sys.path.insert(0, pythonpath)

import openmetadata as om
from openmetadata import constant

root = r's:\test'


def test_data():
    """New Metadata, Channel and Data"""

    metadata = om.MetadataTemplate(parent=root)

    channel = om.ChannelTemplate('chan.txt', parent=metadata)
    
    data = om.DataTemplate('text.txt', parent=channel)
    data.load('some text')

    # print metadata.dir()

    om.create(metadata)

    # assert_equal(om.read(root), metadata.dump())

    shutil.rmtree(metadata.path)
    print "Removed %s" % metadata.path
    
    # Output:
    # Created s:\test\.meta
    # Created s:\test\.meta\chan.txt
    # Wrote s:\test\.meta\chan.txt\text.txt
    # Removed s:\test\.meta


def test_subchannel():
    """Channel within Channel"""

    metadata = om.MetadataTemplate(parent=root)

    channel = om.ChannelTemplate('newchannel.txt', parent=metadata)

    submeta = om.MetadataTemplate(parent=channel)
    subchannel = om.ChannelTemplate('newsubchannel.txt', parent=submeta)

    # Text is explicit, as they are not preceeded with any protocol
    data1 = om.DataTemplate('text', parent=channel)
    data1.load('some text')

    # Images are implicit, since they are preceeded with a protocol
    data2 = om.DataTemplate('text2', parent=subchannel)
    data2.load('some more text')

    # print metadata.dir()
    om.create(metadata)

    shutil.rmtree(metadata.path)
    print "Removed %s" % metadata.path

    # Output:
    # Created s:\test\.meta
    # Created s:\test\.meta\newchannel.txt
    # Wrote s:\test\.meta\newchannel.txt\text.txt
    # Created s:\test\.meta\newchannel.txt\newsubchannel.img
    # Hardlinked 's:\test\image1.png' to 's:\test\.meta\newchannel.txt\newsubchannel.img\image1.png'

def test_metadata():
    """New Metadata"""

    metadata = om.MetadataTemplate(parent=root)

    om.create(metadata)

    shutil.rmtree(metadata.path)
    print "Removed %s" % metadata.path

    # Output:
    # Created 's:\test\.meta'


def test_metadata_dump():
    """Dump metadata"""
    metadata = om.MetadataTemplate(parent=root)

    channel = om.ChannelTemplate('chan.txt', parent=metadata)
    
    data = om.DataTemplate('text.txt', parent=channel)
    data.load('some text')

    # print metadata.dump()
    dump = {'s:\\test\\.meta\\chan.txt': {'s:\\test\\.meta\\chan.txt\\text.txt': 'some text'}}
    assert_equals(dump, metadata.dump())


def test_metadata_load():
    """Load metadata"""
    metadata = om.MetadataTemplate(parent=root)

    channel1 = om.ChannelTemplate('chan1.txt', parent=metadata)
    channel2 = om.ChannelTemplate('chan2.txt', parent=metadata)
    
    data = om.DataTemplate('text.txt', parent=channel1)
    data.load('some text')

    data2 = om.DataTemplate('text2.txt', parent=channel2)
    data2.load('some text')

    # output = {'s:\\test\\.meta\\chan1.txt': {'s:\\test\\.meta\\chan1.txt\\text.txt': 'some text'}, 's:\\test\\.meta\\chan2.txt': {}}

    before = metadata.dump()
    metadata.load(metadata.dump())
    after = metadata.dump()

    assert_equals(before, after)


def test_load():
    """Load existing path"""

    root = r's:\test'
    
    existing_meta = om.MetadataTemplate(parent=root)
    existing_meta.dir()
    
    # Name           Format      Path
    # meta
    #   channel1     txt         s:/test/.meta/channel1.txt
    #       data1    txt         s:/text/.meta/
    # channel2       img         s:/test/.meta/channel2.img
    # channel3       vid         s:/test/.meta/channel3.vid
    

# def test_reference_http():
#     # Reference a file from the internet
    
#     root = r's:\root'
    
#     metadata = om.MetadataTemplate(parent=root)
#     chan = om.ChannelReference(name='channel1', parent=metadata)
#     chan.setformat(om.Image)
#     data = om.DataTemplate(name='data1', parent=metadata)
#     data.set('http://pipi.io/logo.png')
    
#     om.create(metadata)
#     print "Removed %s" % metadata.path
    
#     # Created 's:/root/.meta
#     # Created 's:/root/.meta/channel1.png
#     # Copied 's:/root/.meta/channel1.png/data1.png'

    
# def test_root_ftp():
#     pass
    
# def test_reference_to_incompatible_channel():
#     # Try loading a file via reference into a text channel
#     pass
    
# def test_nonexisting_reference():
#     # Tey loading a plain text document as reference.
#     # It won't exist since it is explicit data.
#     pass

# def test_txt():
#     pass

# def test_img():
#     pass


if __name__ == '__main__':
    import nose
    nose.run(defaultTest=__name__)

    # test_data()
    # test_subchannel()
    # test_metadata_dump()
    # test_metadata_load()
    # test_dump()
    # test_txt()
    # test_img()
