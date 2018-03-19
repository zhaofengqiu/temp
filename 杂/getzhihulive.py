import requests
import json
import time
import random
import MySQLdb
url='https://api.zhihu.com/lives/homefeed?includes=live&limit=10&offset='
i=10
headers={'Host':'api.zhihu.com',
        'Origin':'https://www.zhihu.com',
        'Referer':'https://www.zhihu.com/lives',
         'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
         }
def getdata(jsurl):
    dic={}
    li=[]
    global can
    print(jsurl)
    r=requests.get(jsurl,headers=headers)
    json_data=json.loads(r.text)
    if json_data["paging"]['is_end']:
        can=False
    for data in json_data['data']:
        dic = {}#在这里要初始化，不然在前面被初始化，不知道为什么会出问题。
        data=data['live']
        dic['subject']=data['subject']
        dic['speakname']=data['speaker']['member']['name']
        dic['speakid']=data['id']
        dic['speaksort']=data['tags'][0]['name']
        li.append(dic)
    return li
def putdb(data_dic):
    global con
    cur = con.cursor()
    content="("+"'"+data_dic['subject']+"','"+data_dic['speakname']+"','"+data_dic['speakid']+"','"+data_dic['speaksort']+"');"
    cmd="insert into zhihulive(speaksubject,speakname,speakid,speaksort) values "+content
    cur.execute(cmd)
    con.commit()
    print(data_dic['speakid'],'insert succeed')
can=True
con=MySQLdb.connect(host='localhost',user='root',password='1234',db='jdgoods',charset="utf8")
#python链接数据库的时候，最后的那个charset要改成utf8因为mysql默认的编码方式不是utf8而且如果字符插入一定要括号括起来。
while can:
    jsurl = url + str(i)
    data_dic_list=getdata(jsurl)
    for data_dic in data_dic_list:
        putdb(data_dic)
    sleep_time=random.randint(0,2)+random.random()
    time.sleep(sleep_time)
    i = i + 10
con.close()
#需要:tag里面的’name‘,'subject',speaker里面的’name'