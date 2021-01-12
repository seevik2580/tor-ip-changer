import start, subprocess, os, signal

def ukoncit() :
        os.system(r'killall tor')
        os.system(r'killall tail')
        os._exit(1)


def signal_handler(signal, frame):
        ukoncit()

#vykresleni aplikace
if __name__ == '__main__':
    try:
        mw = start.IpChanger()
        signal.signal(signal.SIGINT, signal_handler)
        mw.mainloop()
    finally:
        #zabij vse co jsi pustil
        ukoncit()