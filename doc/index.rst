Welcome to the Open Metadata documentation
===========================================

Hello. I'm a *simple*, cross-platform, hierarchical `metadata <http://en.wikipedia.org/wiki/Metadata>`_ API for storing and accessing various `formats <http://en.wikipedia.org/wiki/File_format>`_ via quite a few `protocols <http://en.wikipedia.org/wiki/Communications_protocol>`_ of any size and complexity you could think to throw at me. Oh, I'm also open source and `available on GitHub <https://github.com/mottosso/openmetadata>`_ under the `MIT license <http://opensource.org/licenses/MIT>`_.

I'm part of a `larger whole <http://pipi.io>`_. Here are some links.

* Website:      `<www.pipi.io>`_
* Blog:         `<www.pipi.io/blog>`_
* Facebook:     `<www.facebook.com/pipisoftware>`_
* Twitter:      `<www.twitter.com/pipi_io>`_
* Development:  `<github.com/mottosso/OpenMetadata>`_

Care to help? Get `in touch <marcus@pipi.io>`_.

Installation & Hello World
--------------------------
I'm being tested using Python 2.6 and 2.7 under Linux (CentOS) and Windows (7) using `nose <https://pypi.python.org/pypi/nose/1.3.0>`_::

    $ git clone https://github.com/mottosso/openmetadata.git
    $ python openmetadata/test.py

::

    >>> import openmetadata as om
    >>> om.read(r'c:\my_project\my_asset')
    {'broadcast': {'message': 'hello, world'}}

How it works
~~~~~~~~~~~~
Underneath 'my_asset' there is a folder. A special folder which this API writes and reads from. The name of this folder is not relevant (it's '.meta') but it's content are. Each piece of data within this folder corresponds to a "channel" (which are also folders).

A channel is a group. A collection. It contains data of similar types, such as plain text documents, JSON files or images.

That's right. "images". Not "image". That's because a JPEG is an image format, but so is PNG. A channel then may contain a variety of image formats, as long as they all conform to the more universal concept of being an image (a 2-dimensional grid of pixels).

So why are some channels groups of identical formats and some not? Because what matters to you as a programmer is not what file-protocol is being used to store your content. It is the content itself. OpenMetadata does not care about file-protocols, it cares about content. Specifically, about content after it has been read by whatever file-protocol or compression method hosted it.

Discussion & Support
~~~~~~~~~~~~~~~~~~~~~
Whatever is troubling you, we can `talk about it <https://groups.google.com/forum/#!forum/open-metadata>`_. If you want, you can also `report an issue <https://github.com/mottosso/openmetadata/issues>`_.


More
----
I'm `Marcus <uk.linkedin.com/in/marcusottosson/>`_. An animation artist in the VFX industry with an interest in Pipeline development and write Python daily to solve my problems.

Motivation
~~~~~~~~~~
This is my motivation and goal with Open Metadata.

Development Style
~~~~~~~~~~~~~~~~~
This project is being built upon by a proprietary project being developed on the side.

Style Guide for Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PEP-08


API Reference
==============
Care to know a secret?

I am three. We are Metadata, Channel and Data. We live together in hierarchies. Metadata is the parent of Channel and Data is its child.

[uml image here]

The metadata lies hidden in your folders under the name ".meta" and it hosts one or more channels, like this::

    $ \parent_folder\.meta\channel_1
    $ \parent_folder\.meta\channel_2

Channels have a type too. For instance, channels of type ".txt" store plain-text documents while ".img" store images of any format. This separation is for your convenience and designed to be relevant in building graphical interfaces that presents and manipulates this data, such as `About <http://pipi.io/about>`_


The Five Tenets
---------------
I'm built upon a slim specification. In whatever language you use to talk with me, these are some of the things I promise you:
 
1. *The representation, manipulation and storage of metadata is not be tied to that of the content it describes.*
2. *The metadata supports referencing (cross-channel, user, time etc.) as well as many types of data formats, including text, images, video, key/value pairs etc.*
3. *The authoring and publication of metadata is be separable from its consumption.*
4. *The metadata language has reflective abilities. It is be possible, from within the language, to view any metadata itself as content and thus be nested.*
5. *It is be possible to aggregate two or more channels into a single channel or into a channel of channels.*
