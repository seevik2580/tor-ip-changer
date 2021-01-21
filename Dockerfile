FROM ubuntu:20.04
RUN apt-get update \ 
        && DEBIAN_FRONTEND=noninteractive apt -y install subversion authbind tor obfs4proxy psmisc python3-pip libcurl4-openssl-dev libssl-dev tk-dev python3-tk iputils-ping \
        && apt -y clean \
        && rm -rf /var/lib/apt/lists/* \
        && svn export https://github.com/seevik2580/tor-ip-changer/trunk/source-code-linux /app \
        && cd /app \
        && cd */ \
        && dpkg -i requirements/meek-client_0.20+git20151006-1_amd64.deb \
        && python3 -m pip install -r requirements/pip-requirements.txt \
        && LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib pyinstaller --onefile ipchanger.py \
        && mv dist/ipchanger /usr/bin/ipchanger \
        && rm -fr /app \
        && chmod +x /usr/bin/ipchanger \
        && apt -y purge subversion libcurl4-openssl-dev libssl-dev python3-pip tk-dev \
        && apt -y autoremove \
        && apt -y clean \
        && rm -rf /var/lib/apt/lists/* \
        && rm -rf /root/.cache/*
WORKDIR /app
CMD ["ipchanger"]
