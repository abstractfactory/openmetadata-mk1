
import os
import logging

from abc import ABCMeta, abstractmethod

log = logging.getLogger('openmetadata.interface')


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