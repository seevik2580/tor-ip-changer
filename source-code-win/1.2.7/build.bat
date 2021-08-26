@echo off
nuitka --onefile --standalone --plugin-enable=multiprocessing --plugin-enable=tk-inter --windows-disable-console --remove-output .\ipchanger.py