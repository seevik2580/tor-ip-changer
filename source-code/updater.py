#! /usr/bin/env python
import subprocess, shutil, time, os, tkinter.ttk, tkinter.scrolledtext, _thread, urllib.request, urllib3
from urllib.request import urlopen
from tkinter import *
from pathlib import Path

c = 1

class IpChangerUpdater(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("TOR IP Changer Updater | Created by Seva")
        self.resizable(width = False, height = False)  
        self.frame = Frame(self)
        self.minsize(500,200)
        self.lastver = None
        s = tkinter.ttk.Style()
        s.theme_use("default")
        s.configure("red.Horizontal.TProgressbar", foreground='red', background='red', thickness=1)
        s.configure("orange.Horizontal.TProgressbar", foreground='orange', background='orange', thickness=1)
        s.configure("green.Horizontal.TProgressbar", foreground='green', background='green', thickness=1)
        s.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue', thickness=1)
        self.progressbar = tkinter.ttk.Progressbar(self, orient="horizontal",mode ="determinate", style="green.Horizontal.TProgressbar", length = 500)
        self.progressbar.grid(row=1,column=1,sticky="NEWS")
        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0
        self.output = tkinter.scrolledtext.ScrolledText(self, foreground="green", background="black", highlightcolor="white", highlightbackground="purple", wrap=WORD, width=60)
        self.output.grid(row=2, column=1,sticky="NEWS")
        _thread.start_new_thread(self.init, ())  
        
    def init(self):
        SW_HIDE = 0
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = SW_HIDE
        subprocess.Popen(r'taskkill /f /im tor.exe', startupinfo=info)
        subprocess.Popen(r'taskkill /f /im obfs4proxy.exe', startupinfo=info)
        subprocess.Popen(r'taskkill /f /im tail.exe', startupinfo=info)
        subprocess.Popen(r'taskkill /f /im ipchanger.exe', startupinfo=info)
        http = urllib3.PoolManager()
        f = http.request('GET', 'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/version.txt') 
        self.lastver = f.data.decode('utf-8') 

        try:
            self.changelog()  
        except:
            pass
        try:
            _thread.start_new_thread(self.Update, ())  
        except:
            pass

    def changelog(self):
        http = urllib3.PoolManager()
        r = http.request('GET', 'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/'+self.lastver+'/changelog')
        obsah = r.data.decode('utf-8')
        self.write("%s\n" % obsah,'orange') 

    def write(self, message, color=None):
        if color is None:
            color = "red"
        global c
        name = "line%s" % c
        try:
            self.output.insert(END, message, name)  
        except:
            pass
        self.output.tag_config(name, foreground=color)  
        self.output.see('end') 
        c = c + 1 

    def done(self):
        subprocess.Popen(["ipchanger.exe"],stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        os._exit(1)

    def checkFileSize(self, url=None, write=None, folder=None):
        file_name = url.split('/')[-1]
        self.write("Checking %s\n" % file_name, "orange")
        u = urlopen(url)
        fo = folder
        if folder is None:
            fo = ""
        else:
            fo = "%s/" % folder
        localFile = "%s%s" % (fo,file_name)
        meta = u.info()
        totalUrlFileSize = int(meta['Content-Length'])
        if os.path.exists(localFile):
            totalLocalFileSize = os.stat(localFile).st_size
        else:
            totalLocalFileSize = 0
        if totalUrlFileSize == totalLocalFileSize:
            return True
        else:
            return False
    
    def extract(self):
        proc = subprocess.Popen(["UnRAR.exe", "x", "-y", "ipchanger.rar"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (out, err) = proc.communicate()
        for o in out.decode("utf-8").split('\n'):
            latency = str(o).split('\n')[-1]
            reg = re.compile('\d{1,3}%')
            match = reg.search(latency)
            if (match):
                self.progressbar["value"] = match.group().rstrip("%")
            self.write("%s\n" % o, "green")

    def Update(self):
        try:
            urlipchanger = 'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/%s/ipchanger.rar' % self.lastver
            urlunrar = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/UnRAR.exe"
            if os.path.exists("ipchanger.rar"):
                if self.checkFileSize(urlipchanger) is False:
                    self.download(urlipchanger)
            else:
                self.download(urlipchanger)
            if os.path.exists("UnRAR.exe"):
                if self.checkFileSize(urlunrar) is False:
                    self.download(urlunrar)
            else:
                self.download(urlunrar)
            if os.path.exists('ipchanger.rar'):
                if os.path.exists('UnRAR.exe'):
                    if os.path.exists('Lib'):
                        shutil.rmtree('Lib')
                    if os.path.exists('Data'):
                        shutil.rmtree('Data')
                    if os.path.exists('Tor'):
                        shutil.rmtree('Tor')            
                    if os.path.exists('ipchanger.exe'):
                        os.remove('ipchanger.exe')
                    for p in Path(".").glob("python*.dll"):
                        p.unlink()
                    
                    self.write("Extracting files\n", "green")
                    time.sleep(1)       
                    self.progressbar["value"] = 0
                    self.progressbar['style'] = "green.Horizontal.TProgressbar"
                    self.extract()
                    os.remove('ipchanger.rar')
                    os.remove('UnRAR.exe')
                    
                    self.progressbar["value"] = 100
                    Button(self, text = "Done!", command=self.done, width = 9).grid(row=3,column=1)                    
                    
            else:
                self.write("file ipchanger.rar not found")
                self.progressbar["value"] = 100
                self.progressbar['style'] = "red.Horizontal.TProgressbar"
        except Exception as e:
            self.write("%s\n" % e, "red")
            pass

    def download(self, url=None, write=None, folder=None):
        file_name = url.split('/')[-1]
        try:
            req = urllib.request.Request(
                url, 
                data=None, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                }
            )

            u = urllib.request.urlopen(req)
            fo = folder
            if folder is None:
                fo = ""
            else:
                fo = "%s/" % folder
            
            f = open("%s%s" % (fo,file_name), 'wb')
            meta = u.info()
            totalFileSize = int(meta['Content-Length'])
            if write is None:
                tfs = (totalFileSize/1024)
                self.write("Downloading:  {:<30}{:>13} KB\n".format(file_name, int(round(tfs))), "orange")
                self.progressbar['style'] = "orange.Horizontal.TProgressbar"
                
            bufferSize = 9192
            count    = fielSize = 0
            
            while True:
                buffer = u.read(bufferSize)
                if not buffer:
                    break
            
                fielSize += len(buffer)
                f.write(buffer)
                per = (fielSize * 100 / totalFileSize)
                status = "%3.2f" % per + "" * (int)(per/2)
                if count > 200:
                    count = 0
                    if write is None:
                        self.progressbar['value'] = status
                else:
                    if write is None:
                        self.progressbar['value'] = status
                count += 1
            f.close()
        except Exception as e:
            self.write("%s %s" % (url, e), "red")
            print(e)

if __name__ == '__main__':
    try:
        mw = IpChangerUpdater()
        mw.mainloop()
    finally:
        os._exit(1)
        