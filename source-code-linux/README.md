## requirements:
- linux (ubuntu,debian..)
- pynev python 3.4.10
 
## dependency install:
- `curl https://pyenv.run | bash`
- add at the end of ~/.bashrc
```
export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
- `env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.4.10`
- `sudo apt install libcurl4-openssl-dev libssl-dev`
- `pyenv global 3.4.10`
- `python -m pip install -r requirements/pip-requirements.txt`

## binaries:
- use build.sh to build binaries for linux
- binaries can be found inside folder Dist
