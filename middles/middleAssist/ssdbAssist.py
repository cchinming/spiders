#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

import ssdb
from settings import SsdbHost

from ssdb import SSDB
class SSDBsession(object):
    def __init__(self):
        self.ssdb = ssdb.SSDB(ssdb_host, ssdb_port)

    def connect(self):
        return self.ssdb

    def __del__(self):
        del self