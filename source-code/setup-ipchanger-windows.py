from distutils.core import setup
import py2exe
import sys
import shutil, errno, os 
 
def py2_exe(file_in, ico=None):
    if ico == None:
        pass
    else:
        dest_ico = ico.split('.')[0]
    if len(sys.argv) == 1:
        sys.argv.append('py2exe')
    
    # Py2exe finds most module,here you can include,exclude moduls
    includes = []
    excludes = []
    packages = []
    dll_excludes = []
 
    # Bundle_files : 3 most stable | bundle_files : 1 create 1 big exe
    setup(options =\
    {'py2exe': {'compressed': 1,
                'optimize': 1,
                'bundle_files': 3,
                'includes': includes,
                'excludes': excludes,
                'packages': packages,
                'dll_excludes': dll_excludes,}},
                 zipfile = "Lib\library.zip", #None or "lib\library.zip"
    
    # Can use console(Command line) or windows(GUI)
    windows = [{
              'script': file_in,
              #--| Uncomment for ico
              ##'icon_resources' : [(1, ico)],
              ##'dest_base' : dest_ico
                   }])
 
if __name__ == '__main__':
    #--| The .py file you want to make exe of
    file_in = 'ipchanger.py'
    #--| Ico in same folder as .py
    #ico = 'your.ico'
    if os.path.exists('dist'):
      shutil.rmtree('dist')
    py2_exe(file_in)
