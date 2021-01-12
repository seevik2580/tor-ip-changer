FROM ubuntu:20.04
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt -y install git curl authbind tor obfs4proxy psmisc python3-pip libcurl4-openssl-dev libssl-dev tk-dev python3-tk x11-apps iputils-ping
RUN cd /root ; git clone https://github.com/seevik2580/tor-ip-changer.git
RUN cd /root/tor-ip-changer/source-code-linux/1.2.7 ; dpkg -i requirements/meek-client_0.20+git20151006-1_amd64.deb
RUN python3 -m pip install -r /root/tor-ip-changer/source-code-linux/1.2.7/requirements/pip-requirements.txt
RUN ln -fs /root/tor-ip-changer/source-code-linux/1.2.7/ipchanger.py ipchanger
ENTRYPOINT ["/usr/bin/python3"]
CMD ["ipchanger"]
