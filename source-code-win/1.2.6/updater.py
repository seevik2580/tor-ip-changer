#! /usr/bin/env python
import os
import urllib.request
import subprocess, shutil,time, argparse

parser = argparse.ArgumentParser()  
parser.add_argument("-u", "--update", action='store_true', required=False, help="")
args = parser.parse_args()

version = "1.2.6"

if args.update is False:
    os._exit(1)
    
def download(url=None, write=None):
    
    file_name = url.split('/')[-1]
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )

    u = urllib.request.urlopen(req)
    f = open(file_name, 'wb')
    meta = u.info()
    totalFileSize = int(meta['Content-Length'])
    bufferSize = 9192
    count    = fielSize = 0
    
    while True:
        buffer = u.read(bufferSize)
        if not buffer:
            break
        fielSize += len(buffer)
        f.write(buffer)

    f.close()

try:
    if os.path.exists('ipchanger.rar'):
        SW_HIDE = 0
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = SW_HIDE
        subprocess.Popen(r'taskkill /f /im tor.exe', startupinfo=info)
        subprocess.Popen(r'taskkill /f /im obfs4proxy.exe', startupinfo=info)
        subprocess.Popen(r'taskkill /f /im tail.exe', startupinfo=info)
        subprocess.Popen(r'taskkill /f /im ipchanger.exe', startupinfo=info)
        if not os.path.exists('UnRAR.exe'):
            download("https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/UnRAR.exe")
            time.sleep(1)
        if os.path.exists('Lib'):
            shutil.rmtree('Lib')
        if os.path.exists('Data'):
            shutil.rmtree('Data')
        if os.path.exists('Tor'):
            shutil.rmtree('Tor')            
        if os.path.exists('ipchanger.exe'):
            os.remove('ipchanger.exe')
        if os.path.exists('python34.dll'):
            os.remove('python34.dll')                                    
        if os.path.exists('python37.dll'):
            os.remove('python37.dll')                                    
        os.system('UnRAR.exe x -y ipchanger.rar')
        time.sleep(1)            
        os.remove('UnRAR.exe')
        os.remove('ipchanger.rar')
        subprocess.Popen(r'ipchanger.exe')
except:
    pass