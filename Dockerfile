FROM ubuntu:20.04
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt -y install subversion authbind tor obfs4proxy psmisc python3-pip libcurl4-openssl-dev libssl-dev tk-dev python3-tk iputils-ping
RUN svn export https://github.com/seevik2580/tor-ip-changer/trunk/source-code-linux /app
WORKDIR /app
RUN cd */ ; dpkg -i requirements/meek-client_0.20+git20151006-1_amd64.deb
RUN cd */ ; python3 -m pip install -r requirements/pip-requirements.txt
RUN cd */ ; LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib pyinstaller --onefile ipchanger.py
RUN cd */ ; mv dist/ipchanger /usr/bin/ipchanger && rm -fr /app && chmod +x /usr/bin/ipchanger
RUN apt -y purge subversion libcurl4-openssl-dev libssl-dev python3-pip x11-apps tk-dev && apt -y autoremove && apt -y clean && rm -rf /var/lib/apt/lists/* && rm -rf /root/.cache/*
CMD ["ipchanger"]
