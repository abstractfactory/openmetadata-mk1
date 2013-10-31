![Open Metadata](logo.png) 

A cross-platform, hierarchical metadata API for storage and retrieval of any format of any size and complexity via your file-system. 
Open-source software and [available on GitHub](https://github.com/abstract-factory/openmetadata) under the [MIT license](http://opensource.org/licenses/MIT>).
Contact [Marcus](mailto:marcus@abstractfactory.io>) for more information

**Introduction**

The people behind this project go under the name of [Abstract Factory](http://abstractfactory.io) and Open Metadata is a foundational layer of our software, such as [About](http://abstractfactory.io/about).

**Installation**

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

Tested with Python 2.6 and 2.7 under Linux (CentOS) and Windows (7) and OSX (10.8.5).
To run the tests, you also need [nose](https://pypi.python.org/pypi/nose/1.3.0)

**GUI**

![About](about_logo.png)

[About](http://abstractfactory.io/about) is a Graphical User Interface for Open Metadata. Find our more information about it [here](http://abstractfactory.io/about)
