FROM python:3.8
RUN apt-get update && apt-get install -y iptables sudo
RUN pip3 install --upgrade pip

RUN mkdir -p /var/lib/transi2p
COPY . /var/lib/transi2p/

COPY ./config.json /etc/transi2p/config.json

RUN chmod +x /var/lib/transi2p/rules.sh
RUN chmod +x /var/lib/transi2p/start.sh
RUN pip3 install /var/lib/transi2p

COPY twisted/plugins/transi2p_plugin.py /usr/local/lib/python3.8/site-packages/twisted/plugins/

CMD ["/var/lib/transi2p/start.sh"]