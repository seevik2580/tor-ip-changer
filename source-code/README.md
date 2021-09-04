# Windows 
## requirements:
- windows 10
- python 3.7.x

## requirements install with:
`pip install -r requirements/windows/pip-requirements.txt`

or

```
pip install urllib3
pip install pysocks
pip install py2exe==0.10.2.0
```
## build exe file:
`python setup-ipchanger-windows.py`

---

# Linux
## requirements:
- linux (ubuntu,debian..)
- pynev python 3.7.x+

## Docker
 - [Dockerfile](https://github.com/seevik2580/tor-ip-changer/blob/master/Dockerfile)
```
cd ../ ; docker build . -t ipchanger
xhost +
docker run -p 14999:14999 -p 9050:9050 -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ipchanger
```
 - [docker-compose](https://github.com/seevik2580/tor-ip-changer/blob/master/docker-compose.yml)
```
xhost +
docker-compose up -d
```
 - [docker hub](https://hub.docker.com/r/seevik2580/tor-ip-changer)
```
docker run -p 14999:14999 -p 9050:9050 -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix seevik2580/tor-ip-changer
```
************************************************************

## dependency install:
### part1 - install curl, authbind, tor, obfs4proxy, meek-client, libsqlite3-dev, tk-dev, and stop tor service after install and allow to bind port 53 without root permission
```
sudo apt install curl authbind tor obfs4proxy psmisc build-essential libsqlite3-dev tk-dev
sudo dpkg -i requirements/linux/meek-client_0.20+git20151006-1_amd64.deb
sudo systemctl disable tor
sudo systemctl stop tor
sudo touch /etc/authbind/byport/53
sudo chmod 777 /etc/authbind/byport/53
```

### part2 - install pyenv
```
curl https://pyenv.run | bash`

echo 'export PATH="~/.pyenv/bin:$PATH"' | tee -a ~/.bashrc
echo 'eval "$(pyenv init -)"' | tee -a ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' | tee -a ~/.bashrc

exec $SHELL
```

### part3 - install python 3.7.x with pyenv
```
env PYTHON_CONFIGURE_OPTS="--enable-shared" ~/.pyenv/bin/pyenv install 3.7.7
pyenv global 3.7.7
```

### part4 - install requirements with pip
`python -m pip install -r requirements/linux/pip-requirements.txt`

or
```
pip install urllib3
pip install pysocks
pip install pyinstaller
```

### run tor-ip-changer with python
`python ipchanger.py`
 
### compile, run tor-ip-changer
```
sh setup-ipchanger-linux.sh
chmod +x ipchanger
./ipchanger
```

### run on linux without display (console only)
```
sudo apt install xvfb
export DISPLAY=:1
Xvfb :1 -screen 0 1024x768x16 &
./ipchanger --nogui
# or 
python ipchanger.py --nogui
```