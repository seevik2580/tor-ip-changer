FROM ubuntu:20.04 AS builder
COPY source-code /app
RUN apt-get update \
        && DEBIAN_FRONTEND=noninteractive apt -y install libsqlite3-dev python3-pip libcurl4-openssl-dev libssl-dev tk-dev python3-tk \
        && python3 -m pip install -r /app/requirements/linux/pip-requirements.txt \
        && sed -i 's/authbind \-\-deep//g' /app/ipchanger.py \
        && LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib pyinstaller --onefile /app/ipchanger.py \
        && mv /dist/ipchanger /usr/bin/ipchanger

FROM ubuntu:20.04
WORKDIR ["/app"]
COPY --from=builder /usr/bin/ipchanger /usr/bin/ipchanger
COPY --from=builder /app/requirements/linux/meek-client_0.20+git20151006-1_amd64.deb /app/meek-client_0.20+git20151006-1_amd64.deb
RUN apt-get update \
        && DEBIAN_FRONTEND=noninteractive apt -y install tor obfs4proxy psmisc python3-tk iputils-ping ca-certificates \
        && dpkg -i /app/meek-client_0.20+git20151006-1_amd64.deb \
        && rm -f /app/meek-client_0.20+git20151006-1_amd64.deb \
        && apt -y clean \
        && rm -rf /var/lib/apt/lists/*
CMD ["ipchanger"]
