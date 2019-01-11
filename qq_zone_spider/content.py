import os
import logging


USER_DETAIL='https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/user/cgi_userinfo_get_all'
PT_QR_SHOW = "https://ssl.ptlogin2.qq.com/ptqrshow?appid={app_id}&e=2&l=M&s=3&d=72&v=4&daid=5&t={time}"
PT_QR_LOGIN = "https://ssl.ptlogin2.qq.com/ptqrlogin?aid={app_id}&ptqrtoken={ptqrtoken}&u1=https://qzs.qzone.qq.com/qzone/v5/loginsucc.html?para=izone&from_ui=1&pt_uistyle=40"
REQUEST_HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',

}
APP_ID = "549000912"
QZONE_HEADERS={

    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Referer': 'https://qzone.qq.com/',
    'Host': 'user.qzone.qq.com'
}



class MyLogger(logging.Logger):
    def __init__(self, spidername,filename='spider.log'):
        # super(MyLogger, self).__init__(filename)
        logging.Logger.__init__(self, filename)

        # 设置日志格式
        fmtHandler = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)s][%(levelname)s] {} %(message)s'.format(spidername))

        # 设置log文件
        try:
            os.makedirs(os.path.dirname(filename))
        except :
            pass
        try:
            consoleHd = logging.StreamHandler()
            consoleHd.setLevel(logging.ERROR)
            consoleHd.setFormatter(fmtHandler)

            fileHd = logging.FileHandler(filename)
            fileHd.setLevel(logging.INFO)
            fileHd.setFormatter(fmtHandler)
            self.addHandler(fileHd)
            self.addHandler(consoleHd)
        except :
            pass

        return
        # 设置回滚日志,每个日志最大10M,最多备份5个日志
        try:
            rtfHandler = logging.BaseRotatingHandler(
                filename, maxBytes=10 * 1024 * 1024, backupCount=5)
        except Exception as reason:
            self.error("%s" % reason)
        else:
            self.addHandler(rtfHandler)



def hash(qusy):

    hash = 0

    for code in qusy:
        hash  =hash + (hash  << 5) +  ord(code)

    return str(0x7fffffff & hash)


def hashtwo(p_skey):
    hashes = 5381

    for letter in p_skey:
        hashes += (hashes << 5) + ord(letter)
    return str(hashes & 0x7fffffff)
def get_params(kwargs):
    params=''
    flag=0
    for key , value in kwargs.items():
        key=str(key)
        value=str(value)
        if flag==0:
            params = params + '?' + key + '=' + value
            flag+=1
        else:
            params = params + '&' + key + '=' + value

    return params
