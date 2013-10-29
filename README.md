![Open Metadata](logo.png) 

Open Metadata is a cross-platform, hierarchical metadata API for storage and retrieval of any format of any size and complexity via your file-system. It is open-source software and [available on GitHub](https://github.com/mottosso/openmetadata) under the [MIT license](http://opensource.org/licenses/MIT>).

[Contact](mailto:marcus@pipi.io>)

# Introduction
The people behind this project go under the name of [Abstract Factory](abstractfactory.io) and Open Metadata is a foundation layer of our software, such as [About](about.pipi.io) - a graphical front-end to Open Metadata.

## Installation
To install, clone the repository into your PYTHONPATH or download it manually.
```bash
$ git clone https://github.com/mottosso/openmetadata.git
$ python openmetadata/test.py
```

In Python, access your metadata via the read() convenience method. It will return a dictionary with each channel as a key and the contained data as its value.
```python
>>> import openmetadata as om
>>> om.read(r'c:\My Project\My Asset')
>>> {'broadcast': {'message': 'hello, world'}}
```

Tested with Python 2.6 and 2.7 under Linux (CentOS) and Windows (7) and OSX (10.8.5)
To run the tests, you also need [nose](https://pypi.python.org/pypi/nose/1.3.0)

# Graphical Front-End
![About](about_logo.png)
End-users may communicate with the metadata using [About](about.pipi.io)
