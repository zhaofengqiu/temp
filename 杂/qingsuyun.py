import requests
import re
import urllib3
urllib3.disable_warnings()
class Question():
    def __init__(self,questionId):
        self.answerContent = ''  # index
        self.qusetionId=questionId
        self.answerId = ''
def get_loginmessage(url):
    global papaId
    list=[]
    papaId=re.findall('(\d{1,10})',url,re.S)[2]
    print(papaId)
    postdata={'paperId':papaId,'queryCollection':'false'}
    jsondatas=requests.post('https://www.qingsuyun.com/h5/actions/exam/execute/find-collection.json',data=postdata,verify=False).json()

    for jsondata in jsondatas['body']:
        loginmessage={}
        loginmessage['fieldType'] = jsondata['fieldType']
        loginmessage['fieldName'] = jsondata['fieldName']
        loginmessage['creatorId'] = jsondata['creatorId']
        loginmessage['sortIndex'] = jsondata['sortIndex']
        loginmessage['fieldType'] = jsondata['fieldType']
        loginmessage['.answerContent']=input('输入%s:'%(loginmessage['fieldName']))
        list.append(loginmessage)
    return list

def get_answerId(messages):
    postdata={}
    for i in range(len(messages)):

        pre='collections[%d].'%(i)
        for key,value in messages[i].items():
            postdata[pre+key]=value
    postdata['paperId']=papaId
    postdata['startNow']='true'
    jsondata=requests.post('https://www.qingsuyun.com/h5/actions/exam/execute/create-exam.json',data=postdata,verify=False).json()
    answerId=jsondata['body']['answerId']
    return answerId

def getanswerAndquestion(answerId):
    questiondata = {'answerId': answerId, 'queryItems': 'true'}
    rawquestions = requests.post('https://www.qingsuyun.com/h5/actions/exam/execute/find-exam.json',
                                  data=questiondata, verify=False).json()

    print(rawquestions)
    jsonquestions = rawquestions
    jsonquestions = jsonquestions['body']['examItems']
    questionlist = []
    for jsonquestion in jsonquestions:
        temp = []
        question = Question(jsonquestion['questionId'])
        question.answerId = jsonquestion['answerId']
        try:
            for js in jsonquestion['jsonData']['single']['options']:
                if js['rightAnswers'] == True:
                    temp.append(js['sortIndex'])
        except:
            for js in jsonquestion['jsonData']['multiple']['options']:
                if js['rightAnswers'] == True:
                    temp.append(js['sortIndex'])
        finally:
            question.answerContent = str(temp).replace('[', '').replace(']', '').replace(' ', '')
            questionlist.append(question)
    print(questionlist)

if __name__=="__main__":
    url='https://www.qingsuyun.com/h5/109998/1805011392/'
    messages=get_loginmessage(url)
    answerId=get_answerId(messages)
    getanswerAndquestion(answerId)
    
    
#现在来不及了，我现在做到了获取到考试数据和答案，等以后有时间了接着做

