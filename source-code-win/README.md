## requirements:
- windows 10
- python 3.4.x-3.7.x
 
## dependency install:
## for python 3.4.x
- `pip install -r requirements/pip-requirements.txt`
- `install requirements/pycurl-7.43.0.win-amd64-py3.4.exe`
## for python 3.5+
- `pip install pycurl pysocks urllib3`
- download py2exe wheel file from [HERE](https://github.com/albertosottile/py2exe/releases)
- `pip install downloadedWheelFileName.whl`


## binaries:
- use build.bat to build binaries for windows or `python setup-ipchanger.py`
- alternative exe builder `pip install pyinstaller` then use `pyinstaller -F ipchanger.py`
- binaries can be found inside folder Dist
