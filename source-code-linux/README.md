# experimental! not stable!

## requirements:
- linux (ubuntu,debian..)
- pynev python 3.4.10
 
## dependency install:
### part1 - install curl + libs, authbind, tor, obfs4proxy, meek-client, ssl libs, stop tor service after install and allow to bind port 53 without root permission
- `sudo apt install curl libcurl4-openssl-dev libssl-dev authbind tor obfs4proxy`
- `sudo dpkg -i requirements/meek-client_0.20+git20151006-1_amd64.deb`
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

### part3 - install python 3.4.10 with pyenv + install pip requirements, pip needs openssl1.0 or installation crashes
- `exec $SHELL`
- `echo "deb [trusted=yes] http://security.ubuntu.com/ubuntu bionic-security main" >> /etc/apt/sources.list`
- `sudo apt update`
- `sudo apt install libssl1.0-dev`
- `env LDFLAGS=-L/usr/lib/openssl-1.0 CFLAGS="-DOPENSSL_NO_SSL3 -I/usr/include/openssl-1.0" PYTHON_CONFIGURE_OPTS="--enable-shared" ~/.pyenv/bin/pyenv install 3.4.10`
- `pyenv global 3.4.10`
- `python -m pip install -r requirements/pip-requirements.txt`

### run tor-ip-changer with python
- `python ipchanger.py`

### compile, install and run tor-ip-changer
- `./build.sh`
- `ipchanger`

```
usage: ipchanger [-h] [-a n] [-d] [-m 1-100] [-p] [-c COUNTRY]
    '-a n' automaticaly change ip after start every n
            example:   ipchanger.exe -a 35
                        change ip auto every 35 sec

    '-m n' start multiple proxy n instances
            example:   ipchanger.exe -m 5
                        start proxy 5 times
                        with different ports
                        and generate list

    '-d' open debug console live log

    '-s' hide sponsor bar after start
    
    '-c {COUNTRYCODE}' select specific country
    
    '-p | --publicAPI' bind API to public IP (default localhost only)

    '-g | --nogui' run without GUI, control through API
            to run in background use `nohup ipchanger -g &`
```