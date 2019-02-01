import requests
import re
from urllib import parse


def process_url(url, domain=False):
    url = parse.unquote(url, errors="ignore")
    url = re.sub("([\u4e00-\u9fa5]+?)", "0", url)
    return re.sub("[0-9]{1,10000}", '0', url)


def get_list_data_from_request(url_list):
    anslist = []
    noaurilist = []

    for item in url_list:
        if "GET" in item or "POST" in item:
            url = item.split(" ")[1]
            ur = process_url(url,)
            if ur is not None :

                anslist.append(ur)

    return anslist


def get_list_data_from_url(url_list):
    anslist = []
    noaurilist = []
    for item in url_list:
        url = process_url(item)
        if url is not None :
            anslist.append(url)

    return anslist


if __name__ == '__main__':
    url = "https://raw.githubusercontent.com/duoergun0729/1book/master/data/sql-10000.txt"

    filename = url.split("/")[-1]
    newfilename = r'C:\Users\asus\Desktop\test\new_%s' % (filename)
    r=requests.get(url)

    url_list = r.text.split("\n")


    # ur_list = get_list_data_from_request(url_list)
    ur_list = get_list_data_from_url(url_list)
    print(len(ur_list))
    with open(newfilename,'w+',encoding='utf-8') as f:
        for ur in ur_list:
            f.write(ur+'\n')
