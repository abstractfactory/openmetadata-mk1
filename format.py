
"""
Format reads and writes to target.

There are two ways in which data is written. 
    - Explicit
    - Implicit

Explicit
    Here, the data supplied by the user is written to the file* on disk.
    This includes text documents, dictionaries, lists. Essentially any
    datastructure that you could think to fill using any of the natively
    supported Python datastructures.

Implicit
    In this case, the data is somehow referenced and not actually written
    to the file. Instead, the data is written at the referenced target and
    only linked to by the file. This includes database communication,
    internet downloads or streams.


* MetaFile refers to the end-result of any written data. OM is a file-based 
database and this is the means with which it communicates with persistant
storage.

"""

# import os
import json
import logging
import ConfigParser

log = logging.getLogger('openmetadata.format')


class Txt:
    """Plain-text file support"""
    @classmethod
    def read(cls, path):
        data = None
        with open(path, 'r') as file:
            data = file.read()
        return data

    @classmethod
    def write(cls, path, data):
        try:
            with open(path, 'w') as file:
                file.write(data)
            return True
        except:
            return False


class Json:
    """JSON file support"""
    @classmethod
    def read(cls, path):
        data = None
        with open(path, 'r') as file:
            data = json.load(file)
        return data

    @classmethod
    def write(cls, path, data):
        try:
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)
            return True 
        except:
            return False


class Ini:
    """Config file support"""
    @classmethod
    def read(cls, path):
        config = ConfigParser.ConfigParser()
        config.optionxform = str  # Case-sensitive
        config.read(path)

        # Convert to dictionary
        data = {}
        for section in config.sections():
            data[section] = {}
            for option in config.options(section):
                data[section][option] = config.get(section, option)

        return path


class GSheet:
    pass


class GDoc:
    pass


mapping = {'.txt': Txt,
           '.json': Json,
           '.ini': Ini,
           '.gsheet': GSheet,
           '.gdoc': GDoc}

# mapping = {basestring: Txt,
#            dict: Json,
#            list: Json}

class Factory:
    """Read and write is based on Extension, not DataType.

    If based on DataType, for instance dict or basestring,
    since .ini reads as a dict and dict are assigned to Json,
    then reading a .ini will produce a .json once written.

    Being based on Extension guarantees output correlates to
    input, as well as enables multiple extensions to be outputted.

    """

    @classmethod
    def create(cls, ext):
        return mapping.get(ext)


def create(ext):
    return Factory.create(ext)


if __name__ == '__main__':
    path = r'C:\studio\appdata\scripts\python\openmetadata\test\.meta\chan.txt\anotherchannel.txt\document.txt'
    txt = Txt(path)
    print txt.read()