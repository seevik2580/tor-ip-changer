import start, subprocess, os

#vykresleni aplikace
if __name__ == '__main__':
    try:
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