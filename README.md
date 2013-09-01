# OpenMetadata

A cross-platform, hierarchical [Metadata](http://en.wikipedia.org/wiki/Metadata) API for storing and accessing any [format](http://en.wikipedia.org/wiki/File_format) via any [protocol](http://en.wikipedia.org/wiki/Communications_protocol) of unlimited size and complexity. OM is part of the [Pipi](http://pipi.io) project and uses [Python](http://www.python.org) but is in itself language-agnostic and will be expanded upon to later support other languages as well. 

Care to help? Get in [contact](mailto:marcus@pipi.io)

### Example
~~~ python
>>> import openmetadata as om
>>> root = r'c:\folder'
>>> metadata = om.Metadata(parent=root)
>>> channel = om.Channel('new_channel.txt', parent=metadata)
>>> data = om.Data('new_document.txt', parent=channel)
>>> data.set('Hello World')
>>> 
>>> om.write(metadata)

# Created 'c:\folder\.meta'
# Created 'c:\folder\.meta\new_channel.txt'
# Created 'c:\folder\.meta\new_channel.txt\new_document.txt' with 'Hello World'
~~~

### Resources

|                         |                                                   |
|------------------------:|:--------------------------------------------------|
|       **Website**:      | www.pipi.io                                       |
|       **Blog**:         | www.pipi.io/blog                                  |
|       **Facebook**:     | www.facebook.com/pipisoftware                     |
|       **Twitter**:      | www.twitter.com/pipi_io                           |
|       **Development**:  | http://github.com/mottosso/OpenMetadata           |
|

### License

OpenMetadata is Open Source software and licensed under the `MIT License`. You are welcome to change and redistribute it under certain conditions. For more information see the `LICENSE` file.