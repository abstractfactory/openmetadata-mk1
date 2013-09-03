#!/usr/bin python
import os
import sys
import shutil

from nose.tools import *

package = os.path.dirname(__file__)
path = os.path.dirname(package)

if not path in sys.path:
    sys.path.insert(0, path)

root = os.path.join(package, 'test')

import openmetadata as om


def test_read():
    path = os.path.join(root, 'persist')
    metadata = om.read(path)
    
    for name, channel in metadata.iteritems():
        print name
        for key, value in channel.iteritems():
            print "\t" + key


def test_data():
    """New Metadata, Channel and Data"""

    metadata = om.Metadata(parent=root)

    channel = om.Channel('chan.txt', parent=metadata)
    
    data = om.Data('text.txt', parent=channel)
    data.load('some text')

    # print metadata.dir()

    om.write(metadata)

    # assert_equal(om.read(root), metadata.dump())

    om.delete(metadata.path)
    
    # Output:
    # Created s:\test\.meta
    # Created s:\test\.meta\chan.txt
    # Wrote s:\test\.meta\chan.txt\text.txt
    # Removed s:\test\.meta


def test_subchannel():
    """Channel within Channel"""

    metadata = om.Metadata(parent=root)

    channel = om.Channel('newchannel.txt', parent=metadata)

    submeta = om.Metadata(parent=channel)
    subchannel = om.Channel('newsubchannel.txt', parent=submeta)

    # Text is explicit, as they are not preceeded with any protocol
    data1 = om.Data('text', parent=channel)
    data1.load('some text')

    # Images are implicit, since they are preceeded with a protocol
    data2 = om.Data('text2', parent=subchannel)
    data2.load('some more text')

    # print metadata.dir()
    om.write(metadata)

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

    metadata = om.Metadata(parent=root)

    om.write(metadata)

    shutil.rmtree(metadata.path)
    print "Removed %s" % metadata.path

    # Output:
    # Created 's:\test\.meta'


def test_metadata_dump():
    """Dump metadata"""
    
    if not os.name == 'nt':
        return

    metadata = om.Metadata(parent=root)

    channel = om.Channel('chan.txt', parent=metadata)
    
    data = om.Data('text.txt', parent=channel)
    data.load('some text')

    assert_is_instance(metadata.dump(), dict)


def test_metadata_load():
    """Load metadata"""
    metadata = om.Metadata(parent=root)

    channel1 = om.Channel('chan1.txt', parent=metadata)
    channel2 = om.Channel('chan2.txt', parent=metadata)
    
    data = om.Data('text.txt', parent=channel1)
    data.load('some text')

    data2 = om.Data('text2.txt', parent=channel2)
    data2.load('some text')

    # output = {'s:\\test\\.meta\\chan1.txt': {'s:\\test\\.meta\\chan1.txt\\text.txt': 'some text'}, 's:\\test\\.meta\\chan2.txt': {}}

    before = metadata.dump()
    metadata.load(metadata.dump())
    after = metadata.dump()

    assert_equals(before, after)


def test_load():
    """Load existing path"""

    existing_meta = om.Metadata(parent=root)
    existing_meta.dir()
    
    # Name           Format      Path
    # meta
    #   channel1     txt         s:/test/.meta/channel1.txt
    #       data1    txt         s:/text/.meta/
    # channel2       img         s:/test/.meta/channel2.img
    # channel3       vid         s:/test/.meta/channel3.vid
    
def test_link_versus_set():
    """Hardlink versus Set

    Ensure that setting data to a Link object directly is the
    same as using link() with a path

    """

    metadata = om.Metadata(parent=root)

    channel = om.Channel('chan.img', parent=metadata)
    
    linked = om.Data('image1.png', parent=channel)
    linked.hardlink(os.path.join(root, 'image1.png'))

    link = om.template.Hardlink(os.path.join(root, 'image1.png'))
    manual = om.Data('image1.png', parent=channel)
    manual.set(link)

    assert_equals(linked.get(), manual.get())


def test_link():
    """Link to binary file"""
    metadata = om.Metadata(parent=root)

    channel = om.Channel('chan.img', parent=metadata)
    
    source = os.path.join(root, 'image1.png')
    linked = om.Data('image1.png', parent=channel)
    linked.hardlink(source)

    om.write(metadata)

    shutil.rmtree(metadata.path)
    print "Removed %s" % metadata.path


# def test_file_metadata():
#     """New metadata to file"""

#     root = r'C:\studio\appdata\scripts\python\openmetadata\test\image1.png'
#     metadata = om.Metadata(parent=root)

# def test_reference_http():
#     # Reference a file from the internet
    
#     root = r's:\root'
    
#     metadata = om.Metadata(parent=root)

#     chan = om.ChannelReference(name='channel1.bin', parent=metadata)

#     data = om.Data(name='index.html', parent=chan)
#     data.copy('http://pipi.io/index.html')
    
#     om.write(metadata)
#     print "Removed %s" % metadata.path
    
    # Created 's:/root/.meta
    # Created 's:/root/.meta/channel1.png
    # Copied 's:/root/.meta/channel1.png/data1.png'

    
# def test_root_ftp():
#     pass
    
# def test_reference_to_incompatible_channel():
#     # Try loading a file via reference into a text channel
#     pass
    
def test_nonexisting_reference():
    """Load non-existing reference"""


# def test_txt():
#     pass

# def test_img():
#     pass


if __name__ == '__main__':
    # import nose
    # nose.run(defaultTest=__name__)
    # print root
    test_read()
    # test_data()
    # test_subchannel()
    # test_metadata_dump()
    # test_metadata_load()
    # test_load()
    # test_link_versus_manual()
    # test_dump()
    # test_txt()
    # test_img()
