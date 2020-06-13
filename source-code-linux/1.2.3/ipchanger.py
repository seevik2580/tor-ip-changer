import start, subprocess, os

#vykresleni aplikace
if __name__ == '__main__':
    try:
        mw = start.IpChanger()
        mw.mainloop()
    finally:
        #zabij vse co jsi pustil
        os.system(r'killall tor')
        os.system(r'killall obfs4proxy')
        os.system(r'killall tail')
        os._exit(1)