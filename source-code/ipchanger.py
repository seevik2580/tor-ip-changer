#! /usr/bin/env python

# import vsech potrebnych modulu
import sys, tkinter.ttk, random, _thread, time, tkinter.scrolledtext, socket, logging, os, argparse, urllib3, string, json, urllib.request, configparser, subprocess, sqlite3, webbrowser, re, ssl

if sys.platform == "win32":
    windows = True
    linux = False
elif sys.platform == "linux":
    import multiprocessing
    import signal
    linux = True
    windows = False
else:
    print("Platform %s not supported" % sys.platform)
    os._exit(1)

from functools import partial
from tkinter import *
from tkinter import ttk
from timeit import default_timer as timer
from datetime import datetime
from urllib3.contrib.socks import SOCKSProxyManager

# nastaveni debug level pro urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)
urllib3.disable_warnings()

# verze programku a cislo buildu
version = "1.3.0"
build = 8

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

# nastavitelne argumenty programku
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-h", "--help", help="this help", action='store_true', required=False)
parser.add_argument("-a", "--auto", type=int, required=False, help="-a 10   change ip every 10 seconds after program start")
parser.add_argument("-d", "--debug", help="start debug logging", action='store_true')
parser.add_argument("-m", "--multi", type=int, required=False, help="-m 5   run 5 different TOR instances", choices=range(1, 101))
parser.add_argument("-p", "--publicAPI", action='store_true', required=False, help="bind API to 0.0.0.0 instead of 127.0.0.1")
parser.add_argument("-c", "--country", type=str, required=False, help="-c cz,sk,us   select czech republic, slovakia and united states country")
parser.add_argument("-n", "--noupdate", action='store_true', required=False, help="disable check for update")
parser.add_argument("-b", "--bridges", action='store_true', required=False, help="use bridges by default")
parser.add_argument("-u", "--unique", action='store_true', required=False, help="always obtain unique ip address !experimental")
if linux:
    parser.add_argument("-g", "--nogui", help="run without GUI - control through API", action='store_true', required=False)
args = parser.parse_args()


# trida pro smerovani chyb do devnull
class DevNull:
    def write(self, msg):
        pass


# trida tkinter
class IpChanger(Tk):

    # definice rozhrani aplikace
    def __init__(self):
        Tk.__init__(self)
        ######### ZACATEK PROMENNYCH
        # definice pro aplikaci, nazev, ruzne hodnoty
        global start
        self.title("TOR IP Changer | Created by Seva | v%s-%s" % (version, build))
        self.host = StringVar()
        self.port = IntVar()
        self.proxy = IntVar()
        self.time = DoubleVar()
        self.timeout = DoubleVar()
        self.blacklist = IntVar()
        self.session = IntVar()
        self.postponetime = IntVar()
        self.controlport = 15000
        self.control = 15000
        self.appPORT = 14999
        self.proxy = 9050
        self.lastver = version
        self.lastbuild = build
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
        self.bezi = 0
        self.meni = 0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed = 0
        self.missing = 1
        self.buttonup = 0
        self.forall = 0
        self.oldpercent = None
        self.countries = ['ac', 'af', 'ax', 'al', 'dz', 'ad', 'ao', 'ai', 'aq', 'ag', 'ar', 'am', 'aw', 'au', 'at',
                          'az', 'bs', 'bh', 'bd', 'bb', 'by', 'be', 'bz', 'bj', 'bm', 'bt', 'bo', 'ba', 'bw', 'bv',
                          'br', 'io', 'vg', 'bn', 'bg', 'bf', 'bi', 'kh', 'cm', 'ca', 'cv', 'ky', 'cf', 'td', 'cl',
                          'cn', 'cx', 'cc', 'co', 'km', 'cg', 'cd', 'ck', 'cr', 'ci', 'hr', 'cu', 'cy', 'cz', 'dk',
                          'dj', 'dm', 'do', 'tp', 'ec', 'eg', 'sv', 'gq', 'ee', 'et', 'fk', 'fo', 'fj', 'fi', 'fr',
                          'fx', 'gf', 'pf', 'tf', 'ga', 'gm', 'ge', 'de', 'gh', 'gi', 'gr', 'gl', 'gd', 'gp', 'gu',
                          'gt', 'gn', 'gw', 'gy', 'ht', 'hm', 'hn', 'hk', 'hu', 'is', 'in', 'id', 'ir', 'iq', 'ie',
                          'im', 'il', 'it', 'jm', 'jp', 'jo', 'kz', 'ke', 'ki', 'kp', 'kr', 'kw', 'kg', 'la', 'lv',
                          'lb', 'ls', 'lr', 'ly', 'li', 'lt', 'lu', 'mo', 'mk', 'mg', 'mw', 'my', 'mv', 'ml', 'mt',
                          'mh', 'mq', 'mr', 'mu', 'yt', 'mx', 'fm', 'md', 'mc', 'mn', 'me', 'ms', 'ma', 'mz', 'mm',
                          'na', 'nr', 'np', 'an', 'nl', 'nc', 'nz', 'ni', 'ne', 'ng', 'nu', 'nf', 'mp', 'no', 'om',
                          'pk', 'pw', 'ps', 'pa', 'pg', 'py', 'pe', 'ph', 'pn', 'pl', 'pt', 'pr', 'qa', 're', 'ro',
                          'ru', 'rw', 'ws', 'sm', 'st', 'sa', 'uk', 'sn', 'rs', 'sc', 'sl', 'sg', 'sk', 'si', 'sb',
                          'so', 'as', 'za', 'gs', 'su', 'es', 'lk', 'sh', 'kn', 'lc', 'pm', 'vc', 'sd', 'sr', 'sj',
                          'sz', 'se', 'ch', 'sy', 'tw', 'tj', 'tz', 'th', 'tg', 'tk', 'to', 'tt', 'tn', 'tr', 'tm',
                          'tc', 'tv', 'ug', 'ua', 'ae', 'gb', 'uk', 'us', 'um', 'uy', 'uz', 'vu', 'va', 've', 'vn',
                          'vi', 'wf', 'eh', 'ye', 'zm', 'zw']
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
        self.tailexe = "tail.exe"
        self.noUpdate = False
        self.unique = False
        if args.unique is True:
            self.unique = True
        if args.noupdate is True:
            self.noUpdate = True
        self.settingsIni = "settings.ini"
        self.ipresolver = "http://checkip.amazonaws.com"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.resizable(width=False, height=True)
        # definice rozmeru aplikace
        self.frame = Frame(self)
        self.minsize(500, 418)
        # self.maxsize(500,418)
        if linux:
            if args.nogui is True:
                self.withdraw()

        # definice pro menu
        self.menubar = Menu(self)

        # definice pro menu TOR server
        self.tormenu = Menu(self, tearoff=0)
        self.tormenu.add_command(label="Start", command=self.prestart)
        self.tormenu.add_command(label="Stop", command=self.stoptor, state="disabled")
        self.tormenu.add_command(label="Restart", command=self.restarttor)
        self.tormenu.add_command(label="Check & Repair", command=self.repairtor)
        self.menubar.add_cascade(label="TOR server".ljust(10), menu=self.tormenu)

        # definice pro menu IP Changer
        self.changermenu = Menu(self, tearoff=0)
        self.changermenu.add_command(label="Start", state="disabled", command=self.startchange)
        self.changermenu.add_command(label="Stop", state="disabled", command=self.stopchange)
        self.changermenu.add_command(label="Just once", state="disabled", command=self.justonce)
        self.menubar.add_cascade(label="IP changer".ljust(10), menu=self.changermenu)

        # definice pro menu Logs
        self.logmenu = Menu(self, tearoff=0)
        self.logmenu.add_command(label="Changelog", command=self.changelog)
        self.logmenu.add_command(label="Show IPCHANGER debugging console", command=self.showlogipchanger)
        self.logmenu.add_command(label="Show TOR debugging console", command=self.showlogtor)
        self.logmenu.add_command(label="Open log directory", command=self.opendirectory)
        self.menubar.add_cascade(label="Logs".ljust(10), menu=self.logmenu)

        # definice pro menu Options
        self.optionmenu = Menu(self, tearoff=0)
        self.optionmenu.add_command(label="Settings".ljust(10), command=self.configwindow)
        self.optionmenu.add_command(label="Clean output", command=self.clean)
        # self.optionmenu.add_command(label="Recount relays", command=self.countAllRelays)
        self.menubar.add_cascade(label="Options".ljust(20), menu=self.optionmenu)

        # prazdne neviditelne tlacitko pro odsazeni
        self.blankmenu = Menu(self, tearoff=0)
        if windows:
            self.menubar.add_cascade(label="".ljust(34), menu=self.blankmenu, state="disabled")
        elif linux:
            self.menubar.add_cascade(label="".rjust(10), menu=self.blankmenu, state="disabled")

        # definice pro menu Help
        self.helpmenu = Menu(self, tearoff=0)
        self.helpmenu.add_command(label="Help", command=self.help)
        if self.noUpdate is False:
            self.helpmenu.add_command(label="Check updates", command=self.buttonupdate)
        self.helpmenu.add_command(label="About", command=self.about)
        if windows:
            self.menubar.add_cascade(label="Help".ljust(15), menu=self.helpmenu)
        elif linux:
            self.menubar.add_cascade(label="Help".rjust(15), menu=self.helpmenu)

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
                exec("self.proxyblacklist_" + str(i) + "= 0")

                if args.country is not None:

                    exec('self.lang_' + str(i) + '.set("' + args.country + '")')
                else:
                    exec('self.lang_' + str(i) + '.set("random")')

                exec('self.useBridges_' + str(i) + ' = BooleanVar()')
                exec('self.checkvarUnique_' + str(i) + ' = IntVar()')
                exec('self.checkvarUnique_' + str(i) + '.set(0)')
                exec('self.depleted_' + str(i) + ' = IntVar()')
                exec('self.depleted_' + str(i) + '.set(0)')

        else:
            self.maxfailed = 3
            self.lang_0 = StringVar()
            self.controlPassword_0 = StringVar()
            self.controlPassword_0.set(get_random_alphanumeric_string(16))
            self.depleted_0 = IntVar()
            self.depleted_0.set(0)
            self.proxyblacklist_0 = 0
            if args.country is not None:
                self.lang_0.set(args.country)
            else:
                self.lang_0.set('random')

            self.useBridges_0 = BooleanVar()
            self.checkvarUnique_0 = IntVar()
            self.checkvarUnique_0.set(0)

        self.logtorm = datetime.now().strftime('Logs/tor_%Y_%m_%d_%H_%M_%S.txt')
        self.allProxyblacklist = 0
        self.postpone = 0
        if args.debug is True:
            self.debuglevel = 1

        # definice pro debug level aplikace pokud pouzit parametr -d
        if self.debuglevel == 1:
            logging.basicConfig(filename=logchanger, level=logging.DEBUG,
                                format='%(asctime)s.%(msecs)03d <%(funcName)s:%(lineno)d> %(message)s',
                                datefmt='%b %d %H:%M:%S')
            self.tordebuglevel = "debug"
        else:
            logging.basicConfig(filename=logchanger, level=logging.INFO, format='%(asctime)s.%(msecs)03d %(message)s',
                                datefmt='%b %d %H:%M:%S')
            self.tordebuglevel = "notice"
            sys.stderr = DevNull()

        # definice stylu progressbaru, zmena barev a tloustka, maximalni hodnoty
        s = tkinter.ttk.Style()
        s.theme_use("default")
        s.configure("red.Horizontal.TProgressbar", foreground='red', background='red', thickness=1)
        s.configure("orange.Horizontal.TProgressbar", foreground='orange', background='orange', thickness=1)
        s.configure("green.Horizontal.TProgressbar", foreground='green', background='green', thickness=1)
        s.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue', thickness=1)
        self.statusBarText = StringVar()
        self.statusBar = Entry(self, textvariable=self.statusBarText, state=DISABLED)
        self.statusBarText.set("")
        self.statusBar.grid(row=0, column=1, sticky="EW")
        self.progressbar = tkinter.ttk.Progressbar(self, orient="horizontal", mode="determinate",
                                                   style="blue.Horizontal.TProgressbar", length=500)
        self.progressbar.grid(row=1, column=1, sticky="NEWS")
        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0
        self.progressbar2 = tkinter.ttk.Progressbar(self, orient="horizontal", mode="determinate",
                                                    style="blue.Horizontal.TProgressbar", length=500)
        self.progressbar2.grid(row=1, column=1, sticky="NEWS", pady=(0, 4))
        self.progressbar2["maximum"] = 60
        self.progressbar2["value"] = 0
        # definice stylu pseudoconsole v aplikaci kam se vypisuji veskere veci
        self.output = tkinter.scrolledtext.ScrolledText(self, foreground="green", background="black",
                                                        highlightcolor="white", highlightbackground="purple", wrap=WORD,
                                                        width=60)
        self.output.grid(row=2, column=1, sticky="NEWS")
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

    # funkce pro precteni a nastaveni hodnot z settings.ini
    def readConfigAndSetValues(self):
        def checkDatabaseblacklist(file):
            con = sqlite3.connect(file)
            cur = con.cursor()
            cur.execute("create table blacklist (ip, country, time, permanent)")
            con.commit()
            cur.close()

        def createDatabaseblacklist():
            if args.multi is not None:
                instances = args.multi
            else:
                instances = 1

            for i in range(instances):
                file = "Data/tordata%s/blacklist.db" % i
                if not os.path.exists("Data"):
                    os.makedirs("Data")
                if not os.path.exists("Data/tordata%s" % i):
                    os.makedirs("Data/tordata%s" % i)
                if not os.path.exists(file):
                    open(file, 'a').close()
                try:
                    checkDatabaseblacklist(file)
                except:
                    pass

        def default():
            try:
                createDatabaseblacklist()
            except:
                pass
            config = configparser.ConfigParser()
            config['DEFAULT'] = {}
            if args.auto is not None:
                self.time.set(args.auto)

            config['DEFAULT']['interval'] = '%s' % int(self.time.get())
            config['DEFAULT']['disableupdates'] = 'no'
            if args.auto is not None:
                config['DEFAULT']['auto'] = 'yes'
            else:
                config['DEFAULT']['auto'] = 'no'
            config['DEFAULT']['timeblacklist'] = '3600'
            self.blacklist.set(3600)
            config['DEFAULT']['sessionblacklist'] = 'no'
            if args.multi is not None:
                instances = args.multi
            else:
                instances = 1

            for i in range(instances):
                proxy = 9050 + i
                config['127.0.0.1:%s' % proxy] = {}
                config['127.0.0.1:%s' % proxy]['bridge'] = 'no'
                config['127.0.0.1:%s' % proxy]['country'] = '%s' % self.lang_0.get()
                if args.unique is True:
                    config['127.0.0.1:%s' % proxy]['unique'] = 'yes'
                else:
                    config['127.0.0.1:%s' % proxy]['unique'] = 'no'

            with open(self.settingsIni, 'w') as configfile:
                config.write(configfile)

        config = configparser.ConfigParser()
        try:
            try:
                createDatabaseblacklist()
            except:
                pass
            if config.read(self.settingsIni):
                interval = config['DEFAULT']['interval']
                disableUpdates = config['DEFAULT']['disableupdates']
                auto = config['DEFAULT']['auto']
                blacklist = config['DEFAULT']['timeblacklist']
                session = config['DEFAULT']['sessionblacklist']
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
                if int(blacklist) >= 0:
                    self.blacklist.set(blacklist)
                else:
                    self.blacklist.set('3600')
                if session == "yes":
                    self.session.set(1)
                else:
                    self.session.set(0)
                instances = 1
                if args.multi is not None:
                    instances = args.multi
                self.debug("instances: %s" % instances)
                for i, section in enumerate(config.sections()):
                    self.debug(i)
                    if i > instances - 1:
                        break
                    bridge = eval("config['%s']['bridge']" % section)
                    country = eval("config['%s']['country']" % section)
                    unique = eval("config['%s']['unique']" % section)

                    if country is not None:
                        exec('self.lang_' + str(i) + '.set("' + str(country) + '")')
                    if args.country is not None:
                        exec('self.lang_' + str(i) + '.set("' + str(args.country) + '")')

                    if bridge == "yes":
                        exec('self.useBridges_' + str(i) + '.set("True")')
                    else:
                        exec('self.useBridges_' + str(i) + '.set("False")')

                    if args.bridges is True:
                        exec('self.useBridges_' + str(i) + '.set("True")')

                    if unique == "yes":
                        exec('self.checkvarUnique_' + str(i) + '.set("1")')
                    else:
                        exec('self.checkvarUnique_' + str(i) + '.set("0")')

                    if args.unique is True:
                        exec('self.checkvarUnique_' + str(i) + '.set("1")')
            else:
                default()
        except:
            default()

    # funkce pro spusteni overeni chybejicich souboru pro chod TORa
    def startcheck(self):
        self.progressbar['maximum'] = 100
        self.progressbar['value'] = 0
        self.progressbar['style'] = "blue.Horizontal.TProgressbar"
        _thread.start_new_thread(self.checkmissingfiles, ())

    # funkce pro zadost o jednu zmenu ip adresy
    def once(self):
        self.allProxyblacklist = 0
        if args.multi is not None:
            instances = args.multi
        else:
            instances = 1
        for i in range(instances):
            exec("self.proxyblacklist_%s = 0" % i)
        self.newIP()
        self.IPandlatency()

    # funkce pro spusteni funkce na zadost o jednu zmenu ip adresy ve vlakne
    def justonce(self):
        _thread.start_new_thread(self.once, ())

    # funkce pro spusteni funkce opravy chybejicich nebo poskozenych tor souboru ve vlakne
    def repairtor(self):
        if not sys.platform == "win32":
            self.write("This operation is not supported on platform %s" % sys.platform, "error", 1)
            return
        _thread.start_new_thread(self.repairmissingfiles, ())

    # funkce pro spusteni funkce restartu tor.exe ve vlakne
    def restarttor(self):
        _thread.start_new_thread(self.threadRestartTor, ())

    # funkce pro restart tor.exe
    def threadRestartTor(self):
        self.stoptor()
        time.sleep(2)
        self.checkmissingfiles()

    # funkce pro overeni chybejicich souboru pro chod TORa, a nasledne jejich stazeni
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

            http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
            r = http.request('GET', torfiles)
            obsah = r.data.decode('utf-8')
            self.file = ""
            for o in obsah.split():
                if not o == "bridges.txt":
                    if windows:
                        if not os.path.exists("Tor/%s" % o):
                            self.missing = self.missing + 1
                            self.download("%s%s" % (tordir, o), None, "Tor")
                else:
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
                self.write("Missing files downloaded\n", "green", 1)
            else:
                self.write("No missing files\n", "green", 1)
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
            cc2 = 0

            for c in country.replace(",", " ").split():
                url = "https://onionoo.torproject.org/summary?search=country:%s" % str(c)
                exit = "https://onionoo.torproject.org/summary?search=country:%s%%20flag:exit" % str(c)
                http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
                r = http.request('GET', url)
                r2 = http.request('GET', exit)
                obsah = r.data.decode('utf-8')
                obsah2 = r2.data.decode('utf-8')
                jsonobsah = json.loads(obsah)
                jsonobsah2 = json.loads(obsah2)
                pocet = len(jsonobsah['relays'])
                pocet2 = len(jsonobsah2['relays'])
                cc = cc + pocet
                cc2 = cc2 + pocet2
            pocet = cc
            pocet2 = cc2

            if pocet >= 1 and pocet2 >= 1:
                color = "orange"
            else:
                color = "error"
            if self.tmpCountries != country:
                text = "Relays in %s: %s\nExitNodes in %s: %s" % (country.upper(), pocet, country.upper(), pocet2)
                # self.statusBarText.set(text)
                self.write("%s\n" % text, color, 1)
                self.tmpCountries = country

            if pocet == 0:
                self.write("You won't be able to connect, please select another country\n", "error", 1)
        else:
            if self.relaysNumber.get() == 0:
                self.countAllRelays()

    # funkce pro pusteni pocitani relay pro vsechny zeme
    def countAllRelays(self):
        _thread.start_new_thread(self.threadCountAllRelays, ())

    # funkce pro spocitani relay pro vsechny zeme
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
                            exit = "https://onionoo.torproject.org/summary?search=flag:exit"
                            http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
                            r = http.request('GET', url)
                            r2 = http.request('GET', exit)
                            obsah = r.data.decode('utf-8')
                            obsah2 = r2.data.decode('utf-8')
                            jsonobsah = json.loads(obsah)
                            jsonobsah2 = json.loads(obsah2)
                            c = len(jsonobsah['relays'])
                            c2 = len(jsonobsah2['relays'])
                            self.relaysNumber.set(c)
                            self.dopocitano = True
                            text = "%s relays and %s exitNodes in Tor network" % (c, c2)
                            self.statusBarText.set(text)
                        except:
                            self.dopocitano = True
                            pass

                    _thread.start_new_thread(pocitej, ())
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

    # funkce na opravu poskozenych / chybejicich souboru
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
                torfiles = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/files.txt"
                tordir = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/"
                bridges = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/bridges.txt"

                if windows:
                    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
                    r = http.request('GET', torfiles)
                    obsah = r.data.decode('utf-8')
                    self.file = ""
                    for o in obsah.split():
                        self.write("Checking file %s\n" % o, "orange", 1)
                        if not self.checkFileSize("%s%s" % (tordir, o), None, "Tor") is True:
                            self.missing = self.missing + 1
                            self.download("%s%s" % (tordir, o), None, "Tor")
                elif linux:
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
                    self.write("Files (re)downloaded\n", "green", 1)
                else:
                    self.write("No repair needed\n", "green", 1)
                # self.starttor()
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
                # _thread.start_new_thread(self.startcheck, ())

    # funkce tlacitka na otevreni slozky s logy
    def opendirectory(self):
        if windows:
            subprocess.Popen(r'explorer Logs')
        elif linux:
            return

    # funkce na vyvolani noveho okna options > settings, a jeho nalezitosti
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
                    config['DEFAULT']['timeblacklist'] = '%s' % self.blacklist.get()
                    if self.session.get() == 1:
                        session = "yes"
                    else:
                        session = "no"
                    config['DEFAULT']['sessionblacklist'] = '%s' % session
                    if args.multi is not None:
                        for i in range(args.multi):
                            port = 9050 + i
                            exec('self.lang_' + str(i) + '.set(self.tor_' + str(i) + '.get())')
                            exec('self.useBridges_' + str(i) + '.set(self.useBridges_' + str(i) + '.get())')
                            exec('self.checkvarUnique_' + str(i) + '.set(self.checkvarUnique_' + str(i) + '.get())')
                            exec('config[\'127.0.0.1:' + str(port) + '\'] = {}')
                            if eval("self.useBridges_%s.get()" % str(i)) == 1:
                                exec('config[\'127.0.0.1:' + str(port) + '\'][\'bridge\'] = \'yes\'')
                            else:
                                exec('config[\'127.0.0.1:' + str(port) + '\'][\'bridge\'] = \'no\'')
                            if eval("self.checkvarUnique_%s.get()" % str(i)) == 1:
                                exec('config[\'127.0.0.1:' + str(port) + '\'][\'unique\'] = \'yes\'')
                            else:
                                exec('config[\'127.0.0.1:' + str(port) + '\'][\'unique\'] = \'no\'')
                                exec("self.proxyblacklist_%s = 0" % str(i))
                            lang = eval('self.tor_' + str(i) + '.get()')
                            exec('config[\'127.0.0.1:' + str(port) + '\'][\'country\'] = \'' + str(lang) + '\'')

                    else:
                        exec('self.lang_0.set(self.tor_0.get())')
                        exec('self.useBridges_0.set(self.useBridges_0.get())')
                        exec('self.checkvarUnique_0.set(self.checkvarUnique_0.get())')
                        exec('config[\'127.0.0.1:9050\'] = {}')
                        if eval("self.useBridges_0.get()") == 1:
                            exec('config[\'127.0.0.1:9050\'][\'bridge\'] = \'yes\'')
                        else:
                            exec('config[\'127.0.0.1:9050\'][\'bridge\'] = \'no\'')
                        if eval("self.checkvarUnique_0.get()") == 1:
                            exec('config[\'127.0.0.1:9050\'][\'unique\'] = \'yes\'')
                        else:
                            exec('config[\'127.0.0.1:9050\'][\'unique\'] = \'no\'')
                            exec("self.proxyblacklist_0 = 0")
                        lang = eval('self.tor_0.get()')
                        exec('config[\'127.0.0.1:9050\'][\'country\'] = \'' + str(lang) + '\'')
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
        self.newWindow.resizable(width=False, height=False)

        Label(self.newWindow, text=' ').grid(row=0, column=6)
        Label(self.newWindow, text=' ').grid(row=1, column=6)
        Label(self.newWindow, text=' ').grid(row=2, column=6)

        Label(self.newWindow, text='Change IP every').place(x=8, y=2)
        if self.meni == 1:
            interval = Entry(self.newWindow, textvariable=self.time, width=7, state="disabled")
        else:
            interval = Entry(self.newWindow, textvariable=self.time, width=7, state="normal")
            # interval.grid(row=r,column=1)
        interval.place(x=100, y=3)

        Label(self.newWindow, text='Blacklist IP for').place(x=8, y=22)
        blacklist = Entry(self.newWindow, textvariable=self.blacklist, width=7, state="normal")
        blacklist.place(x=100, y=23)

        # Label(self.newWindow, text = 'sec').grid(row=r,column=1)
        Label(self.newWindow, text='sec').place(x=136, y=2)
        Label(self.newWindow, text='sec').place(x=136, y=22)

        self.sessionCheck = Checkbutton(self.newWindow, text="Session blacklist", variable=self.session,onvalue=1, offvalue=0)
        self.sessionCheck.place(x=290,y=0)

        if self.auto == 1:
            self.checkvarAuto = IntVar(value=1)
        else:
            self.checkvarAuto = IntVar(value=0)
        x = 180
        self.checkButtonAuto = Checkbutton(self.newWindow, text="Auto start", variable=self.checkvarAuto, onvalue=1,
                                           offvalue=0)
        self.checkButtonAuto.place(x=x, y=0)
        if self.noUpdate is True:
            self.checkvarUpdates = IntVar(value=1)
        else:
            self.checkvarUpdates = IntVar(value=0)

        self.checkButtonUpdates = Checkbutton(self.newWindow, text="Disable updates", variable=self.checkvarUpdates,
                                              onvalue=1, offvalue=0)
        self.checkButtonUpdates.place(x=x, y=20)

        r = r + 1
        # ttk.Separator(self.newWindow, orient=HORIZONTAL).place(x=0, y=64, relwidth=1)
        # ttk.Separator(self.newWindow, orient=HORIZONTAL).place(x=0, y=65, relwidth=1)

        if args.multi is not None:
            if self.forall == 1:
                self.checkvar = IntVar(value=1)
                self.checkforall = Checkbutton(self.newWindow, text="Set country for all proxies", variable=self.checkvar, onvalue=1,
                                               offvalue=0, command=self.unsetforall)

            else:
                self.checkvar = IntVar(value=0)
                self.checkforall = Checkbutton(self.newWindow, text="Set country for all proxies", variable=self.checkvar, onvalue=1,
                                               offvalue=0, command=self.setforall)

            self.checkforall.place(x=290,y=20)

        r = r + 1
        langs = []
        langs = self.countries
        if args.multi is not None:

            for i in range(args.multi):
                if i % 10 == 0 or i % 1 != 0:
                    r = 3
                    cl = cl + 6
                    cc = cc + 6
                    w = w + 50

                Label(self.newWindow, text='%s:%s' % (self.host.get(), proxy + i)).grid(row=r, column=cl - 6)
                if self.forall == 1 and i != 0:
                    exec('self.tor_' + str(i) + ' = ttk.Combobox(self.newWindow, width = 9, state = "disabled")')

                else:
                    exec('self.tor_' + str(i) + ' = ttk.Combobox(self.newWindow, width = 9, state = "readonly")')

                exec('self.tor_' + str(i) + '.grid(row=r,column=cc-6)')
                exec('self.tor_' + str(i) + '["values"] = (langs)')

                exec('self.tor_bridge_yes_' + str(
                    i) + ' = Radiobutton(self.newWindow, text = "Bridge", variable = self.useBridges_' + str(
                    i) + ', value = True, width = 5)')
                exec('self.tor_bridge_yes_' + str(i) + '.grid(row=r,column=cc+1-6)')

                exec('self.tor_bridge_no_' + str(
                    i) + ' = Radiobutton(self.newWindow, text = "Direct", variable = self.useBridges_' + str(
                    i) + ', value = False, width = 5)')
                exec('self.tor_bridge_no_' + str(i) + '.grid(row=r,column=cc+2-6)')

                exec('self.checkAlwaysUnique_' + str(i) + ' = Checkbutton(self.newWindow, text="Unique IP", variable=self.checkvarUnique_' + str(i) + ',onvalue=1, offvalue=0)')
                exec('self.checkAlwaysUnique_' + str(i) + '.grid(row=r, column=cc + 3 - 6)')

                try:
                    exec('Button(self.newWindow, text="Open blacklist", command=partial(self.blacklistWindow, ' + str(i) + '), width=12).grid(row=r, column=cc + 4 - 6)')
                except Exception as e:
                    print(e)

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
            Button(self.newWindow, text="Save", command=save, width=9).grid(row=r, column=1)
        else:
            cl = cl + 4
            cc = cc + 4
            Label(self.newWindow, text='%s:%s' % (self.host.get(), self.proxy)).grid(row=r, column=cl - 4)
            exec('self.tor_0 = ttk.Combobox(self.newWindow, width = 9, state = "readonly")')
            exec('self.tor_0.grid(row=r,column=cc-4)')
            exec('self.tor_0["values"] = (langs)')

            self.tor_bridge_yes_0 = Radiobutton(self.newWindow, text="Bridge", variable=self.useBridges_0, value=True,
                                                width=5)
            self.tor_bridge_yes_0.grid(row=r, column=cc + 1 - 4)
            self.tor_bridge_no_0 = Radiobutton(self.newWindow, text="Direct", variable=self.useBridges_0, value=False,
                                               width=5)
            self.tor_bridge_no_0.grid(row=r, column=cc + 2 - 4)

            self.checkAlwaysUnique_0 = Checkbutton(self.newWindow, text="Unique IP", variable=self.checkvarUnique_0,
                                                   onvalue=1, offvalue=0)
            self.checkAlwaysUnique_0.grid(row=r, column=cc + 3 - 4)
            Button(self.newWindow, text="Open blacklist", command=self.blacklistWindow, width=12).grid(row=r, column=cc + 4 - 4)

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
            Button(self.newWindow, text="Save", command=save, width=9).grid(row=r, column=1)

        exec('self.tor_0.bind("<Return>", self.getsetforall)')
        exec('self.tor_0.bind("<<ComboboxSelected>>", self.getsetforall)')

    def about(self):
        self.newWindow2 = Toplevel(self)
        self.newWindow2.title("About")
        if windows:
            width = 350
            height = 150
        elif linux:
            width = 400
            height = 150
        screenwidth = self.newWindow2.winfo_screenwidth()
        screenheight = self.newWindow2.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.newWindow2.geometry(alignstr)
        self.newWindow2.resizable(width=False, height=False)
        repourl = "https://github.com/seevik2580/tor-ip-changer"
        issuesurl = "%s/issues" % repourl
        def ok():
            if self.newWindow2:
                try:
                    self.newWindow2.destroy()
                except ():
                    pass
                self.newWindow2 = None

        def issues():
            webbrowser.open_new(issuesurl)

        try:
            bok = Button(self.newWindow2)
            bok["bg"] = "#efefef"
            bok["fg"] = "#000000"
            bok["justify"] = "center"
            bok["text"] = "OK"
            bok["command"] = ok
            bok.place(x=10, y=110, width=56, height=30)

            bissues = Button(self.newWindow2)
            bissues["bg"] = "#efefef"
            bissues["fg"] = "#000000"
            bissues["justify"] = "center"
            bissues["text"] = "Issues"
            bissues["command"] = issues
            bissues.place(x=70, y=110, width=56, height=30)

            lrepo = Label(self.newWindow2)
            lrepo["fg"] = "#333333"
            lrepo["justify"] = "center"
            lrepo["text"] = "Repo URL:"
            if windows:
                lrepo.place(x=0, y=0, width=71, height=30)
            elif linux:
                lrepo.place(x=0, y=0, width=91, height=30)

            lurl = Label(self.newWindow2)
            lurl["fg"] = "#1e90ff"
            lurl["justify"] = "center"
            lurl["text"] = "%s" % repourl
            lurl["cursor"] = "hand2"
            lurl.bind("<Button-1>", lambda e: webbrowser.open_new(repourl))
            if windows:
                lurl.place(x=69, y=0, width=288, height=30)
            elif linux:
                lurl.place(x=89, y=0, width=308, height=30)

            ltv = Label(self.newWindow2)
            ltv["fg"] = "#333333"
            ltv["justify"] = "center"
            ltv["text"] = "This version:"
            if windows:
                ltv.place(x=0, y=25, width=82, height=30)
            elif linux:
                ltv.place(x=2, y=25, width=102, height=30)

            llv = Label(self.newWindow2)
            llv["fg"] = "#333333"
            llv["justify"] = "center"
            llv["text"] = "Last version:"
            if windows:
                llv.place(x=0, y=45, width=83, height=30)
            elif linux:
                llv.place(x=2, y=45, width=103, height=30)

            ltvt = Label(self.newWindow2)
            ltvt["fg"] = "#333333"
            ltvt["justify"] = "center"
            ltvt["text"] = "%s build %s" % (self.lastver, self.lastbuild)
            if windows:
                ltvt.place(x=80, y=45, width=80, height=30)
            elif linux:
                ltvt.place(x=100, y=46, width=100, height=27)

            llvt = Label(self.newWindow2)
            llvt["fg"] = "#333333"
            llvt["justify"] = "center"
            llvt["text"] = "%s build %s" % (version, build)
            if windows:
                llvt.place(x=83, y=25, width=80, height=30)
            elif linux:
                llvt.place(x=104, y=26, width=100, height=27)

            lseva = Label(self.newWindow2)
            lseva["fg"] = "#333333"
            lseva["justify"] = "center"
            lseva["text"] = "Created by Seva"
            if windows:
                lseva.place(x=242, y=119, width=100, height=30)
            elif linux:
                lseva.place(x=272, y=119, width=120, height=30)

        except Exception as e:
            self.error(e)

    def updateWindow(self):
        self.newWindow3 = Toplevel(self)
        self.newWindow3.title("Update")

        Label(self.newWindow3, text='Do you want to update ?').grid(row=1, column=1, columnspan=3, padx=(20, 20))

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

        Button(self.newWindow3, text="Yes", command=yes, width=5).grid(row=2, column=2, padx=(20, 20))
        Button(self.newWindow3, text="No", command=no, width=5).grid(row=2, column=3, padx=(20, 20))

    def blacklistWindow(self, proxy=None):
        if proxy is None:
            proxy = 9050
        else:
            proxy = 9050 + proxy
        cport = 5950 + proxy
        languagenumber = proxy - 9050
        file = "Data/tordata%s/blacklist.db" % languagenumber
        exec("self.blacklistWindow_%s = Toplevel(self)" % proxy)
        exec("self.blacklistWindow_%s.title('Blacklist for 127.0.0.1:%s')" % (proxy,proxy))
        window = eval("self.blacklistWindow_%s" % proxy)
        window.resizable(width=False, height=False)

        frameTop = Frame(window)
        frameTop.grid()

        frameBottom = Frame(window)
        frameBottom.grid()

        def refresh(proxy):
            vykresliTabulku(proxy)

        def deleteAllExceptPermanent(proxy, cport, languagenumber, file):
            self.clearBlacklistIpDB(cport, languagenumber, file)
            refresh(proxy)

        def deleteSelected(file):
            try:
                items = self.treeView.selection()
                for i in items:
                    item = self.treeView.item(i, "values")
                    ip = item[0]
                    con = sqlite3.connect(file)
                    cur = con.cursor()
                    cur.execute("delete from blacklist where ip='%s'" % (ip))
                    con.commit()
                    cur.close()
                refresh(proxy)
            except Exception as e:
                self.error(e)

        def add(file, proxy):
            ip = addE.get()
            if re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$', ip):
                try:
                    con = sqlite3.connect(file)
                    cur = con.cursor()
                    duplikace = cur.execute("select ip from blacklist where ip = '%s'" % ip).fetchall()
                    print(duplikace)
                    if not duplikace:
                        cur.execute("insert into blacklist values('%s', '??', '%s', 'no')" % (ip, time.time()))
                        addL["text"] = "Accepted"
                    else:
                        addL["text"] = "Duplicated"
                    con.commit()
                    cur.close()
                    addE.delete(0, END)
                    refresh(proxy)
                except Exception as e:
                    self.error(e)
            else:
                addE.delete(0, END)
                addL["text"] = "Invalid"

        try:
            Label(frameTop, text="* Double click to set permanent").grid(row=0, column=0)
            Button(frameTop, text="Refresh", command=partial(refresh, proxy)).grid(row=0, column=1, padx=8)
            Button(frameTop, text="Delete selected", command=partial(deleteSelected, file)).grid(row=0, column=2)
            Button(frameTop, text="Delete all (except permanent)", command=partial(deleteAllExceptPermanent, proxy, cport, languagenumber, file)).grid(row=0, column=3)
            Button(frameTop, text="Add", command=partial(add, file, proxy)).grid(row=0, column=5)
            addE = Entry(frameTop, text="")
            addE.grid(row=0, column=4, padx=8)
            addL = Label(frameTop, text="", width=20, justify=LEFT)
            addL.grid(row=0,column=6)


        except Exception as e:
            print(e)

        def vykresliTabulku(proxy):
            try:
                languagenumber = proxy - 9050
                file = "Data/tordata%s/blacklist.db" % languagenumber

                def doubleClick(event):
                    try:
                        languagenumber = proxy - 9050
                        file = "Data/tordata%s/blacklist.db" % languagenumber
                        item = self.treeView.selection()
                        item = self.treeView.item(item, "values")
                        ip = item[0]
                        permanent = item[2].strip("\n")
                        if permanent == "no":
                            akce = "yes"
                        else:
                            akce = "no"
                        con = sqlite3.connect(file)
                        cur = con.cursor()
                        cur.execute("update blacklist set permanent='%s' where ip='%s'" % (akce,ip))
                        con.commit()
                        cur.close()
                        refresh(proxy)
                    except Exception as e:
                        self.error(e)

                self.treeView = ttk.Treeview(frameBottom, columns=(1, 2, 3, 4), show='headings', height=8)
                self.treeView.grid(row=2, column=3)
                self.treeView.heading(1, text='IP')
                self.treeView.heading(2, text='Country')
                self.treeView.heading(3, text='Permanent *')
                self.treeView.heading(4, text='Until')

                con = sqlite3.connect(file)
                cur = con.cursor()
                c = 0
                for row in cur.execute("select * from blacklist").fetchall():
                    ip = row[0]
                    country = row[1]
                    permanent = row[3]
                    until = row[2]
                    until = datetime.fromtimestamp(float(until) + self.blacklist.get())
                    until = until.strftime('%Y-%m-%d %H:%M:%S')
                    if permanent == "yes":
                        until = ""
                    self.treeView.insert(parent='', index=c, values=(ip, country, permanent, until))
                    c = c +1
                self.treeView.bind("<Double-1>", doubleClick)
                cur.close()
                vsb = ttk.Scrollbar(frameBottom, orient="vertical", command=self.treeView.yview)
                vsb.grid(row=2, column=4, sticky="NEWS")
                self.treeView.configure(yscrollcommand=vsb.set)
            except Exception as e:
                self.error(e)
        vykresliTabulku(proxy)

    # funkce na prepnuti vsech tlacitek pro vyber zeme podle prvniho pokud zaskrtnuta volba for all
    def getsetforall(self, event):
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

    # funkce pro zaskrtavaci policko
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

    # funkce na zobrazeni napovedy
    def threadhelp(self):
        text = """************************************************************
usage: ipchanger.exe [-a AUTO] [-d] [-m 1-100] [-p] [-c COUNTRY] [-b] [-n] [-u]
    '-a n' automaticaly change ip after start every n
            example:   ipchanger.exe -a 35
                        change ip auto every 35 sec

    '-m n' start multiple proxy n instances
            example:   ipchanger.exe -m 5
                        start proxy 5 times
                        with different ports
                        and generate list

    '-d' open debug console live log

    '-c COUNTRYCODE' select specific country

    '-p' bind API to public IP

    '-b' use bridges by default

    '-n' disable check for updates

    '-u' always obtain unique ip addresses
            """

        self.write(text, 'white', 0)
        if windows:
            try:
                help = 'help.txt'
                if not os.path.exists(help):
                    self.download(
                        "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/%s/%s" % (version, help),
                        1)

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

    # funkce na zobrazeni zpravy dne
    def motd(self):
        http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
        r = http.request('GET', 'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/motd.txt')
        obsah = r.data.decode('utf-8')
        self.write(obsah, 'white', 1)

    # funkce na zobrazeni changelogu verze aplikace
    def changelog(self):
        http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
        r = http.request('GET',
                         'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/' + version + '/changelog')
        obsah = r.data.decode('utf-8')
        self.write(obsah, 'orange', 1)

    # funkce na spusteni tail.exe a vypis logu IPCHANGER live
    def showlogipchanger(self):
        self.logmenu.entryconfig(1, label="Hide IPCHANGER debugging console", command=self.hidelog)
        try:
            _thread.start_new_thread(self.tailchanger, ())
        except:
            pass

    # funkce na spusteni tail.exe a vypis logu TOR live
    def showlogtor(self):
        self.logmenu.entryconfig(2, label="Hide TOR debugging console", command=self.hidelog)
        try:
            _thread.start_new_thread(self.tailtor, ())
        except:
            pass

    # funkce na tail.exe logu ipchangeru
    def tailchanger(self):
        if windows:
            tail = "tail.exe"
        elif linux:
            tail = "tail"
        try:
            if not os.path.exists(self.tailexe):
                if windows:
                    self.download("https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/%s" % (self.tailexe), 1)
            os.system("%s -q -f %s" % (tail, logchanger))
        except:
            pass

    # funkce na tail.exe logu tora
    def tailtor(self):
        if windows:
            tail = "tail.exe"
        elif linux:
            tail = "tail"
        try:
            if not os.path.exists(self.tailexe):
                if windows:
                    self.download("https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/tor/%s" % (self.tailexe), 1)
            os.system("%s -q -f %s" % (tail, logtor))
        except:
            pass

    # funkce na schovani logu live
    def hidelog(self):
        self.logmenu.entryconfig(1, label="Show IPCHANGER debugging console", command=self.showlogipchanger)
        self.logmenu.entryconfig(2, label="Show TOR debugging console", command=self.showlogtor)
        if windows:
            SW_HIDE = 0
            info = subprocess.STARTUPINFO()
            info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = SW_HIDE
            subprocess.Popen(r'cmd /c taskkill /f /im tail.exe', startupinfo=info)
        elif linux:
            os.system(r'killall tail')

    # funkce na vypsani debug infa aplikace do console a logu
    def appInfo(self):
        key = self.ident
        while key == self.ident:
            logging.info("IPchanged=%s" % self.IPchanged)
            logging.info("IPresolved=%s" % self.IPfetched)
            logging.info("IPchangeFailed=%s" % self.failed)
            logging.info("IPchangeMaxFailedBeforeExit=%s" % self.maxfailed)
            jakdlouhobezi = timer()
            logging.info("AppRunning=%s sec" % (jakdlouhobezi - startchanger))
            time.sleep(10)

    # funkce na ovladani ipchangeru pres API skrz telnet
    def API(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind((self.appHOST, self.appPORT))
            self.write('API server binded to %s:%s (%s) OK.\n' % (self.appHOST, self.appPORT, self.bindtype), 'green',
                       1)

        except socket.error as msg:
            self.write('API server binded to %s:%s (%s) ERROR.\n' % (self.appHOST, self.appPORT, self.bindtype), "red",
                       1)
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
                    reply += b'blacklist N    | set blacklist to N seconds\r\n'
                    reply += b'changeip start | start autochanging ip\r\n'
                    reply += b'changeip stop  | stop autochanging ip\r\n'
                    reply += b'changeip once  | dont autochange, but change once\r\n'
                    reply += b'changeip onceport N | change ip once for port N\r\n'
                    reply += b'uniqueip port N| set on/off to always obtain unique ip for port N\r\n'
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
                            self.startchange()
                        else:
                            reply = b'tor server not running\r\n'
                    elif data == b'changeip stop\r\n':
                        if self.bezi == 1:
                            reply = b'stop ip changing\r\n'
                            self.stopchange()
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
                    elif rozdel[0] == 'blacklist':
                        try:
                            cislo = int(rozdel[1])
                            reply = bytes('set blacklist to %s seconds\r\n' % cislo, 'utf-8')
                            self.blacklist.set(cislo)
                        except ValueError:
                            reply = bytes('blacklist interval has to be number!\r\n', 'utf-8')
                            pass
                    elif rozdel[0] == 'uniqueip' and rozdel[1] == "port":
                        try:
                            reply = b''
                            port = int(rozdel[2])
                            if args.multi is None:
                                if not port == 9050:
                                    reply += bytes('u cant use port %s without ipchanger -m, only 9050\r\n' % port, 'utf-8')
                                    port = 9050

                            cislo = port - 9050
                            if eval('self.checkvarUnique_%s.get()' % cislo) == 1:
                                exec('self.checkvarUnique_%s.set("0")' % cislo)
                                reply += bytes('set OFF to always obtain unique IP for port %s\r\n' % port, 'utf-8')
                            elif eval('self.checkvarUnique_%s.get()' % cislo) == 0:
                                exec('self.checkvarUnique_%s.set("1")' % cislo)
                                reply += bytes('set ON to always obtain unique IP for port %s\r\n' % port, 'utf-8')
                        except ValueError:
                            reply = bytes('port has to be number!\r\n', 'utf-8')
                            pass
                    elif rozdel[0] == 'changeip' and rozdel[1] == 'onceport':
                        if args.multi is not None:
                            if self.bezi == 1:
                                reply = b'changing ip once for port\r\n'
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
            _thread.start_new_thread(clientthread, (conn,))

        s.close()

    # funkce na start updatu
    def startthings(self):
        try:
            if self.session.get() == 1:
                if args.multi is not None:
                    instances = args.multi
                else:
                    instances = 1
                for i in range(instances):
                    proxy = 9050 + i
                    cport = 5950 + proxy
                    file = "Data/tordata%s/blacklist.db" % str(i)
                    self.clearBlacklistIpDB(cport, i, file)
        except Exception as e:
            self.error(e)
        time.sleep(1)
        if args.auto is not None:
            self.tormenu.entryconfig(0, state="disabled")
        try:
            _thread.start_new_thread(self.update, ())
        except:
            pass

    # funkce na prestart, overeni tora
    def prestart(self):
        self.startcheck()

    # funkce spusteni startu tora
    def starttor(self):
        self.tormenu.entryconfig(0, state="disabled")
        self.tormenu.entryconfig(1, state="normal")
        self.progressbar["style"] = "blue.Horizontal.TProgressbar"
        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0
        _thread.start_new_thread(self.tor, ())

    # funkce zastaveni tora
    def stoptor(self):
        self.controlport = 15000
        self.control = 15000
        self.appPORT = 14999
        self.proxy = 9050
        self.tormenu.entryconfig(0, state="normal")
        self.tormenu.entryconfig(1, state="disabled")
        if self.meni == 1:
            _thread.start_new_thread(self.stopchange, ())

        if windows:
            SW_HIDE = 0
            info = subprocess.STARTUPINFO()
            info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = SW_HIDE
            subprocess.Popen(r'cmd /c taskkill /f /im tor.exe', startupinfo=info)
            subprocess.Popen(r'cmd /c taskkill /f /im obfs4proxy.exe', startupinfo=info)
        elif linux:
            os.system(r'killall tor')

        self.write("TOR server stopped. \n", "error", 1)
        self.ident = random.random()
        if self.meni == 0:
            self.progressbar["value"] = 0
        self.bezi = 0
        self.meni = 0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed = 0
        self.control = 15000
        self.proxy = 9050
        self.b = 0
        self.data = "Data/tordata%s" % self.b
        self.changermenu.entryconfig(0, state="disabled")
        self.changermenu.entryconfig(1, state="disabled")
        self.changermenu.entryconfig(2, state="disabled")

    # funkce k pouziti bridges
    def bridges(self, identify=None):
        if eval("self.useBridges_%s.get()" % str(identify)) == 1:
            with open('Tor/bridges.txt', 'r') as f:
                self.bridge = '--UseBridges 1 '
                if windows:
                    self.bridge += '--ClientTransportPlugin "obfs2,obfs3,obfs4 exec Tor\obfs4proxy.exe managed" '
                    self.bridge += '--clientTransportPlugin "meek exec Tor\meek-client" '
                elif linux:
                    self.bridge += '--ClientTransportPlugin "obfs2,obfs3,obfs4 exec /usr/bin/obfs4proxy managed" '
                    self.bridge += '--clientTransportPlugin "meek exec /usr/bin/obfs4proxy" '
                for line in f:
                    l = line.split('\n')[0]
                    self.bridge += '--Bridge "%s" ' % l
            self.write('using bridges. \n', "green", 1)
            self.write("Always obtain unique IP ", "white", 1)
            if eval("self.checkvarUnique_%s.get()" % str(identify)) == 1:
                self.write("ON\n", "green", 1)
            else:
                self.write("OFF\n", "red", 1)
            ff = open('Tor/bridges.txt', 'r')
            for line in ff:
                logging.info(line.split('\n')[0])
            return self.bridge
        else:
            self.bridge = '--UseBridges 0 '
            self.write('using direct connection. \n', "red", 1)
            self.write("Always obtain unique IP ", "white", 1)
            if eval("self.checkvarUnique_%s.get()" % str(identify)) == 1:
                self.write("ON\n", "green", 1)
            else:
                self.write("OFF\n", "red", 1)
            return self.bridge

    # funkce na generovani hashe hesla ke kontrolnimu portu
    def generateControlPasswordHash(self, password, identify=None):
        if windows:
            SW_HIDE = 0
            info = subprocess.STARTUPINFO()
            info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = SW_HIDE
            out = subprocess.check_output('Tor/tor.exe --quiet --hash-password "%s"' % (password), startupinfo=info)
        elif linux:
            proc = subprocess.Popen('tor --quiet --hash-password "%s"' % (password), stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()

        exec('self.controlPasswordHash_' + str(identify) + ' = StringVar()')
        exec('self.controlPasswordHash_' + str(identify) + '.set(out.decode("utf-8").rstrip())')

    # funkce na ziskani hashe hesla ke kontrolnimu portu
    def get_controlPasswordHash(self, identify=None):
        return eval("self.controlPasswordHash_%s.get()" % identify)

    # funkce na ziskani hesla ke kontrolnimu portu
    def get_controlPassword(self, identify=None):
        return eval("self.controlPassword_%s.get()" % identify)

    # funkce multiinstanci tora
    def multiTor(self, identify=None):
        self.logtorm = datetime.now().strftime('Logs/tor_%Y_%m_%d_%H_%M_%S.txt')
        files = self.logtorm
        self.bridges(identify)
        if windows:
            SW_HIDE = 0
            info = subprocess.STARTUPINFO()
            info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = SW_HIDE

        exec('self.generateControlPasswordHash(self.controlPassword_' + str(identify) + '.get(), str(identify))')
        if not os.path.exists('Data'):
            os.mkdir('Data')
        if not os.path.exists(self.data):
            os.mkdir(self.data)
        if not os.path.exists('%s/torrc' % self.data):
            open('%s/torrc' % self.data, mode='a').close()
        if eval("self.lang_%s.get()" % str(identify)) == "random":
            options = "--StrictNodes 0"
            with open('%s/torrc' % self.data, 'r+') as f:
                new_f = f.readlines()
                f.seek(0)
                for line in new_f:
                    l = line.split(" ")
                    if not l[0] == "ExitNodes":
                        f.write(line)
                f.truncate()
        else:
            language = eval("self.lang_%s.get()" % str(identify))
            cc = ""
            for c in language.replace(",", " ").split():
                cc += ",{%s}" % c

            self.debug(cc.lstrip(","))
            options = "--ExitNodes %s --StrictNodes 1" % cc.lstrip(",")
            self.debug(options)
            self.countRelays(str(language))

        if windows:
            subprocess.Popen(r'Tor/tor.exe -f %s/torrc %s --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "%s" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log %s --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 %s' % (self.data, self.bridge, self.get_controlPasswordHash(identify), self.control, self.proxy, self.data, self.tordebuglevel, options), startupinfo=info, stdout=open(files, 'a'))
        elif linux:
            os.system(r'(authbind --deep tor -f %s/torrc %s --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "%s" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log %s --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 %s | tee %s ) > /dev/null &' % (self.data, self.bridge, self.get_controlPasswordHash(identify), self.control, self.proxy, self.data, self.tordebuglevel, options, files))
        self.control = self.control + 1
        self.proxy = self.proxy + 1
        self.b = self.b + 1
        self.data = "Data/tordata%s" % self.b

    # funkce na ovladani Tor skrz control port
    def torControl(self, port, password, command=None):
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
        # self.debug(status)
        # print(status)
        return status

    # funkce startu tora a jeho logu a urcovani procent v progressbaru
    def tor(self):
        if args.multi is not None:
            file = self.logtorm
        else:
            file = logtor
        if windows:
            SW_HIDE = 0
            info = subprocess.STARTUPINFO()
            info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = SW_HIDE
        key = self.ident
        self.generateControlPasswordHash(self.controlPassword_0.get(), 0)
        if args.multi is not None:
            self.write("TOR server %s starting " % self.b, "green", 1)
            self.bridges('0')
            self.countRelays(str(self.lang_0.get()))
            if not os.path.exists('Data'):
                os.mkdir('Data')
            if not os.path.exists(self.data):
                os.mkdir(self.data)
            if not os.path.exists('%s/torrc' % self.data):
                open('%s/torrc' % self.data, mode='a').close()
            if self.lang_0.get() == "random":
                options = "--StrictNodes 0"
                with open('%s/torrc' % self.data, 'r+') as f:
                    new_f = f.readlines()
                    f.seek(0)
                    for line in new_f:
                        l = line.split(" ")
                        if not l[0] == "ExitNodes":
                            f.write(line)
                    f.truncate()
            else:
                countries = self.lang_0.get()
                cc = ""
                for c in countries.replace(",", " ").split():
                    cc += ",{%s}" % c

                self.debug(cc.lstrip(","))
                options = "--ExitNodes %s --StrictNodes 1" % cc.lstrip(",")
                self.debug(options)

            if windows:
                subprocess.Popen(r'Tor/tor.exe -f %s/torrc %s --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "%s" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log %s --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --DNSport 53 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 %s' % (self.data, self.bridge, self.get_controlPasswordHash('0'), self.control, self.proxy, self.data, self.tordebuglevel, options), startupinfo=info, stdout=open(file, 'a'))
            elif linux:
                os.system(r'(authbind --deep tor -f %s/torrc %s --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "%s" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log %s --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --DNSport 53 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 %s | tee %s ) > /dev/null &' % (self.data, self.bridge, self.get_controlPasswordHash('0'), self.control, self.proxy, self.data, self.tordebuglevel, options, file))
            self.control = self.control + 1
            self.proxy = self.proxy + 1
            self.b = self.b + 1
            self.data = "Data/tordata%s" % self.b
            time.sleep(1.1)
            for m in range(args.multi - 1):
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

            if not os.path.exists('Data'):
                os.mkdir('Data')
            if not os.path.exists(self.data):
                os.mkdir(self.data)
            if not os.path.exists('%s/torrc' % self.data):
                open('%s/torrc' % self.data, mode='a').close()

            if self.lang_0.get() == "random":
                options = "--StrictNodes 0"
                with open('%s/torrc' % self.data, 'r+') as f:
                    new_f = f.readlines()
                    f.seek(0)
                    for line in new_f:
                        l = line.split(" ")
                        if not l[0] == "ExitNodes":
                            f.write(line)
                    f.truncate()

            else:
                countries = self.lang_0.get()
                cc = ""
                for c in countries.replace(",", " ").split():
                    cc += ",{%s}" % c

                self.debug(cc.lstrip(","))
                options = "--ExitNodes %s --StrictNodes 1" % cc.lstrip(",")
                self.debug(options)

            if windows:
                subprocess.Popen(r'Tor/tor.exe -f %s/torrc %s --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "%s" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log %s --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --DNSport 53 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 %s' % (self.data, self.bridge, self.get_controlPasswordHash('0'), self.control, self.proxy, self.data, self.tordebuglevel, options), startupinfo=info, stdout=open(file, 'a'))
            elif linux:
                os.system(r'(authbind --deep tor -f %s/torrc %s --CookieAuthentication 0 --SocksPolicy "accept *" --HashedControlPassword "%s" --ControlPort %s --SocksPort 0.0.0.0:%s --DataDirectory %s --log %s --AvoidDiskWrites 1 --SafeLogging 0 --GeoIPExcludeUnknown 1 --GeoIPFile Tor/geoip --GeoIPv6File Tor/geoip6 --DNSport 53 --AutomapHostsSuffixes .onion --AutomapHostsOnResolve 1 %s | tee %s ) > /dev/null &' % (self.data, self.bridge, self.get_controlPasswordHash('0'), self.control, self.proxy, self.data, self.tordebuglevel, options, file))

        timeout = 0
        count = 1
        self.debug(self.tordebuglevel)
        controlPortConnected = 0
        tout = 2400
        toutout = 300
        tsleep = 0.1
        while not timeout == tout and key == self.ident:
            if not key == self.ident:
                return
            time.sleep(tsleep)
            if timeout % toutout == 0:
                if args.multi is not None:
                    self.write("TOR servers starting. Please wait ... \n", "yellow", 1)
            timeout = timeout + 1
            try:
                status = self.torControl(15000, self.get_controlPassword(0), "GETINFO status/bootstrap-phase")
                statusresult = status.split("\r\n", 3)
                bootstrap = statusresult[1].split(" ", 5)
                progress = bootstrap[2]
                summary = statusresult[1]
                summarystatus = summary.split("=")
                progressnumber = progress.split("=", 2)
                boot = progressnumber[1]
                circuitstatus = self.torControl(15000, self.get_controlPassword(0),
                                                "GETINFO status/circuit-established")
                circuitstatus = circuitstatus.split("\r\n", 3)
                if not self.oldpercent == boot:
                    self.write("%s%% - %s \n" % (boot, summarystatus[4].strip("\"")), "yellow", 0)
                    # logging.info("%s%% - %s" % (boot,status))
                    self.oldpercent = boot
                    logging.info("%s%% - %s - %s" % (boot, status, circuitstatus[1]))

                self.progressbar["value"] = float(boot)

                if (circuitstatus[1]) == "250-status/circuit-established=1":
                    # self.debug(circuitstatus[1])
                    self.write("TOR server started \n", "green", 1)
                    self.write("DNS server started \n", "green", 1)
                    self.progressbar["value"] = 100
                    self.progressbar["style"] = "orange.Horizontal.TProgressbar"
                    self.bezi = 1
                    self.changermenu.entryconfig(0, state="normal")
                    self.changermenu.entryconfig(1, state="disabled")
                    self.changermenu.entryconfig(2, state="normal")

                    self.write("------------------------------------------------------------", "white", 1)
                    self.write("Proxy list:\n", "white", 1)
                    proxy = 9050
                    host = "127.0.0.1"
                    if args.multi is None:
                        multi = 1
                    else:
                        multi = args.multi
                    for i in range(multi):
                        language = eval('self.lang_' + str(i) + '.get()')
                        self.write("%s:%s\n" % (host, proxy), "orange", 1)
                        proxy = proxy + 1
                    self.write("------------------------------------------------------------", "white", 1)
                    if self.auto == 1 or args.auto is not None:
                        try:
                            _thread.start_new_thread(self.startchange, ())
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

            # funkce na vycisteni vystupu

    def clean(self):
        self.output.delete('1.0', END)

    # funkce spusteni predbeznych veci po startu aplikace
    def buttonupdate(self):
        self.buttonup = 1
        _thread.start_new_thread(self.startthings, ())

    def downloadAndUpdate(self):
        if windows:
            try:
                self.download('https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/updater.exe')
                SW_HIDE = 0
                info = subprocess.STARTUPINFO()
                info.dwFlags = subprocess.STARTF_USESHOWWINDOW
                info.wShowWindow = SW_HIDE
                subprocess.Popen(r'taskkill /f /im tor.exe', startupinfo=info)
                subprocess.Popen(r'taskkill /f /im obfs4proxy.exe', startupinfo=info)
                subprocess.Popen(r'taskkill /f /im tail.exe', startupinfo=info)
                subprocess.Popen('updater.exe', close_fds=True)
                os._exit(1)
            except Exception as e:
                self.write("Update error, see logs!\n", "error", 1)
                pass
        elif linux:
            return

    # funkce kontroly verze aplikace, pokud novejsi verze zeptej se zda updatovat
    def update(self):
        try:
            if self.noUpdate is False:
                self.write('This version:            %s-%s\n' % (version, build), "white", 1)
                http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
                f = http.request('GET', 'https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/version.txt')
                self.lastver = f.data.decode('utf-8')
                url = "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/%s/dist.txt" % self.lastver
                u = url.replace("\n", "")
                linkurl = http.request('GET', u)
                link = linkurl.data.decode('utf-8')
                f = http.request('GET', "https://raw.githubusercontent.com/seevik2580/tor-ip-changer/master/dist/%s/build.txt" % self.lastver)

                self.lastbuild = f.data.decode('utf-8')
                self.write('Last available version:  %s-%s\n' % (self.lastver, self.lastbuild), "white", 1)
                v = version.replace(".", "")
                l = self.lastver.replace(".", "")
                if int(v) >= int(l):
                    if int(build) >= int(self.lastbuild):
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
                    if self.auto == 1 or args.auto is not None:
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

    # funkce pro kontrolu velikosti souboru local vs url
    def checkFileSize(self, url=None, write=None, folder=None):
        from urllib.request import urlopen
        file_name = url.split('/')[-1]
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        u = urlopen(url, context=ctx)
        fo = folder
        if folder is None:
            fo = ""
        else:
            fo = "%s/" % folder
        localFile = "%s%s" % (fo, file_name)
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

    # funkce downloaderu pro stazeni souboru z internetu
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
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            u = urllib.request.urlopen(req, context=ctx)
            fo = folder
            if folder is None:
                fo = ""
            else:
                fo = "%s/" % folder

            f = open("%s%s" % (fo, file_name), 'wb')
            meta = u.info()
            totalFileSize = int(meta['Content-Length'])
            if write is None:
                tfs = (totalFileSize / 1024)
                self.write("Downloading:  {:<30}{:>13} KB\n".format(file_name, int(round(tfs))), "error", 1)
                self.progressbar['style'] = "red.Horizontal.TProgressbar"

            bufferSize = 9192
            count = fielSize = 0

            while True:
                buffer = u.read(bufferSize)
                if not buffer:
                    break

                fielSize += len(buffer)
                f.write(buffer)
                per = (fielSize * 100 / totalFileSize)
                status = "%3.2f" % per + "" * (int)(per / 2)
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

    # funkce na pusteni oddelenych procesy zmeny IP a zjisteni IP
    def ipProc(self):
        _thread.start_new_thread(self.startnewIP, ())
        _thread.start_new_thread(self.ip, ())

    # funkce startu zmeny IP
    def startchange(self, custom=None):
        self.start = timer()
        if custom is None:
            self.write('IP Changer started.\n', "green", 1)
        self.progressbar["style"] = "green.Horizontal.TProgressbar"
        if custom is None:
            self.changermenu.entryconfig(0, state="disabled")
            self.changermenu.entryconfig(1, state="normal")
            self.changermenu.entryconfig(2, state="normal")

        _thread.start_new_thread(self.ipProc, ())
        _thread.start_new_thread(self.appInfo, ())

    # funkce zastaveni zmeny IP
    def stopchange(self, custom=None):
        if custom is None:
            self.write('IP Changer stopped.\n', "error", 1)
        self.ident = random.random()
        self.meni = 0
        self.IPchanged = 0
        self.IPfetched = 0
        if args.multi is not None:
            instances = args.multi
        else:
            instances = 1
        for i in range(instances):
            exec("self.proxyblacklist_%s = 0" % i)
        self.allProxyblacklist = 0
        self.postpone = 0
        self.failed = 0

        if custom is None:
            self.changermenu.entryconfig(0, state="normal")
            self.changermenu.entryconfig(1, state="disabled")
            self.changermenu.entryconfig(2, state="normal")

    # funkce na psani vystupu
    def write(self, message, color, log):
        gui = 1
        if linux:
            if args.nogui is True:
                gui = 0
        if gui == 1:
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

        # funkce na psani debug do logu

    def debug(self, message):
        if self.debuglevel == 1:
            global c
            try:
                logging.debug(message)
            except:
                pass

    # funkce na zjisteni IP adresy z TOR site
    def GetExternalIP(self, proxy=None, url=None):
        if url is None:
            url = self.ipresolver
        file = "Data/tordata%s/ip.txt" % (proxy - 9050)
        interval = int(self.time.get() - 1)
        soc = SOCKSProxyManager('socks5://127.0.0.1:%s/' % proxy)
        s = soc.request('GET', url, timeout=urllib3.Timeout(connect=interval, read=interval), retries=True)
        d = s.data.decode('utf-8').split('\n')
        f = open(file, 'w')
        f.write(d[0])
        f.close()
        s.close()

    def pocetSekund(self, file, languagenumber, country):
        con = sqlite3.connect(file)
        cur = con.cursor()
        try:
            if not country == "random":
                row = cur.execute("select ip,time,country from blacklist where country = '%s' and permanent = 'no'" % country).fetchone()
            else:
                row = cur.execute("select ip,time,country from blacklist where permanent = 'no'").fetchone()
            if row is not None:
                now = time.time()

                vysledek = float(now) - float(row[1])
                vysledek = self.blacklist.get() - vysledek + 10
                seconds = vysledek
            else:
                seconds = 0
        except Exception as e:
            self.error(e)
            seconds = 0
        return int(seconds)

    def clearBlacklistIpDB(self, cport, languagenumber, file):
        con = sqlite3.connect(file)
        cur = con.cursor()
        cur.execute("delete from blacklist where permanent = 'no'")
        con.commit()
        cur.close()
        if self.bezi == 1:
            self.blacklistIpTorrc(cport, languagenumber, file)

    def clearBlacklistIpTorrc(self, cport, languagenumber):
        self.torControl(cport, self.get_controlPassword(languagenumber), "setconf ExcludeExitNodes={??}")
        self.torControl(cport, self.get_controlPassword(languagenumber), "saveconf")

    def blacklistIpDB(self, cport, ip, languagenumber, country, host=None, proxy=None):
        file = "Data/tordata%s/blacklist.db" % languagenumber
        pocete = self.countExitNodes(eval("self.lang_" + str(languagenumber) + ".get()"))
        pocetb = self.countblacklistIps(languagenumber, file, eval("self.lang_" + str(languagenumber) + ".get()"))
        con = sqlite3.connect(file)
        cur = con.cursor()
        cur.execute("select ip from blacklist where ip = '%s'" % ip)
        if args.multi is not None:
            instances = args.multi
        else:
            instances = 1
        if cur.fetchone() is None:
            try:
                if int(pocete) - 1 > int(pocetb):
                    cur.execute("insert into blacklist values ('%s', '%s', '%s', 'no')" % (ip, country, time.time()))
                    con.commit()
                    cur.close()
                    exec("self.proxyblacklist_%s = 0" % languagenumber)
                    self.blacklistIpTorrc(cport, languagenumber, file)
                else:
                    exec("self.proxyblacklist_%s = 1" % languagenumber)
                    seconds = self.pocetSekund(file, languagenumber, country)
                    self.write("------------------------------------------------------------\n|%s:%s |%s \tDepleted! postponed for %s seconds\n" % (host, proxy, eval("self.lang_" + str(languagenumber) + ".get()"), int(seconds)), "error", 1)
                    self.write("|%s:%s |%s \tLast available IP = %s\n------------------------------------------------------------\n" % (host, proxy, eval("self.lang_" + str(languagenumber) + ".get()"), ip), "error", 1)

                    c = 0
                    for i in range(instances):
                        c = c + eval("self.proxyblacklist_%s" % i)
                    if c == instances:
                        self.allProxyblacklist = 1

                    if self.allProxyblacklist == 1:
                        seconds = self.pocetSekund(file, languagenumber, country)
                        if args.multi is not None:
                            self.write("------------------------------------------------------------\n|All proxies depleted, next change postponed for %s seconds\n" % (int(seconds)), "error", 1)
                        if self.meni == 1:
                            self.stopchange(1)
                            self.postpone = 1
                            progress = 0
                            start = timer()
                            max = int(self.pocetSekund(file, languagenumber, country))
                            self.postponetime.set(max)
                            self.progressbar['max'] = self.postponetime.get()
                            while not progress > self.postponetime.get():
                                self.progressbar['max'] = self.postponetime.get()
                                if self.bezi == 0 or self.postpone == 0:
                                    return
                                progress = timer() - start
                                self.progressbar['value'] = self.postponetime.get() - progress
                                time.sleep(0.01)
                            self.postpone = 0
                            self.allProxyblacklist = 0
                            for i in range(instances):
                                exec("self.proxyblacklist_%s = 0" % i)
                            self.startchange(1)

            except Exception as e:
                self.error(e)

    def blacklistIpTorrc(self, cport, languagenumber, file):
        con = sqlite3.connect(file)
        cur = con.cursor()
        list = ""
        cur.execute("select ip from blacklist")
        if not cur.fetchone() is None:
            for row in cur.execute("select ip from blacklist").fetchall():
                list += "%s," % row[0]
            list = "%s{??}" % list
        else:
            list = "{??}"
        cur.close()
        self.torControl(cport, self.get_controlPassword(languagenumber), "setconf ExcludeExitNodes=%s" % (list))
        self.torControl(cport, self.get_controlPassword(languagenumber), "saveconf")

    def countExitNodes(self, country=None):
        if country is not None and country != "random":
            country = re.sub('[\(\)\{\}<>]', '', country)
            cc = 0
            for c in country.replace(",", " ").split():
                url = "https://onionoo.torproject.org/summary?search=country:%s%%20flag:exit" % str(c)
                http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
                r = http.request('GET', url)
                obsah = r.data.decode('utf-8')
                jsonobsah = json.loads(obsah)
                pocet = len(jsonobsah['relays'])
                cc = cc + pocet
            pocet = cc
            return pocet
        else:
            url = "https://onionoo.torproject.org/summary?search=flag:exit"
            http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
            r = http.request('GET', url)
            obsah = r.data.decode('utf-8')
            jsonobsah = json.loads(obsah)
            pocet = len(jsonobsah['relays'])
            return pocet


    def countblacklistIps(self, languagenumber, file, country=None):
        if country is not None and country != "random":
            country = re.sub('[\(\)\{\}<>]', '', country)
            cc = 0
            pocet = 0
            for c in country.replace(",", " ").split():
                con = sqlite3.connect(file)
                cur = con.cursor()
                for row in cur.execute("select ip,country from blacklist where country = '%s'" % c).fetchall():
                    if row[1] == c:
                        cc = cc + 1
                pocet = pocet + cc
                cur.close()
            return pocet
        else:
            cc = 0
            con = sqlite3.connect(file)
            cur = con.cursor()
            for row in cur.execute("select ip from blacklist").fetchall():
                cc = cc + 1
            cur.close()
            return cc


    def checkExcludedIps(self, cport, languagenumber):
        try:
            file = "Data/tordata%s/blacklist.db" % languagenumber
            con = sqlite3.connect(file)
            cur = con.cursor()
            for row in cur.execute("select ip,time from blacklist where permanent = 'no'").fetchall():
                ip = row[0]
                cas = row[1]
                now = time.time()
                if now - float(cas) > self.blacklist.get():
                    cur.execute("delete from blacklist where ip = '%s'" % ip)
            con.commit()

            list = ""
            cur.execute("select ip from blacklist")
            if not cur.fetchone() is None:
                for row in cur.execute("select ip from blacklist").fetchall():
                    list += "%s," % row[0]
                list = "%s{??}" % list
            else:
                list = "{??}"
            cur.close()
            self.torControl(cport, self.get_controlPassword(languagenumber), "setconf ExcludeExitNodes=%s" % (list))
            self.torControl(cport, self.get_controlPassword(languagenumber), "saveconf")
        except Exception as e:
            self.error(e)

    def error(self, e):
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    # funkce na zjisteni odezvy pro zjistenou IP adresu, nejdrive zavola zjisteni IP a nasledne provede overeni odezvy, a vypise vystup do aplikace
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
            blacklist = "Data/tordata%s/blacklist.db" % languagenumber
            language = eval('self.lang_' + str(languagenumber) + '.get()')
            cport = 5950 + proxy
            try:
                color = "white"
                self.GetExternalIP(proxy, self.ipresolver)
                file = "Data/tordata%s/ip.txt" % languagenumber
                f = open(file, 'r')
                ip = f.read()
                f.close()
                if windows:
                    ping = os.popen('ping -n 1 -w 1 %s' % ip)
                elif linux:
                    ping = os.popen('ping -c 1 -w 1 %s' % ip)
                result = ping.readlines()
                msLine = result[-1].strip()
                latency = msLine.split(' = ')[-1]
                iptocountry = self.torControl(cport, self.get_controlPassword(languagenumber), "GETINFO ip-to-country/%s" % ip)
                iptocountry = iptocountry.split("\r\n", 3)
                output = iptocountry[1].split(" ", 5)
                country = output[0].split("=")
                unique = eval("self.checkvarUnique_%s.get()" % languagenumber)

                if latency == "Ping request could not find host None. Please check the name and try again.":
                    latency = "OFFLINE"
                    color = "red"

                try:
                    if windows:
                        ms = latency.split('ms')[0]
                    elif linux:
                        ms = latency.split('ms')[0].split('/')[0].split(".")[0]
                    if ms.isdigit() is True or latency == "1000+" or latency == "500+" or latency == "OFFLINE":
                        latency = "%sms" % ms
                    else:
                        latency = "####"
                        color = "orange"
                except:
                    latency = "####"
                    color = "red"
                if len(language) > 9:
                    language = language.replace(language[6:], "...")

                pos = self.output.index('end-1c linestart')
                pos = float(pos) - 1
                opakovani = 0
                try:
                    lastoutput = self.output.get(pos, END).strip("\n").split(" ")
                    prvni = lastoutput[0]
                    j = 0
                    for i in lastoutput:
                        if i == "|%s:%s" % (host, proxy):
                            j = 1
                        if i == ip:
                            if j == 1:
                                opakovani = 1
                                break
                except:
                    pass
                if not opakovani == 1:
                    self.checkExcludedIps(cport, languagenumber)
                    if eval("self.proxyblacklist_%s" % languagenumber) == 0:
                        try:
                            cl = country[1]
                        except:
                            cl = "??"
                        self.write("|" + host.ljust(9) + ":" + str(proxy).ljust(5) + "|" + str(language).ljust(12) + "-> " + str(ip).rjust(16) + " |" + str(cl) + "|" + str(latency).rjust(6) + "|\n", color, 0)
                        logging.info("127.0.0.1:%s IP %s %s " % (proxy, ip, latency))
                        self.IPfetched = self.IPfetched + 1
                f.close()
                if unique == 1:
                    try:
                        self.blacklistIpDB(cport, ip, languagenumber, cl, host, proxy)
                    except:
                        pass
                else:
                    try:
                        self.clearBlacklistIpTorrc(cport)
                    except:
                        pass
                if self.bezi == 0:
                    return
            except Exception as e:
                logging.error(e)
                self.error(e)
                status = eval("self.proxystatus_%s" % str(proxy))
                if self.bezi == 0 or self.meni == 0:
                    return

                if status == "FAILED":
                    status = "Changing FAILED"
                else:
                    status = "Changing OK but unable to connect"

                if len(language) > 6:
                    language = language.replace(language[6:], "...")

                pos = self.output.index('end-1c linestart')
                pos = float(pos) - 1
                opakovani = 0
                try:
                    lastoutput = self.output.get(pos, END).strip("\n").split(" ")
                    prvni = lastoutput[0]
                    druhy = lastoutput[8]
                    statustext = status.split(" ")
                    if prvni == "|%s:%s" % (host, proxy) and druhy == "%s" % statustext[0]:
                        opakovani = 1
                except:
                    pass

                if not opakovani == 1:
                    try:
                        with open(logtor, 'rb') as f:
                            f.seek(-2, os.SEEK_END)
                            while f.read(1) != b'\n':
                                f.seek(-2, os.SEEK_CUR)
                            last_line = f.readline().decode()
                            routers = last_line.strip('\n').split(" ")
                            if routers[4] == "All" and routers[5] == "routers":
                                #status = "All routers down or blacklist"
                                exec("self.proxyblacklist_%s = 1" % languagenumber)
                                seconds = self.pocetSekund(blacklist, languagenumber, eval("self.lang_" + str(languagenumber) + ".get()"))
                                self.write("------------------------------------------------------------\n|%s:%s |%s \tDepleted! postponed for %s seconds\n" % (host, proxy, eval("self.lang_" + str(languagenumber) + ".get()"), int(seconds)), "error", 1)

                                c = 0
                                if args.multi is not None:
                                    instances = args.multi
                                else:
                                    instances = 1
                                for i in range(instances):
                                    c = c + eval("self.proxyblacklist_%s" % i)
                                if c == instances:
                                    self.allProxyblacklist = 1

                                if self.allProxyblacklist == 1:
                                    seconds = self.pocetSekund(blacklist, languagenumber, eval("self.lang_" + str(languagenumber) + ".get()"))
                                    if args.multi is not None:
                                        self.write("------------------------------------------------------------\n|All proxies depleted, next change postponed for %s seconds\n" % (int(seconds)), "error", 1)
                                    if self.meni == 1:
                                        self.stopchange(1)
                                        self.postpone = 1
                                        progress = 0
                                        start = timer()
                                        max = int(self.pocetSekund(blacklist, languagenumber, eval("self.lang_" + str(languagenumber) + ".get()")))
                                        self.progressbar['max'] = max
                                        while not progress > max:
                                            if self.bezi == 0 or self.postpone == 0:
                                                return
                                            progress = timer() - start
                                            self.progressbar['value'] = max - progress
                                            time.sleep(0.01)
                                        self.postpone = 0
                                        self.allProxyblacklist = 0
                                        for i in range(instances):
                                            exec("self.proxyblacklist_%s = 0" % i)
                                        self.startchange(1)
                                        return
                    except Exception as e:
                        self.error(e)
                        pass
                    self.write("|" + host.ljust(9) + ":" + str(proxy).ljust(5) + "|" + str(language).ljust(8) + " " + str(status).rjust(1) + "|\n", "error", 0)
                logging.info("127.0.0.1:%s failed - status: %s" % (proxy, status))
                pass

        for i in range(instanci):
            _thread.start_new_thread(fetching, (proxy,))
            proxy = proxy + 1

    # funkce startu zjistovani aktualni IP adresy ve smycce
    def ip(self):
        key = self.ident
        while key == self.ident:
            if key != self.ident:
                break
            try:
                interval = self.time.get()
                start = timer()
                while not float(self.progressbar['value']) > float(interval) - 1:
                    if key != self.ident:
                        break
                    time.sleep(0.01)
                if key != self.ident:
                    break
                self.IPandlatency()
                time.sleep(2)
                end = timer()
                result = (end - start)
                seconds = float(result)
            except:
                self.failed = self.failed + 1

        self.meni = 0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed = 0

    # funkce na overeni zda je hodnota cislo
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

    # funkce spusteni zmeny IP adresy ve smycce
    def startnewIP(self):
        key = self.ident
        interval = self.time.get()
        while key == self.ident:
            try:
                self.IPchanged = self.IPchanged + 1
                self.meni = 1
                timeout = 0
                interval = self.time.get()
                self.progressbar["maximum"] = interval
                self.progressbar["value"] = timeout
                start = timer()
                progress = 1
                _thread.start_new_thread(self.newIP, ())
                while not progress > interval:
                    progress = timer() - start

                    if key != self.ident:
                        break
                    self.progressbar["style"] = "green.Horizontal.TProgressbar"
                    self.progressbar["maximum"] = interval
                    self.progressbar["value"] = interval - progress
                    time.sleep(0.01)
            except:
                pass
        self.meni = 0
        self.IPchanged = 0
        self.IPfetched = 0
        self.failed = 0
        if self.bezi == 1:
            self.progressbar["style"] = "orange.Horizontal.TProgressbar"
        else:
            self.progressbar["value"] = 0

    # funkce na zmenu IP adresy, odpojeni predeslych circuit a spojeni
    def newIP(self, port=None):

        self.controlport = 15000
        proxy = 9050
        try:
            pos = self.output.index('end-1c linestart')
            pos = float(pos) - 1
            if not self.output.get(pos, END).strip("\n") == "-------------------------CHANGING-IP------------------------":
                self.write("-------------------------CHANGING-IP------------------------\n", "white", 1)
        except:
            pass
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
            for i in range(instanci):
                try:
                    if eval("self.proxyblacklist_%s" % i) == 0:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(2)
                        s.connect((host, self.controlport))
                        authcmd = 'AUTHENTICATE "%s"' % self.get_controlPassword(identify)
                        s.send((authcmd).encode('utf-8') + b"\r\n")
                        s.send(("signal RELOAD").encode('ascii') + b"\r\n")
                        s.send(("GETINFO circuit-status").encode('ascii') + b"\r\n")
                        circ = s.recv(8192).decode("utf-8")

                        try:
                            with open("Data/tordata%s/circ.txt" % i, "w") as f:
                                f.write(circ)
                                f.close()

                            with open("Data/tordata%s/circ.txt" % i, "r") as f:
                                result = f.readlines()
                                self.debug(result)

                                for r in result:
                                    d = re.findall(r'\b\d+\b', r.split(" BUILT ")[0])
                                    for q in d:
                                        self.debug(q)
                                        if q != "250":
                                            s.send(("closecircuit %s" % q).encode('ascii') + b"\r\n")
                                            data = s.recv(128)
                                            if data == b'250 OK\r\n':
                                                logging.debug("Killing previous circuit ID %s " % q)
                                f.close()

                            with open("Data/tordata%s/circ.txt" % i, "w") as f:
                                f.write("ok")
                                f.close()

                            os.remove("Data/tordata%s/circ.txt" % i)
                        except Exception as e:
                            self.error(e)


                        self.checkExcludedIps(self.controlport, identify)
                        s.send(("signal NEWNYM").encode('ascii') + b"\r\n")
                        s.send(("QUIT").encode('ascii') + b"\r\n")
                        s.close()
                        self.failed = 0
                        status = "OK"
                    else:
                        self.checkExcludedIps(self.controlport, identify)
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(2)
                        s.connect((host, self.controlport))
                        authcmd = 'AUTHENTICATE "%s"' % self.get_controlPassword(identify)
                        s.send((authcmd).encode('utf-8') + b"\r\n")
                        s.send(("signal RELOAD").encode('ascii') + b"\r\n")
                        s.send(("QUIT").encode('ascii') + b"\r\n")
                        s.close()
                        self.failed = 0
                        status = "OK"

                except Exception as e:
                    self.error(e)
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


def ukoncit():
    os.system(r'killall tor')
    os.system(r'killall tail')
    os._exit(1)

def signal_handler(signal, frame):
    ukoncit()

# vykresleni aplikace
if __name__ == '__main__':
    try:
        mw = IpChanger()
        if linux:
            signal.signal(signal.SIGINT, signal_handler)
        mw.mainloop()
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
    finally:
        # os._exit(1)
        # zabij vse co jsi pustil
        if windows:
            SW_HIDE = 0
            info = subprocess.STARTUPINFO()
            info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = SW_HIDE
            subprocess.Popen(r'taskkill /f /im tor.exe', startupinfo=info)
            subprocess.Popen(r'taskkill /f /im obfs4proxy.exe', startupinfo=info)
            subprocess.Popen(r'taskkill /f /im tail.exe', startupinfo=info)
            os._exit(1)
        elif linux:
            ukoncit()
