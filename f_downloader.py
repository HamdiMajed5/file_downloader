import requests,re
from datetime import datetime
from contextlib import redirect_stdout
import os.path
from os import path
import json





def get_file(url='',file_path='',log_file=''):
	now=datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
	file_pattern = r'[\w-]+?(?=\.)'
	extension_pattern=r'[^\\]*\.(\w+)'
	file_name=re.findall(file_pattern,url)
	error=0
	if file_name:
		file_name=file_name[-1]
	else:
		file_name='FILE_ERROR'
		error=1
	with open(os.path.join(log_file,f'{file_name}-{now}.log'), 'w') as f_log:
		with redirect_stdout(f_log) as log:	
			if error==1:
				print(f'{now}:Failed getting file name for url:({url})')
				return 0
			full_name= file_name+ '.' + re.findall(extension_pattern,url)[-1]
			log_file=f'{file_name}-{now}.log'
			headers={
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
			'Accept-Language': 'en-US,en;q=0.5',
			'Accept-Encoding': 'gzip, deflate, br',
			'Upgrade-Insecure-Requests': '1',
			'Connection': 'keep-alive',
			'Sec-Fetch-Dest': 'document',
			'Sec-Fetch-Mode': 'navigate',
			'Sec-Fetch-Site': 'none',
			'Sec-Fetch-User': '?1'
			}


			now=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			print (f'{now}:Start getting file {full_name}')
			r = requests.get(url, allow_redirects=True, headers=headers)
			now=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			print (f'{now}:End getting file {full_name}')
			with open(os.path.join(file_path,full_name), 'wb') as f:
				f.write(r.content)
				f.close()
				now=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
				print(f'{now}:File {full_name} donloaded successfully')
			log.close()
		f_log.close()
		




cfg='config.json'



if path.exists(cfg):
	with open(cfg,'r', encoding='utf-8', errors='ignore') as config:
		data = json.load(config,strict=False)
		if not os.path.exists(data['log_path']) :
			os.makedirs(data['log_path'])
			print ("Make log Path directory")
		if not os.path.exists(data['file_path']) :
			os.makedirs(data['file_path'])
			print ("Make file Path directory")
		url_list=data['urls']
		if url_list:
			for url in url_list:
				get_file(url=url,file_path=data['file_path'],log_file=data['log_path'])
				print(url)
		
else :
	with open(cfg,'w') as config:
		txt='{\n \t"file_path":"c:\\\\file_downloader\\\\files",\n\t"log_path":"c:\\\\file_downloader\\\\log",\n\t"urls":["http://datagearbi.com/img/Mazen/logo.png","https://www.facebook.com/favicon.ico"]\n}'
		config.write(txt)
		print('Please Edit config.json file and add your file full URL')
		config.close()
		

	
