
import os
from abc import ABCMeta, abstractmethod


class AbstractTemplate:
    """Abc to all objects in openmetadata"""

    __metaclass__ = ABCMeta
    _parentobj = None

    @abstractmethod
    def __init__(self, path, parent):
        path = path if not parent else os.path.join(str(parent), path)

        self._path = path
        self._parent = parent

    def __str__(self):
        return self.path

    def __repr__(self):
        return u"%s(%r)" % (self.__class__.__name__, self.__str__())

    @property
    def version(self):
        return Version(0, 7, 0)

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
        """
        Return basename.

        Post-condition:
            - Output must include extension.

        """

        basename = os.path.basename(self._path)
        
        # ASSERT START
        name, ext = os.path.splitext(basename)
        assert ext
        # ASSERT END

        return basename

    @property
    def path(self):
        """
        Return full path

        Taking parent into account, return the full path
        to self.

        """
        
        path = self._path
        if self.parent:
            path = os.path.join(str(self.parent), path)

        return path

    @property
    def exists(self):
        return os.path.exists(self._path)

    # @property
    # def parent(self):
    #     """
    #     Lazy instantiation of parent

    #     If no parent exists, return None
    #     If parent exists, and isinstance(AbstractTemplate), return parent
    #     If parent exists and isinstance(basestring), convert and return

    #     """
    #     parent = self._parent
    #     if parent:
    #         if not isinstance(parent, AbstractTemplate):
    #             parent = self._parentobj(os.path.dirname(self.path))

    #     return parent

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


class Version(object):
    """Based on API Design for C++ page 244"""
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self):
        return "%s.%s.%s" % (self.major, self.minor, self.patch)

    def __repr__(self):
        return u"%s(%r)" % (self.__class__.__name__, self.__str__())

    def isatleast(self, major=int(), minor=int(), patch=int()):
        raise NotImplementedError

    def hasfeature(self, name=str()):
        raise NotImplementedError