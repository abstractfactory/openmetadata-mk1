"""Instances are persistant, readable elements on disk.

Each instance correlates to a template, which provides
the writing mechanisms

"""

import os
import logging
from abc import ABCMeta, abstractmethod

from openmetadata import format
from openmetadata import constant
from openmetadata import interface

log = logging.getLogger('openmetadata.instance')


class BaseClass(interface.AbstractPath):
    """Currently, instances contain their full paths, but
    Templates do not. They only contain their relative paths, and are
    assembled upon query"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, path):
        super(BaseClass, self).__init__(path)
        assert os.path.exists(path)

    @property
    def path(self):
        return self._path

    @property
    def ext(self):
        return ".%s" % self.path.rsplit(".", 1)[-1]

    @property
    def parent(self):
        """Return parent os `self` as an object"""
        parent_path = super(BaseClass, self).parent
        return InstanceFactory.create(parent_path)


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

        children = os.listdir(self.path) if os.path.exists(self.path) else []
        while children:
            fullpath = os.path.join(self.path, children.pop())
            instance = InstanceFactory.create(fullpath)
            
            # Builder returns either an object or None.
            # Only yield valid objects.
            if instance:
                yield instance


class Channel(BaseClass):
    """File and submetadata representation"""

    def __init__(self, path):
        super(Channel, self).__init__(path)

    @property
    def children(self):
        """Return files or metadata hierarchy of `self`

        Returns (list) of valid files and metadata hierarchies.

        """

        children = os.listdir(self.path) if os.path.exists(self.path) else []
        while children:
            fullpath = os.path.join(self.path, children.pop())
            instance = InstanceFactory.create(fullpath)
            if instance:
                yield instance


class File(BaseClass):
    """Represents a file on disk"""

    def __init__(self, path):
        super(File, self).__init__(path)

    def read(self):
        """Fetch appropriate reader and output contents of `path`"""

        value = None

        # If it quacks like a duck
        reader =  format.create(ext=self.ext)

        try:
            value = reader.read(self._path)
        except AttributeError:
            value = None
        
        return value or self._path


class InstanceFactory:
    @classmethod
    def create(cls, path):
        if not os.path.exists(path):
            raise OSError('"%s" not found' % path)

        basename = os.path.basename(path)
        parent = os.path.dirname(path)
        ext = os.path.splitext(path)[1]

        # print "\n\tPath: %s" % path
        # print "\tBasename: %s" % basename
        # print "\tParent: %s" % parent
        # print "\tExtension: %s" % ext

        if os.path.isdir(path):
            children = os.listdir(path)
            # print "\tChildren: %s" % children

            if constant.Meta in children:
                # Presence of Metadata folder within `path`
                # makes `path` a Folder object...
                
                if os.path.basename(parent) == constant.Meta:
                    # ..unless its parent is a metadata folder,
                    # then it's a channel that may be treated 
                    # as a folder.
                    if not ext:
                        log.debug('Invalid channel found within metadata folder: %s' % path)
                        return None
                    return Channel(path)

                return Folder(path)

            if os.path.basename(parent) == constant.Meta:
                # Folders within a metadata folder are
                # always channels..

                if not ext:
                    # ..but only channels with an extension are valid
                    log.debug('Invalid channel found within metadata folder: %s' % path)
                    return None
                return Channel(path)
        else:
            # If it isn't a folder, it's a file.
            #
            # Take two steps up, if its a metadata folder
            # then this is a File object.

            possible_channel = os.path.dirname(path)
            possible_metafolder = os.path.dirname(possible_channel)
            if os.path.basename(possible_metafolder) == constant.Meta:
                if not ext:
                    # ..but only channels with an extension are valid
                    log.debug('Invalid file found within channel: %s' % path)
                    return None

                return File(path)

        log.debug('What is "%s"?' % path)
        return None


create = InstanceFactory.create


if __name__ == '__main__':
    cwd = os.getcwd()
    root = os.path.join(cwd, 'test', 'persist')
    fold = Folder(root)
    # print fold.children
    print len(fold.children)
    for child in fold.children:
        print child
