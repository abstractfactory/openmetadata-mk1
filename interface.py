
import os
from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractTemplate:
    """Abstract Baseclass to all objects in Open Metadata"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, path, parent):
        self._path = path if not parent else os.path.join(str(parent), path)
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
        pass

    @abstractmethod
    def load(self, other):
        pass