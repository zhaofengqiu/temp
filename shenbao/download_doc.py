import requests
if __name__ == '__main__':
    index = 0
    flag=0
    try:
        with open('down.txt','r+',encoding='utf-8') as f:
            ans = f.readlines()
            ans = [int(a.strip() ) for a in ans]
    except Exception as ce:
        print(ce)
        with open('down.txt', 'w+', encoding='utf-8') as f:
            f.write('')
    while True:

        if flag>10:
            break
        print(index)
        if index not in ans:
            try:
                req = requests.get('http://shenbao.ilab-x.com/file?id=%d' % (index), headers={'Range': "bytes=0-1"})
            except:
                index += 1
                continue
            filename_all = req.headers.get('Content-Disposition')

            if filename_all==None :

                print(flag)
                flag+=1
            elif 'doc' in filename_all:
                filename = filename_all .encode(encoding="ISO-8859-1").decode('utf-8',errors='ignore').split('filename=')[-1]
                print(filename)
                req = requests.head('http://shenbao.ilab-x.com/file?id=%d' % (index))
                with open(filename,'wb') as f:
                    f.write(req.content)
            else:
                print(filename_all)
            with open('down.txt', 'a', encoding='utf-8') as f:
               f.write(str(index)+'\n')
        index += 1
