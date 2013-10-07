
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
        with open(path, 'w') as file:
            file.write(data)
        return path


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
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
        return path


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


class Factory:
    @classmethod
    def create(cls, path):
        format = os.path.splitext(path)[1]
        return mapping.get(format)


def create(path):
    return Factory.create(path)


if __name__ == '__main__':
    path = r'C:\studio\appdata\scripts\python\openmetadata\test\.meta\chan.txt\anotherchannel.txt\document.txt'
    txt = Txt(path)
    print txt.read()