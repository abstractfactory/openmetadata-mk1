![Open Metadata](logo.png) 

*Note: This is **alpha** software and is not guaranteed to remain unchanged*

Open Metadata is a cross-platform, hierarchical metadata API for storage and retrieval of any format of any size and complexity via your file-system. It is open-source software and [available on GitHub](https://github.com/mottosso/openmetadata) under the [MIT license](http://opensource.org/licenses/MIT>).

[Contact](mailto:marcus@pipi.io>)

# Introduction
The people behind this project go under the name of [Abstract Factory](abstractfactory.io) and Open Metadata is a layer of [About](about.pipi.io), a graphical front-end to Open Metadata which in turn is a component of [Pipi](pipi.io), a Digital Content Creation Platform for feature film and commercial visual effects production.

## Installation
Tested with Python 2.6 and 2.7 under Linux (CentOS) and Windows (7) and OSX (10.8.5) using [nose](https://pypi.python.org/pypi/nose/1.3.0)

> git clone https://github.com/mottosso/openmetadata.git
> python openmetadata/test.py
>
> import openmetadata as om
> om.read(r'c:\My Project\My Asset')
> {'broadcast': {'message': 'hello, world'}}