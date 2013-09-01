
import os
import logging
import shutil

from interface import AbstractTemplate
import template

log = logging.getLogger('openmetadata.transaction')


def write(root):
    """Recursively create all metadata under `root`"""

    assert isinstance(root, AbstractTemplate)
    assert root.parent is not None
    assert os.path.exists( str(root.parent) )

    if root.exists:
        log.warning('"%s" already exists' % root)
        return

    if isinstance(root, template.Data):
        data = root.get()

        if isinstance(data, template.Hardlink):
            src = data.path
            dst = root.path

            try:
                hardlink(src, dst)
            except (AttributeError, OSError) as e:
                raise OSError("Could not create hardlink %s\n%s" % (src, e))

            log.debug("Linked '%s' to '%s'" % (src, dst))

        elif isinstance(data, template.Softlink):
            src = data.path
            dst = root.path

            try:
                softlink(src, dst)
            except (AttributeError, OSError) as e:
                raise OSError("Could not create softlink %s\n%s" % (src, e))

            log.debug("Linked '%s' to '%s'" % (src, dst))

        elif isinstance(data, template.Junction):
            src = data.path
            dst = root.path

            try:
                junction(src, dst)
            except (AttributeError, OSError) as e:
                raise OSError("Could not create junction %s\n%s" % (src, e))

            log.debug("Linked '%s' to '%s'" % (src, dst))


        elif isinstance(data, template.Copy):
            src = data.path
            dst = root.path

            try:
                shutil.copy(src, dst)
            except OSError as e:
                raise e

            log.debug("Copied '%s' to '%s'" % (src, dst))


        else:
            with open(root.path, 'w') as f:
                f.write(data)

            log.debug("Wrote %s" % root)
    else:
        os.mkdir(root.path)

        print "Created %s" % root

        # Recursively create children
        for child in root.children:
            write(child)
        

def read(root):
    return template.create(root).dump()


def update(root):
    print "Updating %r" % root


def delete(root):
    assert os.path.exists(root)
    assert os.path.isdir(root)

    __remove = lambda: shutil.rmtree(root)

    try:
        __remove()
    except WindowsError as e:
        # Sometimes, Dropbox can bother this operation,
        # creating files in the midst of deleting a
        # folder.
        #
        # If this happens, try again in a short while.
        import time
        time.sleep(0.1)
        log.debug("Slept before removing %s" % root)

        try:
            __remove()
        except WindowsError as e:
            raise e

    log.debug("Removed %s" % root)


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
