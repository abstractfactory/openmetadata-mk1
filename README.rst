| Note: This is **alpha** software and is not guaranteed to remain unchanged

Welcome to the Open Folder documentation
===========================================

Hello. I'm a *simple*, cross-platform, hierarchical metadata API for storing and accessing various formats via quite a few protocols of any size and complexity via your file-system. Oh, I'm also open source and `available on GitHub <https://github.com/mottosso/openmetadata>`_ under the `MIT license <http://opensource.org/licenses/MIT>`_.

Care to help? Get `in touch <marcus@pipi.io>`_.

Currently
----------
Making a graphical front-end which will help determine how things are accesses and used. Expect substantial changes to happen during this period.

.. image:: currently.png

Calling for
~~~~~~~~~~~
Review, developers and testers. I've been at this development for quite some time and now I need your help. Being my first open source project, have a look through the code and let me know of anything you find odd or would like to help with. Including how you see the division of modules and code in general being appropriate for distributed work on github.

I'm looking to develop the technique in some more languages. Notably C# and Lua due to myself being involved in the developemnt of film and games and the three languages being the most commonly used. Eventually there will be room for C/C++ and other lower-level languages too. The point is, the techinque is what matters and thus exposing it to as many languages as possble is to be one of the major subjects of development.

Motivation
-----------
I set out developing an efficient way to store, retrieve and otherwise manipulate metadata by researching what was being done currently and found that this wheel is constantly being re-invented. The reason for this I believe lies in the simple fact that the concept of metadata is poorly defined and understood, so lets start out by defining it.

"Data about data"
~~~~~~~~~~~~~~~~~~

Thats right. Thats all it is. Simple right? 

Well, no. What is "data"?

* `Text? <http://media.npr.org/assets/img/2013/06/19/istock_000018865341large-b25b5ec24a67b7c6f1e4cd830f7024f2edda78bc-s6-c30.jpg>`_
* `Binary file-format propertes? <http://i.msdn.microsoft.com/dynimg/IC534518.png>`_
* `Cells in a database? <https://support.shotgunsoftware.com/entries/24806218-query-various-values-names>`_

The definition of "data" in Open Folder is *"anything that is a file"* and thus the definition of metadata becomes *"files about files"*.


This narrows it down a bit, but lets not stop there. Data may be abstract. A collection of pictures can be referred to as a "group" of those pictures. This "group" may also contain metadata. Luckily, abstract content is well defined in any file-system. It is the common folder.

A Common Folder
~~~~~~~~~~~~~~~~~~
OM stores metadata as-is. Rather than converting, re-locating and linking or otherwise simplifying the data about data, OM stores it in a folder just underneath its parent.


Installation & Hello World
--------------------------
I'm being tested using Python 2.6 and 2.7 under Linux (CentOS) and Windows (7) using `nose <https://pypi.python.org/pypi/nose/1.3.0>`_::

    $ git clone https://github.com/mottosso/openmetadata.git
    $ python openmetadata/test.py

::

    >>> import openmetadata as om
    >>> om.read(r'c:\my_project\my_asset')
    {'broadcast': {'message': 'hello, world'}}

	| **Under construction**
	| Note that the following pages are in the process of being written.
	| If you are immediately interested, get in touch via marcus@pipi.io
	| and we'll talk.

How it works
~~~~~~~~~~~~
Underneath 'my_asset' there is a folder. A special folder which this API writes and reads from. The name of this folder is not relevant (it's '.meta') but it's content are. Each piece of data within this folder corresponds to a "channel" (which are also folders).

A channel is a group. A collection. It contains data of similar types, such as plain text documents, JSON files or images.

That's right. "images". Not "image". That's because a JPEG is an image format, but so is PNG. A channel then may contain a variety of image formats, as long as they all conform to the more universal concept of being an image (a 2-dimensional grid of pixels).

So why are some channels groups of identical formats and some not? Because what matters to you as a programmer is not what file-protocol is being used to store your content. It is the content itself. OpenFolder does not care about file-protocols, it cares about content. Specifically, about content after it has been read by whatever file-protocol or compression method hosted it.

More
----
I'm `Marcus <http://uk.linkedin.com/in/marcusottosson/>`_. An animation artist in the VFX industry with an interest in Pipeline development and write Python daily to solve my problems.

Development Style
~~~~~~~~~~~~~~~~~
This project is being built upon by a proprietary project being developed on the side.

Style Guide for Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PEP-08

# Single leading underscore for private members

Good example
 	_private_variable

 Bad example
  	private_variable
  	__private_variable

# Plural for modules

A module containing one or more objects ends with "s"

This is due to singular names being more useful in code, 
e.g. channel.py conflicts with use of channel as a variable.

Reasoning for using singular is when using in code, channel.TextChannel is nicer
than channels.TextChannel as it may seem as though TextChannel is a multple.

Good example
channels.py

Bad example
channel.py


API Reference
==============
Care to know a secret?

I am three. We are Folder, Channel and Data. We live together in hierarchies. Folder is the parent of Channel and Data is its child.

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

Discussion & Support
~~~~~~~~~~~~~~~~~~~~~
Whatever is troubling you, we can `talk about it <https://groups.google.com/forum/#!forum/open-metadata>`_. If you want, you can also `report an issue <https://github.com/mottosso/openmetadata/issues>`_.
