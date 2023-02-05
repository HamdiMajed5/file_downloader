import requests, re
from datetime import datetime
import os.path
import platform
import json
import sys
import argparse

company='Datagear LLC'
version=1.1

env = platform.system()
base_path = os.path.dirname(os.path.abspath(__file__))
cfg = 'config.json'

def get_file(url='', file_path='', log_file=''):
    now = datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
    file_pattern = r'[\w-]+?(?=\.)'
    extension_pattern = r'[^\\]*\.(\w+)'
    file_name = re.findall(file_pattern, url)
    ext=re.findall(extension_pattern, url)[-1]
    error = 0
    if file_name:
        file_name = file_name[-1]
    else:
        file_name = 'FILE_ERROR'
        error = 1
    with open(os.path.join(log_file, file_name + '-' + str(now) + '.log'), 'w') as f_log:
        if error == 1:
            f_log.write(str(now) + ':Failed getting file name for url:(' + str(url) +')\n')
            return 0
        full_name = file_name + '.' + re.findall(extension_pattern, url)[-1]
        log_file = file_name + '-' + str(now) + '.log'
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
        f_log.write(str(now) + ':Start getting file ' + full_name + '\n')
        r=None
        try:
            r = requests.get(url, allow_redirects=True, headers=headers)
            r.raise_for_status()
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        except requests.exceptions.RequestException as err:
            f_log.write( str(now) + ':HTTP Error <' +url + '> Cause:'+ str( err ) +'\n')
        except requests.exceptions.HTTPError as errh:
            f_log.write(str(now) + ':HTTP Error <' + url + '> Cause:'+ str( errh) + '\n')
        except requests.exceptions.ConnectionError as errc:
            f_log.write(str(now) + ':HTTP Connection Error<' + url +'> Cause:'+ str( errc) +'\n')
        except requests.exceptions.Timeout as errt:
            f_log.write(str(now) + ':HTTP Timeout Error <' + url + '> Cause:'+ str( errt) + '\n')
        except requests.exceptions.MissingSchema as errm:
            f_log.write(str(now) + ':HTTP Invalid URL Error <' + url + '> Cause:'+ str( errm ) + '\n')
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        f_log.write(str(now) + ':End getting file ' + full_name + '\n' )
        if r:
            with open(os.path.join(file_path, full_name), 'wb') as f:
                f.write(r.content)
                f.close()
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                f_log.write(str(now) + ':File ' + full_name + ' downloaded successfully\n')
                if str(ext).upper()=='XLSX':
                    xlsx_to_xls(os.path.join(file_path, full_name))
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                f_log.write(str(now) + ':File ' + full_name + ' converted to xls successfully\n')

        else:
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            f_log.write(str(now) + ':File ' + full_name + ' Failed to Download\n')
        f_log.close()



def base_log(txt):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    text=(str(now) + ':' + txt +'\n')
    base_log_file=os.path.join(base_path,'log')
    if not os.path.exists(base_log_file):
        os.makedirs(base_log_file)
    f = open(os.path.join(base_log_file,'base_log.log'), 'a')
    f.write(text)
    f.close()

def create_dir(path,msg=None):
    if not os.path.exists(path):
        os.makedirs(path)
    if msg:
        base_log(msg)


def no_cli():
    if os.path.exists(cfg):
        with open(cfg, 'r', encoding='utf-8', errors='ignore') as config:
            data={}
            try:
                data = json.load(config, strict=False)
            except json.decoder.JSONDecodeError as jsonerr:  # includes simplejson.decoder.JSONDecodeError
                base_log('Decoding JSON has failed:'+ str(jsonerr))
            log_path=data.get('log_path',os.path.join(base_path,'log'))
            file_path=data.get('file_path',os.path.join(base_path,'files'))
            create_dir(log_path,"Make log Path directory")
            create_dir(file_path,"Make file Path directory")
            url_list = data.get('urls',[])
            if url_list:
                for url in url_list:
                    base_log('Getting:'+ url)
                    get_file(url=url, file_path=file_path, log_file=log_path)
                    base_log('Finished Getting:' +url)
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

def from_cli(args=None):
    data={
        'url':args.url[0] if args.url else None,
        'file_path':args.file[0] if args.file else os.path.join(base_path, 'files') ,
        'log_path':args.log[0] if args.log else os.path.join(base_path, 'log')
    }
    url = data.get('url')
    if url is None:
        base_log('URL is not passed')
        return 0
    log_path = data.get('log_path')
    file_path = data.get('file_path')
    create_dir(log_path, "Make log Path directory")
    create_dir(file_path, "Make file Path directory")
    return get_file(url,file_path,log_path)

def xlsx_to_xls(infile):
    import openpyxl
    #workbook = openpyxl.load_workbook(infile)
    outfile = f"{infile.split('.')[0]}.xls"
    #workbook.save(outfile)
    import pandas as pd

    df = pd.read_excel(infile, header=None)
    df.to_excel(outfile, index=False, header=False)

def main():
    parser = argparse.ArgumentParser(
        prog='File Downloader',
        description=company +' File Downloader Program version:' + str(version) +' by Eng.Hamdi Majed'
    )
    parser.add_argument("-u", "--url",metavar='url', type=str, nargs=1,
                        help="Url to Download the file it is required if you pass arguments.")
    parser.add_argument("-f", "--file", type=str, nargs=1,metavar='file_path',
                        help="Folder path to download file to.")
    parser.add_argument("-l", "--log", type=str, nargs=1,metavar='log_path',
                        help="Logs folder path.")

    args = parser.parse_args()
    try:
        test=sys.argv[1], args
        if test:
            return from_cli(args)
    except IndexError:
        return no_cli()


if __name__ == "__main__":
    # calling the main function
    main()


