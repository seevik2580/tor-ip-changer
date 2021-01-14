@echo off
python setup-ipchanger.py
pyinstaller -F -w updater.py
move /Y dist\Lib\*.* dist\tcl
rmdir dist\Lib
ren dist\tcl Lib 	
