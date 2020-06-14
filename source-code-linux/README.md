# experimental! not stable!

## requirements:
- linux (ubuntu,debian..)
- pynev python 3.4.10
 
## dependency install:
### part1 - install curl + libs, authbind, tor, obfs4proxy, meek-client, ssl libs, stop tor service after install and allow to bind port 53 without root permission
- `sudo apt install curl libcurl4-openssl-dev libssl-dev authbind tor obfs4proxy`
- `sudo dpkg -i requirements/meek-client_0.20+git20151006-1_amd64.deb`
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
### part3 - install python 3.4.10 with pyenv + install pip requirements
- `exec $SHELL`
- `env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.4.10`
- `pyenv global 3.4.10`
- `python -m pip install -r requirements/pip-requirements.txt`

### run tor-ip-changer
- `python ipchanger.py`

### compile and install tor-ip-changer
- `./build.sh`
