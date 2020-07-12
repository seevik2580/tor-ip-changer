#! /usr/bin/env python
#import vsech potrebnych modulu
import random, telnetlib, thread, threading, time, ScrolledText, socks, sockshandler, win_inet_pton, socket, re, urllib2, logging, base64, os, subprocess, sys, pycurl, cStringIO, webbrowser
from Tkinter import *
from time import gmtime, strftime
from timeit import default_timer as timer
from threading import Thread
#import _winreg as winreg
#from map import *

#verze programku
version = '1.0.0'
c = 1 

#trida tkinter
class Switcher(Tk):

#definice rozhrani aplikace
    def __init__(self):
        
        Tk.__init__(self)
        self.minsize(474,400)
        self.maxsize(474,400)
        global start
        title = base64.b64decode('VE9SIElQIGNoYW5nZXIgfCBDcmVhdGVkIGJ5IFNldmEgfCB2')
        self.title(string = title + version)
        self.host = StringVar()
        self.port = IntVar()
        self.passwd = StringVar()
        self.time = DoubleVar()
        self.timeout = DoubleVar()
        self.host.set('127.0.0.1')
        self.port.set('9051')
        self.passwd.set('')
        self.time.set('10')
        self.timeout.set('5')
        logchanger = "ipchanger.log"
        logging.basicConfig(filename=logchanger,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        Label(self, text = 'Interval:').grid(row = 1, column = 5)
        Entry(self, textvariable = self.time, width = 5).grid(row = 1, column = 6)
        self.buttonstart = Button(self, text = 'Change IP', command = self.start, state=DISABLED)
        self.buttonstart.grid(row = 1, column = 2)
        self.buttonstop = Button(self, text = 'Stop', command = self.stop, state=DISABLED)
        self.buttonstop.grid(row = 1, column = 3)
        self.buttonlog = Button(self, text = 'Show log', command = self.showlog, state=NORMAL, width = 8)
        self.buttonlog.grid(row = 1, column = 7)
        Button(self, text = 'Clear', command = self.clean, height = 1).grid(row = 1, column = 4)
        self.output = ScrolledText.ScrolledText(self, foreground="green", background="black", highlightcolor="white", wrap=WORD, width = 64)
        self.output.grid(row = 2, column = 1, columnspan = 7)
        text = "Changelog: v" + version + "\n"
        text += "Released:   TOR IP changer for Mac OS X \n"
        self.write(text, "orange", 0)
        self.write("Send logs: ", "orange", 0)
        self.write("toripchanger@gmail.com\n\n", "yellow", 0)
        self.buttonstarttor = Button(self, text = 'Start TOR', command = self.starttor, width = 8)
        self.buttonstoptor = Button(self, text = 'Stop TOR', command = self.stoptor, width = 8)
        self.write("Thank you for using TOR IP changer\n", "white", 0)
        thread.start_new_thread(self.startthings, ())  
    
    def showlog(self):
        self.buttonlog['text'] = 'Hide log'
        self.buttonlog['command'] = self.hidelog
        thread.start_new_thread(self.tail, ())
    def tail(self):
        os.system("open -F /Applications/Utilities/Console.app ipchanger.log &")
    
    def hidelog(self):
        thread.start_new_thread(self.killlog, ())
        
    def killlog(self):
        self.buttonlog['text'] = 'Show log'
        self.buttonlog['command'] = self.showlog
        os.system("killall -9 Console & echo 1")
        
        
    def simpleip(self):
        file = "ip.txt"
        with open(file, 'r') as r:
          result = r.readlines()
          msLine = result[-1].strip()
          latency = msLine.split('[')[-1]
          reg = re.compile('\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}')
          match = reg.search(latency)
          return match.group()
          r.close()
    
#funkce na start updatu        

    def startthings(self):
        self.buttonstarttor = Button(self, text = 'Start TOR', command = self.starttor, width = 8)
        self.buttonstarttor.grid(row = 1, column = 1) 
        thread.start_new_thread(self.update, ())
       
        
        
#funkce na ovladani tora
    def starttor(self):
        self.write("TOR server starting. \n", "green", 1)
        thread.start_new_thread(self.tor, ())
        self.buttonstarttor.destroy()
        self.buttonstoptor = Button(self, text = 'Starting', command = self.stoptor, width = 8)
        self.buttonstoptor.grid(row = 1, column = 1)
        
        
        
        
    def stoptor(self):
        self.buttonstoptor.destroy()
        self.buttonstarttor = Button(self, text = 'Start TOR', command = self.starttor, width = 8)
        self.buttonstarttor.grid(row = 1, column = 1)
        self.buttonstop['state'] = 'disabled'
        self.buttonstart['state'] = 'disabled'
        os.system("pkill tor.real &")
        self.write("TOR server stopped. \n", "error", 1)   
        self.ident = random.random()
        
    def tor(self):
        file = "tor.txt"
        
        os.system("./tor.real -f torrc > %s &" %file)
        print "neco"
        timeout = 0
        while not timeout==60:
            time.sleep(1)
            timeout = timeout + 1
            with open(file, 'r+') as f:
           
            
                result = f.readlines(50)
                msLine = result[-1].strip()
                latency = msLine.split(' Bootstrap ')[-1]
                reg = re.compile('\d{1,3}%')
                match = reg.search(latency)
                if (match):
                    boot = match.group()
                    logging.info(boot)
                    self.buttonstoptor = Button(self, text = boot, command = self.stoptor, width = 8)
                    self.buttonstoptor.grid(row = 1, column = 1) 
                    if match.group() == "100%":
                        self.write("TOR server started.\n", "green", 1) 
                        self.buttonstart['state'] = 'normal'
                        self.buttonstoptor = Button(self, text = 'Stop TOR', command = self.stoptor, width = 8)
                        self.buttonstoptor.grid(row = 1, column = 1) 
                        
                        break          
                else:
                    pass
                
                f.close() 
        else:                 
            self.write("TOR server timed out.\n", "error", 1) 
            time.sleep(.1)
            self.stoptor()                
           
        
#funkce na vycisteni vystupu
    def clean(self):
        self.output.delete('1.0', END)
        
#funkce updatu
    def update(self):
        while 1==1:
            self.write("Checking internet connection. \n", "white", 1)
            time.sleep(1)
            ping = os.popen('ping -c 1 www.google.com')
            result = ping.readlines()
            msLine = result[-1].strip()
            latency = msLine.split(' = ')[-1] 
            reg = re.compile('\d{1,3}')
            match = reg.search(latency)
            if not match:
                self.write("No internet connection detected. \n", "error", 1) 
                time.sleep(60)
                match = reg.search(latency)
            else:
                self.write("Internet connection detected. \n", "green", 1)
                self.write('This version:            ' +version+ "\n", "white", 1)
                lastverurl = urllib2.urlopen('https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/mac/version.txt')
                lastver = lastverurl.read()
                lastverurl.close()
                linkurl = urllib2.urlopen('https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/mac/dist/'+lastver+'/dist.txt')
                link = linkurl.read()
                self.write('Last available version:  %s\n' % lastver, "white", 1)
                if version >= lastver:
                    self.write('No update required. \n', "white", 1)
                else:
                    self.write('Update required ! \nDownload: ', "white", 1)
                    def openHLink(event): 
                        start, end = t.tag_prevrange("hlink", t.index("@%s,%s" % (event.x, event.y))) 
                        webbrowser.open(t.get(start, end)) 
                    
                    t = self.output
                    t.tag_prevrange("hlink", link) 
                    t.tag_configure("hlink", foreground='blue', underline=1) 
                    t.tag_bind("hlink", "<Button-1>", openHLink) 
                    t.insert(END, link, "hlink") 
                    t.insert(END, "\n")
                break     
                
        
#funkce startu zmeny IP
    def start(self):
        self.start = timer()
        self.write('TOR switcher starting.\n', "green", 1) 
        self.ident = random.random()
        t = Thread(target = self.startnewnym)                                                                                                           
        t.start()
        time.sleep(.1)
        t = Thread(target = self.ip)                                                                                                           
        t.start()
        self.buttonstop['state'] = 'normal'
        self.buttonstart['state'] = 'disabled'
        
#funkce zastaveni zmeny IP
    def stop(self): 
        self.write('TOR switcher stopping.\n', "error", 1)
        self.write('Fetching IP stopping.\n', "error", 1)
        self.ident = random.random() 
             
#funkce na psani vystupu   
    def write(self, message, color, log):
        global c
        name = "line%s" % c
        if color == "error":
            color = "red"
        try:
            self.output.insert(END, message, name)  
        except:
            pass
        if log == True:
            message = message.rstrip("\n")
            logging.info(message)
        self.output.tag_config(name, foreground=color)  
        self.output.see('end') 
        c = c + 1

#funkce na vypsani IP adresy z TOR site        
    def GetExternalIP(self): 
        file = "ip.txt"
        url = 'checkip.amazonaws.com'
        logging.info("connecting to %s" % url)
        response = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.PROXY, '127.0.0.1')
        c.setopt(c.PROXYPORT, 9050)
        c.setopt(c.PROXYTYPE, c.PROXYTYPE_SOCKS5)
        logging.info("Fetching IP from %s" % url)
        try:    
            with open(file, 'w') as f:
                c.setopt(c.WRITEFUNCTION, f.write)
                c.setopt(c.CONNECTTIMEOUT, 60)
                c.setopt(c.NOSIGNAL, 1)
                c.perform()
                f.close()
        except:
            pass    
        with open(file, 'r') as r:
            result = r.readlines()
            msLine = result[-1].strip()
            latency = msLine.split('[')[-1]
            reg = re.compile('\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}')
            match = reg.search(latency)
            logging.info("IP %s" % match.group())
            return match.group()
            r.close()
          
      
      
    def IPandlatency(self):    
        ip = self.GetExternalIP()
        file = "ip.txt"
        with open(file, 'r') as r:
              result = r.readlines()
              msLine = result[-1].strip()
              latency = msLine.split(' <body> ')[-1]
              reg = re.compile('\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}')
              match = reg.search(latency)
              ping = os.popen('ping -c 1 %s' % match.group())
              result = ping.readlines()
              msLine = result[-1].strip()
              latency = msLine.split(' = ')[-1]
              bezlomitka = re.compile('\d{1,3}') 
              bezlomitkareg = bezlomitka.search(latency)
              latency = bezlomitkareg.group()
              ping = int(float(latency))
              ms = "ms"
              if ping <= 1:
                  color = "red"
                  latency = "OFFLINE"
                  ms = ""
              elif ping < 100:
                  color = "white"
              elif ping < 300:
                  color = "yellow"
              elif ping < 500:
                  color = "orange"
              else:
                  color = "red"
              latency = latency + ms    
              self.write("----------------------------------------------------------------", color, 0)
              self.write(ip.ljust(20), color, 0)
              self.write(latency.rjust(44) + "\n", color, 0)
              logging.info("ping %s" % latency)
              r.close()         
              self.write("----------------------------------------------------------------", color, 0)
              
              
    def ip(self):
        self.write("Fetching IP starting.\n","green", 1)
        key = self.ident
        while key == self.ident:
            try:
                interval = self.time.get()
                start = timer()
                self.IPandlatency()
                end = timer()
                result = (end - start)
                if (int(result) > int(interval)):
                    interval = 0
                    time.sleep(.1)
                else:
                    interval = (int(interval) - int(result))
                    time.sleep(int(interval))
                seconds = (int(result) + interval) 
                logging.info("Fetching IP take %s seconds" % seconds)
            except:
                pass
        self.write("Fetching IP stopped.\n","error", 1)    
#funkce na zmenu IP adresy    
    def startnewnym(self):
        key = self.ident
        self.failed = 0
        while key == self.ident:
            interval = self.time.get()
            thread.start_new_thread(self.newnym, ())
            time.sleep(interval)
            
            
        self.write('TOR switcher stopped.\n', "error", 1)
        self.buttonstop['state'] = 'disabled'
        self.buttonstart['state'] = 'normal'
        
    
    def newnym(self):
        host = self.host.get()
        port = self.port.get()
        passwd = self.passwd.get()
        interval = self.time.get()
        start = timer()
        try:
            tn = telnetlib.Telnet(host, port)
            if passwd == '':
                tn.write("AUTHENTICATE\r\n")
            else:
                tn.write("AUTHENTICATE \"%s\"\r\n" % (passwd))
            res = tn.read_until('250 OK', 5)
            if res.find('250 OK') > -1:
                pass
            else:
                self.write('TOR switcher control responded "%s\n".', "error", 1)
        except Exception, ex:
            self.write("Error. See log for more details.\n", "error", 0)
            logging.info(ex)
        
        try:
            
            tn.write("signal NEWNYM\r\n")
            res = tn.read_until('250 OK', 5)
            if res.find('250 OK') > -1:
                time.sleep(interval)
                
            else:
                failed = failed + 1
                self.write('TOR switcher control cant accept request.\n', "error", 1)
                self.write('Failed %s.\n' % self.failed, "error", 1) 
                if self.failed == 3:
                    key = self.ident + 1
                    
        except Exception, ex:
            failed = failed + 1
            self.write("Request failed, restarting process %s.\n" % self.failed, "error", 1)
            logging.info(ex)
            if self.failed == 3:
                key = self.ident + 1
        
        tn.write("QUIT\r\n")   
        tn.close()
        end = timer()
        result = (end - start)
        logging.info("Requesting new IP take %s seconds" % (int(result)))
               
        
        
            
