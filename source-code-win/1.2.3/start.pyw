#! /usr/bin/env python

#import vsech potrebnych modulu
import tkinter.ttk, random, _thread, time, tkinter.scrolledtext, socket, re, logging, os,sys, multiprocessing, subprocess, pycurl, io, webbrowser,argparse, urllib3
from tkinter import *
from timeit import default_timer as timer
from datetime import datetime
from urllib3.contrib.socks import SOCKSProxyManager

#nastaveni debug level pro urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)
urllib3.disable_warnings()

#verze programku + doplnky
version = "1.2.3"
startchanger = timer()
directory = "Logs"
datadirectory = "Data"
tordirectory = "Tor"
if not os.path.exists(directory):
    os.makedirs(directory)
if not os.path.exists(datadirectory):
    os.makedirs(datadirectory)
    
logchanger = datetime.now().strftime('Logs/ipchanger_%Y_%m_%d_%H_%M_%S.log')
logtor = datetime.now().strftime('Logs/tor_%Y_%m_%d_%H_%M_%S.txt')
c = 1 


#nastavitelne argumenty programku
parser = argparse.ArgumentParser()  
parser.add_argument("-a", "--auto", type=int, required=False, help="-a 10   change ip every 10 seconds after program start")
parser.add_argument("-d", "--debug", help="start debug logging", action='store_true')
parser.add_argument("-m", "--multi", type=int, required=False, help="-m 5   run 5 different TOR instances", choices=range(1,101))
parser.add_argument("-p", "--publicAPI", action='store_true', required=False, help="bind API to 0.0.0.0 instead of 127.0.0.1")
parser.add_argument("-c", "--country", type=str, required=False, help="-c {cz}   select czech republic country")       #for future update

args = parser.parse_args()   

#definice debug levelu pokud existuje argument -d
debug = 1


#trida tkinter
class IpChanger(Tk):

    #definice rozhrani aplikace
    def __init__(self):  
        Tk.__init__(self)
        #kontrola souboru icony a tail.exe pro zobrazeni logu live, pokud neexistuje tak stahni
        self.favicon = "Data/favicon.png"
        self.tailexe = "tail.exe"
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.resizable(width = False, height = True)  
        #definice rozmeru aplikace  
        self.frame = Frame(self)
        self.minsize(500,418)
        #self.maxsize(500,418)
        
        #definice pro menu
        self.menubar = Menu(self)
        
        #definice pro menu TOR server
        self.tormenu = Menu(self, tearoff=0)
        self.tormenu.add_command(label="Start", command=self.prestart)
        self.tormenu.add_command(label="Stop", command=self.stoptor, state="disabled")
        self.menubar.add_cascade(label="TOR server".ljust(10), menu=self.tormenu)
         
        #definice pro menu IP Changer 
        self.changermenu = Menu(self, tearoff=0)
        self.changermenu.add_command(label="Start", state="disabled", command=self.start)
        self.changermenu.add_command(label="Stop", state="disabled", command=self.stop)
        self.menubar.add_cascade(label="IP changer".ljust(10), menu=self.changermenu)
        
        #definice pro menu Logs
        self.logmenu = Menu(self, tearoff=0)
        self.logmenu.add_command(label="Changelog", command=self.changelog)
        self.logmenu.add_command(label="Debug console", command=self.showlog)
        self.logmenu.add_command(label="Open log directory", command=self.opendirectory)
        self.menubar.add_cascade(label="Logs".ljust(10), menu=self.logmenu)
        
        #definice pro menu Options
        self.optionmenu = Menu(self, tearoff=0)
        self.optionmenu.add_command(label="Settings".ljust(10), command=self.configwindow)
        self.optionmenu.add_command(label="Clean output", command=self.clean)    
        self.menubar.add_cascade(label="Options".ljust(20), menu=self.optionmenu)
        
        #prazdne neviditelne tlacitko pro odsazeni
        self.blankmenu = Menu(self, tearoff=0)
        self.menubar.add_cascade(label="".ljust(34), menu=self.blankmenu, state="disabled")

        #definice pro menu Help
        self.helpmenu = Menu(self, tearoff=0)
        self.helpmenu.add_command(label="Help", command=self.help)
        self.helpmenu.add_command(label="Check updates", command=self.buttonupdate)
        self.helpmenu.add_command(label="About", command=self.aboutwhat)
        self.menubar.add_cascade(label="Help".ljust(15), menu=self.helpmenu)
        
        self.config(menu=self.menubar)
        
        #definice pro aplikaci, nazev, ruzne hodnoty
        global start
        title = "TOR IP Changer | Created by Seva | v"
        self.title(string = title + "" + version)
        self.host = StringVar()
        self.port = IntVar()
        self.proxy = IntVar()
        self.time = DoubleVar()
        self.timeout = DoubleVar()
        self.controlport = 15000
        self.control = 15000
        if args.publicAPI is not True:
          self.appHOST = "127.0.0.1"
          self.bindtype = "local"
        else:
          self.appHOST = "0.0.0.0"
          self.bindtype = "public"
        self.appPORT = 14999
        self.proxy = 9050
        self.b = 0
        self.data = "Data/tordata%s" % self.b
        self.count = 1
        self.host.set('127.0.0.1')
        self.port.set(self.control)
        self.time.set('10')
        self.timeout.set('5')
        self.auto = 0
        self.ident = random.random()
        self.bezi=0
        self.meni=0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed=0
        self.missing = 1
        self.buttonup = 0
        self.forall = 0
        self.oldpercent = None   
        self.countries = []
        self.countries = ('{random}','{ac}','{af}','{ax}','{al}','{dz}','{ad}','{ao}','{ai}','{aq}','{ag}','{ar}','{am}','{aw}','{au}','{at}','{az}','{bs}','{bh}','{bd}','{bb}','{by}','{be}','{bz}','{bj}','{bm}','{bt}','{bo}','{ba}','{bw}','{bv}','{br}','{io}','{vg}','{bn}','{bg}','{bf}','{bi}','{kh}','{cm}','{ca}','{cv}','{ky}','{cf}','{td}','{cl}','{cn}','{cx}','{cc}','{co}','{km}','{cg}','{cd}','{ck}','{cr}','{ci}','{hr}','{cu}','{cy}','{cz}','{dk}','{dj}','{dm}','{do}','{tp}','{ec}','{eg}','{sv}','{gq}','{ee}','{et}','{fk}','{fo}','{fj}','{fi}','{fr}','{fx}','{gf}','{pf}','{tf}','{ga}','{gm}','{ge}','{de}','{gh}','{gi}','{gr}','{gl}','{gd}','{gp}','{gu}','{gt}','{gn}','{gw}','{gy}','{ht}','{hm}','{hn}','{hk}','{hu}','{is}','{in}','{id}','{ir}','{iq}','{ie}','{im}','{il}','{it}','{jm}','{jp}','{jo}','{kz}','{ke}','{ki}','{kp}','{kr}','{kw}','{kg}','{la}','{lv}','{lb}','{ls}','{lr}','{ly}','{li}','{lt}','{lu}','{mo}','{mk}','{mg}','{mw}','{my}','{mv}','{ml}','{mt}','{mh}','{mq}','{mr}','{mu}','{yt}','{mx}','{fm}','{md}','{mc}','{mn}','{me}','{ms}','{ma}','{mz}','{mm}','{na}','{nr}','{np}','{an}','{nl}','{nc}','{nz}','{ni}','{ne}','{ng}','{nu}','{nf}','{mp}','{no}','{om}','{pk}','{pw}','{ps}','{pa}','{pg}','{py}','{pe}','{ph}','{pn}','{pl}','{pt}','{pr}','{qa}','{re}','{ro}','{ru}','{rw}','{ws}','{sm}','{st}','{sa}','{uk}','{sn}','{rs}','{sc}','{sl}','{sg}','{sk}','{si}','{sb}','{so}','{as}','{za}','{gs}','{su}','{es}','{lk}','{sh}','{kn}','{lc}','{pm}','{vc}','{sd}','{sr}','{sj}','{sz}','{se}','{ch}','{sy}','{tw}','{tj}','{tz}','{th}','{tg}','{tk}','{to}','{tt}','{tn}','{tr}','{tm}','{tc}','{tv}','{ug}','{ua}','{ae}','{gb}','{uk}','{us}','{um}','{uy}','{uz}','{vu}','{va}','{ve}','{vn}','{vi}','{wf}','{eh}','{ye}','{zm}','{zw}')         
        
        
        if args.multi is not None:
            self.maxfailed = args.multi + 3
            for i in range(args.multi):
                exec('self.lang_' + str(i) + ' = StringVar()')  
                if args.country is not None:
                    
                    exec('self.lang_' + str(i) + '.set("' + args.country + '")')
                else:
                    exec('self.lang_' + str(i) + '.set("{random}")')
                
                exec('self.useBridges_' + str(i) + ' = BooleanVar()')
                
                
                
        else:
            self.maxfailed = 3
            self.lang_0 = StringVar()
            if args.country is not None:
                self.lang_0.set(args.country)
            else:
                self.lang_0.set('{random}')
            
            self.useBridges_0 = BooleanVar()
              
        self.logtorm = datetime.now().strftime('Logs/tor_%Y_%m_%d_%H_%M_%S.txt')
        
        #definice pro debug level aplikace pokud pouzit parametr -d
        if debug == 1:
            logging.basicConfig(filename=logchanger,level=logging.DEBUG,format='%(asctime)s.%(msecs)03d <%(funcName)s:%(lineno)d> %(message)s', datefmt='%b %d %H:%M:%S')
        else:            
            logging.basicConfig(filename=logchanger,level=logging.INFO,format='%(asctime)s.%(msecs)03d %(message)s', datefmt='%b %d %H:%M:%S')
        
        self.menubar = Menu
        
        #definice stylu progressbaru, zmena barev a tloustka, maximalni hodnoty
        s = tkinter.ttk.Style()
        s.theme_use("default")
        s.configure("red.Horizontal.TProgressbar", foreground='red', background='red', thickness=3)
        s.configure("orange.Horizontal.TProgressbar", foreground='orange', background='orange', thickness=3)
        s.configure("green.Horizontal.TProgressbar", foreground='green', background='green', thickness=3)
        s.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue', thickness=3)
        self.progressbar = tkinter.ttk.Progressbar(self, orient="horizontal",mode ="determinate", style="blue.Horizontal.TProgressbar", length = 500)
        self.progressbar.grid(row=1,column=1,sticky="NEWS")
        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0
        #definice stylu pseudoconsole v aplikaci kam se vypisuji veskere veci
        self.output = tkinter.scrolledtext.ScrolledText(self, foreground="green", background="black", highlightcolor="white", highlightbackground="purple", wrap=WORD, width=60)
        self.output.grid(row=2, column=1,sticky="NEWS")
        self.write("Thank you for using TOR IP changer\n", "white", 0)
        self.write("Iam not responsible for any causalities or whatever\n", "white", 0)
        try:
            _thread.start_new_thread(self.API, ())
        except:
            pass
        
        _thread.start_new_thread(self.startthings, ())  
        if args.debug is True:
            _thread.start_new_thread(self.showlog, ())
        
    
    #funkce na spusteni overeni chybejicich souboru pro chod TORa
    def startcheck(self):
        self.progressbar['maximum'] = 100
        self.progressbar['value'] = 0
        self.progressbar['style'] = "blue.Horizontal.TProgressbar"
        _thread.start_new_thread(self.checkmissingfiles, ())
    
    #funkce na overeni chybejicich souboru pro chod TORa, a nasledne jejich stazeni 
    def checkmissingfiles(self):
        if not os.path.exists(tordirectory):
            os.makedirs(tordirectory)
        self.write("------------------------------------------------------------", "error", 1)
        self.write("Checking files. \n", "error", 1)
        try:
            
            if not os.path.exists("Tor/geoip"):
              self.missing = self.missing + 1
              self.download("https://raw.githubusercontent.com/torproject/tor/master/src/config/geoip", None, "Tor")
            if not os.path.exists("Tor/geoip6"):
              self.missing = self.missing + 1
              self.download("https://raw.githubusercontent.com/torproject/tor/master/src/config/geoip6", None, "Tor")
            
            http = urllib3.PoolManager()
            r = http.request('GET', 'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/files.txt')
            obsah = r.data.decode('utf-8')
            self.file=""
            for o in obsah.split():
                if not os.path.exists("Tor/%s" % o):
                    self.missing = self.missing + 1
                    self.download("https://github.com/seevik2580/tor-ip-changer/raw/master/tor/%s" % (o), None, "Tor")
                
            
            if self.missing != 1:
                self.write("Missing files downloaded\n","green",1)    
            else:
                self.write("No missing files\n","green",1)
            self.starttor()
            self.missing = 1
        except:
            self.write("Failed...repeating \n", "error", 1)
            self.failed = self.failed + 1
            if self.failed == 3:
                self.write("Cannot download Tor files\n", "error", 1)
                return
            time.sleep(1) 
            _thread.start_new_thread(self.startcheck, ())           
        self.write("------------------------------------------------------------", "error", 1)
        
    #funkce tlacitka na otevreni slozky s logy
    def opendirectory(self):
        subprocess.Popen(r'explorer Logs')
    
    #funkce na vyvolani noveho okna options > settings, a jeho nalezitosti
    def configwindow(self):
        w = 200
        h = 200
        r = 1
        cl = 0
        cc = 1
        proxy = 9050
        self.newWindow = Toplevel(self)
        self.newWindow.title("Settings")
        
        Label(self.newWindow, text = 'Interval:').grid(row=r,column=0)
        if self.meni == 1:
            interval = Entry(self.newWindow, textvariable = self.time, width = 5, state="disabled")
        else:
            interval = Entry(self.newWindow, textvariable = self.time, width = 5, state="normal")    
        interval.grid(row=r,column=1)
        def save():
            if self.newWindow:
                try:
                    ee = self.time.get()
                    if ee < 10:
                        self.time.set('10')
                    else:
                        self.time.set(ee)
                    if args.multi is not None:
                        for i in range(args.multi):    
                            exec('self.lang_' + str(i) + '.set(self.tor_' + str(i) + '.get())')
                            exec('self.useBridges_' + str(i) + '.set(self.useBridges_' + str(i) + '.get())')  
                    else:
                        exec('self.lang_0.set(self.tor_0.get())')  
                        exec('self.useBridges_0.set(self.useBridges_0.get())')  
                                                                             
                                                                        
                    self.newWindow.destroy()   
                except ():
                    pass
                self.newWindow = None   
        
        Label(self.newWindow, text = 'sec').grid(row=r,column=2) 
        r = r + 1
        
        Label(self.newWindow, text = 'Select country').grid(row=r,column=0, columnspan=1)
        Label(self.newWindow, text = 'Use bridges ?').grid(row=r,column=2, columnspan=2)
        if args.multi is not None:
            if self.forall == 1:
                self.checkvar = IntVar(value=1)
                self.checkforall = Checkbutton(self.newWindow, text = "for all?", variable = self.checkvar, onvalue = 1, offvalue = 0, command = self.unsetforall)
                
            else:
                self.checkvar = IntVar(value=0)
                self.checkforall = Checkbutton(self.newWindow, text = "for all?", variable = self.checkvar, onvalue = 1, offvalue = 0, command = self.setforall)
                
            self.checkforall.grid(row=r, column=1)
            
        
        r = r + 1
        langs = []
        langs = self.countries
        if args.multi is not None:
            
            for i in range(args.multi):
                if i % 10 == 0 or i % 1 != 0:
                    r = 3
                    cl = cl + 4
                    cc = cc + 4 
                    w = w + 50
                
                Label(self.newWindow, text = '%s:%s' % (self.host.get(), proxy+i)).grid(row=r,column=cl-4, padx=(10, 10)) 
                if self.forall == 1 and i != 0:
                    exec('self.tor_' + str(i) + ' = ttk.Combobox(self.newWindow, width = 9, state = "disabled")')
                    
                else:
                    exec('self.tor_' + str(i) + ' = ttk.Combobox(self.newWindow, width = 9, state = "readonly")')
                  
                    
                exec('self.tor_' + str(i) + '.grid(row=r,column=cc-4, padx=(10, 10))')
                exec('self.tor_' + str(i) + '["values"] = (langs)')
                
                exec('self.tor_bridge_yes_' + str(i) + ' = Radiobutton(self.newWindow, text = "Yes", variable = self.useBridges_' + str(i) + ', value = True, width = 3)')
                exec('self.tor_bridge_yes_' + str(i) + '.grid(row=r,column=cc+1-4)')
                
                exec('self.tor_bridge_no_' + str(i) + ' = Radiobutton(self.newWindow, text = "No", variable = self.useBridges_' + str(i) + ', value = False, width = 3)')
                exec('self.tor_bridge_no_' + str(i) + '.grid(row=r,column=cc+2-4)')
                
                if eval("self.lang_%s.get()" % str(i)) == "{random}":
                    exec('self.tor_' + str(i) + '.current(0)')
                else:
                    p = 0
                    for l in langs:
                        if l == eval("self.lang_%s.get()" % str(i)):
                            break
                        else:
                            p = p + 1
                    exec('self.tor_' + str(i) + '.current(p)')
                r = r + 1
                h = h + 15
                
            r = 15    
            Button(self.newWindow, text = "Save", command=save, width = 9).grid(row=r,column=1)
        else:
            cl = cl + 4
            cc = cc + 4 
            Label(self.newWindow, text = '%s:%s' % (self.host.get(),self.proxy)).grid(row=r,column=cl-4) 
            exec('self.tor_0 = ttk.Combobox(self.newWindow, width = 9, state = "readonly")')
            exec('self.tor_0.grid(row=r,column=cc-4)')
            exec('self.tor_0["values"] = (langs)')
            
            
            self.tor_bridge_yes_0 = Radiobutton(self.newWindow, text = "Yes", variable = self.useBridges_0, value = True, width = 3)
            self.tor_bridge_yes_0.grid(row=r,column=cc+1-4)
            self.tor_bridge_no_0 = Radiobutton(self.newWindow, text = "No", variable = self.useBridges_0, value = False, width = 3)
            self.tor_bridge_no_0.grid(row=r,column=cc+2-4)
            
            
            
            if self.lang_0.get() == "{random}":
                self.tor_0.current(0)
            else:
                p = 0
                for l in langs:
                    if l == self.lang_0.get():
                        break
                    else:
                        p = p + 1
                self.tor_0.current(p)  
            r = r + 1
            Button(self.newWindow, text = "Save", command=save, width = 9).grid(row=r,column=1)                    
        
        exec('self.tor_0.bind("<Return>", self.getsetforall)')
        exec('self.tor_0.bind("<<ComboboxSelected>>", self.getsetforall)')
        
        
    def aboutwhat(self):
        self.newWindow2 = Toplevel(self)
        self.newWindow2.title("About")
        
        Label(self.newWindow2, text = 'About what ? ...').grid(row=1,column=1,columnspan=3,padx=(20, 20))
        def ok():
            if self.newWindow2:
                try:
                    self.newWindow2.destroy()   
                except ():
                    pass
                self.newWindow2 = None   
        Button(self.newWindow2, text = "Ok", command=ok,width=5).grid(row=2,column=2,padx=(20, 20))
            
        
    #funkce na prepnuti vsech tlacitek podle prvniho pokud zaskrtnuta volba for all
    def getsetforall(self,event):
        if self.forall == 1:
            langs = []
            langs = self.countries
            if args.multi is not None:
                for i in range(1, args.multi):
                    p = 0
                    for l in langs:
                        if l == self.tor_0.get():
                            break
                        else:
                            p = p + 1
                    exec('self.tor_' + str(i) + '.current(p)')
    
    #funkce pro zaskrtavaci policko                    
    def setforall(self):
        if args.multi is not None:
            for i in range(1, args.multi):
                exec('self.tor_' + str(i) + '["state"] = "disabled"')
        exec('self.tor_0.bind("<Return>", self.getsetforall)')
        exec('self.tor_0.bind("<<ComboboxSelected>>", self.getsetforall)')
        self.checkforall['command'] = self.unsetforall
        self.forall = 1
                    
    
    def unsetforall(self):
        if args.multi is not None:
            for i in range(1, args.multi):
                exec('self.tor_' + str(i) + '["state"] = "readonly"')
        exec('self.tor_0.bind("<Return>", self.getsetforall)')            
        exec('self.tor_0.bind("<<ComboboxSelected>>", self.getsetforall)')
        self.checkforall['command'] = self.setforall
        self.forall = 0
        

    #funkce na zobrazeni napovedy        
    def threadhelp(self):
        try:
            help = 'help.txt'
            if not os.path.exists(help):
                self.download("https://github.com/seevik2580/tor-ip-changer/raw/master/dist/%s/%s" % (version,help), 1)
        
            SW_HIDE = 0
            info = subprocess.STARTUPINFO()
            info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = SW_HIDE
            subprocess.Popen(r'cmd /c start notepad.exe help.txt', startupinfo=info)
        except:
            self.write("Can't open help.txt \n", "orange", 1)
            pass
            
    def help(self):
        _thread.start_new_thread(self.threadhelp, ())
        
    #funkce na zobrazeni zpravy dne            
    def motd(self):
        http = urllib3.PoolManager()
        r = http.request('GET', 'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/motd.txt')
        obsah = r.data.decode('utf-8')
        self.write(obsah,'white',1)
        
    #funkce na zobrazeni changelogu verze aplikace        
    def changelog(self):
        http = urllib3.PoolManager()
        r = http.request('GET', 'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/'+version+'/changelog')
        obsah = r.data.decode('utf-8')
        self.write(obsah,'orange',1)    

    #funkce na spusteni tail.exe a vypis logu live        
    def showlog(self):
        self.logmenu.entryconfig(1, label = "Hide debug console", command=self.hidelog)
        _thread.start_new_thread(self.tail, ())
    
    #funkce na tail.exe
    def tail(self):
        if not os.path.exists(self.tailexe):
            self.download("https://github.com/seevik2580/tor-ip-changer/raw/master/dist/%s/%s" % (version,self.tailexe), 1)
        os.system("tail.exe -q -f %s" % (logchanger))
        os.system("tail.exe -q -f %s" % (logtor))
        
    #funkce na schovani logu live    
    def hidelog(self):
        self.logmenu.entryconfig(1, label = "Debug console", command=self.showlog)
        SW_HIDE = 0
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = SW_HIDE
        subprocess.Popen(r'cmd /c taskkill /f /im tail.exe', startupinfo=info)
        
    #funkce na vypsani debug infa aplikace do console a logu
    def appInfo(self):
        key = self.ident
        while key == self.ident:
            logging.info("IPchanged=%s" % self.IPchanged)
            logging.info("IPfetched=%s" % self.IPfetched)
            logging.info("IPchangeFailed=%s" % self.failed)
            logging.info("IPchangeMaxFailedBeforeExit=%s" % self.maxfailed)
            jakdlouhobezi=timer()
            logging.info("AppRunning=%s sec" % (jakdlouhobezi-startchanger))
            time.sleep(10)
        
    #funkce na ovladani API skrz telnet
    def API(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            s.bind((self.appHOST, self.appPORT))
            self.write('API server binded to %s:%s (%s) OK.\n' % (self.appHOST,self.appPORT,self.bindtype), 'green', 1)
            
        except socket.error as msg:
            self.write('API server binded to %s:%s (%s) ERROR.\n' % (self.appHOST,self.appPORT,self.bindtype), "red", 1)
            return

        s.listen(10)
         
        def clientthread(conn):
          try:
            conn.send(b'IPCHANGER API. Type "help" for usage\n')
            while True:
                data = conn.recv(1024)  
                reply = b'\r\nUsable commands:\r\n'
                reply += b'help           | print usage\r\n'
                reply += b'tor start      | start tor server\r\n'
                reply += b'tor stop       | stop tor server\r\n'
                reply += b'interval N     | set interval to N seconds\r\n'
                reply += b'changeip start | start autochanging ip\r\n'
                reply += b'changeip stop  | stop autochanging ip\r\n'
                reply += b'changeip once  | dont autochange, but change once\r\n'
                reply += b'exit           | close connection\r\n'
                rozdelit = '%s' % data.decode("utf-8")
                rozdel = rozdelit.split(" ")
                if data == b'exit\r\n':
                    reply = b'closing connection\r\n'
                    conn.close()
                    break
                elif data == b'tor start\r\n':
                    reply = b'starting tor server\r\n'
                    self.prestart()
                elif data == b'tor stop\r\n':
                    reply = b'stopping tor server\r\n'
                    self.stoptor()
                elif data == b'changeip once\r\n':
                    if self.bezi == 1:
                        reply = b'changing ip once\r\n'
                        self.newIP()
                        self.IPandlatency()
                    else:
                        reply = b'tor server not running\r\n'
                elif data == b'changeip start\r\n':
                    if self.bezi == 1:
                        reply = b'start ip changing\r\n'
                        self.start()
                    else:
                        reply = b'tor server not running\r\n'
                elif data == b'changeip stop\r\n':
                    if self.bezi == 1:
                        reply = b'stop ip changing\r\n'
                        self.stop()
                    else:
                        reply = b'tor server not running\r\n'
                elif rozdel[0] == 'interval':
                    try:
                        cislo = int(rozdel[1])
                        reply = bytes('set interval to %s seconds\r\n' % cislo, 'utf-8')
                        self.time.set(cislo)
                    except ValueError:
                        reply = bytes('interval has to be number!\r\n', 'utf-8')
                        pass
                        
                elif data == b'\r\n':
                    break
                    conn.close()
                elif not data:
                    break
                
                try:
                    conn.sendall(reply)
                except:
                    pass
                
            conn.close()
          except:
            pass
        while 1:
            conn, addr = s.accept()
            _thread.start_new_thread(clientthread ,(conn,))
         
         
        s.close()

    #funkce na start updatu        
    def startthings(self):
        time.sleep(1)
        if args.auto is not None:
            self.tormenu.entryconfig(0, state="disabled")
        _thread.start_new_thread(self.update, ())
        
    #funkce na prestart, overeni tora
    def prestart(self):
        self.startcheck() 
                            
    #funkce spusteni startu tora                            
    def starttor(self):      
        self.tormenu.entryconfig(0, state="disabled")
        self.tormenu.entryconfig(1, state="normal")
        self.progressbar["style"] = "blue.Horizontal.TProgressbar"
        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0
        _thread.start_new_thread(self.tor, ())
        
    #funkce zastaveni tora
    def stoptor(self):
        self.tormenu.entryconfig(0, state="normal")
        self.tormenu.entryconfig(1, state="disabled")
        if self.meni == 1:
          _thread.start_new_thread(self.stop, ())
        
        SW_HIDE = 0
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = SW_HIDE
        subprocess.Popen(r'cmd /c taskkill /f /im tor.exe', startupinfo=info)
        subprocess.Popen(r'cmd /c taskkill /f /im obfs4proxy.exe', startupinfo=info)
        
        self.write("TOR server stopped. \n", "error", 1)   
        self.ident = random.random()
        if self.meni == 0:
            self.progressbar["value"] = 0
        self.bezi=0
        self.meni=0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed=0
        self.control = 15000
        self.proxy = 9050
        self.b = 0
        self.data = "Data/tordata%s" % self.b
        self.changermenu.entryconfig(0, state="disabled")
        self.changermenu.entryconfig(1, state="disabled")
        
    #funkce k pouziti bridges
    def bridges(self, identify=None):
        if eval("self.useBridges_%s.get()" % str(identify)) == 1:
            with open('Tor/bridges.txt', 'r') as f:
                self.bridge = '--UseBridges 1 '
                self.bridge += '--ClientTransportPlugin "obfs2,obfs3,obfs4 exec Tor\obfs4proxy.exe managed" '
                self.bridge += '--clientTransportPlugin "meek exec Tor\meek-client" '
                for line in f:
                    l = line.split('\n')[0]
                    self.bridge += '--Bridge "%s" ' % l
            self.write('using bridges. \n', "green", 1)
            ff = open('Tor/bridges.txt', 'r')
            for line in ff:
                logging.info(line.split('\n')[0])
            return self.bridge    
        else:
            self.bridge = '--UseBridges 0 '
            self.write('using direct connection. \n', "red", 1)
            return self.bridge

    #funkce multiinstanci tora        
    def multiTor(self, identify=None):
        self.logtorm = datetime.now().strftime('Logs/tor_%Y_%m_%d_%H_%M_%S.txt')
        files = self.logtorm
        self.bridges(identify)
        SW_HIDE = 0
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = SW_HIDE
        if eval("self.lang_%s.get()" % str(identify)) == "{random}":
            subprocess.Popen(r'Tor/tor.exe %s --RunAsDaemon 1 --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "16:BA0E52DF882381A2609FF0E3D1C3B9F78C55375AEE5D7EEF9B39C4EA76" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log notice --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1' % (self.bridge, self.control,self.proxy,self.data), startupinfo=info, stdout = open(files, 'w'))
        else:
            language = eval("self.lang_%s.get()" % str(identify))
            subprocess.Popen(r'Tor/tor.exe %s --RunAsDaemon 1 --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "16:BA0E52DF882381A2609FF0E3D1C3B9F78C55375AEE5D7EEF9B39C4EA76" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log notice --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 --StrictNodes 1 --ExitNodes %s' % (self.bridge, self.control,self.proxy,self.data,language), startupinfo=info, stdout = open(files, 'w'))                
        
        self.control = self.control + 1
        self.proxy = self.proxy + 1
        self.b = self.b + 1
        self.data = "Data/tordata%s" % self.b
          
        
    #funkce startu tora a jeho logu a urcovani procent v progressbaru 
    def tor(self):
        if args.multi is not None:
            file = self.logtorm
        else:
            file = logtor
        
        SW_HIDE = 0
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = SW_HIDE
        key = self.ident   
        if args.multi is not None:
            self.write("TOR server %s starting " % self.b, "green", 1)
            self.bridges('0')
            if self.lang_0.get() == "{random}":
                subprocess.Popen(r'Tor/tor.exe %s --RunAsDaemon 1 --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "16:BA0E52DF882381A2609FF0E3D1C3B9F78C55375AEE5D7EEF9B39C4EA76" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log notice --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --DNSport 53 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1' % (self.bridge, self.control,self.proxy,self.data), startupinfo=info, stdout = open(file, 'w'))
            else:
                subprocess.Popen(r'Tor/tor.exe %s --RunAsDaemon 1 --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "16:BA0E52DF882381A2609FF0E3D1C3B9F78C55375AEE5D7EEF9B39C4EA76" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log notice --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --DNSport 53 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 --StrictNodes 1 --ExitNodes %s' % (self.bridge, self.control,self.proxy,self.data,self.lang_0.get()), startupinfo=info, stdout = open(file, 'w'))
        
            self.control = self.control + 1
            self.proxy = self.proxy + 1
            self.b = self.b + 1
            self.data = "Data/tordata%s" % self.b
            time.sleep(1)
            
            for m in range(args.multi-1):
                if not key == self.ident:
                    return  
                self.write("TOR server %s starting " % self.b, "green", 1)
                _thread.start_new_thread(self.multiTor, (self.b,))
                time.sleep(1)
                
        else:
            self.write("TOR server starting ", "green", 1)
            self.bridges('0')
            self.write("Please wait ... \n", "green", 1)
            if self.lang_0.get() == "{random}":
                subprocess.Popen(r'Tor/tor.exe %s --RunAsDaemon 1 --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "16:BA0E52DF882381A2609FF0E3D1C3B9F78C55375AEE5D7EEF9B39C4EA76" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log notice --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --DNSport 53 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1' % (self.bridge, self.control,self.proxy,self.data), startupinfo=info, stdout = open(file, 'w'))
            else:
                subprocess.Popen(r'Tor/tor.exe %s --RunAsDaemon 1 --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "16:BA0E52DF882381A2609FF0E3D1C3B9F78C55375AEE5D7EEF9B39C4EA76" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log notice --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --DNSport 53 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 --StrictNodes 1 --ExitNodes %s' % (self.bridge, self.control,self.proxy,self.data,self.lang_0.get()), startupinfo=info, stdout = open(file, 'w'))
        timeout = 0
        count = 1    
        while not timeout==240 and key == self.ident:
            if args.multi is not None:
                file = self.logtorm
            else:
                file = logtor
            
            if not key == self.ident:
                return
            self.debug("Wait. \n")
            time.sleep(1)
            if timeout % 30 == 0:
                if args.multi is not None:
                    self.write("TOR servers starting. Please wait ... \n", "green", 1)
            timeout = timeout + 1
            try:
              with open(file, 'r') as f:
                self.debug("Open. \n")
                result = f.readlines()
                msLine = result[-1].strip()
                
                errors = msLine.split(' [err] ')[-1]
                bootstrapped = msLine.split(' [Bootstrapped] ')[-1]
                bootstrap = bootstrapped.split(':')
                if errors == "Reading config failed--see warnings above.":
                    self.write("another instance of TOR server is running\n", "error", 1) 
                    self.stoptor()
                    break
                    
                latency = msLine.split(' Bootstrap ')[-1]
                reg = re.compile('\d{1,3}%')
               
                match = reg.search(latency)
                
                if (match):
                    boot = match.group()# + "\r"
                    if not self.oldpercent == boot: 
                        self.write("%s:%s \n" % (boot,bootstrap[3]), "green", 0)
                        logging.info("%s:%s" % (boot,bootstrap[3]))
                        self.oldpercent = boot
                    
                    self.progressbar["value"] = float(match.group().rstrip("%"))
                    if (match.group() == "100%") or (match.group() == "90%") or (match.group() == "85%"):
                        self.write("TOR server started \n", "green", 1) 
                        self.progressbar["value"] = 100 
                        self.progressbar["style"] = "orange.Horizontal.TProgressbar"
                        self.bezi=1
                        self.changermenu.entryconfig(0, state="normal")
                        self.changermenu.entryconfig(1, state="disabled")
        
                        if args.multi is not None:
                            self.write("------------------------------------------------------------", "white", 1)
                            self.write("Proxy list:\n", "white", 1) 
                            proxy = 9050
                            host = "127.0.0.1"
                            for i in range(args.multi):
                                language = eval('self.lang_' + str(i) + '.get()')
                                self.write("%s:%s\n" % (host,proxy), "orange", 1)
                                proxy = proxy + 1 
                            self.write("------------------------------------------------------------", "white", 1)                                
                        if args.auto is not None:
                            try:
                                _thread.start_new_thread(self.start, ())
                            except:
                                pass    
                        self.write("DNS server started \n", "green", 1) 
                        
                        
                        break          
                else:
                    pass
                f.close()
            except:
              pass
            
        else:                 
            self.write("TOR server timed out.\n", "error", 1) 
            self.write("Problem connecting to this node try to change country \nor delete all tordata folders inside Data folder\n", "error",1)
            self.progressbar["style"] = "red.Horizontal.TProgressbar"
            time.sleep(.1)
            self.stoptor()                
        
    #funkce na vycisteni vystupu
    def clean(self):
        self.output.delete('1.0', END)
        
    #funkce spusteni predbeznych veci po startu aplikace
    def buttonupdate(self):
        self.buttonup = 1
        self.startthings()

    #funkce kontroly verze aplikace, pokud novejsi verze .. stahni
    def update(self):
          try:  
              self.write('This version:            %s\n' % version, "white", 1)
              http = urllib3.PoolManager()
              f = http.request('GET', 'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/version.txt')
              lastver = f.data.decode('utf-8') 
              url = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/%s/dist.txt" % lastver
              u = url.replace("\n", "")
              linkurl = http.request('GET', u)
              link = linkurl.data.decode('utf-8') 
              
                              
              self.write('Last available version:  %s\n' % lastver, "white", 1)
              v = version.replace(".", "")
              l = lastver.replace(".", "")
              if int(v) >= int(l):
                  self.write('No update required. \n', "white", 1)
              elif int(v) < int(l):
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
              _thread.start_new_thread(self.motd, ())
              time.sleep(1)
              if self.buttonup == 0:
                  if args.auto is not None:
                      self.auto = 1
                      if args.auto < 10:
                          args.auto = 10
                      
                      self.write("Autostart ON, change every %s seconds \n" % args.auto, "green", 1)     
                      self.time.set(args.auto)
                  else:
                      self.time.set(10)
                      self.write("Autostart OFF. \n", "error", 1) 
                  if self.auto == 1: 
                      _thread.start_new_thread(self.prestart, ())
              
              
                   
          except:
            pass      

    #funkce downloaderu pro stazeni souboru z internetu
    def download(self, url=None, write=None, folder=None):
        from urllib.request import urlopen
        file_name = url.split('/')[-1]
        u = urlopen(url)
        fo = folder
        if folder is None:
            fo = ""
        else:
            fo = "%s/" % folder
        
        f = open("%s%s" % (fo,file_name), 'wb')
        meta = u.info()
        totalFileSize = int(meta['Content-Length'])
        if write is None:
            self.write("Downloading: %s \n" % (file_name), "error", 1)
            self.progressbar['style'] = "red.Horizontal.TProgressbar"
            
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
                    logging.debug(status)
            else:
            	  if write is None:
                    self.progressbar['value'] = status
                    logging.debug(status)
            count += 1
        f.close()

    #funkce na pusteni oddelenych procesy zmeny IP a zjisteni IP
    def ipProc(self):
        _thread.start_new_thread(self.startnewIP, ())                                                                                                        
        _thread.start_new_thread(self.ip, ())
        
    #funkce startu zmeny IP
    def start(self):
        self.start = timer()
        self.write('IP Changer started.\n', "green", 1)
        self.progressbar["style"] = "green.Horizontal.TProgressbar" 
        self.changermenu.entryconfig(0, state="disabled")
        self.changermenu.entryconfig(1, state="normal")
        
        _thread.start_new_thread(self.ipProc, ())  
        _thread.start_new_thread(self.appInfo, ())
            
    #funkce zastaveni zmeny IP
    def stop(self): 
        self.write('IP Changer stopping. Wait..\n', "error", 1)
        self.write('Fetching IP stopping. Wait..\n', "error", 1)
        self.ident = random.random() 
        self.meni=0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed=0
        self.changermenu.entryconfig(0, state="disabled")
        self.changermenu.entryconfig(1, state="disabled")
             
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

    #funkce na psani debug do logu                                  
    def debug(self, message):
        if debug == 2:
            global c
            try:
                logging.debug(message)  
            except:
                pass
    
    #funkce na zjisteni IP adresy z TOR site        
    def GetExternalIP(self, proxy=None): 
        timeout = self.timeout.get()
        
        file = "Data/tordata%s/ip.txt" % (proxy-9050)
        url = 'http://checkip.amazonaws.com'
        interval = int(self.time.get()-1)
        soc = SOCKSProxyManager('socks5://127.0.0.1:%s/' % proxy)
        s = soc.request('GET', url, timeout=urllib3.Timeout(connect=interval, read=interval), retries=False)
        d = s.data.decode('utf-8').split('\n')
        f = open(file, 'w')
        f.write(d[0])
        f.close()
        s.close()
        
        
    #funkce na zjisteni odezvy pro zjistenou IP adresu, nejdrive zavola zjisteni IP a nasledne provede overeni odezvy, a vypise vystup do aplikace        
    def IPandlatency(self):      
        if args.multi is not None:
          instanci = int(args.multi)
        else:
          instanci = 1
        host = "127.0.0.1"
        proxy = 9050   
        languagenumber = 0
        
        def fetching(proxy):
            languagenumber = proxy - 9050
            language = eval('self.lang_' + str(languagenumber) + '.get()')
            if language == "{random}":
                  language = ""  
            try:
              color = "white"
              self.GetExternalIP(proxy)  
              file = "Data/tordata%s/ip.txt" % languagenumber
              f = open(file, 'r')
              ip = f.read()
              ping = os.popen('ping -n 1 -w 1 %s' % ip)
              result = ping.readlines()
              msLine = result[-1].strip()
              latency = msLine.split(' = ')[-1] 
              
              if latency == "1 (100% loss),":
                  latency = "1000+"
                  color = "orange"
              if latency == "0 (0% loss),":
                  latency = "500+"
                  color = "yellow"
            
              if latency == "Ping request could not find host None. Please check the name and try again.":
                  latency = "OFFLINE"
                  color = "red"
              
              try:
                  ms = latency.split('ms')[0]
                  if ms.isdigit() is True or latency == "1000+" or latency == "500+" or latency == "OFFLINE":
                      latency = "%sms" % ms
                  else:
                      latency = "####"
              except:
                  latency = "####"
              self.write("------------------------------------------------------------" + host.ljust(9) + ":" + str(proxy).ljust(5) + str(language).ljust(15) + ip.rjust(22) + str(latency).rjust(8) + "\n" + "------------------------------------------------------------"                                                 , color, 0)
              logging.info("127.0.0.1:%s IP %s %s " % (proxy,ip,latency))
              self.IPfetched = self.IPfetched + 1
              f.close()
              
              if self.bezi == 0:
                  return               
            except:
              status = eval("self.proxystatus_%s" % str(proxy))
              logging.info("127.0.0.1:%s failed" % (proxy))
              if self.bezi == 0 or self.meni == 0:
                  return
              
              if status == "FAILED":
                  status = "Changing FAILED"
              else:
                  status = "Changing OK - Fetching timeout"
              
              
              self.write("------------------------------------------------------------" + host.ljust(9) + ":" + str(proxy).ljust(5) + str(language).ljust(15) + str(status).rjust(1) + "\n" + "------------------------------------------------------------"                                                 , "error", 0)
              
              
              pass
    
        
        for i in range(instanci):
              _thread.start_new_thread(fetching, (proxy,))
              proxy = proxy + 1
          
    #funkce startu zjistovani aktualni IP adresy ve smycce    
    def ip(self):
        self.write("Fetching IP started.\n","green", 1)
        key = self.ident
        while key == self.ident:
            if key != self.ident:
                break
            try:
                interval = self.time.get()
                start = timer()
                self.IPandlatency()
                
                while not float(self.progressbar['value']) == float(interval)-1:
                    if key != self.ident:
                        break
                    time.sleep(.1)
                time.sleep(1)
                end = timer()
                result = (end - start)
                seconds = float(result)  
                
                
            except:
                self.failed = self.failed + 1
                
        self.write("Fetching IP stopped.\n","error", 1) 
        self.meni=0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed=0
        if self.bezi == 1:
            self.changermenu.entryconfig(0, state="normal")
            self.changermenu.entryconfig(1, state="disabled")
                        
    #funkce na overeni zda je hodnota cislo  
    def isnumeric(self, s=None):
        try:
            s = s.decode('utf-8')
        except:
            return False
        
        try:
            float(s)
            return True
        except Exception as e:
            return False
    
    #funkce spusteni zmeny IP adresy ve smycce
    def startnewIP(self):
        key = self.ident
        interval = self.time.get()
        while key == self.ident:
            try:
              self.IPchanged = self.IPchanged + 1
              self.meni=1
              timeout = 0
              interval = self.time.get()
              self.progressbar["maximum"] = interval
              self.progressbar["value"] = timeout
              _thread.start_new_thread(self.newIP, ())
              while not timeout==interval:
                  if key != self.ident:
                      break
                  self.progressbar["style"] = "green.Horizontal.TProgressbar"
                  time.sleep(1)
                  timeout = timeout + 1
                  self.progressbar["maximum"] = interval
                  self.progressbar["value"] = timeout
              
            except:
              pass
        self.write('IP Changer stopped.\n', "error", 1)
        self.meni=0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed=0
        if self.bezi == 1:
            self.progressbar["style"] = "orange.Horizontal.TProgressbar"
        else:
            self.progressbar["value"] = 0
  
    #funkce na zmenu IP adresy, odpojeni predeslych circuit a spojeni        
    def newIP(self):
      self.controlport = 15000
      proxy = 9050
      self.write("-------------------------CHANGING-IP------------------------\n", "white", 1)  
      if self.bezi == 1:  
        host = self.host.get()
        passwd = ""
        interval = self.time.get()
        start = timer()
        if args.multi is not None:
            instanci = int(args.multi)
        else:
            instanci = 1
        for i in range(instanci):    
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((host, self.controlport))
                s.send(("AUTHENTICATE \"supertajneheslo\"").encode('ascii') + b"\r\n")
                s.send(("GETINFO circuit-status").encode('ascii') + b"\r\n")
                circ = s.recv(8192).decode("utf-8")
                try:
                    with open("circ.txt", "w") as f:
                        f.write(circ)  
                        f.close()
                
                    with open("circ.txt", "r") as f:
                        result = f.readlines()
                        self.debug(result)
                        
                        for i in result:
                            d = re.findall(r'\b\d+\b', i.split(" BUILT ")[0])
                            for q in d:
                                self.debug(q)
                                if q != "250":
                                    s.send(("closecircuit %s" % q).encode('ascii') + b"\r\n")
                                    data = s.recv(128)
                                    if data == b'250 OK\r\n':
                                        logging.debug("Killing previous circuit ID %s " % q)                       
                        f.close()
                        
                    with open("circ.txt", "w") as f:
                        f.write("ok") 
                        f.close()
                    
                    os.remove('circ.txt')
                except:
                    pass
                s.send(("signal NEWNYM").encode('ascii') + b"\r\n")
                s.send(("QUIT").encode('ascii') + b"\r\n")
                s.close()
                self.failed = 0
                status = "OK"
                
            except:
                self.failed = self.failed + 1
                status = "FAILED"
                if self.failed == self.maxfailed:
                    self.write("Too many failed attempts.\n", "error", 1)
                    self.ident = random.random()
                    self.stoptor()
                
            logging.info("Requesting new IP %s:%s %s" % (host, proxy, status))    
            self.controlport = self.controlport + 1
            exec('self.proxystatus_' + str(proxy) + ' = status')
            proxy = proxy + 1
        
        self.controlport = 15000
        proxy = 9050        
        

