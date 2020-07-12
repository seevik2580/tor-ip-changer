import start, os

#vykresleni aplikace
if __name__ == '__main__':
    try:
        mw = start.Switcher()
        mw.mainloop()
    finally:
        
        os.system("pkill tor.real &")
        os.system("pkill python &")
        