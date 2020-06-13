## requirements:
- linux (ubuntu,debian..)
- python 3.4.x
- pynev
 
 
## dependency install:
- `curl https://pyenv.run | bash`
- ```
write at the end of .bashrc

export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

- `pip install -r requirements/pip-requirements.txt`

## binaries:
- use build.sh to build binaries for linux
- binaries can be found inside folder Dist
