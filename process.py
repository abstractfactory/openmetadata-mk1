"""Pre- and post-processing of data prior to being input or output

Inbetween data being either read or written, processing occurs.


     ------------           -------------          ------------ 
    |    disk    |  ---->  |   process   | ---->  |   output   |
    |____________|         |_____________|        |____________|


     ------------           -------------          ------------ 
    |   python   |  ---->  |   process   | ---->  |   output   |
    |____________|         |_____________|        |____________|    


# Examples
    When reading a plain-text document, processing means to first cast
    the raw data to a string, str()

    Reading a key/value store, such as Json, processing means running it
    through json.loads() which converts the raw string into a Python dict.

    Reading a Google Drive document, processing means authorising with 
    Google and downloading the document from the internet.


# Writing data
    Open Metadata is a file-based database. This means that at the end 
    of each write, a file must get written to disk. Whether it be 
    writing to Shotgun, Google Drive or Streaming data explicitly, a
    record of said operation is always stored on disk.

    When updating a document on Google Drive, it may not be necessary to
    update the link on disk, and thus the disk-writing action may be skipped.

"""

from abc import ABCMeta, abstractmethod
import logging
import json

log = logging.getLogger('openmetadata.process')


def postprocess(raw, format):
    """Process incoming data"""
    format = mapping.get(format)
    if not format:
        raise ValueError('Format "%s" not supported' % format)

    return format.post(raw)


def preprocess(raw, format):
    """Process outgoing data"""
    format = mapping.get(format)
    if not format:
        raise ValueError('Format "%s" not supported' % format)

    return format.pre(raw)


class BaseClass(object):
    """Interface for each format"""
    @abstractmethod
    def pre(cls, raw):
        pass

    @abstractmethod
    def post(cls, raw):
        pass


class DotTxt(BaseClass):
    @classmethod
    def pre(self, raw):
        return str(raw)

    @classmethod
    def post(self, raw):
        return str(raw)


class DotJson(BaseClass):
    @classmethod
    def pre(self, raw):
        processed = json.loads(raw)
        return processed

    @classmethod
    def post(self, raw):
        processed = json.dumps(raw)
        return processed


class DotGdoc(BaseClass):
    @classmethod
    def pre(self, raw):
        raise NotImplementedError

        # Raw is a Gdoc data-structure
        link = raw.get('link')

        # Download document
        google = gdata.login(usr, pw)
        document = google.download(link)

        return document

    @classmethod
    def post(self, raw):
        raise NotImplementedError

        link = raw.get('link')
        data = raw.get('data')

        # Upload document
        google = gdata.login(usr, pw)
        google.upload(data, link)

        # Create what will eventually be written to disk.
        # E.g. {"url": link, "resource_id": "document:1Euj54DtjdkRFd"}
        gdoc = raw.dump()
        
        return gdoc


mapping = {'.txt': DotTxt,
           '.json': DotJson,
           '.gdoc': DotGdoc}


if __name__ == '__main__':
    output = "This is a string"
    # print postprocess(output, '.txt')

    inputted = '{"Key": "Value"}'
    print preprocess(inputted, '.json')