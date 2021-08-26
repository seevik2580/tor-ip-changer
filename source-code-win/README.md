## requirements:
- windows 10
- python 3.7.x
- nuitka (https://nuitka.net)
 
## dependency install:
- `pip install -r requirements/pip-requirements.txt`

## binaries:
- use build.bat to build binaries for windows or use command:`nuitka --onefile --standalone --plugin-enable=multiprocessing --plugin-enable=tk-inter --windows-disable-console --remove-output .\ipchanger.py`
