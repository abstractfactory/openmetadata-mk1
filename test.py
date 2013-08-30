
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


# def test_metadata_dump():
#     """Dump metadata"""
    
#     if not os.name == 'nt':
#         return

#     metadata = om.MetadataTemplate(parent=root)

#     channel = om.ChannelTemplate('chan.txt', parent=metadata)
    
#     data = om.DataTemplate('text.txt', parent=channel)
#     data.load('some text')

#     # print metadata.dump()
#     print root
#     dump = {
#                 os.path.join(root, r'\.meta\chan.txt'): 
#                     {os.path.join(root, r'\.meta\chan.txt\text.txt'): 
#                         'some text'
#                     }
#             }

#     assert_equals(dump, metadata.dump())


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

    existing_meta = om.MetadataTemplate(parent=root)
    existing_meta.dir()
    
    # Name           Format      Path
    # meta
    #   channel1     txt         s:/test/.meta/channel1.txt
    #       data1    txt         s:/text/.meta/
    # channel2       img         s:/test/.meta/channel2.img
    # channel3       vid         s:/test/.meta/channel3.vid
    
def test_link_versus_manual():
    """Test Linking versus Manual set

    Ensure that setting data to a Link object directly is the
    same as using link() with a path

    """

    metadata = om.MetadataTemplate(parent=root)

    channel = om.ChannelTemplate('chan.img', parent=metadata)
    
    linked = om.DataTemplate('image1.png', parent=channel)
    linked.link(os.path.join(root, 'image1.png'))

    link = om.template.Link(os.path.join(root, 'image1.png'))
    manual = om.DataTemplate('image1.png', parent=channel)
    manual.set(link)

    assert_equals(linked.data, manual.data)


def test_link():
    """Test linking to binary file"""
    metadata = om.MetadataTemplate(parent=root)

    channel = om.ChannelTemplate('chan.img', parent=metadata)
    
    linked = om.DataTemplate('image1.png', parent=channel)
    linked.link(os.path.join(root, 'image1.png'))

    om.create(metadata)

    shutil.rmtree(metadata.path)
    print "Removed %s" % metadata.path


# def test_reference_http():
#     # Reference a file from the internet
    
#     root = r's:\root'
    
#     metadata = om.MetadataTemplate(parent=root)

#     chan = om.ChannelReference(name='channel1.bin', parent=metadata)

#     data = om.DataTemplate(name='index.html', parent=chan)
#     data.copy('http://pipi.io/index.html')
    
#     om.create(metadata)
#     print "Removed %s" % metadata.path
    
    # Created 's:/root/.meta
    # Created 's:/root/.meta/channel1.png
    # Copied 's:/root/.meta/channel1.png/data1.png'

    
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
    # print root
    # test_data()
    # test_subchannel()
    # test_metadata_dump()
    # test_metadata_load()
    # test_load()
    # test_link_versus_manual()
    # test_dump()
    # test_txt()
    # test_img()
