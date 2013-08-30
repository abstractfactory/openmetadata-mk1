import os
import logging
import shutil

from interface import AbstractTemplate
import template
# import constant

log = logging.getLogger('openmetadata.transaction')


def create(root):
    """Recursively create all metadata under `root`"""

    assert isinstance(root, AbstractTemplate)
    assert root.parent is not None
    assert os.path.exists( str(root.parent) )

    if root.exists:
        log.warning('"%s" already exists' % root)
        return

    if isinstance(root, template.DataTemplate):
        data = root.data

        if isinstance(data, template.Link):
            src = data.path
            dst = root.path

            try:
                hardlink(src, dst)
            except OSError:
                softlink(src, dst)
            except OSError:
                raise OSError("Could not link %s" % src)

            log.info("Linked '%s' to '%s'" % (src, dst))

        elif isinstance(data, template.Copy):
            src = data.path
            dst = root.path

            try:
                shutil.copy(src, dst)
            except OSError as e:
                raise e

            log.info("Copied '%s' to '%s'" % (src, dst))

        else:
            with open(root.path, 'w') as f:
                f.write(data)

            print "Wrote %s" % root
    else:
        os.mkdir(root.path)

        print "Created %s" % root

        # Recursively create children
        for child in root.children:
            create(child)
        

def read(root):
    return {}


def update(channel):
    print "Updating %r" % channel


def delete(channel):
    print "Deleted %r" % channel


# ------------------------------------


def hardlink(src, dst):
    import ctypes
    if not ctypes.windll.kernel32.CreateHardLinkA(dst, src, 0): 
        raise OSError("Could not hardlink '%s' to '%s'" % (src, dst))


def softlink(src, dst):
    return


def junction(src, dst):
    return


if __name__ == '__main__':
    src = r'S:\research\beast\openmetadata\api\image1.png'
    dst = r'S:\research\beast\openmetadata\api\hardlinked_image1.png'
    # os.link(src, dst)
