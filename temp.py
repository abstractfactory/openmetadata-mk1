from __future__ import absolute_import

from abc import abstractmethod, abstractproperty
import os
import json
import ConfigParser

from openmetadata import constant


if __name__ == '__main__':
    chan1 = r'C:\studio\appdata\scripts\python\openmetadata\test\.meta\chan.txt'
    chan2 = r'C:\studio\appdata\scripts\python\openmetadata\test\.meta\chan2.kvs'
    channel1 = Channel(chan1)
    channel2 = Channel(chan2)
    
    model = KvsModel()
    model.setup(channel2)

    view = MockView()
    view.setmodel(model)
    view.read()
