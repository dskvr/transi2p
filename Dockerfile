FROM python:3.8
RUN pip install transi2p
COPY config.json /etc/transi2p/config.json
# Add other necessary configurations and scripts
CMD ["twistd", "-n", "transi2p"]
