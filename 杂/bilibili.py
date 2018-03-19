import requests
import json
import requests
import json
from lxml import etree
from bs4 import BeautifulSoup
import time
import random
from threading import Thread
from collections import deque
from lxml import etree
from changeIP import Adsl
A=Adsl()
a=10
user=['Mozilla/5.0(Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
      'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
      'Opera/9.80(Macintosh;IntelMacOSX10.6.8;U;en)Presto/2.8.131Version/11.11',
      'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11',
      'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11',
      'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)',
      'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)',
      'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TheWorld)',
      'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)',
      'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)',
      'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;AvantBrowser)',
      'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)',
      'Mozilla/5.0(BlackBerry;U;BlackBerry9800;en)AppleWebKit/534.1+(KHTML,likeGecko)Version/6.0.0.337MobileSafari/534.1+',
      'Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)']
class myipProcess(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        while True:
            pass
def getusermsg(i,index=0):
    dic={}
    if index==0:
        try:
            data = {'mid': '{:}'.format(i), '_': '1492863092419', 'csrf': ''}
            msgurl = 'http://space.bilibili.com/ajax/member/GetInfo'
            json_data =getjson(url=msgurl,data=data,index=1)
            dic['mid']=json_data['mid']
            dic['name']=json_data['name']
            dic['sex']=json_data['sex']
            dic['regtime'] = json_data['regtime']
            dic['sign'] = json_data['sign']
            dic['birthday'] = json_data['birthday']
            dic['place'] = json_data['place']
            dic['level'] = json_data['level_info']['current_level']
            dic['vip']=json_data['vip']['vipStatus']
            '''ds = getusermsg(i, index=1)
            for key, value in ds.items():
                dic[key] = value
                '''
        except Exception as ce:
            print(ce)
    else:
        msgurl = 'http://api.bilibili.com/x/relation/stat?vmid=%d&jsonp=jsonp' % (i)
        json_data = getjson(url=msgurl,index=2)
        dic['following'] = json_data['follower']
        dic['follower'] = json_data['follower']
    return dic
def getjson(**kw):
    global i,proxy
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Host': 'space.bilibili.com',
        'Origin': 'http://space.bilibili.com',
        'Referer': 'http://space.bilibili.com/%s/'%(str(i)),
        'User-Agent':random.choice(user),
        'X-Requested-With': 'XMLHttpRequest'
    }
    if len(kw)==2:
        r=requests.get(kw['url'],headers={'User-Agent':random.choice(user)})
    else:
        r = requests.post(kw['url'],headers=headers,data=kw['data'])
    if kw['index']==1:
        if not r.json()['status']:
            i+=1
            getusermsg(i)
    return r.json()['data']
def input(sql):
    pass
def get():
    msgdic = getusermsg(i)
    if not msgdic:
        A.reconnect()
        msgdic = getusermsg(i)
    print(msgdic)
if __name__=='__main__':
    process=myipProcess()
    process.start()
    msgdic={}
    for i in range(1,290000000):
        msgdic=getusermsg(i)
        if not msgdic:
            A.reconnect()
            msgdic = getusermsg(i)
#这个可以鉴借的是那个up主的个人信息都是存在一个网址，通过post数据得到相应的data
#还有各种api