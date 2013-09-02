Welcome to the Open Metadata documentation
===========================================

Hello. I'm a simple, cross-platform, hierarchical `metadata <http://en.wikipedia.org/wiki/Metadata>`_ API for storing and accessing various `formats <http://en.wikipedia.org/wiki/File_format>`_ via quite a few `protocols <http://en.wikipedia.org/wiki/Communications_protocol>`_ of any size and complexity you could think to throw at me. Oh, I'm also open source and `available on GitHub <https://github.com/mottosso/openmetadata>`_ under the MIT license.

Here's something for you.

* Website:      `<www.pipi.io>`_
* Blog:         `<www.pipi.io/blog>`_
* Facebook:     `<www.facebook.com/pipisoftware>`_
* Twitter:      `<www.twitter.com/pipi_io>`_
* Development:  `<github.com/mottosso/OpenMetadata>`_

Installation
=============
I run great using Python 2.6 and 2.7 under Linux (CentOS) and Windows (7). I'd also like `nose <https://pypi.python.org/pypi/nose/1.3.0>`_ for my tests::

    $ git clone https://github.com/mottosso/openmetadata.git
    $ ./openmetadata/test.py


Hello, World
============

    >>> import openmetadata as om
    >>> root = r'c:\folder'
    >>> metadata = om.Metadata(parent=root)
    >>> channel = om.Channel('new_channel.txt', parent=metadata)
    >>> data = om.Data('new_document.txt', parent=channel)
    >>> data.set('Hello World')
    >>> om.write(metadata)
    # Created 'c:\folder\.meta'
    # Created 'c:\folder\.meta\new_channel.txt'
    # Created 'c:\folder\.meta\new_channel.txt\new_document.txt' with 'Hello World'


The Five Tenets
================
I'm built upon a slim specification. In whatever language you use to talk with me, these are some of the things I promise you:
 
1. *The representation, manipulation and storage of metadata should not be tied to that of the content it describes.*
2. *The metadata support referencing (cross-channel, user, time etc.) as well as many types of data formats, including text, images, video, key/value pairs etc.*
3. *The authoring and publication of metadata should be separable from its consumption.*
4. *The metadata language should have reflective abilities. It should be possible, from within the language, to view metadata itself as content and thus be combined into hierarchies.*
5. *It should be possible to aggregate two or more channels into a single channel or into a channel of channels.*


Discussion and Support
======================
Whatever is troubling you, we can `talk about it <https://groups.google.com/forum/#!forum/open-metadata>`_. If you want, you can also report anything you find odd `here <https://github.com/mottosso/openmetadata/issues>`_.

When you're ready to take a leap of faith, just know that I'm available under the `MIT License <http://opensource.org/licenses/MIT>`_.