"""Instances are persistant, readable elements on disk.

Each instance correlates to a template, which provides
the writing mechanisms

"""

import os
import logging
from abc import ABCMeta

from openmetadata import format
from openmetadata import constant

log = logging.getLogger('openmetadata.instance')


class BaseClass:
    """Abc to all instances"""

    __metaclass__ = ABCMeta

    def __init__(self, path):
        assert os.path.exists(path)
        self._path = path

    def __str__(self):
        return str(self.basename)

    def __repr__(self):
        return u"%s.%s(%r)" % (__name__, self.__class__.__name__, self.__str__())

    @property
    def ext(self):
        return ".%s" % self._path.rsplit(".", 1)[-1]

    @property
    def basename(self):
        return os.path.basename(self.path)

    @property
    def path(self):
        return self._path

    @property
    def parent(self):
        """Return parent os `self` as an object"""
        return InstanceFactory.create(os.path.dirname(self.path))

    # def dump(self):
    #     hierarchy = {self: {}}

    #     if not hasattr(self, "children"):
    #         return self

    #     for child in self.children:
    #         print "Putting %r in %r" % (child.dump(), child)
    #         hierarchy[self][child] = child.dump()

    #     return hierarchy

    # def read(self):
    #     """Return hierarchy of files and folders as objects

    #     """

    #     data = {}
    #     for child in self.children:
    #         basename = os.path.basename(child._path)
    #         if not hasattr(child, 'children'):
    #             data[basename] = child.read()
    #         else:
    #             data[basename] = child
    #     return data


class Folder(BaseClass):
    def __init__(self, path):
        super(Folder, self).__init__(path)

    @property
    def path(self):
        """Return meta folder

        Folders are only concerned with what lies within
        the meta folder, anything outside of that is out
        of bounds.

        """
        
        return os.path.join(self._path, constant.Meta)

    @property
    def children(self):
        """Return channels of `self`

        Returns (list) of valid channels

        """
        
        children = []

        for child in os.listdir(self.path):
            fullpath = os.path.join(self.path, child)
            
            # Children can only be channels
            if not os.path.isdir(fullpath):
                basename = os.path.basename(fullpath)
                if not "." in basename:
                    # Channels are those with an extension
                    log.debug("Not including %s in children request" % fullpath)
                    continue

            instance = InstanceFactory.create(fullpath)
            assert isinstance(instance, Channel), "%s not a channel" % fullpath
            children.append(instance)

        return children


class Channel(BaseClass):
    """File and submetadata representation"""

    def __init__(self, path):
        super(Channel, self).__init__(path)

    @property
    def children(self):
        """Return files or metadata hierarchy of `self`

        Returns (list) of valid files and metadata hierarchies.

        """

        children = []

        for item in os.listdir(self._path):
            fullpath = os.path.join(self._path, item)
            
            # Children can only be either 
            # files, other metadata folders.
            if os.path.isdir(fullpath):
                basename = os.path.basename(fullpath)
                if basename != constant.Meta:
                    log.debug("Not including %s in children request" % fullpath)
                    continue

            instance = InstanceFactory.create(fullpath)
            assert isinstance(instance, Folder) or isinstance(instance, File)
            children.append(instance)

        return children


class File(BaseClass):
    """Represents a file on disk"""

    def __init__(self, path):
        super(File, self).__init__(path)

    def read(self):
        """Fetch appropriate reader and output contents of `path`"""

        value = None

        # If it quacks like a duck
        reader =  format.create(self._path)

        try:
            value = reader.read(self._path)
        except AttributeError:
            value = None
        
        return value or self._path


class InstanceFactory:
    @classmethod
    def create(cls, path):
        if os.path.isdir(path):
            basename = os.path.basename(path)
            if not "." in basename:
                return Folder(path)

            if basename == '.meta':
                return Folder(os.path.dirname(path))

            # Return only valid channels (with an extension)
            components = basename.rsplit(".", 1)
            if len(components) > 1:
                return Channel(path)
        else:
            return File(path)

        raise ValueError("What is %s?" % path)


create = InstanceFactory.create


if __name__ == '__main__':
    cwd = os.getcwd()
    root = os.path.join(cwd, 'test', 'persist')
    fold = Folder(root)
    
    for child in fold.children:
        print child
