
import os
import logging

from abc import ABCMeta, abstractmethod

log = logging.getLogger('openmetadata.interface')


class AbstractPath:

    __metaclass__ = ABCMeta

    def __init__(self, path):
        self._path = path

    def __str__(self):
        return str(self.basename)

    def __repr__(self):
        return u"%s.%s(%r)" % (__name__, self.__class__.__name__, self.__str__())

    @property
    def ext(self):
        return ".%s" % self.path.rsplit(".", 1)[-1]

    @property
    def basename(self):
        return os.path.basename(self.path)

    def exists(self):
        """Does `self.path` exist?

        Being able to create an Instance object even though
        it may not exist is important due to:

            - A folder isn't looking at the path given, it appends
            .meta first. And thus, asking for if a Folder has metadata
            you will either have to append it first, which means doubling
            of code (both in constructor and before each creation call).

            - An instance could not check 
        
        """
        
        return os.path.exists(self.path)

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

# class Version(object):
#     """Based on API Design for C++ page 244"""
#     def __init__(self, major, minor, patch):
#         self.major = major
#         self.minor = minor
#         self.patch = patch

#     def __str__(self):
#         return "%s.%s.%s" % (self.major, self.minor, self.patch)

#     def __repr__(self):
#         return u"%s(%r)" % (self.__class__.__name__, self.__str__())

#     def isatleast(self, major=int(), minor=int(), patch=int()):
#         raise NotImplementedError

#     def hasfeature(self, name=str()):
#         raise NotImplementedError