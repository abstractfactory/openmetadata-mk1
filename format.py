
import os
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