@echo off
python setup-ipchanger.py
pyinstaller -F -w updater.py
