FROM ubuntu:20.04 AS builder
RUN apt-get update \
        && DEBIAN_FRONTEND=noninteractive apt -y install subversion python3-pip libcurl4-openssl-dev libssl-dev tk-dev python3-tk \
        && svn export https://github.com/seevik2580/tor-ip-changer/trunk/source-code-linux /app \
        && cd /app \
        && cd */ \
        && dpkg -i requirements/meek-client_0.20+git20151006-1_amd64.deb \
        && python3 -m pip install -r requirements/pip-requirements.txt \
        && sed -i 's/authbind \-\-deep//g' start.py \
        && LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib pyinstaller --onefile ipchanger.py \
        && mv dist/ipchanger /usr/bin/ipchanger

FROM ubuntu:20.04
WORKDIR ["/app"]
COPY --from=builder /usr/bin/ipchanger /usr/bin/ipchanger
RUN apt-get update \
        && DEBIAN_FRONTEND=noninteractive apt -y install tor obfs4proxy psmisc python3-tk iputils-ping ca-certificates \
        && apt -y clean \
        && rm -rf /var/lib/apt/lists/*
CMD ["ipchanger"]
