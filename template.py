"""Creation objects for metadata"""

import os
import logging

from interface import AbstractTemplate, AbstractSource

log = logging.getLogger('openmetadata.template')

VERSION = '0.6'
METANAME = '.meta'


class Metadata(AbstractTemplate):

    log = logging.getLogger('openmetadata.template.Metadata')

    def __init__(self, path=METANAME, parent=None):
        super(Metadata, self).__init__(path, parent)
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
            channel = Channel(path)
            self.addchild(channel)


class Channel(AbstractTemplate):

    log = logging.getLogger('openmetadata.template.Channel')

    def __init__(self, path, parent=None):
        super(Channel, self).__init__(path, parent)

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
        print self.path
        for child in os.listdir(other):
            path = os.path.join(self.path, child)
            
            if os.path.isdir(path):
                if not os.path.basename(path) == METANAME:
                    # Skip any folder other than the .meta folder
                    log.warning("Non-metadata folder found: %s" % path)
                    continue

                child_object = Metadata(path)
            else:
                # Otherwise it's a file which makes it a Data object
                child_object = Data(path)

            self.addchild(child_object)


class Data(AbstractTemplate):
    def __init__(self, path, parent=None):
        super(Data, self).__init__(path, parent)
        self._input = None

        if isinstance(parent, AbstractTemplate):
            parent.addchild(self)

        if os.path.exists(self.path):
            self.loadp(self.path)

    def get(self):
        return self._input

    def set(self, data):
        """
            Set data to `data` without any pre-processing

            Advanced usage. This does not guarantee that object
            can be written or later read via standard mechanisms
            provided by openmetadata

            You are recommended to use load() or any of the
            convenience methods.

        """
        self._input = data

    def load(self, other):
        """Convert `other` to string"""
        self._input = str(other)

    def dump(self):
        return self._input

    def loadp(self, other):
        path = os.path.join(self.path, other)
        assert os.path.isfile(path)

        with open(path, 'r') as f:
            data = f.read()
            self.load(data)

    def hardlink(self, path):
        """Convenience method for set() using a Hardlink object"""
        self._input = Hardlink(path)

    def softlink(self, path):
        """Convenience method for set() using a Softlink object"""
        self._input = Softlink(path)

    def junction(self, path):
        """Convenience method for set() using a Junction object"""
        self._input = Junction(path)



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
            # Metadata
            # \.meta
            #
            if basename.startswith('.'):
                return Metadata(path)
            else:
                parent_basename = os.path.basename(parent_path)
                if parent_basename.startswith('.'):
                    #
                    # Channel
                    # \.meta\channel.txt
                    #
                    return Channel(path)

        else:
            #
            # Data
            # \.meta\channel.txt\data.txt
            # 
            return Data(path)

        return path


# Convenience method for use external to this module
# 
#    E.g.
#       import template
#       template.create(r'c:\path')
create = TemplateFactory.create


# Source Objects
#
# Used in Data and passed to write() which
# determines how to process `path` of each source.
#
#   Copy        -- From any disk
#   Hardlink    -- From local disk
#   Softlink    -- From any disk
#   Junction    -- from local disk
#   Download    -- From http
#   Stream      -- From pipe
#   Fetch       -- From database

Copy = type('Copy', (AbstractSource,), {})
Hardlink = type('Hardlink', (AbstractSource,), {})
Softlink = type('Softlink', (AbstractSource,), {})
Junction = type('Junction', (AbstractSource,), {})
Download = type('Download', (AbstractSource,), {})
Stream = type('Stream', (AbstractSource,), {})
Fetch = type('Fetch', (AbstractSource,), {})



if __name__ == '__main__':
    cpy = Copy(r's:\test\image1.png')
    hlink = Hardlink(r's:\test\image1.png')
    slink = Softlink(r's:\test\image1.png')

    print repr(slink)