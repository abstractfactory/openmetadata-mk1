"""Creation objects for metadata"""

import os
import logging

from interface import AbstractTemplate, AbstractSource
import constant

log = logging.getLogger('openmetadata.template')

VERSION = '0.5'
METANAME = '.meta'


class MetadataTemplate(AbstractTemplate):

    log = logging.getLogger('openmetadata.template.MetadataTemplate')

    def __init__(self, path=METANAME, parent=None):
        super(MetadataTemplate, self).__init__(path, parent)
        self._children = []

        if isinstance(parent, AbstractTemplate):
            parent.addchild(self)

        if os.path.exists(self.path):
            self.loadp(self.path)

    @property
    def children(self):
        return self._children

    def addchild(self, child):
        self._children.append(child)
        child._parent = self

    def removechild(self, child):
        self._children.remove(child)

        if child._parent == self:
            child._parent = None

    def load(self, other):
        """Add channels from dict"""
        # for meta, 

        for key, value in other.iteritems():
            print key, value

    def dump(self):
        """
        Serialize each channel into dict of strings.

        {channel_name: {data_name: data_value}}

        """
        output = {}
        for child in self.children:
            output[str(child)] = child.dump()
        return output

    def loadp(self, other):
        """Load metadata from path"""
        
        for child in os.listdir(other):
            path = os.path.join(self.path, child)
            channel = ChannelTemplate(path)
            self.addchild(channel)


class ChannelTemplate(AbstractTemplate):

    log = logging.getLogger('openmetadata.template.ChannelTemplate')

    def __init__(self, path, parent=None):
        super(ChannelTemplate, self).__init__(path, parent)

        self._children = []

        if isinstance(parent, AbstractTemplate):
            parent.addchild(self)

        if os.path.exists(self.path):
            self.loadp(self.path)

    @property
    def children(self):
        return self._children

    def addchild(self, child):
        self._children.append(child)

        child._parent = self

    def removechild(self, child):
        self._children.remove(child)

        child._parent = None

    def load(self, other):
        for key, value in other.iteritems():
            print key, value

    def dump(self):
        output = {}
        for child in self.children:
            output[str(child)] = child.dump()
        return output

    def loadp(self, other):
        for child in os.listdir(other):
            path = os.path.join(self.path, child)
            
            if os.path.isdir(path):
                # A directory could only be a .meta folder
                assert os.path.basename(path) == METANAME

                child_object = MetadataTemplate(path)
            else:
                # Otherwise it's a file which makes it a Data object
                child_object = DataTemplate(path)

            self.addchild(child_object)


class DataTemplate(AbstractTemplate):
    def __init__(self, path, parent=None):
        super(DataTemplate, self).__init__(path, parent)
        self._data = str()

        if isinstance(parent, AbstractTemplate):
            parent.addchild(self)

        if os.path.exists(self.path):
            self.loadp(self.path)

    def get(self):
        return self._data

    def set(self, data):
        """Set data to `data` directly, without any conversion"""
        self._data = data

    def hardlink(self, path):
        """Hardlink if possible, otherwise softlink"""
        self._data = Hardlink(path)

    def softlink(self, path):
        self._data = Softlink(path)

    def junction(self, path):
        self._data = Junction(path)

    def load(self, other):
        """Convert `other` to string"""
        self._data = str(other)

    def dump(self):
        return self._data

    def loadp(self, other):
        path = os.path.join(self.path, other)
        assert os.path.isfile(path)

        with open(path, 'r') as f:
            data = f.read()
            self.load(data)


# Source objects
Copy = type('Copy', (AbstractSource,), {})
Hardlink = type('Hardlink', (AbstractSource,), {})
Softlink = type('Softlink', (AbstractSource,), {})
Junction = type('Junction', (AbstractSource,), {})


class TemplateFactory:
    """Given an existing path, return the appropriate template
    based on the following set of rules.

    Rules:
        - Metadata is preceded by a dot
        - Channels are any folder with an extension
        - Data are files

    """

    @classmethod
    def create(cls, path):
        if not os.path.exists(path):
            raise OSError("'%s' did not exist" % path)

        basename = os.path.basename(path)
        parent_path = os.path.dirname(path)

        if os.path.isdir(path):
            #
            # MetadataTemplate
            # \.meta
            #
            if basename.startswith('.'):
                return MetadataTemplate(path)
            else:
                parent_basename = os.path.basename(parent_path)
                if parent_basename.startswith('.'):
                    #
                    # ChannelTemplate
                    # \.meta\channel.txt
                    #
                    return ChannelTemplate(path)

        else:
            #
            # DataTemplate
            # \.meta\channel.txt\data.txt
            # 
            return DataTemplate(path)

        return path


# def getprotocol(url):
#     if url.startswith(constant.File):
#         return constant.File

#     return None


if __name__ == '__main__':
    cpy = Copy(r's:\test\image1.png')
    hlink = Hardlink(r's:\test\image1.png')
    slink = Softlink(r's:\test\image1.png')

    print repr(slink)