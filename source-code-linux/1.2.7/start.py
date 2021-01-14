#! /usr/bin/env python

#import vsech potrebnych modulu
import tkinter.ttk, random, _thread, time, tkinter.scrolledtext, socket, re, logging, os,sys, multiprocessing, subprocess, pycurl, io, argparse, urllib3, string, json, urllib.request, configparser
from tkinter import *
from timeit import default_timer as timer
from datetime import datetime
from urllib3.contrib.socks import SOCKSProxyManager

#nastaveni debug level pro urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)
urllib3.disable_warnings()

#verze programku + doplnky

version = "1.2.7"
build = 2

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
if not os.path.exists(logchanger):
    with open(logchanger, 'w'):
        pass
if not os.path.exists(logtor):
    with open(logtor, 'w'):
        pass    
c = 1 

#nastavitelne argumenty programku
parser = argparse.ArgumentParser(add_help=False)  
parser.add_argument("-h", "--help", help="this help", action='store_true',required=False)
parser.add_argument("-a", "--auto", type=int, required=False, help="-a 10   change ip every 10 seconds after program start")
parser.add_argument("-d", "--debug", help="start debug logging", action='store_true')
parser.add_argument("-m", "--multi", type=int, required=False, help="-m 5   run 5 different TOR instances", choices=range(1,101))
parser.add_argument("-p", "--publicAPI", action='store_true', required=False, help="bind API to 0.0.0.0 instead of 127.0.0.1")
parser.add_argument("-c", "--country", type=str, required=False, help="-c cz,sk,us   select czech republic, slovakia and united states country")
parser.add_argument("-n", "--noupdate", action='store_true', required=False, help="disable check for update")
parser.add_argument("-b", "--bridges", action='store_true', required=False, help="use bridges by default")
parser.add_argument("-g", "--nogui", help="run without GUI - control through API", action='store_true',required=False)
args = parser.parse_args()   

#trida pro smerovani chyb do devnull
class DevNull:
    def write(self, msg):
        pass

#trida tkinter
class IpChanger(Tk):

    #definice rozhrani aplikace
    def __init__(self):  
        Tk.__init__(self)
######### ZACATEK PROMENNYCH
        #definice pro aplikaci, nazev, ruzne hodnoty
        global start
        self.title("TOR IP Changer | Created by Seva | v%s-%s" % (version,build))
        self.host = StringVar()
        self.port = IntVar()
        self.proxy = IntVar()
        self.time = DoubleVar()
        self.timeout = DoubleVar()
        self.controlport = 15000
        self.control = 15000
        self.appPORT = 14999
        self.proxy = 9050
        self.lastver = version
        if args.publicAPI is not True:
          self.appHOST = "127.0.0.1"
          self.bindtype = "local"
        else:
          self.appHOST = "0.0.0.0"
          self.bindtype = "public"
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
        self.countries = ['ac','af','ax','al','dz','ad','ao','ai','aq','ag','ar','am','aw','au','at','az','bs','bh','bd','bb','by','be','bz','bj','bm','bt','bo','ba','bw','bv','br','io','vg','bn','bg','bf','bi','kh','cm','ca','cv','ky','cf','td','cl','cn','cx','cc','co','km','cg','cd','ck','cr','ci','hr','cu','cy','cz','dk','dj','dm','do','tp','ec','eg','sv','gq','ee','et','fk','fo','fj','fi','fr','fx','gf','pf','tf','ga','gm','ge','de','gh','gi','gr','gl','gd','gp','gu','gt','gn','gw','gy','ht','hm','hn','hk','hu','is','in','id','ir','iq','ie','im','il','it','jm','jp','jo','kz','ke','ki','kp','kr','kw','kg','la','lv','lb','ls','lr','ly','li','lt','lu','mo','mk','mg','mw','my','mv','ml','mt','mh','mq','mr','mu','yt','mx','fm','md','mc','mn','me','ms','ma','mz','mm','na','nr','np','an','nl','nc','nz','ni','ne','ng','nu','nf','mp','no','om','pk','pw','ps','pa','pg','py','pe','ph','pn','pl','pt','pr','qa','re','ro','ru','rw','ws','sm','st','sa','uk','sn','rs','sc','sl','sg','sk','si','sb','so','as','za','gs','su','es','lk','sh','kn','lc','pm','vc','sd','sr','sj','sz','se','ch','sy','tw','tj','tz','th','tg','tk','to','tt','tn','tr','tm','tc','tv','ug','ua','ae','gb','uk','us','um','uy','uz','vu','va','ve','vn','vi','wf','eh','ye','zm','zw']
        self.countries.sort()
        self.countries.insert(0, 'random')
        self.relaysNumber = IntVar()
        self.relaysNumber.set(0)
        self.countBezi = 0
        self.beziRepair = 0
        self.apistarted = False
        self.programFirstStart = True
        self.tmpCountries = ""
        self.debuglevel = 0
        self.tailexe = "tail"
        self.noUpdate = False
        if args.noupdate is True:
            self.noUpdate = True
        self.settingsIni = "settings.ini"
        self.ipresolver = "http://checkip.amazonaws.com"
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.resizable(width = False, height = True)  
        #definice rozmeru aplikace  
        self.frame = Frame(self)
        self.minsize(500,418)
        #self.maxsize(500,418)
        
        if args.nogui is True:
            self.withdraw()


        #definice pro menu
        self.menubar = Menu(self)
        
        #definice pro menu TOR server
        self.tormenu = Menu(self, tearoff=0)
        self.tormenu.add_command(label="Start", command=self.prestart)
        self.tormenu.add_command(label="Stop", command=self.stoptor, state="disabled")
        self.tormenu.add_command(label="Restart", command=self.restarttor)
        self.tormenu.add_command(label="Check & Repair", command=self.repairtor)
        self.menubar.add_cascade(label="TOR server".ljust(10), menu=self.tormenu)
         
        #definice pro menu IP Changer 
        self.changermenu = Menu(self, tearoff=0)
        self.changermenu.add_command(label="Start", state="disabled", command=self.start)
        self.changermenu.add_command(label="Stop", state="disabled", command=self.stop)
        self.changermenu.add_command(label="Just once", state="disabled", command=self.justonce)
        self.menubar.add_cascade(label="IP changer".ljust(10), menu=self.changermenu)
        
        #definice pro menu Logs
        self.logmenu = Menu(self, tearoff=0)
        self.logmenu.add_command(label="Changelog", command=self.changelog)
        self.logmenu.add_command(label="Show IPCHANGER debugging console", command=self.showlogipchanger)
        self.logmenu.add_command(label="Show TOR debugging console", command=self.showlogtor)
        self.logmenu.add_command(label="Open log directory", command=self.opendirectory)
        self.menubar.add_cascade(label="Logs".ljust(10), menu=self.logmenu)
        
        #definice pro menu Options
        self.optionmenu = Menu(self, tearoff=0)
        self.optionmenu.add_command(label="Settings".ljust(10), command=self.configwindow)
        self.optionmenu.add_command(label="Clean output", command=self.clean)    
        #self.optionmenu.add_command(label="Recount relays", command=self.countAllRelays)    
        self.menubar.add_cascade(label="Options".ljust(20), menu=self.optionmenu)
        
        #prazdne neviditelne tlacitko pro odsazeni
        self.blankmenu = Menu(self, tearoff=0)
        self.menubar.add_cascade(label="".ljust(10), menu=self.blankmenu, state="disabled")

        #definice pro menu Help
        self.helpmenu = Menu(self, tearoff=0)
        self.helpmenu.add_command(label="Help", command=self.help)
        if self.noUpdate is False:
            self.helpmenu.add_command(label="Check updates", command=self.buttonupdate)
        self.helpmenu.add_command(label="About", command=self.aboutwhat)
        self.menubar.add_cascade(label="Help".ljust(15), menu=self.helpmenu)
        
        self.config(menu=self.menubar)
        self.menubar = Menu
        
        def get_random_alphanumeric_string(length):
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(length))
            return result_str
        
        if args.multi is not None:
            self.maxfailed = args.multi + 3
            for i in range(args.multi):
                exec('self.controlPassword_' + str(i) + ' = StringVar()')  
                exec('self.controlPassword_' + str(i) + '.set("' + get_random_alphanumeric_string(16) + '")')
                exec('self.lang_' + str(i) + ' = StringVar()')  
                if args.country is not None:
                    
                    exec('self.lang_' + str(i) + '.set("' + args.country + '")')
                else:
                    exec('self.lang_' + str(i) + '.set("random")')
                
                exec('self.useBridges_' + str(i) + ' = BooleanVar()')
                
        else:
            self.maxfailed = 3
            self.lang_0 = StringVar()
            self.controlPassword_0 = StringVar()
            self.controlPassword_0.set(get_random_alphanumeric_string(16))
            if args.country is not None:
                self.lang_0.set(args.country)
            else:
                self.lang_0.set('random')
            
            self.useBridges_0 = BooleanVar()
              
        self.logtorm = datetime.now().strftime('Logs/tor_%Y_%m_%d_%H_%M_%S.txt')
        
        if args.debug is True:
            self.debuglevel = 1

        #definice pro debug level aplikace pokud pouzit parametr -d
        if self.debuglevel == 1:
            logging.basicConfig(filename=logchanger,level=logging.DEBUG,format='%(asctime)s.%(msecs)03d <%(funcName)s:%(lineno)d> %(message)s', datefmt='%b %d %H:%M:%S')
            self.tordebuglevel = "debug"
        else:            
            logging.basicConfig(filename=logchanger,level=logging.INFO,format='%(asctime)s.%(msecs)03d %(message)s', datefmt='%b %d %H:%M:%S')
            self.tordebuglevel = "notice"
            sys.stderr = DevNull()
        
        
        
        #definice stylu progressbaru, zmena barev a tloustka, maximalni hodnoty
        s = tkinter.ttk.Style()
        s.theme_use("default")
        s.configure("red.Horizontal.TProgressbar", foreground='red', background='red', thickness=1)
        s.configure("orange.Horizontal.TProgressbar", foreground='orange', background='orange', thickness=1)
        s.configure("green.Horizontal.TProgressbar", foreground='green', background='green', thickness=1)
        s.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue', thickness=1)
        self.statusBarText = StringVar()
        self.statusBar = Entry(self, textvariable=self.statusBarText,state=DISABLED)
        self.statusBarText.set("")
        self.statusBar.grid(row=0,column=1,sticky="EW")
        self.progressbar = tkinter.ttk.Progressbar(self, orient="horizontal",mode ="determinate", style="blue.Horizontal.TProgressbar", length = 500)
        self.progressbar.grid(row=1,column=1,sticky="NEWS")
        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0
        self.progressbar2 = tkinter.ttk.Progressbar(self, orient="horizontal",mode ="determinate", style="blue.Horizontal.TProgressbar", length = 500)
        self.progressbar2.grid(row=1,column=1,sticky="NEWS",pady=(0,4))
        self.progressbar2["maximum"] = 60
        self.progressbar2["value"] = 0
        #self.progressStatus = Label(self, text = "0%",bg='grey')
        #self.progressStatus.grid(row=4,column=1)
        #definice stylu pseudoconsole v aplikaci kam se vypisuji veskere veci
        self.output = tkinter.scrolledtext.ScrolledText(self, foreground="green", background="black", highlightcolor="white", highlightbackground="purple", wrap=WORD, width=60)
        self.output.grid(row=2, column=1,sticky="NEWS")
        self.write("Thank you for using TOR IP changer\n", "white", 0)
        self.write("Iam not responsible for any causalities or whatever\n", "white", 0)
        
        self.readConfigAndSetValues()
        _thread.start_new_thread(self.startthings, ())  
        if args.debug is True:
            _thread.start_new_thread(self.showlogipchanger, ())
            time.sleep(1)
            _thread.start_new_thread(self.showlogtor, ())
        
######### KONEC PROMENNYCH            
######### ZACATEK FUNKCI

    # funkce pro precteni a nastaveni hodnot z configu
    def readConfigAndSetValues(self):
        try:
            config = configparser.ConfigParser()
            if config.read(self.settingsIni):
                interval = config['DEFAULT']['interval']
                disableUpdates = config['DEFAULT']['disableupdates']
                auto = config['DEFAULT']['auto']
                if auto == "yes":
                    self.auto = 1
                else:
                    self.auto = 0
                if disableUpdates == "yes":
                    self.noUpdate = True
                else:
                    self.noUpdate = False
                if args.noupdate is True:
                    self.noUpdate = True
                self.time.set(int(interval))
                if args.auto is not None:
                    self.auto = 1
                    self.time.set(args.auto)
                
                instances = 1
                if args.multi is not None:
                    instances = args.multi
                self.debug("instances: %s" % instances)
                for i,section in enumerate(config.sections()):
                    self.debug(i)
                    if i > instances-1:
                        break
                    bridge = eval("config['%s']['bridge']" % section)
                    country = eval("config['%s']['country']" % section)
                    
                    if country is not None:
                        exec('self.lang_' + str(i) + '.set("'+str(country)+'")')
                    if args.country is not None:
                        exec('self.lang_' + str(i) + '.set("'+str(args.country)+'")')

                    if bridge == "yes":
                        exec('self.useBridges_' + str(i) + '.set("True")')  
                    else:
                        exec('self.useBridges_' + str(i) + '.set("False")')  
                    
                    if args.bridges is True:
                        exec('self.useBridges_' + str(i) + '.set("True")')

            elif not os.path.exists(self.settingsIni):
                    config = configparser.ConfigParser()
                    config['DEFAULT'] = {}
                    if args.auto is not None:
                        config['DEFAULT']['interval'] = '%s' % int(args.auto)
                    else:
                        config['DEFAULT']['interval'] = '%s' % int(self.time.get())
                    if args.noupdate is False:
                        config['DEFAULT']['disableupdates'] = 'no'
                    else:
                        config['DEFAULT']['disableupdates'] = 'yes'
                    if args.auto is not None:
                        config['DEFAULT']['auto'] = 'yes'
                    else:
                        config['DEFAULT']['auto'] = 'no'
                    config['127.0.0.1:9050'] = {}
                    if args.bridges is not True:
                        config['127.0.0.1:9050']['bridge'] = 'no'
                    else:
                        config['127.0.0.1:9050']['bridge'] = 'yes'
                        exec('self.useBridges_0.set("True")')  
                    if args.country is not None:
                        config['127.0.0.1:9050']['country'] = '%s' % args.country
                    else:
                        config['127.0.0.1:9050']['country'] = '%s' % self.lang_0.get()
                    with open(self.settingsIni, 'w') as configfile:
                        config.write(configfile)        

        except Exception as e:
            self.debug(e)

    #funkce pro spusteni overeni chybejicich souboru pro chod TORa
    def startcheck(self):
        self.progressbar['maximum'] = 100
        self.progressbar['value'] = 0
        self.progressbar['style'] = "blue.Horizontal.TProgressbar"
        _thread.start_new_thread(self.checkmissingfiles, ())
        
    #funkce pro zadost o jednu zmenu ip adresy
    def once(self):
        self.IPchanged = 1
        if args.multi is not None:
            self.IPchanged = args.multi
        self.IPfetched = 0
        self.newIP()
        self.IPandlatency()
        

    # funkce pro spusteni funkce na zadost o jednu zmenu ip adresy ve vlakne
    def justonce(self):
        _thread.start_new_thread(self.once, ())
        
    # funkce pro spusteni funkce opravy chybejicich nebo poskozenych tor souboru ve vlakne
    def repairtor(self):
        _thread.start_new_thread(self.repairmissingfiles, ())

    # funkce pro spusteni funkce restartu tor ve vlakne
    def restarttor(self):
        _thread.start_new_thread(self.threadRestartTor, ())

    # funkce pro restart tor
    def threadRestartTor(self):
        self.stoptor()
        time.sleep(2)
        self.checkmissingfiles()

    #funkce pro overeni chybejicich souboru pro chod TORa, a nasledne jejich stazeni 
    def checkmissingfiles(self):
        if not os.path.exists(tordirectory):
            os.makedirs(tordirectory)
        self.write("------------------------------------------------------------", "error", 1)
        self.write("Checking files. \n", "error", 1)
        try:
            geoip = "https://raw.githubusercontent.com/torproject/tor/master/src/config/geoip"            
            geoip6 = "https://raw.githubusercontent.com/torproject/tor/master/src/config/geoip6"
            torfiles = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/files.txt"
            tordir = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/"

            http = urllib3.PoolManager()
            r = http.request('GET', torfiles)
            obsah = r.data.decode('utf-8')
            self.file=""
            for o in obsah.split():
                if o == "bridges.txt":
                    if not os.path.exists("Tor/%s" % o):
                        self.missing = self.missing + 1
                        self.download("%s%s" % (tordir, o), None, "Tor")

            if not os.path.exists("Tor/geoip"):
              self.missing = self.missing + 1
              self.download("https://raw.githubusercontent.com/torproject/tor/master/src/config/geoip", None, "Tor")
            if not os.path.exists("Tor/geoip6"):
              self.missing = self.missing + 1
              self.download("https://raw.githubusercontent.com/torproject/tor/master/src/config/geoip6", None, "Tor")
            
            if self.missing != 1:
                self.write("Missing files downloaded\n","green",1)    
            else:
                self.write("No missing files\n","green",1)
            self.starttor()
            self.missing = 1
        except Exception as e:
            self.debug(e)
            self.write("Failed...repeating \n", "error", 1)
            self.failed = self.failed + 1
            if self.failed == 3:
                self.write("Cannot download Tor files\n", "error", 1)
                return
            time.sleep(1) 
            _thread.start_new_thread(self.startcheck, ())           
        self.write("------------------------------------------------------------", "error", 1)

    # funkce pro spocitani relay podle definovane zeme nebo pro vsechny zeme
    def countRelays(self, country=None):
        if country is not None and country != "random":
            country = re.sub('[\(\)\{\}<>]', '', country)
            cc = 0
            for c in country.replace(",", " ").split():
                url = "https://onionoo.torproject.org/summary?search=country:%s" % str(c)
                http = urllib3.PoolManager()
                r = http.request('GET', url)
                obsah = r.data.decode('utf-8')
                jsonobsah = json.loads(obsah)
                pocet = len(jsonobsah['relays'])
                cc = cc + pocet
            pocet = cc

            if pocet >= 1:
                color = "orange"
            else:
                color = "error"
            if self.tmpCountries != country:
                text = "Relays in %s: %s" % (country.upper(), pocet)
                #self.statusBarText.set(text)
                self.write("%s\n" % text, color, 1)
                self.tmpCountries = country

            if pocet == 0:
                self.write("You won't be able to connect, please select another country\n", "error", 1)
        else:
            if self.relaysNumber.get() == 0:
                self.countAllRelays()

    # funkce pro spocitani relay pro vsechny zeme            
    def countAllRelays(self):
        _thread.start_new_thread(self.threadCountAllRelays, ())    

    def threadCountAllRelays(self):
        self.debug("looking for relays: self.countBezi=%s" % self.countBezi)
        if self.countBezi == 0:
            self.countBezi = 1
            while True:
                self.debug("looking for relays: start")
                try:
                    self.dopocitano = False
                    def pocitej():
                        try:
                            url = "https://onionoo.torproject.org/summary"
                            http = urllib3.PoolManager()
                            r = http.request('GET', url)
                            obsah = r.data.decode('utf-8')
                            jsonobsah = json.loads(obsah)
                            c = len(jsonobsah['relays'])
                            self.relaysNumber.set(c)
                            self.dopocitano = True
                            text = "%s relays in Tor network" % c
                            self.statusBarText.set(text)
                        except:
                            self.dopocitano = True
                            pass
                    _thread.start_new_thread(pocitej,())
                    tmpstatus = self.statusBarText.get()
                    self.statusBarText.set("%s" % tmpstatus)
                    while not self.dopocitano is True:
                        self.statusBarText.set("%s" % tmpstatus)
                        if self.dopocitano is True:
                            self.statusBarText.set("%s" % tmpstatus)
                            break
                        time.sleep(0.1)
                        for i in range(3):
                            self.statusBarText.set("%s." % self.statusBarText.get())
                            time.sleep(0.1)
                        time.sleep(0.1)
                    
                except Exception as e:
                    self.statusBarText.set("Can't count relays right now")
                    self.debug(e)
                self.debug("looking for relays: end, waiting 60 seconds")
                start = timer()
                progress = 0
                max = 60
                self.progressbar2['max'] = max
                while not progress > max:
                    progress = timer() - start
                    self.progressbar2['value'] = max - progress
                    time.sleep(0.01)

    
    def repairmissingfiles(self):
        if self.beziRepair == 0:
            _thread.start_new_thread(self.stoptor, ())
            self.beziRepair = 1
            if not os.path.exists(tordirectory):
                os.makedirs(tordirectory)
            self.write("------------------------------------------------------------", "error", 1)
            self.write("Checking files. \n", "error", 1)
            try:
                geoip = "https://raw.githubusercontent.com/torproject/tor/master/src/config/geoip"            
                geoip6 = "https://raw.githubusercontent.com/torproject/tor/master/src/config/geoip6"
                bridges = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/bridges.txt"
                tordir = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/"

                self.write("Checking file bridges.txt\n", "orange", 1)    
                if not self.checkFileSize(bridges, None, "Tor") is True:
                    self.missing = self.missing + 1
                    self.download(geoip, None, "Tor")
                self.write("Checking file geoip\n", "orange", 1)    
                if not self.checkFileSize(geoip, None, "Tor") is True:
                    self.missing = self.missing + 1
                    self.download(geoip, None, "Tor")
                self.write("Checking file geoip6\n", "orange", 1)    
                if not self.checkFileSize(geoip6, None, "Tor") is True:
                    self.missing = self.missing + 1
                    self.download(geoip6, None, "Tor")
                
                if self.missing != 1:
                    self.write("Files (re)downloaded\n","green",1)    
                else:
                    self.write("No repair needed\n","green",1)
                #self.starttor()
                self.missing = 1
                self.beziRepair = 0
            except Exception as e:
                self.beziRepair = 0
                self.debug(e)
                self.write("Failed...repeating \n", "error", 1)
                self.failed = self.failed + 1
                if self.failed == 3:
                    self.write("Cannot download Tor files\n", "error", 1)
                    return
                time.sleep(1) 
                #_thread.start_new_thread(self.startcheck, ())           
                    
        
    #funkce tlacitka na otevreni slozky s logy
    def opendirectory(self):
        return
        os.system(r'explorer Logs')
    
    #funkce na vyvolani noveho okna options > settings, a jeho nalezitosti
    def configwindow(self):
        def save():
            if self.newWindow:
                config = configparser.ConfigParser()
                try:
                    ee = int(self.time.get())
                    if ee < 10:
                        self.time.set('10')
                    else:
                        self.time.set(ee)
                    config['DEFAULT']['interval'] = '%i' % ee
                    if self.checkvarUpdates.get() == 1:
                        disableUpdates = "yes"
                        self.noUpdate = True
                    else:
                        disableUpdates = "no"
                        self.noUpdate = False
                    config['DEFAULT']['disableupdates'] = '%s' % disableUpdates
                    if self.checkvarAuto.get() == 1:
                        auto = "yes"
                        self.auto = 1
                    else:
                        auto = "no"
                        self.auto = 0
                    config['DEFAULT']['auto'] = '%s' % auto
                    
                    if args.multi is not None:
                        for i in range(args.multi):    
                            port = 9050 + i
                            exec('self.lang_' + str(i) + '.set(self.tor_' + str(i) + '.get())')
                            exec('self.useBridges_' + str(i) + '.set(self.useBridges_' + str(i) + '.get())')  
                            exec('config[\'127.0.0.1:' + str(port) + '\'] = {}')
                            if eval("self.useBridges_%s.get()" % str(i)) == 1:
                                exec('config[\'127.0.0.1:' + str(port) + '\'][\'bridge\'] = \'yes\'')
                            else:
                                exec('config[\'127.0.0.1:' + str(port) + '\'][\'bridge\'] = \'no\'')                                
                            lang = eval('self.tor_' + str(i) + '.get()')
                            exec('config[\'127.0.0.1:' + str(port) + '\'][\'country\'] = \''+ str(lang) +'\'')
                            
                    else:
                        exec('self.lang_0.set(self.tor_0.get())')  
                        exec('self.useBridges_0.set(self.useBridges_0.get())')  
                        exec('config[\'127.0.0.1:9050\'] = {}')
                        if eval("self.useBridges_0.get()") == 1:
                            exec('config[\'127.0.0.1:9050\'][\'bridge\'] = \'yes\'')
                        else:
                            exec('config[\'127.0.0.1:9050\'][\'bridge\'] = \'no\'')                                
                        lang = eval('self.tor_0.get()')
                        exec('config[\'127.0.0.1:9050\'][\'country\'] = \''+ str(lang) +'\'')
                    with open(self.settingsIni, 'w') as configfile:
                        config.write(configfile)
                    
                    self.newWindow.destroy()   
                except Exception as e:
                    self.debug(e)
                    pass
                self.newWindow = None 
        
        w = 200
        h = 200
        r = 1
        cl = 0
        cc = 1
        proxy = 9050
        self.newWindow = Toplevel(self)
        self.newWindow.title("Settings")
        self.newWindow.resizable(width = False, height = False)  

        Label(self.newWindow, text = ' ').grid(row=0,column=6)
        Label(self.newWindow, text = ' ').grid(row=1,column=6)
        Label(self.newWindow, text = ' ').grid(row=2,column=6)
        
        Label(self.newWindow, text = 'Interval:').place(x=8,y=2)
        if self.meni == 1:
            interval = Entry(self.newWindow, textvariable = self.time, width = 5, state="disabled")
        else:
            interval = Entry(self.newWindow, textvariable = self.time, width = 5, state="normal")    
        #interval.grid(row=r,column=1)
        interval.place(x=65,y=3)

        #Label(self.newWindow, text = 'sec').grid(row=r,column=1) 
        Label(self.newWindow, text = 'sec').place(x=106,y=2)

        if self.auto == 1:
            self.checkvarAuto = IntVar(value=1)
        else:
            self.checkvarAuto = IntVar(value=0)
        if args.multi is not None:
            x = 180
        else:
            x = 145
        self.checkButtonAuto = Checkbutton(self.newWindow, text = "Auto start", variable = self.checkvarAuto, onvalue = 1, offvalue = 0)
        self.checkButtonAuto.place(x=x,y=0)
        if self.noUpdate is True:
            self.checkvarUpdates = IntVar(value=1)
        else:
            self.checkvarUpdates = IntVar(value=0)
        
        self.checkButtonUpdates = Checkbutton(self.newWindow, text = "Disable updates", variable = self.checkvarUpdates, onvalue = 1, offvalue = 0)
        self.checkButtonUpdates.place(x=x,y=20)

        r = r + 1
        ttk.Separator(self.newWindow, orient=HORIZONTAL).place(x=0, y=40, relwidth=1)
        ttk.Separator(self.newWindow, orient=HORIZONTAL).place(x=0, y=41, relwidth=1)



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
                
                if eval("self.lang_%s.get()" % str(i)) == "random":
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
            
            
            
            if self.lang_0.get() == "random":
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
            
        
    def updateWindow(self):
        self.newWindow3 = Toplevel(self)
        self.newWindow3.title("Update")
        
        Label(self.newWindow3, text = 'Do you want to update ?').grid(row=1,column=1,columnspan=3,padx=(20, 20))
        
        def close():
            if self.newWindow3:
                try:
                    self.newWindow3.destroy()   
                except ():
                    pass
                self.newWindow3 = None   
        
        def no():
            close()    

        def yes():
            _thread.start_new_thread(self.downloadAndUpdate, ())
            close()

        Button(self.newWindow3, text = "Yes", command=yes,width=5).grid(row=2,column=2,padx=(20, 20))
        Button(self.newWindow3, text = "No", command=no,width=5).grid(row=2,column=3,padx=(20, 20))

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
                self.download("https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/%s/%s" % (version,help), 1)
            with open('help.txt', 'r') as f:
                self.write(f.read(), "green", 1)
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

    #funkce na spusteni tail a vypis logu IPCHANGER live        
    def showlogipchanger(self):
        self.logmenu.entryconfig(1, label = "Hide IPCHANGER debugging console", command=self.hidelog)
        try:
            _thread.start_new_thread(self.tailchanger, ())
        except:
            pass

    #funkce na spusteni tail a vypis logu TOR live        
    def showlogtor(self):
        self.logmenu.entryconfig(2, label = "Hide TOR debugging console", command=self.hidelog)
        try:
            _thread.start_new_thread(self.tailtor, ())
        except:
            pass
    
    #funkce na tail
    def tailchanger(self):
        try:
            os.system("tail -q -f %s" % (logchanger))
        except:
            pass

    def tailtor(self):
        try:
            os.system("tail -q -f %s" % (logtor))
        except:
            pass
        
    #funkce na schovani logu live    
    def hidelog(self):
        self.logmenu.entryconfig(1, label = "Show IPCHANGER debugging console", command=self.showlogipchanger)
        self.logmenu.entryconfig(2, label = "Show TOR debugging console", command=self.showlogtor)
        os.system(r'killall tail')
        
    #funkce na vypsani debug infa aplikace do console a logu
    def appInfo(self):
        key = self.ident
        while key == self.ident:
            logging.info("IPchanged=%s" % self.IPchanged)
            logging.info("IPresolved=%s" % self.IPfetched)
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
                reply += b'changeip onceport N | change ip once for port N\r\n'
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
                        self.IPchanged = 1
                        if args.multi is not None:
                            self.IPchanged = args.multi
                        self.IPfetched = 0
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
                elif rozdel[0] == 'changeip' and rozdel[1] == 'onceport':
                    if args.multi is not None:
                        if self.bezi == 1:
                            reply = b'changing ip once for port\r\n'
                            self.IPchanged = 1
                            if args.multi is not None:
                                self.IPchanged = args.multi
                            self.IPfetched = 0
                            self.newIP(rozdel[2].strip("\r\n"))
                            self.IPandlatency(rozdel[2].strip("\r\n"))
                        else:
                            reply = b'tor server not running\r\n'        
                    else:
                        reply = b'use only with ipchanger -m\r\n'        
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
        try:
            _thread.start_new_thread(self.update, ())
        except:
            pass
        
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
        self.controlport = 15000
        self.control = 15000
        self.appPORT = 14999
        self.proxy = 9050
        self.tormenu.entryconfig(0, state="normal")
        self.tormenu.entryconfig(1, state="disabled")
        if self.meni == 1:
          _thread.start_new_thread(self.stop, ())
        
        os.system(r'killall tor')
        
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
        self.changermenu.entryconfig(2, state="disabled")
        
    #funkce k pouziti bridges
    def bridges(self, identify=None):
        if eval("self.useBridges_%s.get()" % str(identify)) == 1:
            with open('Tor/bridges.txt', 'r') as f:
                self.bridge = '--UseBridges 1 '
                self.bridge += '--ClientTransportPlugin "obfs2,obfs3,obfs4 exec /usr/bin/obfs4proxy managed" '
                self.bridge += '--clientTransportPlugin "meek exec /usr/bin/obfs4proxy" '
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

    def generateControlPasswordHash(self, password, identify=None):
        proc = subprocess.Popen('tor --quiet --hash-password "%s"' % (password), stdout = subprocess.PIPE, shell=True)
        (out,err) = proc.communicate()
        exec('self.controlPasswordHash_' + str(identify) + ' = StringVar()')  
        exec('self.controlPasswordHash_' + str(identify) + '.set(out.decode("utf-8").rstrip())')  
        
    def get_controlPasswordHash(self, identify=None):
        return eval("self.controlPasswordHash_%s.get()" % identify)

    def get_controlPassword(self, identify=None):
        return eval("self.controlPassword_%s.get()" % identify)
        
    #funkce multiinstanci tora        
    def multiTor(self, identify=None):
        self.logtorm = datetime.now().strftime('Logs/tor_%Y_%m_%d_%H_%M_%S.txt')
        files = self.logtorm
        self.bridges(identify)
        exec('self.generateControlPasswordHash(self.controlPassword_' + str(identify) + '.get(), str(identify))')  
        if eval("self.lang_%s.get()" % str(identify)) == "random":
            options = ""
        else:
            language = eval("self.lang_%s.get()" % str(identify))
            cc = ""
            for c in language.replace(",", " ").split():
                cc += ",{%s}" % c
            
            self.debug(cc.lstrip(","))
            options = "--ExitNodes %s --StrictNodes 1" % cc.lstrip(",")
            self.debug(options)
            self.countRelays(str(language))
        os.system(r'(authbind --deep tor %s --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "%s" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log %s --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 %s | tee %s ) > /dev/null &' % (self.bridge, self.get_controlPasswordHash(identify),self.control,self.proxy,self.data,self.tordebuglevel,options,files))                

        self.control = self.control + 1
        self.proxy = self.proxy + 1
        self.b = self.b + 1
        self.data = "Data/tordata%s" % self.b
          

    def torGetInfo (self, port, password, command=None):
        host = self.host.get()
        if command is None:
            command = "QUIT"

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        authcmd = 'AUTHENTICATE "%s"' % password
        s.send((authcmd).encode('utf-8') + b"\r\n")
        s.send((command).encode('ascii') + b"\r\n")
        status = s.recv(8192).decode("utf-8")
        #self.debug(status)
        return status

    #funkce startu tora a jeho logu a urcovani procent v progressbaru 
    def tor(self):
        if args.multi is not None:
            file = self.logtorm
        else:
            file = logtor
        
        key = self.ident
        self.generateControlPasswordHash(self.controlPassword_0.get(), 0)
        if args.multi is not None:
            self.write("TOR server %s starting " % self.b, "green", 1)
            self.bridges('0')
            self.countRelays(str(self.lang_0.get()))
            if self.lang_0.get() == "random":
                options = ""
            else:
                countries = self.lang_0.get()
                cc = ""
                for c in countries.replace(",", " ").split():
                    cc += ",{%s}" % c
                
                self.debug(cc.lstrip(","))
                options = "--ExitNodes %s --StrictNodes 1" % cc.lstrip(",")
                self.debug(options)
            os.system(r'(authbind --deep tor %s --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "%s" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log %s --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --DNSport 53 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 %s | tee %s ) > /dev/null &' % (self.bridge, self.get_controlPasswordHash('0'), self.control,self.proxy,self.data,self.tordebuglevel,options, file))
        
            self.control = self.control + 1
            self.proxy = self.proxy + 1
            self.b = self.b + 1
            self.data = "Data/tordata%s" % self.b
            time.sleep(1.1)
            for m in range(args.multi-1):
                if not key == self.ident:
                    return  
                self.write("TOR server %s starting " % self.b, "green", 1)
                _thread.start_new_thread(self.multiTor, (self.b,))
                time.sleep(1.1)
                
        else:
            self.countRelays(str(self.lang_0.get()))
            self.write("TOR server starting ", "green", 1)
            self.bridges('0')
            self.write("Please wait ... \n", "green", 1)
            if self.lang_0.get() == "random":
                options = ""
            else:
                countries = self.lang_0.get()
                cc = ""
                for c in countries.replace(",", " ").split():
                    cc += ",{%s}" % c
                
                self.debug(cc.lstrip(","))
                options = "--ExitNodes %s --StrictNodes 1" % cc.lstrip(",")
                self.debug(options)
            os.system(r'(authbind --deep tor %s --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "%s" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log %s --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --DNSport 53 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 %s | tee %s ) > /dev/null &' % (self.bridge, self.get_controlPasswordHash('0'), self.control,self.proxy,self.data,self.tordebuglevel,options,file))

        timeout = 0
        count = 1    
        self.debug(self.tordebuglevel)
        controlPortConnected = 0
        tout = 2400
        toutout = 300
        tsleep = 0.1
        while not timeout==tout and key == self.ident:
            if not key == self.ident:
                return
            time.sleep(tsleep)
            if timeout % toutout == 0:
                if args.multi is not None:
                    self.write("TOR servers starting. Please wait ... \n", "yellow", 1)
            timeout = timeout + 1
            try:
                status = self.torGetInfo(15000, self.get_controlPassword(0), "GETINFO status/bootstrap-phase")
                statusresult = status.split("\r\n", 3)
                bootstrap = statusresult[1].split(" ", 5)
                progress = bootstrap[2]
                summary = statusresult[1]
                summarystatus = summary.split("=")
                progressnumber = progress.split("=", 2)
                boot = progressnumber[1]
                circuitstatus = self.torGetInfo(15000, self.get_controlPassword(0), "GETINFO status/circuit-established")
                circuitstatus = circuitstatus.split("\r\n",3)
                if not self.oldpercent == boot: 
                    self.write("%s%% - %s \n" % (boot,summarystatus[4].strip("\"")), "yellow", 0)
                    #logging.info("%s%% - %s" % (boot,status))
                    self.oldpercent = boot
                    logging.info("%s%% - %s - %s" % (boot,status,circuitstatus[1]))
                
                self.progressbar["value"] = float(boot)

                
                if (circuitstatus[1]) == "250-status/circuit-established=1":
                    #self.debug(circuitstatus[1])
                    self.write("TOR server started \n", "green", 1) 
                    self.write("DNS server started \n", "green", 1) 
                    self.progressbar["value"] = 100 
                    self.progressbar["style"] = "orange.Horizontal.TProgressbar"
                    self.bezi=1
                    self.changermenu.entryconfig(0, state="normal")
                    self.changermenu.entryconfig(1, state="disabled")
                    self.changermenu.entryconfig(2, state="normal")
                    
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
                    if self.auto == 1:
                        try:
                            _thread.start_new_thread(self.start, ())
                        except:
                            pass    
                    break          
                else:
                    pass
            except Exception as e:
                self.debug(e)
                pass
            
        else:                 
            self.write("TOR server timed out.\n", "error", 1) 
            self.progressbar["style"] = "red.Horizontal.TProgressbar"
            time.sleep(.1)
            self.stoptor()                
        
    #funkce na vycisteni vystupu
    def clean(self):
        self.output.delete('1.0', END)
        
    #funkce spusteni predbeznych veci po startu aplikace
    def buttonupdate(self):
        self.buttonup = 1
        _thread.start_new_thread(self.startthings,())

    def downloadAndUpdate(self):
        return

    #funkce kontroly verze aplikace, pokud novejsi verze zeptej se zda updatovat
    def update(self):
          try:
              if self.noUpdate is False:  
                self.write('This version:            %s-%s\n' % (version,build), "white", 1)
                http = urllib3.PoolManager()
                f = http.request('GET', 'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/version.txt') 
                self.lastver = f.data.decode('utf-8') 
                url = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/%s/dist.txt" % self.lastver
                u = url.replace("\n", "")
                linkurl = http.request('GET', u)
                link = linkurl.data.decode('utf-8') 
                f = http.request('GET', "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/%s/build.txt" % self.lastver)
                
                lastbuild = f.data.decode('utf-8') 
                self.write('Last available version:  %s-%s\n' % (self.lastver,lastbuild), "white", 1)
                v = version.replace(".", "")
                l = self.lastver.replace(".", "")
                if int(v) >= int(l):
                    if int(build) >= int(lastbuild):
                        self.write('No update required. \n', "white", 1)
                    else:
                        self.write('Update required !\n', 'red', 1)
                        self.updateWindow()
                elif int(v) < int(l):
                    self.write('Update required !\n', 'red', 1)
                    self.updateWindow()

              if self.programFirstStart is True:
                self.programFirstStart = False
                _thread.start_new_thread(self.motd, ())
                time.sleep(1)
                if self.buttonup == 0:
                    if args.auto is not None:
                        self.auto = 1
                    if self.auto == 1: 
                        self.write("Autostart ON, change every %s seconds \n" % int(self.time.get()), "green", 1)     
                        _thread.start_new_thread(self.prestart, ())
                    else:
                        if args.auto is not None:
                            self.auto = 1
                            if args.auto < 10:
                                args.auto = 10
                            self.time.set(args.auto)
                        else:
                            self.write("Autostart OFF. \n", "error", 1) 
                _thread.start_new_thread(self.countAllRelays, ())  
                time.sleep(0.1)
                if self.apistarted is False:
                    self.apistarted = True
                    _thread.start_new_thread(self.API, ())

       
                   
          except:
            pass      

    #funkce pro kontrolu velikosti souboru local vs url
    def checkFileSize(self, url=None, write=None, folder=None):
        from urllib.request import urlopen
        file_name = url.split('/')[-1]
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
            self.debug("file %s size local %s url size %s" % (file_name, totalLocalFileSize, totalLocalFileSize))
            return True
        else:
            self.debug("file %s size local %s url size %s" % (file_name, totalLocalFileSize, totalLocalFileSize))
            return False

    #funkce downloaderu pro stazeni souboru z internetu
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
                self.write("Downloading:  {:<30}{:>13} KB\n".format(file_name, int(round(tfs))), "error", 1)
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
        except Exception as e:
            logging.info("%s %s" % (url, e))

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
        self.changermenu.entryconfig(2, state="normal")

        _thread.start_new_thread(self.ipProc, ())  
        _thread.start_new_thread(self.appInfo, ())
            
    #funkce zastaveni zmeny IP
    def stop(self): 
        self.write('IP Changer stopping. Wait..\n', "error", 1)
        self.ident = random.random() 
        self.meni=0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed=0
        self.changermenu.entryconfig(0, state="disabled")
        self.changermenu.entryconfig(1, state="disabled")
        self.changermenu.entryconfig(2, state="disabled")
             
    #funkce na psani vystupu   
    def write(self, message, color, log):
        if args.nogui is not True:
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
        else:
            print(message.rstrip("\n"))
            if log == True:
                logging.info(message.rstrip("\n"))                                                      

    #funkce na psani debug do logu                                  
    def debug(self, message):
        if self.debuglevel == 1:
            global c
            try:
                logging.debug(message)  
            except:
                pass
    
    #funkce na zjisteni IP adresy z TOR site        
    def GetExternalIP(self, proxy=None, url=None): 
        if url is None:
            url = self.ipresolver
        timeout = self.timeout.get()
        file = "Data/tordata%s/ip.txt" % (proxy-9050)
        interval = int(self.time.get()-1)
        soc = SOCKSProxyManager('socks5://127.0.0.1:%s/' % proxy)
        s = soc.request('GET', url, timeout=urllib3.Timeout(connect=interval, read=interval), retries=False)
        d = s.data.decode('utf-8').split('\n')
        f = open(file, 'w')
        f.write(d[0])
        f.close()
        s.close()
        
            
        
        
    #funkce na zjisteni odezvy pro zjistenou IP adresu, nejdrive zavola zjisteni IP a nasledne provede overeni odezvy, a vypise vystup do aplikace        
    def IPandlatency(self, port=None):      
        if args.multi is not None:
          instanci = int(args.multi)
        else:
          instanci = 1
        host = "127.0.0.1"
        proxy = 9050   
        languagenumber = 0
        
        if port is not None:
            instanci = 1
            proxy = int(port)

        def fetching(proxy):
            languagenumber = proxy - 9050
            language = eval('self.lang_' + str(languagenumber) + '.get()')
            #if language == "random":
            #      language = ""  
            try:
              color = "white"
              self.GetExternalIP(proxy, self.ipresolver)  
              file = "Data/tordata%s/ip.txt" % languagenumber
              f = open(file, 'r')
              ip = f.read()
              ping = os.popen('ping -c 1 -w 1 %s' % ip)
              result = ping.readlines()
              msLine = result[-1].strip()
              latency = msLine.split(' = ')[-1] 
              cport = 5950 + proxy
              iptocountry = self.torGetInfo(cport, self.get_controlPassword(languagenumber), "GETINFO ip-to-country/%s" % ip)
              iptocountry = iptocountry.split("\r\n", 3)
              output = iptocountry[1].split(" ", 5)
              country = output[0].split("=")
              if latency == "Ping request could not find host None. Please check the name and try again.":
                  latency = "OFFLINE"
                  color = "red"
              
              try:
                  try:
                      ms = latency.split('ms')[0].split('/')[0].split(".")[0]
                      latency = "%sms" % ms
                  except:
                      latency = "####"
                      color = "orange"
              except:
                  ms = latency.split('ms')[0]
                  self.debug("ms except " + ms)
                  latency = "####"
                  color = "red"
              if len(language) > 6:
                  language = language.replace(language[6:], "...")
              if self.IPchanged > self.IPfetched:
                  self.write("|" + host.ljust(9) + ":" + str(proxy).ljust(5) + "|" + str(language).ljust(12) + "-> " + str(ip).rjust(16) + " |" + str(country[1]) + "|" + str(latency).rjust(6) + "|\n", color, 0)
                  logging.info("127.0.0.1:%s IP %s %s " % (proxy,ip,latency))
                  self.IPfetched = self.IPfetched + 1
              f.close()
              
              if self.bezi == 0:
                  return               
            except Exception as e:
              self.debug(e)
              status = eval("self.proxystatus_%s" % str(proxy))
              if self.bezi == 0 or self.meni == 0:
                  return
              
              if status == "FAILED":
                  status = "Changing FAILED"
              else:
                  status = "Changing OK - Resolving timeout"
              
              if len(language) > 6:
                  language = language.replace(language[6:], "...")
              self.write("|" + host.ljust(9) + ":" + str(proxy).ljust(5) + "|" + str(language).ljust(10) + " " + str(status).rjust(1) + "|\n", "error", 0)
              logging.info("127.0.0.1:%s failed - status: %s" % (proxy, status))
              self.IPfetched = self.IPfetched + 1
              pass
    
        
        for i in range(instanci):
              _thread.start_new_thread(fetching, (proxy,))
              proxy = proxy + 1
          
    #funkce startu zjistovani aktualni IP adresy ve smycce    
    def ip(self):
        key = self.ident
        while key == self.ident:
            if key != self.ident:
                break
            try:
                interval = self.time.get()
                start = timer()
                time.sleep(1)
                while not float(self.progressbar['value']) > float(interval)-1:
                    if key != self.ident:
                        break
                    time.sleep(0.01)
                if key != self.ident:
                    break
                self.IPandlatency()
                end = timer()
                result = (end - start)
                seconds = float(result)  
                #print(seconds)
                
            except:
                self.failed = self.failed + 1
                
        self.meni=0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed=0
        if self.bezi == 1:
            self.changermenu.entryconfig(0, state="normal")
            self.changermenu.entryconfig(1, state="disabled")
            self.changermenu.entryconfig(2, state="normal")
                        
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
              if args.multi is not None:
                  self.IPchanged = self.IPchanged + args.multi
              else:
                  self.IPchanged = self.IPchanged + 1
              self.meni=1
              timeout = 0
              interval = self.time.get()
              self.progressbar["maximum"] = interval
              self.progressbar["value"] = timeout
              start = timer()
              progress = 1
              _thread.start_new_thread(self.newIP, ())
              while not progress > interval:
                  progress = timer() - start
                  #print(progress)
                  if key != self.ident:
                      break
                  self.progressbar["style"] = "green.Horizontal.TProgressbar"
                  self.progressbar["maximum"] = interval
                  self.progressbar["value"] = interval - progress
                  time.sleep(0.01)
              
              
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
    def newIP(self, port=None):
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
        if port is not None:
            instanci = 1
            proxy = int(port)
            newcontrolport = 15000 - 9050 + int(port)
            self.controlport = int(newcontrolport)
        identify = proxy - 9050
        self.debug("identify: %s" % identify)
        
        for i in range(instanci):    
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((host, self.controlport))
                authcmd = 'AUTHENTICATE "%s"' % self.get_controlPassword(identify)
                s.send((authcmd).encode('utf-8') + b"\r\n")
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
            identify = identify + 1 
        
        self.controlport = 15000
        proxy = 9050  

######### KONEC FUNKCI