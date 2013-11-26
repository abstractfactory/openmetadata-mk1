"""Main objects of Open Metadata

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


def hidden(name):
    prefix = "__"
    return (name.startswith(prefix) and name.endswith(prefix))


class AbstractPath(object):
    """Lowest level Open Metadata entity

    Parameters
        data        -->   :
        data        <--   :
        read()            :
        name        -->   :
        basename    -->

    Variables
        dirty       : (bool) If a channel contains data not yet written

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, path, parent=None):
        self._path = path
        self._parent = parent
        self._dirty = None

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

    def __hash__(self):
        """Used with set()

        Comparing two path objects is the same as comparing two
        absolute paths with each other. 

        Same absolute path == same objects.

        """

        return hash(self.internalpath)

    @property
    def data(self):
        """Read all contained childrens metadata"""

        metadata = {}
        for child in self:
            data = child.data
            if data:
                metadata.update({child.name: child.data})

        return metadata

    @data.setter
    def data(self, data):
        """Slightly more complex

        Interpret `data` and reverse-engineer it into individual
        Channel and File objects. Then, inject `data` into its 
        corresponding object.

        Channel is doing it by first removing any pre-existing
        files under it prior to writing. This would be inefficient
        on a Folder level.

        """

        raise NotImplementedError

    def read(self):
        """Update contents of all contained File objects

        This reads each individual File from disk and updates its
        content. This must be done each time a file on disk is
        changed.

        """

        for child in self:
            child.read()

        self.dirty = None

        return self

    @property
    def name(self):
        """Return name without extension"""
        name = self.basename.rsplit(".", 1)[0]
        
        # Special names (those with double underscores)
        # are returned without their double underscores.
        if hidden(name):
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

    @property
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

    def remove(self, child):
        """Physically remove `child` from disk"""
        if not child in self._children:
            raise ValueError('"%s" not in "%s"' % (child, self.path))

        child.clear()
        self._children.remove(child)

    @property
    def path(self):
        """Return full path of `self`, including any parent

        If there is a parent and `self._path` is absolute or contains
        a slash, joining is aborted. As per:

        http://docs.python.org/2/library/os.path.html#os.path.join

        """

        path = self._path
        parent = self._parent

        if parent:
            """
                When querying a child of Folder, return the full
                path of that child. 
                
                E.g. \folder\.meta\channel1.txt
     
                However, querying the path of Folder returns
                the logical path.
                
                E.g. \folder
                
                This is so that we can ask a Folder for its parent
                and recieve the result we would expect.
                
                E.g. Folder('\parent\of\folder').parent
                = Folder('\parent\of')
                
                As opposed to
                Folder('\parent\of\folder\.meta').parent
                Folder('\parent\of\folder')

            """

            parent_path = parent.internalpath
            path = os.path.join(parent_path, path)

        return path

    @property
    def internalpath(self):
        """Return full path of `self`, including any internal children

        E.g.
            Folder.path == \folder\.meta
            Channel.internalpath == \folder\.meta\channel

        """
        path = self.path
        if isinstance(self, Folder):
            path = os.path.join(path, constant.Meta)
        return path

    @property
    def parent(self):
        if not self._parent:
            if os.path.exists(self.path):
                parent_path = os.path.dirname(self.path)

                # When dirname reaches the highest parent in a hierarchy,
                # it returns `self` as parent. We circumvent this and
                # return None instead.
                if parent_path == self.path:
                    return None

                return Factory.create(parent_path)
            return None

        return self._parent

    @parent.setter
    def parent(self, parent):
        if os.path.exists(self.path):
            raise ValueError("Can't change the parent of an existing object")

        parent._children.append(self)
        self._parent = parent

    @property
    def folder(self):
        """Return first-found parent of type Folder"""
        folder = self

        count = 0
        while not isinstance(folder, Folder):
            folder = folder.parent

            if count > 100:
                raise ValueError("Something's not right. The layout of"
                    " %s is invalid" % self.path)
            count += 1

        return folder

    @property
    def channel(self):
        channel = self

        count = 0
        while not isinstance(channel, Channel):
            channel = channel.parent

            if count > 100:
                raise ValueError("Something's not right. The layout of"
                    " %s is invalid" % self.path)
            count += 1

        return channel

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
    def hidden(self):
        """Paths prefixed and suffixed with double underscores are hidden"""

        name = self.basename.rsplit(".", 1)[0]
        return hidden(name)

    def findparent(self, parent=None):
        raise NotImplementedError

    def findchild(self, child):
        """Locate a child by name"""
        for _child in self:
            if _child.name == child:
                return _child
        return None

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

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, dirty):
        self._dirty = dirty

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
        self._children = set()

    def __iter__(self):
        for child in self.children:
            yield child

    def clear(self):
        super(AbstractParent, self).clear()
        self._children = set()

    def child(self, name):
        """Return individual child"""
        for child in self:
            if child.name == name:
                return child
        return None

    @property
    def children(self):
        """Return children using relative paths

        Each child of `self` is relative to `self.path` and are instanced as such.

        Such that
            child.path == full path
            child._path == relative path

        Note:
            We must perform some needless checks per request due
            to `self` not necessarily being a physical item on disk. 
            It may be an in-memory item, in which case os.path would fail
            to recognise it, yet it may still have children. I.e. other
            in-memory children.

        """

        path = self.internalpath

        if os.path.exists(path):
            if os.path.isdir(path):
                for child_path in os.listdir(path):
                    if child_path.startswith(".") or child_path in constant.HiddenFiles:
                        # self.log.debug("Skipping hidden folder: '%s'" % os.path.join(path, child_path))
                        continue

                    fullpath = os.path.join(path, child_path)
                    
                    # If the physical child_path on disk already existed
                    # as a logical child of this instance, don't add
                    # it again.
                    if fullpath in [child.path for child in self._children]:
                        # self.log.debug("'%r' already virtual, skipping" % child_path)
                        continue

                    obj = Factory.determine(fullpath)
                    if obj:
                        obj(child_path, self)

        return list(self._children)

    def addchild(self, child):
        # If we're adding a child with identical `path`,
        # assume the new child contains newer data than 
        # the current child and chuck the old one away.
        child._parent = self
        self._children.add(child)

    def removechild(self, child):
        self._children.remove(child)
        child._parent = None

    @property
    def hiddenchildren(self):
        """Return only hidden children

        Todo
            Currently, in-memory hidden children are not included.

        """

        path = self.path

        if not os.path.exists(path):
            return
        if not os.path.isdir(path):
            return

        children = []
        for child_path in os.listdir(path):
            child_name, child_ext = os.path.splitext(child_path)
            if hidden(child_name):
                fullpath = os.path.join(path, child_path)

                obj = Factory.determine(fullpath)
                if not obj:
                    continue

                obj = obj(child_path, self)
                children.add(obj)

        return children


class Folder(AbstractParent):
    log = logging.getLogger('openmetadata.lib.Folder')

    def __init__(self, path, parent=None):
        super(Folder, self).__init__(path, parent)

        # TODO
        self._localchildren = set()


class Channel(AbstractParent):
    """Channels store content, a Folder may have one or more channels.

    -- Overview --
    A Channel abstract the need to manually manage Files. When data is
    set, files are generated based on a cannels `format`. When data is read the
    result is always put in a plain dictionary.

    -- Model --
    Open Metadata is based on content as metadata. Content has no fixed
    datatype or file-type, content is less rigid than so. The channel
    then abstracts away specifics and presents the user with a unified
    interface for all content, regardless of type.

    -- Internal --
    Internal file-formats are based on channel-format. Channel formats
    are simplified in that they are meant to capture, not the datatype,
    but the type of content.

    E.g. Images, Video, Key/Value pairs, Plain-text etc.

    Parameters
        data   -->  : (dict) Return data from each child. {'child': Content}
        data   <--  : (dict) Each key represent a child

    """

    log = logging.getLogger('openmetadata.lib.Channel')

    def __init__(self, path, parent=None):
        super(Channel, self).__init__(path, parent)

        # Local files are those added directly
        # to the channel via data.setter
        self._localchildren = set()

    @property
    def data(self):
        # To maintain correlation between setting data
        # and getting data, we store a temporary copy of data
        # within `self` when we set it.
        #
        # If there is any data currently stored, assume it to be
        # the latest

        if self.dirty:
            metadata = {}
            for child in self._localchildren:
                data = child.data
                if data:
                    metadata.update({child.name: child.data})

            return metadata

        data = super(Channel, self).data


        if not data:
            # If data is empty, return with datatype intact
            # E.g. {}, [], '' etc.
            return data

        return data

    @data.setter
    def data(self, data):
        """
        Setting the data on a channel involves separating
        said data into individual files.

        Requirements
            1. Property may set multiple times without writing inbetween. 
                    This is so that front-ends such as About can safely 
                    update a channel without necessarily writing it out 
                    to disk for every update.

        """

        file_extension = process.channel_to_file.get(self.extension)
        if not file_extension:
            self.log.error('Could not determine file format '
                           'for channel "%s"' % self.basename)
            return

        self.dirty = True
        self._localchildren = set()

        assert(isinstance(data, dict))

        for key, value in data.iteritems():
            assert isinstance(key, basestring)
            new_file = File(key + file_extension, self)
            new_file.data = value
            self._localchildren.add(new_file)


    def write(self):
        """Output locally stored files onto disk.

        Writing effectively parents each written file to `self`
        thus acting just as though it had been read(), without
        actually reading any files from disk.

        * This is allowed, since writing guarantees that resulting
        content is identical to written data.

        Note: Writing effectively removes all prior content

        """

        if self.exists:
            self.clear()

        for file in self._localchildren:
            file.write()

        self.dirty = False
        self._localchildren = set()


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
        
        try:
            processed = process.processincoming(raw, self.extension)
        except ValueError as e:
            self.log.error("File empty: %s" % self.path)
            processed = {}
        except TypeError as e:
            self.log.error(e)
            processed = {}

        self._data = processed

        return self

    def write(self):
        """`self.data` ==> `self.path`

        Store contents of `self.data` in `self.path`

        """

        if not self.parent:
            raise TypeError("No parent set")

        raw = self._data
        ext = self.extension
        
        if not ext in process.mapping:
            self.log.error('Extension "%s" not recognised' % ext)
            return None

        processed = process.processoutgoing(raw, ext)
        
        if not processed:
            self.log.error('Could not process "%s"' % self.path)
            return None

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

            root = self.folder
            if not ctypes.windll.kernel32.SetFileAttributesW(unicode(root.internalpath), 2):
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

        parent = os.path.dirname(path)
        ext = os.path.splitext(path)[1]

        if os.path.isdir(path):
            # Inspect it's children
            children = os.listdir(path)

            if constant.Meta in children:
                # Presence of Folder folder within `path`
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
                # Folders within a metafolder are
                # always channels..

                if not ext:
                    # ..but only channels with an extension are valid
                    log.warning('Invalid channel found within metadata folder: %s' % path)
                    return None
                return Channel
            
            # Blank folders are potential metafolders.
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
    def create(cls, path, parent=None):
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
        return obj(path, parent) if obj else None


if __name__ == '__main__':
    cwd = os.getcwd()
    root = os.path.join(cwd, 'test', 'persist')
    # root = r's:\content\jobs\test\content\shots\1000'
    # root = r's:\content\jobs\test'
    folder = Factory.create(root)
    print folder.child('testing')
    # channel = Channel('testing.kvs', folder)
    # print channel.extension
    # channel.data = {u'file1': {u'some data': u'data'}, 'file2': {'some': u'data'}}
    # channel.data = {u'file1': {u'some data': u'data'}, 'file2': {'some': u'data'}}
    # # channel.data = {u'file4': {u'some data': u'data'}, 'file1': {'some': u'data'}}

    # channel.write()
    # channel.read()
    # print channel.data

    # print folder.children[2].read().data