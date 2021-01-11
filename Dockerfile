FROM ubuntu:20.04
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt -y install git curl authbind tor obfs4proxy psmisc python3-pip libcurl4-openssl-dev libssl-dev tk-dev python3-tk x11-apps
RUN cd /tmp ; git clone https://github.com/seevik2580/tor-ip-changer.git
RUN cd /tmp/tor-ip-changer/source-code-linux/1.2.3 ; dpkg -i requirements/meek-client_0.20+git20151006-1_amd64.deb
RUN python3 -m pip install -r /tmp/tor-ip-changer/source-code-linux/1.2.3/requirements/pip-requirements.txt
RUN ln -fs /tmp/tor-ip-changer/source-code-linux/1.2.3/ipchanger.py ipchanger
ENTRYPOINT ["/usr/bin/python3"]
CMD ["ipchanger"]
