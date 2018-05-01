import requests
import re
import urllib3

urllib3.disable_warnings()

def get_loginmessage(papaId):
    list=[]
    postdata = {'paperId': papaId, 'queryCollection': 'false'}
    jsondatas = requests.post('https://www.qingsuyun.com/h5/actions/exam/execute/find-collection.json', data=postdata,
                              verify=False).json()

    for jsondata in jsondatas['body']:
        loginmessage = {}
        loginmessage['fieldType'] = jsondata['fieldType']
        loginmessage['fieldName'] = jsondata['fieldName']
        loginmessage['creatorId'] = jsondata['creatorId']
        loginmessage['sortIndex'] = jsondata['sortIndex']
        loginmessage['fieldType'] = jsondata['fieldType']
        loginmessage['.answerContent'] = input('输入%s:' % (loginmessage['fieldName']))
        list.append(loginmessage)
    return list


def get_answerId(messages,papaId):

    postdata = {}
    for i in range(len(messages)):

        pre = 'collections[%d].' % (i)
        for key, value in messages[i].items():
            postdata[pre + key] = value
    postdata['paperId'] = papaId
    postdata['startNow'] = 'true'
    jsondata = requests.post('https://www.qingsuyun.com/h5/actions/exam/execute/create-exam.json', data=postdata,
                             verify=False).json()
    answerId = jsondata['body']['answerId']
    return answerId


def postanswerAndquestion(answerId):
    questiondata = {'answerId': answerId, 'queryItems': 'true'}
    rawquestions = requests.post('https://www.qingsuyun.com/h5/actions/exam/execute/find-exam.json',
                                 data=questiondata, verify=False).json()

    jsonquestions = rawquestions
    jsonquestions = jsonquestions['body']['examItems']
    questionlist = []
    for jsonquestion in jsonquestions:
        temp = []
        postdata={'questionId':jsonquestion['questionId'],
                  'answerId':jsonquestion['answerId']}
        if 'single' in jsonquestion['jsonData']:
            for js in jsonquestion['jsonData']['single']['options']:
                if js['rightAnswers'] == True:
                    postdata['answerContent']=js['sortIndex']


        elif  'multiple' in jsonquestion['jsonData']:
            for js in jsonquestion['jsonData']['multiple']['options']:
                if js['rightAnswers'] == True:
                    temp.append(js['sortIndex'])
            temp=str(temp).replace(' ','').replace('[','').replace(']','')
            postdata['answerContent'] = temp

        elif 'judge' in jsonquestion['jsonData']:
            postdata['answerContent']=str(jsonquestion['jsonData']['judge']['rightAnswers']).lower()


        elif 'vacancy' in jsonquestion['jsonData']:
            for js in jsonquestion['jsonData']['vacancy']['options']:
                try:
                    temp.append(js['rightAnswers'].split('|||')[-1])
                except:
                    temp.append(js['rightAnswers'])
            postdata['answerContent']=str(temp).replace("'",'"')
            print(str(temp).replace("'",'"'))
        requests.post('https://www.qingsuyun.com/h5/actions/exam/execute/submit-answer.json', data=postdata,
                          verify=False)

def end(answerId):
    postdata={"answerId":answerId,'interrupt':'false'}
    requests.post('https://www.qingsuyun.com/h5/actions/exam/execute/finish-exam.json',data=postdata,verify=False)

def get_result(answerId):
    postdata={'answerId':answerId,'queryItems':"false",'queryScoreLevels':'false'}
    jsondata=requests.post('https://www.qingsuyun.com/h5/actions/exam/execute/find-exam.json',data=postdata,verify=False).json()
    return jsondata['body']['answerSheet']['queryCode']
if __name__ == "__main__":

    url = input('输入网址：')
    Ids = re.findall('(\d{1,10})', url, re.S)
    papaId=Ids[2]
    orizationId=Ids[1]
    messages = get_loginmessage(papaId)
    answerId = get_answerId(messages,papaId)
    postanswerAndquestion(answerId)
    end(answerId)
    queryCode=get_result(answerId)
    print('https://www.qingsuyun.com/h5/%s/exam-result/%s/'%(orizationId,queryCode))
