"""Templates are temporary, editable elements on in memory.

Templates correlates to each Instance object, which are used for reading,
and provides the writing mechanisms.


"""

import os
import logging
from abc import ABCMeta, abstractmethod

from openmetadata import format
from openmetadata import instance
from openmetadata import interface
from openmetadata import constant

log = logging.getLogger('openmetadata.template')

VERSION = '0.14.0'


class BaseClass(interface.AbstractPath):

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, path, parent=None):
        super(BaseClass, self).__init__(path)
        self._parent = parent

        if hasattr(parent, 'addchild'):
            parent.addchild(self)

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
        self._children = []

    @property
    def path(self):
        return os.path.join(super(Folder, self).path, constant.Meta)

    @property
    def children(self):
        for child in self._children:
            yield child

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
        self._children = []

    @property
    def children(self):
        for child in self._children:
            yield child

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

    def load(self, instance):
        """Promote `instance` to template"""
        self.setdata(instance.read())

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

        # Fetch appropriate writing-object
        transation = format.create(ext=self.ext)
        if not hasattr(transation, 'write'):
            self.log.warning("No transation found for %r" % self)
            return

        # Ensure preceeding hierarchy exists,
        # otherwise writing will fail.
        parent = self.parent
        if not os.path.exists(parent.path):
            os.makedirs(parent.path)

        result = transation.write(self.path, self.data)
        if result is True:
            self.log.debug("Successfully wrote to %s" % self.path)
        
        return result


class Factory:
    @classmethod
    def create(cls, obj):
        """Promote `instance` to template"""
        if isinstance(obj, instance.Folder):
            return Folder(obj)

        if isinstance(obj, instance.Channel):
            return Channel(obj)

        if isinstance(obj, instance.File):
            return File(obj)

        raise ValueError("%r not recognised" % obj)


if __name__ == '__main__':
    cwd = os.getcwd()
    root = os.path.join(cwd, 'test', 'persist')
    
    # New everything
    # folder = Folder(root, parent=None)
    # channel = Channel('chanx.txt', parent=folder)
    # file = File('document.txt', parent=channel)
    # file.setdata('written via python, yet again')
    # file.write()

    # Append to existing
    folder = instance.Folder(root)
    channel = folder.children[0]
    file_instance = channel.children[0]
    
    # convert to template
    folder_template = Folder(folder)
    # folder_template.load(folder)
    # print folder_template.children

    # # repeat it 5 times
    # data = file_instance.read().values()[0]
    # data += "\n" + data

    # file_template.setdata(data)

    # # file_template.write()
