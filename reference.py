import os
import shutil
import ctypes
import logging

from openmetadata import transaction

log = logging.getLogger('openmetadata.reference')


class Hardlink(object):
    def __init__(self, src):
        assert os.path.exists(src)
        self._src = src

    def write(self, dst):
        if os.path.exists(dst):
            transaction.delete(dst)

        parent = os.path.dirname(dst)
        if not os.path.exists(parent):
            os.makedirs(parent)

        src = self._src
        if not ctypes.windll.kernel32.CreateHardLinkA(dst, src, 0): 
            raise OSError("Could not hardlink '%s' to '%s'" % (src, dst))
        
        log.debug("Hardlinked %s to %s" % (src, dst))
        return True


class Copy(object):
    def __init__(self, src):
        assert os.path.exists(src)
        self._src = src

    def write(self, dst):
        if os.path.exists(dst):
            transaction.delete(dst)

        parent = os.path.dirname(dst)
        if not os.path.exists(parent):
            os.makedirs(parent)

        src = self._src
        shutil.copy(src, dst)

        log.debug("Copied %s to %s" % (src, dst))
        return True


if __name__ == '__main__':
    src = r'C:\studio\appdata\scripts\python\openmetadata\test\image1.png'
    dst = r'C:\studio\appdata\scripts\python\openmetadata\test\.meta\image1.png\image1.png'

    l = Hardlink(src)
    # l.write(dst)
