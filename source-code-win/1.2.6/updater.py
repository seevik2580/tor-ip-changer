#! /usr/bin/env python
import subprocess, shutil, time, os

try:
    if os.path.exists('ipchanger.rar'):
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