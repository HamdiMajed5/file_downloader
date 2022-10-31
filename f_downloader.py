import requests, re
from datetime import datetime
from contextlib import redirect_stdout
import os.path
import platform
import json

env = platform.system()
base_path = os.path.dirname(os.path.abspath(__file__))

def get_file(url='', file_path='', log_file=''):
    now = datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
    file_pattern = r'[\w-]+?(?=\.)'
    extension_pattern = r'[^\\]*\.(\w+)'
    file_name = re.findall(file_pattern, url)
    error = 0
    if file_name:
        file_name = file_name[-1]
    else:
        file_name = 'FILE_ERROR'
        error = 1
    with open(os.path.join(log_file, f'{file_name}-{now}.log'), 'w') as f_log:
        with redirect_stdout(f_log) as log:
            if error == 1:
                print(f'{now}:Failed getting file name for url:({url})')
                return 0
            full_name = file_name + '.' + re.findall(extension_pattern, url)[-1]
            log_file = f'{file_name}-{now}.log'
            headers = {
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

            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f'{now}:Start getting file {full_name}')
            r=None
            try:
                r = requests.get(url, allow_redirects=True, headers=headers)
                r.raise_for_status()
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            except requests.exceptions.RequestException as err:
                print(f'{now}:HTTP Error <{url}> Cause:', err)
            except requests.exceptions.HTTPError as errh:
                print(f'{now}:HTTP Error <{url}> Cause:', errh)
            except requests.exceptions.ConnectionError as errc:
                print(f'{now}:HTTP Connection Error<{url}> Cause:', errc)
            except requests.exceptions.Timeout as errt:
                print(f'{now}:HTTP Timeout Error <{url}> Cause:', errt)
            except requests.exceptions.MissingSchema as errm:
                print(f'{now}:HTTP Invalid URL Error <{url}> Cause:', errm)
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f'{now}:End getting file {full_name}')
            if r:
                with open(os.path.join(file_path, full_name), 'wb') as f:
                    f.write(r.content)
                    f.close()
                    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    print(f'{now}:File {full_name} donloaded successfully')
            else:
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                print(f'{now}:File {full_name} Failed to Download')
            log.close()
        f_log.close()


cfg = 'config.json'
def base_log(txt):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    text=(f'{now}: {txt}\n')
    base_log_file=os.path.join(base_path,'log')
    if not os.path.exists(base_log_file):
        os.makedirs(base_log_file)
    f = open(os.path.join(base_log_file,'base_log.log'), 'a')
    f.write(text)
    f.close()



if os.path.exists(cfg):
    with open(cfg, 'r', encoding='utf-8', errors='ignore') as config:
        data={}
        try:
            data = json.load(config, strict=False)
        except json.decoder.JSONDecodeError as jsonerr:  # includes simplejson.decoder.JSONDecodeError
            base_log('Decoding JSON has failed:'+ str(jsonerr))
        log_path=data.get('log_path',os.path.join(base_path,'log'))
        file_path=data.get('file_path',os.path.join(base_path,'files'))
        if not os.path.exists(log_path):
            os.makedirs(log_path)
            base_log("Make log Path directory")
        if not os.path.exists(file_path):
            os.makedirs(file_path)
            base_log("Make file Path directory")
        url_list = data.get('urls',[])
        if url_list:
            for url in url_list:
                base_log(f'Getting:{url}')
                get_file(url=url, file_path=file_path, log_file=log_path)
                base_log(f'Finished Getting:{url}')
        else:
            base_log('URLs list is empty!')
        config.close()
else:
    with open(cfg, 'w') as config:
        if env == 'Linux':
            txt = '{\n \t"file_path":"' + os.path.join(base_path, 'files') + '",\n\t"log_path":"' + os.path.join(
                base_path, 'log') + '",' \
                                    '\n\t"urls":["http://datagearbi.com/img/Mazen/logo.png",' \
                                    '"https://www.facebook.com/favicon.ico"]\n} '
        else:
            txt = '{\n \t"file_path":"c:\\\\file_downloader\\\\files",\n\t"log_path":"c:\\\\file_downloader\\\\log",' \
                  '\n\t"urls":["http://datagearbi.com/img/Mazen/logo.png","https://www.facebook.com/favicon.ico"]\n} '
        config.write(txt)
        print('Please Edit config.json file and add your file full URL')
        base_log('Create/Update config.json file')
        config.close()
