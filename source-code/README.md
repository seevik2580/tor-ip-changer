# Windows 
## requirements:
- windows 10
- python 3.7.x

## requirements install with:
- `pip install -r requirements/windows/pip-requirements.txt`

or

- `pip install urllib3`
- `pip install pysocks`
- `pip install py2exe==0.10.2.0`
- `pip install pycurl`

## binaries:
- to build binaries for windows use command:`python setup-ipchanger-windows.py`


# Linux
## requirements:
- linux (ubuntu,debian..)
- pynev python 3.7.x+

## Docker
 - Dockerfile
```
cd ../ ; docker build . -t ipchanger
xhost +
docker run -p 14999:14999 -p 9050:9050 -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ipchanger
```
 - docker-compose
```
xhost +
docker-compose up -d
```
 - docker hub
```
docker pull seevik2580/tor-ip-changer
```
************************************************************

## dependency install:
### part1 - install curl + libs, authbind, tor, obfs4proxy, meek-client, ssl libs, libsqlite3-dev, stop tor service after install and allow to bind port 53 without root permission
- `sudo apt install curl authbind tor obfs4proxy psmisc build-essential libsqlite3-dev`
- `sudo dpkg -i requirements/linux/meek-client_0.20+git20151006-1_amd64.deb`
- `sudo systemctl disable tor`
- `sudo systemctl stop tor`
- `sudo touch /etc/authbind/byport/53`
- `sudo chmod 777 /etc/authbind/byport/53`

### part2 - install pyenv
- `curl https://pyenv.run | bash`
- add at the end of ~/.bashrc
```
export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
- run `exec $SHELL` to setup new $PATH
### part3 - install python 3.7.x with pyenv and tkinter module + install pip requirements

- `echo "deb [trusted=yes] http://security.ubuntu.com/ubuntu bionic-security main" | sudo tee -a /etc/apt/sources.list`
- `sudo apt update`
- `sudo apt install libssl1.0-dev tk-dev`
- `env LDFLAGS=-L~/usr/lib/openssl-1.0 CFLAGS="-DOPENSSL_NO_SSL3 -I/usr/include/openssl-1.0" PYTHON_CONFIGURE_OPTS="--enable-shared" ~/.pyenv/bin/pyenv install 3.7.7`
- `pyenv global 3.7.7`
- `sudo apt install libcurl4-openssl-dev libssl-dev`

install requirements with
- `python -m pip install -r requirements/linux/pip-requirements.txt`

or
- `pip install urllib3`
- `pip install pysocks`
- `pip install pyinstaller`
- `pip install pycurl`

### run tor-ip-changer with python
- `python ipchanger.py`

### compile, run tor-ip-changer
- `sh setup-ipchanger-linux.sh`
- `ipchanger`

### run on linux without display (console only)
- `sudo apt install xvfb`
- `export DISPLAY=:1`
- `Xvfb :1 -screen 0 1024x768x16 &`
- `ipchanger --nogui`