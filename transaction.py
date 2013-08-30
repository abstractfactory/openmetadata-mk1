import os
import logging
import shutil

from interface import AbstractTemplate
import template
import constant

log = logging.getLogger('openmetadata.transaction')


def create(root):
	"""Recursively create all metadata under `root`"""

	assert isinstance(root, AbstractTemplate)
	assert root.parent is not None, "%r didn't have a parent" % root
	assert os.path.exists(str(root.parent)), "%r didn't exist" % root.parent

	if root.exists:
		log.warning('"%s" already exists' % root)
		return

	if isinstance(root, template.DataTemplate):
		data = root.dump()
		if os.path.isfile(data):
			src = data
			dst = root.path

			shutil.copy(src, dst)

			print "Copied '%s' to '%s'" % (src, dst)

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
		

def read(channel):
	return {}


def update(channel):
	print "Updating %r" % channel


def delete(channel):
	print "Deleted %r" % channel


# ------------------------------------


def __create_implicit(channel):
	"""Create new channel via references passed as data

	Example
		{'image1': 'c:/image1.jpg'} # 'image1' references data

	..note: implementation detail
	
	"""


def __create_explicit(channel):
	"""Create new channel via contained data

	Example
		{'text1': 'long sentence, not really'} # 'text1' contains data

	..note: implementation detail

	"""

if __name__ == '__main__':
	src = r'S:\research\beast\openmetadata\api\image1.png'
	dst = r'S:\research\beast\openmetadata\api\hardlinked_image1.png'
	# os.link(src, dst)
