"""Templates are temporary, editable elements on in memory.

Templates correlates to each Instance object, which are used for reading,
and provides the writing mechanisms.


"""

import os
import logging
from abc import ABCMeta, abstractmethod

from openmetadata import format
# from openmetadata import constant

log = logging.getLogger('openmetadata.template')

VERSION = '0.14.0'


class BaseClass:
    """Abc to all templates in openmetadata"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, path, parent=None):
        self._path = path
        self._parent = parent
        self._children = []

        if hasattr(parent, 'addchild'):
            parent.addchild(self)

    def __str__(self):
        return self.path

    def __repr__(self):
        return u"%s.%s(%r)" % (__name__, self.__class__.__name__, self.__str__())

    def dir(self, tablevel=-1):
        """
        Depth-first directory listing.

        Todo: 
            - Make it Breadth-first, otherwise, children
            get put in an awkward position

        """

        output     = ""
        tablevel += 1
        
        for i in range(tablevel):
            output += " "
        
        output += "-o " + os.path.basename(self.path) + "\t" + self.path + "\n"

        for child in self._children:
            output += child.dir(tablevel)
        
        tablevel -= 1

        return output

    @property
    def path(self):
        """
        Return full path

        Taking parent into account, return the full path
        to self.

        """
        
        path = self._path
        if self.parent:
            path = os.path.join(self.parent.path, path)

        return path

    @property
    def children(self):
        return self._children

    @property
    def parent(self):
        return self._parent

    def setparent(self, parent):
        parent._children.append(self)
        self._parent = parent


class Folder(BaseClass):
    """Temporary placeholder for future Folder instance"""

    log = logging.getLogger('openmetadata.template.Folder')

    def __init__(self, path, parent=None):
        super(Folder, self).__init__(path, parent)

    def addchild(self, child):
        self._children.append(child)
        child._parent = self

    def removechild(self, child):
        self._children.remove(child)
        child._parent = None


class Channel(BaseClass):
    """Temporary placeholder for future Channel instance"""

    log = logging.getLogger('openmetadata.template.Channel')

    def __init__(self, path, parent=None):
        super(Channel, self).__init__(path, parent)

    def addchild(self, child):
        self._children.append(child)
        child._parent = self

    def removechild(self, child):
        self._children.remove(child)
        child._parent = None


class File(BaseClass):
    """Editable File object

    User edits this objects and then writes to disk using its
    own .write() method.

    """

    log = logging.getLogger('openmetadata.template.File')
    
    def __init__(self, path, parent=None):
        super(File, self).__init__(path, parent)
        self._data = None

    @property
    def data(self):
        return self._data

    def setdata(self, data):
        self._data = data

    def write(self):
        data = self._data

        if not data:
            raise ValueError("No data to be written")

        if not self._parent:
            raise ValueError("No parent set")

        # Write references
        if hasattr(data, 'write'):
            return data.write(self.path)

        # Otherwise, grab a writer
        writer = format.create(self._path)
        if hasattr(writer, 'write'):
            parent = self.parent
            if not os.path.exists(parent.path):
                os.makedirs(parent.path)

            output_path = writer.write(self.path, self.data)

            self.log.debug("Successfully wrote to %s" % self.path)
        else:
            self.log.warning("No writer found for %s" % self.path)

        return output_path


if __name__ == '__main__':
    from openmetadata import instance

    cwd = os.getcwd()
    root = os.path.join(cwd, 'test', '.meta')
    
    # New everything
    meta = Folder(root, parent=None)
    channel = Channel('chanx.txt', parent=meta)
    file = File('document.txt', parent=channel)
    file.setdata('written via python, yet again')
    # file.write()

    # Append to existing
    meta = instance.Folder(root)
    channel = meta.children[0]
    print channel.children
    file_instance = channel.children[0]
    
    # convert to template
    file_template = File(file_instance.path, channel)

    # repeat it 5 times
    data = file_instance.read().values()[0]
    data += "\n" + data

    file_template.setdata(data)

    # file_template.write()
