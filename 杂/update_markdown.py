import requests
import re

dir_path=r'C:/Users/asus/Desktop/network_secrity/'
def get_old_md(filename):
    with open(filename,'r',encoding='utf-8') as f:
        ans = f.readlines()
    return ans
def update_md(filename,markdown_data):
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(markdown_data)
def update_img(path_file):
    f1 = open(path_file, 'rb')
    filename = path_file.split('/')[-1]
    files = {'file': (filename, f1, 'image/png', {})}

    r =requests.post('https://lisenh.myds.me:8/file/upload.php',files=files)
    f1.close()
    return 'https://lisenh.myds.me:8/file/'+ r.json()['url']


if __name__ == '__main__':
    markdown_file = r'C:\Users\asus\Desktop\network_secrity\密码学.md'
    markdown_data=get_old_md(markdown_file)
    for index,md in enumerate(markdown_data):
        ans = re.findall('<img *src="(.*?)"|\[image.png\]\((.*?png|jpeg)\)',md)
        if len(ans) !=0:
            ans = ans[0]
            ab_path = ''.join(ans)
            path_file=dir_path+ab_path
            url = update_img(path_file)
            print(url)
            markdown_data[index] = re.sub('pictures.*(png|grep)',url,md)
    update_md(markdown_file,markdown_data)

