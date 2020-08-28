@echo off
python setup-ipchanger.py py2exe
python setup-updater.py py2exe
move /Y dist\Lib\*.* dist\tcl
rmdir dist\Lib
ren dist\tcl Lib