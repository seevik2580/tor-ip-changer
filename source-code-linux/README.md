# experimental! not stable!

## requirements:
- linux (ubuntu,debian..)
- pynev python 3.4.10
 
## dependency install:
### part1
- `sudo apt install curl libcurl4-openssl-dev libssl-dev authbind tor obfs4proxy`
- `sudo dpkg -i requirements/meek-client_0.20+git20151006-1_amd64.deb`
- `sudo systemctl stop tor`
- `curl https://pyenv.run | bash`
- add at the end of ~/.bashrc
```
export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
### part2
- `exec $SHELL`
- `env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.4.10`
- `pyenv global 3.4.10`
- `python -m pip install -r requirements/pip-requirements.txt`
- `sudo touch /etc/authbind/byport/53`
- `sudo chmod 777 /etc/authbind/byport/53`
- `python ipchanger.py`

## binaries:
- use build.sh to build binaries for linux
- binaries can be found inside folder Dist/ipchanger
- `cd dist/ipchanger`
- `./ipchanger`
