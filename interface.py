
import os
from abc import ABCMeta, abstractmethod


class AbstractTemplate:
    """Abc to all objects in openmetadata"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, path, parent):
        path = path if not parent else os.path.join(str(parent), path)

        # if os.path.isfile(path):
        #     # Make ghost for file
        #     host = os.path.dirname(path)

        self._path = path
        self._parent = parent

    def __str__(self):
        return self.path

    def __repr__(self):
        return u"%s(%r)" % (self.__class__.__name__, self.__str__())

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
        
        output += "-o " + self.name + "\t" + self.path + "\n"

        if hasattr(self, 'children'):
            for child in self._children:
                output += child.dir(tablevel)
        
        tablevel -= 1

        return output

    @property
    def name(self):
        basename = os.path.basename(self._path)
        name, ext = os.path.splitext(basename)
        return name

    @property
    def path(self):
        path = self._path
        if self.parent:
            path = os.path.join(str(self.parent), path)

        # path += self._path
        return path

    @property
    def exists(self):
        return os.path.exists(self._path)

    @property
    def parent(self):
        return self._parent

    def setparent(self, parent):
        parent._children.append(self)
        self._parent = parent

    @abstractmethod
    def dump(self):
        """Return a dict of content"""
        pass

    @abstractmethod
    def load(self, other):
        """Load object with content of identical type from `other`"""
        pass


class AbstractSource(object):
    def __init__(self, path):
        self._path = path

    def __str__(self):
        return str(self._path)

    def __repr__(self):
        return u"%s(%r)" % (self.__class__.__name__, self.__str__())

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __ne__(self, other):
        return repr(self) != repr(other)

    @property
    def path(self):
        return self._path
