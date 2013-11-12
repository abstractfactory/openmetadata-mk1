"""Main objects of Open Metadata.

Notes
    Physical and Virtual entities are kept within the same objects.

    Why separate them?
        Their hierarchies are completely different. Whilst Templates exists
        in memory, Instances exists on disk. Merging the two would
        require mixing in-memory children and on-disk children.

        However, as opposed to Why not 1, the mixture occurs already.
        When appending to an existing folder, that folder is an instance
        whilst the added channel is a template. The template then has an
        instance as a parent.

        This is unavoidable if we ever expect metadata to be appended to 
        existing metadata.

    Why combine them?
        About uses files and folders irregardless of whether or not they are
        in-memory or on-disk. Thus, their use is transparent of type and so
        can their actual objects be.

"""

from __future__ import absolute_import

import os
import logging
import shutil
import time
from abc import ABCMeta, abstractmethod

from openmetadata import constant
from openmetadata import process

log = logging.getLogger('openmetadata.lib')

VERSION = '0.16.0'


def ishidden(name):
    prefix = "__"
    return (name.startswith(prefix) and name.endswith(prefix))


class AbstractPath(object):
    """Baseclass for anything that lives upon a path of some sort.
    This includes Folders, files but also database locations as they
    also depend on a path of sorts."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, path, parent=None):
        self._path = path
        self._parent = parent

        if parent:
            assert isinstance(parent, AbstractPath)

            # If there is a parent, `path` must be either
            # relative or be a child of parent.
            if os.path.isabs(path):
                if path.startswith(parent.path):
                    # If given path is the absolute path of an
                    # already existing parent, shorten the path
                    # to make it relative to that parent.
                    relativepath = os.path.relpath(path, parent.path)
                    self._path = relativepath
                
                else:
                    log.warning('Disregarding "%s" as child "%s" was not '
                        'part of its path' % (parent.path, path))
                    self._parent = None
    
        if parent:
            parent.addchild(self)

    def __str__(self):
        return str(self.basename)
 
    def __repr__(self):
        return u"%s.%s(%r)" % (__name__, self.__class__.__name__, self.__str__())

    def __eq__(self, other):
        """Let user compare AbstractPath objects with each other as 
        well as regular strings. Comparing with strings is useful
        when comparing with a regular path as a string"""

        if isinstance(other, AbstractPath):
            return other.path == self.path
        return other == self.path

    def __ne__(self, other):
        if isinstance(other, AbstractPath):
            return other.path != self.path
        return other != self.path

    @property
    def name(self):
        """Return name without extension"""
        name = self.basename.rsplit(".", 1)[0]
        
        # Special names (those with double underscores)
        # are returned without their double underscores.
        if ishidden(name):
            name = name[2:-2]

        return name

    @property
    def basename(self):
        return os.path.basename(self.path)

    @property
    def relativepath(self):
        return self._path

    @relativepath.setter
    def relativepath(self, path):
        self._path = path

    def exists(self):
        """Does the resolved path exist?

        Return self.path rather than self._path due to Folder (and possibly
        others) modifying their path prior to returning it.

        The problem being that folder.exists would suggest checking for
        the existance of the parent folder, and not the internal .meta
        folder.

        Same goes for .clear() which also erases .meta, and not folder
        which might be the expected behaviour.

        """
        
        return os.path.exists(self.path)

    def dir(self, tablevel=-1):
        """Depth-first directory listing

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
        """Return full path of `self`, including any parent

        If there is a parent and `self._path` is absolute or contains
        a slash, joining is aborted. As per:

        http://docs.python.org/2/library/os.path.html#os.path.join

        """

        path = self._path
        if self._parent:
            path = os.path.join(self._parent.path, path)

        return path

    @property
    def parent(self):
        if not self._parent:
            if os.path.exists(self.path):
                parent_path = os.path.dirname(self.path)
                return Factory.create(parent_path)
            return None

        return self._parent

    @parent.setter
    def parent(self, parent):
        assert not os.path.exists(self.path), "Can't change the parent of an existing object"
        parent._children.append(self)
        self._parent = parent

    @property
    def extension(self):
        """Return extension of `self.path`

        rsplit is used rather than os.path.splitext due
        to basenames starting with dot returning no extension,
        rather than the last part after the dot as expected

        Returns extension prefixed with "." similarly to how
        os.path.splitext does it.

        E.g.
        >>> ".ext"

        """

        return ".%s" % self.path.rsplit(".", 1)[-1]

    @property
    def ishidden(self):
        """Paths prefixed and suffixed with double underscores are hidden"""

        name = self.basename.rsplit(".", 1)[0]
        return ishidden(name)

    def findparent(self, parent=None):
        """Locate a parent up-stream by name `parent`"""
        if not parent:
            return self.parent

        count = 0
        current_parent = self.parent
        while current_parent.basename != parent:
            if current_parent.basename == constant.Meta:
                self.log.debug(".meta root reached")
                return None

            current_parent = current_parent.parent

            count += 1
            if count > 10:
                return None

        return current_parent

    @property
    def trash(self):
        """Return list of deleted items of `self`"""
        return []

    @property
    def revisions(self):
        """Return list of history of `self`"""
        # 1. Find root .meta folder
        # 2. Find .rev folder
        # 3. Return contents

        return []

    def store(self):
        """Copy `self` into revision-history"""
        # 1. Find root .meta folder
        # 2. Find or create .rev folder
        # 3. Duplicate `self` into .rev folder, under the current date and time

        pass

    def clear(self, max_retries=10):
        """Physically remove `self` and any of its children

        Todo: Store in .trash

        If removing ALL metadata, warn user and recommend
        removing ALL channels rather then the .meta folder
        so as to maintain history of the action.

        """

        if self.exists:
            path = self.path
            retries = 0
            while True:
                dirname = os.path.dirname(path)
                basename = os.path.basename(path)

                deleted_time = time.strftime("%Y%m%d%H%M%S", time.gmtime())
                deleted_basename = ".deleted.%s.%s" % (deleted_time, basename)
                deleted_path = os.path.join(dirname, deleted_basename)
                
                if os.path.exists(deleted_path):
                    try:
                        # If `self` has previously been deleted and stored
                        # as a .deleted copy, remove this old copy permanently.
                        #
                        # Note: .deleted path is unique per-second, so odds of
                        # any entry being removed permanently at all is very small.
                        if os.path.isdir(deleted_path):
                            shutil.rmtree(deleted_path)
                        else:
                            os.remove(deleted_path)

                    except WindowsError as e:
                        # Sometimes, Dropbox can bother this operation;
                        # creating files in the midst of deleting a folder.
                        #
                        # If this happens, try again in a short while.
                        
                        retries += 1
                        if retries > max_retries:
                            log.error("%r.clear() failed with msg: %s" % (self, e))
                            break

                        time.sleep(0.1)
                        log.info("Retired %i time(s) for %s" % (retries, path))

                try:
                    # Store `path` as deleted copy.
                    os.rename(path, deleted_path)
                    break

                except WindowsError as e:
                    raise e


            self.log.info("clear(): Removed %s" % path)
        else:
            self.log.warning("clear(): %r did not exist" % self)


class AbstractParent(AbstractPath):
    """Baseclass to anything that can contain children"""

    __metaclass__ = ABCMeta

    def __init__(self, path, parent=None):
        super(AbstractParent, self).__init__(path, parent)
        self._children = []

    def __iter__(self):
        for child in self.children:
            yield child

    @property
    def children(self):
        """Return children using relative paths

        Each child of `self` is relative to `self.path` and are instanced as such.
        Such that 
            child.path == full path 
            child._path == relative path

        """

        path = self.path
        if os.path.exists(path):
            if os.path.isdir(path):
                for child_path in os.listdir(path):
                    if child_path.startswith(".") or child_path in constant.HiddenFiles or ishidden(child_path):
                        self.log.debug("Skipping hidden folder: '%s'" % os.path.join(path, child_path))
                        continue

                    fullpath = os.path.join(path, child_path)
                    
                    # If the physical child_path on disk already existed
                    # as a logical child of this instance, don't add
                    # it again.
                    if fullpath in [child.path for child in self._children]:
                        self.log.debug("'%r' already virtual, skipping" % child_path)
                        continue

                    obj = Factory.determine(fullpath)
                    if obj:
                        obj(child_path, self)

        return self._children

    def addchild(self, child):
        self._children.append(child)
        child._parent = self

    def removechild(self, child):
        self._children.remove(child)
        child._parent = None


class Folder(AbstractParent):
    log = logging.getLogger('openmetadata.lib.Folder')

    def __init__(self, path, parent=None):
        super(Folder, self).__init__(path, parent)

    @property
    def path(self):
        return os.path.join(super(Folder, self).path, constant.Meta)

    def addchild(self, child):
        self._children.append(child)
        child._parent = self


class Channel(AbstractParent):
    log = logging.getLogger('openmetadata.lib.Channel')

    def __init__(self, path, parent=None):
        super(Channel, self).__init__(path, parent)


class File(AbstractPath):
    log = logging.getLogger('openmetadata.lib.File')
    
    def __init__(self, path, parent=None):
        super(File, self).__init__(path, parent)
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def read(self):
        """`self.path` ==> `self.data`

        Store contents of `self.path` in `self.data`

        Post-requirements
            1. method must not fail.

        """

        if not os.path.exists(self.path):
            return self

        try:
            with open(self.path, 'r') as f:
                raw = f.read()

        except OSError as e:
            self.log.error(e)
            return self
        
        processed = process.postprocess(raw, self.extension)
        self._data = processed

        # Return self to allow for chaining of read() and data
        # e.g. self.read().data == data after being read.
        return self

    def write(self):
        """`self.data` ==> `self.path`

        Store contents of `self.data` in `self.path`

        """

        if not self.parent:
            raise TypeError("No parent set")

        raw = self._data
        processed = process.preprocess(raw, self.extension)

        # Ensure preceeding hierarchy exists,
        # otherwise writing will fail.
        parent = self.parent
        if not os.path.exists(parent.path):
            os.makedirs(parent.path)

        with open(self.path, 'w') as f:
            f.write(processed)

        # Hide .meta folder
        if os.name == 'nt':
            import ctypes

            root = self.findparent('.meta')
            if not ctypes.windll.kernel32.SetFileAttributesW(unicode(root.path), 2):
                self.log.warning("Could not hide .meta folder")
        else:
            self.log.warning("Could not hide .meta folder on this OS: '%s'" % os.name)
        self.log.info("Successfully wrote to %s" % self.path)


class Factory:
    @classmethod
    def determine(cls, path):
        """Return appropriate class based on `path`"""
        if not os.path.exists(path):
            raise OSError('"%s" not found' % path)

        # basename = os.path.basename(path)
        parent = os.path.dirname(path)
        ext = os.path.splitext(path)[1]

        if os.path.isdir(path):
            # Inspect it's children
            children = os.listdir(path)

            if constant.Meta in children:
                # Presence of Metadata folder within `path`
                # makes `path` a Folder object...
                
                if os.path.basename(parent) == constant.Meta:
                    # ..unless its parent is a metadata folder,
                    # then it's a channel that may be treated 
                    # as a folder.
                    if not ext:
                        log.warning('Invalid channel found within metadata folder: %s' % path)
                        return None
                    return Channel

                return Folder

            if os.path.basename(parent) == constant.Meta:
                # Folders within a metadata folder are
                # always channels..

                if not ext:
                    # ..but only channels with an extension are valid
                    log.warning('Invalid channel found within metadata folder: %s' % path)
                    return None
                return Channel
            
            # Blank folders are future metadata containers.
            return Folder

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
                    log.warning('Invalid file found within channel: %s' % path)
                    return None

                return File

        log.warning("Can't figure out '%s'" % path)
        return None
        
        
    @classmethod
    def create(cls, path):
        """Return object based on `path`

        Pre-conditions
            `path` must exist

        Post-conditions
            Output is an object if valid
            Output is None if invalid

        """
        # If path is a .meta directory
        if os.path.basename(path) == constant.Meta:
            path = os.path.dirname(path)
        
        obj = cls.determine(path)
        return obj(path) if obj else None


if __name__ == '__main__':
    cwd = os.getcwd()
    root = os.path.join(cwd, 'test', 'persist')
    
    print Factory.create('c:\users\marcus')
    # Existing folder
    # folder = Factory.determine(root)(root)
    # channel = folder.children[0]
    # file = channel.children[0]
    # file2 = File('temp.txt', channel)
    # file2.data = "Hello World"
    # file2.write()
    # print file.parent.relativepath
    # print channel.parent
    # print folder.children
    # print file.findparent('.ka')
    # for channel in folder:
    #     print channel
    #     for file in channel:
    #         print "\t%s" % file
    
    # Add channel to it
    # channel = Channel('newchannel.txt', folder)
    # file = File('document.txt', channel)
    # file.data = "This is some data"

    # print file.path in channel.children
    # # file.write()
    # channel.clear()
    # file.write()
    # channel.clear()
    # print "Removed %s" % channel.path

    # Make new metadata in empty folder
    # root = os.path.join(cwd, 'test', 'dynamic')
    # folder = Folder(os.path.join(root, 'neeew'))
    # channel = Channel('chan1.txt', folder)
    # file = File('document.txt', channel)

    # file.data = "Some data, woho!"

    # file.write()

    # Edit existing file
    # folder = Folder(root)
    # channel = folder.children[0]
    # file = channel.children[1]
    # file.read()
    # file.data += "\nSome additional data"
    # file.write()
    # print "Written to %s" % file.path
