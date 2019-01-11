import os
import re
import json
import time
import urllib3
import urllib
import requests
import content
import configparser
from hashlib import md5
from queue import Queue
urllib3.disable_warnings()
from qzonespider import Qzonespider
user=''
pidsting=''
def get_json(url):

    text=qzoneuer.get(url).text

    return re.findall(r'_preloadCallback\((.*)\)',text,re.S)[0]

def process_jsondata(json_data):
    jsondata=json_data['msglist']
    for data in jsondata:
        if data['tid'] in pidsting:

            continue


        folder=config['PATH']+str(data['created_time'])
        try :

            os.mkdir(folder)

        except:

            pass

        down_conlist(folder, data)

        if data.get('commentlist')!=None:

            down_comments(folder,data['commentlist'])

        if data.get('pic'):#传入的是一个列表

            down_pic_media(folder,data['pic'])
        elif data.get('video'):

            down_video_media(folder,data['video'])


        f = open(config['PATH'] + '/PID.txt', 'a+', encoding='utf-8')
        f.write(data['tid'])
        print('%sdownload succee'%(data['tid']))

def down_comments(folder,jsondata):
    f = open(folder+'/content_and_comment.txt','a+',encoding='utf-8')

    for i in range(len(jsondata)):
        f.write('第 %d 条评论\n创建时间：%s\nreviewer:%s\ncontent:\n%s\n'%(i+1,jsondata[i]['createTime2'],jsondata[i]['name'],jsondata[i]['content']))
        if jsondata[i].get('list_3')!=None:
            f.write('该评论下有%s条讨论:\n\n\n' % (len(jsondata[i].get('list_3'))))
            cnt=1
            for j in jsondata[i].get('list_3'):

                f.write('第%d条讨论创建时间为%s,为\n创建者为%s%s\n\n'%(cnt,j.get('createTime2'),j.get('name'),j.get('content')))
                cnt+=1
        f.write('-----------------------------------------------------------------------------\n')
def down_conlist(folder,jsondata):

    f = open(folder + '/content_and_comment.txt', 'a+', encoding='utf-8')

    f.write('该条说说创建时间为%s\n内容为：\n%s\n'%(jsondata.get("createTime"),jsondata.get("conlist")[0].get("con")))

    f.write('=========================================================================================\n')
def down_pic_media(folder,jsondata):
    for json in jsondata:
        path = folder+'/'+md5(os.urandom(24)).hexdigest()+'.jpg'
        path =re.sub('\*|\!','',path)

        r=requests.get(json['url3'],verify=False)

        f = open(path,'wb+')
        f.write(r.content)
        f.close()

def down_video_media(folder,jsondata):
    for json in jsondata:

        path = folder+'/'+json['video_id']+'.mp4'
        r=requests.get(json['url3'],verify=False)

        f = open(path,'wb+')
        f.write(r.content)
        f.close()
def init():

    global pidsting
    global config

    config = configparser.ConfigParser()
    config.read("config.ini")
    config = config['baseconfig']
    path= config['PATH']
    print(path)
    try:
        os.mkdir(path)
    except:

        pass

    try:
        f=open(path+'PID.txt','r+',encoding='utf-8')
        pidsting=f.read()
        f.close()
    except Exception as ce:
        print(config['PATH']+'PID.txt')
        f=open(path+'PID.txt','w+')
        f.close()
        pidsting=''

if __name__ == '__main__':
    global qzoneuer
    init()
    qzoneuer = Qzonespider('first_spider')

    qzoneuer.login()
    user = qzoneuer.session.cookies.get_dict().get('p_uin')[1:]
    html=qzoneuer.get('https://user.qzone.qq.com/%s' % (user)).text
    qzonetoken=re.findall(r'try{return "(.*?)";}',html,re.S)[0]
    uin=config['DOWNLOADN_ACCOUNT']
    g_tk=content.hashtwo(qzoneuer.session.cookies.get_dict()['p_skey'])
    params={'ftype':'0',
            'sort':'0',
            'uin':uin,
            'g_tk':g_tk,
            'callback':'_preloadCallback',
            'code_version':'1',
            'format':'jsonp',
            'need_private_comment':'1'
            }

    pos=0
    num=10
    while True:
        params['pos'] = pos
        params['num'] = num
        params['replynum'] = 100
        urlparams = content.get_params(params)
        url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6' + urlparams
        html = get_json(url)
        json_data=json.loads(html)
        if json_data.get('msglist') ==None:
            break
        try:
            process_jsondata(json_data)
        except Exception as ce:

            pass

        pos=pos+10
        time.sleep(3)

