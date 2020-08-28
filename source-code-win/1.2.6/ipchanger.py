import start, subprocess, os

#vykresleni aplikace
if __name__ == '__main__':
    try:
        
        if os.path.exists('updater.exe'):
            os.remove('updater.exe')
        if os.path.exists('libssl-1_1.dll'):
            os.remove('libssl-1_1.dll')
        if os.path.exists('libcrypto-1_1.dll'):
            os.remove('libcrypto-1_1.dll')
        mw = start.IpChanger()
        mw.mainloop()
    finally:
        #os._exit(1)
        #zabij vse co jsi pustil
        SW_HIDE = 0
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = SW_HIDE
        subprocess.Popen(r'taskkill /f /im tor.exe', startupinfo=info)
        subprocess.Popen(r'taskkill /f /im obfs4proxy.exe', startupinfo=info)
        subprocess.Popen(r'taskkill /f /im tail.exe', startupinfo=info)
        os._exit(1)