#encoding:utf-8
import re
from urllib import parse
def process_url(url,domain=False):
	url =  parse.unquote(url,errors="ignore")
	if "?" in url :
		if not domain:
			url = url.split("?",1)[1]
		else:
			url = url.replace("http://localhost:8080/",'')
		return re.sub("[0-9]{1,10000}", '0', url)
	return None
	
def get_list_data_from_request(filename): 
	anslist=[]
	noaurilist=[]
	with open(filename,'r',encoding='utf-8') as f:
		li = f.readlines()
	for item in li:
		if "GET" in item:
			url = item.split(" ")[1]
			ur = process_url(url,True)
			nouri = process_url(url)
			if ur is not None or url is not None:
				anslist.append(ur)
				noaurilist.append(nouri)
	return anslist,noaurilist
  
def get_list_data_from_url(filename):
	anslist=[]
	noaurilist=[]
	with open(filename,'r',encoding='utf-8') as f:
		li = f.readlines()
	for item in li:
		url = process_url(item)
		nouri = process_url(item,True)
		if url is not None or nouri is not None:
				anslist.append(url)
				noaurilist.append(nouri)
	return anslist,noaurilist

if __name__ == '__main__':
	name = "goodqueries.txt"
	filename = r'C:\Users\asus\Desktop\data\%s'%(name)
	newfilename = r'C:\Users\asus\Desktop\data\process\%s'%(name)
	newfilenamenouri = r'C:\Users\asus\Desktop\data\processnouri\%s'%(name)
	# ur_list,nouri_list = get_list_data_from_request(filename) 
	ur_list,nouri_list = get_list_data_from_url(filename)
	with open(newfilename,'w+',encoding='utf-8') as f:
		for ur in ur_list:
			f.write(ur+'\n')
	with open(newfilenamenouri,'w+',encoding='utf-8') as f:
		for ur in nouri_list:
			f.write(ur+'\n')
	print(len(ur_list),len(nouri_list))
