import os
import re
import json
import copy
import time
import requests
from io import BytesIO
from PIL import Image
from urllib3 import disable_warnings
import logging
from content import *
disable_warnings()
class Qzonespider():

    def __init__(self,name):
        MyLogger.__init__(self, name)
        self.name=name

        self.session = requests.session()
        self.session.headers.update(REQUEST_HEADER)
        self.cookies=copy.deepcopy(self.session.cookies)

        self.logging=MyLogger(self.name)
    def getQRCode(self):

        qrImg = self.session.get(PT_QR_SHOW
                                .replace('{app_id}', APP_ID)
                                .replace('{time}', str(time.time())),
                                headers=REQUEST_HEADER, verify=False).content
        qury = self.session.cookies.get_dict()['qrsig']
        self.ptqrtoken = hash(qury)
        im = Image.open(BytesIO(qrImg))

        im.save('capture.jpg')
        im.show()
    

    def login(self):
        self.qury=self.getQRCode()

        while True:
            time.sleep(2)
            resp = self.session.get(PT_QR_LOGIN  # 二维码网址
                               .replace('{app_id}', APP_ID)
                               .replace('{ptqrtoken}', str(self.ptqrtoken)),
                                verify=False).text

            res = re.findall(r'ptuiCB(\(.*\))', resp)[0] # 判断二维码的状态有 0 ，65，66这些
            ans = eval(res)
            code=ans[0]
            if code == '66':
                self.logging.info('please scan the QRcode')
            elif code == '67':
                self.logging.info('confirm the submit in phone')
            elif code == '0':

                self.logging.info('login succeed')
                self.session.headers.update(REQUEST_HEADER)
                self.session.get(ans[2],verify=False)

                break
            else:
                self.login()
                break
    def get(self,url):

        return self.session.get(url,verify=False,headers=QZONE_HEADERS)

    def put(self,url,**data):

        return self.session.put(url,data=data)

    def post(self,url,**data):

        return self.session.post(url,data=data)





















