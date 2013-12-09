"""Pre- and post-processing of data prior to being input or output

# Overview
    Assume all data is written as plain-text documents. Formatting occurs
    within the plain-text and is interpreted based on the file-extension.

    E.g. ".json" is run through json.loads() whilst a ".txt" is
    run through str()

    Processing occurs before/after data is read/written.


     ------------           -------------          ------------ 
    |    disk    |  ---->  | postprocess | ---->  |   python   |
    |____________|         |_____________|        |____________|


     ------------           -------------          ------------ 
    |   python   |  ---->  |  preprocess | ---->  |    disk    |
    |____________|         |_____________|        |____________|    


# Examples
    When reading a plain-text document, processing means to first cast
    the raw data to a string, str()

    Reading a key/value store, such as Json, processing means running it
    through json.loads() which converts the raw string into a Python dict.

    Reading a Google Drive document, processing means authorising with 
    Google and downloading the document from the internet.


# Writing data
    Open Folder is a file-based database. This means that at the end 
    of each write, a file must get written to disk. Whether it be 
    writing to Shotgun, Google Drive or Streaming data explicitly, a
    record of said operation is always stored on disk.

    When updating a document on Google Drive, it may not be necessary to
    update the link on disk, and thus the disk-writing action may be skipped.

"""

from abc import ABCMeta, abstractmethod
import logging
import json
# from numbers import Number  # Used to map dt to key ext.
# import ConfigParser

log = logging.getLogger('openmetadata.process')


def processoutgoing(raw, format):
    """Process outgoing data"""
    process = mapping.get(format)
    if not process:
        return None

    return process.outgoing(raw)


def processincoming(raw, format):
    """Process incoming data"""
    process = mapping.get(format)
    if not process:
        return None

    return process.incoming(raw)


def cast(raw, format):
    """Cast `raw` to datatype appropriate to `format`"""
    process = mapping.get(format)
    if not process:
        return None

    return process.cast(raw)


class AbstractFormat(object):
    """Required interface to each format"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def outgoing(cls, raw):
        """Process --> Written

        `raw` is interpreted based on the given format and
        may be of any datatype.

        Output is given in an appropriate Python data-structure.

        """

        pass

    @abstractmethod
    def incoming(cls, raw):
        """Process <-- Read"""
        pass

    @abstractmethod
    def cast(cls, raw):
        pass


class DotTxt(AbstractFormat):
    @classmethod
    def outgoing(cls, raw):
        return str(raw or '')

    @classmethod
    def incoming(cls, raw):
        return str(raw)

    @classmethod
    def cast(cls, raw):
        return str(raw)


class DotMdw(DotTxt):
    """Markdown is identical to Txt"""


class DotJson(AbstractFormat):
    @classmethod
    def outgoing(self, raw):
        processed = {}

        try:
            processed = json.dumps(raw, indent=4)
        except ValueError as e:
            log.debug(e)
        except TypeError as e:
            raise TypeError("Data corrupt | %s\n%s" % (raw, e))

        return processed

    @classmethod
    def incoming(self, raw):
        processed = json.loads(raw)
        return processed

    @classmethod
    def cast(self, raw):
        return 


# class DotIni(AbstractFormat):
#     @classmethod
#     def outgoing(self, raw):
#         config = ConfigParser.ConfigParser()
#         config.optionxform = str  # Case-sensitive
#         config.read_string(raw)

#         # Convert to dictionary
#         data = {}
#         for section in config.sections():
#             data[section] = {}
#             for option in config.options(section):
#                 data[section][option] = config.get(section, option)

#         return data

#     @classmethod
#     def incoming(self, raw):
#         pass


# class DotGdoc(AbstractFormat):
#     @classmethod
#     def outgoing(self, raw):
#         raise NotImplementedError

#         # Raw is a Gdoc data-structure
#         link = raw.get('link')

#         # Download document
#         google = gdata.login(usr, pw)
#         document = google.download(link)

#         return document

#     @classmethod
#     def incoming(self, raw):
#         raise NotImplementedError

#         link = raw.get('link')
#         data = raw.get('data')

#         # Upload document
#         google = gdata.login(usr, pw)
#         google.upload(data, link)

#         # Create what will eventually be written to disk.
#         # E.g. {"url": link, "resource_id": "document:1Euj54DtjdkRFd"}
#         gdoc = raw.dump()
        
#         return gdoc



# Cast channel-extension to key-extension
channel_to_file =   {
                        '.kvs': '.json',
                        '.txt': '.txt',
                        '.mdw': '.txt',
                    }


mapping =   {
                '.txt': DotTxt,
                '.mdw': DotMdw,
                '.json': DotJson
                # '.ini': DotIni,
                # '.gdoc': DotGdoc
            }


if __name__ == '__main__':
    import openmetadata as om

    path = r'A:\development\marcus\scripts\python\about\test\.meta\chan4.kvs\properties.json'
    key = om.Key(path)
    key.read()
    print key.path
    print key.exists
    print key.data

    # inputted = {"Key": "Value"}
    # asstring = processoutgoing(inputted, '.json')
    # asdict = processincoming(asstring, '.json')

    # print asstring
    # print asdict
