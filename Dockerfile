FROM debian
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt -qqy install x11-apps git curl authbind tor obfs4proxy psmisc build-essential python3-pip libcurl4-openssl-dev libssl-dev xvfb tk-dev python3-tk
RUN cd /tmp ; git clone https://github.com/seevik2580/tor-ip-changer.git
RUN cd /tmp/tor-ip-changer/source-code-linux/1.2.3 ; dpkg -i requirements/meek-client_0.20+git20151006-1_amd64.deb
RUN python3 -m pip install -r /tmp/tor-ip-changer/source-code-linux/1.2.3/requirements/pip-requirements.txt
ENV DISPLAY :0
CMD ["/bin/bash", "-c", "python3 /tmp/tor-ip-changer/source-code-linux/1.2.3/ipchanger.py"]
