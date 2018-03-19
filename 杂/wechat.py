#coding=utf8
import itchat
from itchat.content import *
import requests
import re
from lxml import etree
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
def chat_robot(text):#字母不能返回
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key': '71f28bf79c820df10d39b4074345ef8c',  # 如果这个Tuling Key不能用，我去找一个
        'info': text,  # 这是我们发出去的消息
        'userid': 'wechat-robot',
    }
    # 我们通过如下命令发送一个post请求，提交给微信聊天机器人
    if re.search(r'百度',text ):
        find=text.split('，')[-1]
        url='https://baike.baidu.com/item/'+find
        r=requests.get(url,headers=headers)
        r.encoding=r.apparent_encoding
        data=etree.HTML(r.text)
        try:
            answer=data.xpath('//div[@class="lemma-summary"]')[0]
            answer=answer.xpath('string(.)')
            return str(answer+url)
        except :
            return '未收入百度百科'
    else:
        r = requests.post(apiUrl, data=data).json()
        return r['text']
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    text=chat_robot(msg['Text'])
    print(msg['Text'])
    print(text)
    print('_____________________________________')
    itchat.send('%s' % text, msg['FromUserName'])
itchat.auto_login(hotReload=True)
itchat.run()


