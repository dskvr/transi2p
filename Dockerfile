FROM python:3.8
RUN apt-get update && apt-get install -y iptables net-tools dnsutils wget
RUN pip3 install --upgrade pip
RUN wget -qO /usr/local/bin/websocat https://github.com/vi/websocat/releases/latest/download/websocat.x86_64-unknown-linux-musl
RUN chmod +x /usr/local/bin/websocat

# Create the application directory
RUN mkdir -p /var/lib/transi2p
WORKDIR /var/lib/transi2p

# Copy the application files
COPY . /var/lib/transi2p/
COPY ./etc/resolv.conf /etc/resolv.conf
RUN pip3 install /var/lib/transi2p
COPY twisted/plugins/transi2p_plugin.py /usr/local/lib/python3.8/site-packages/twisted/plugins/

# Create a user
RUN useradd -m -s /usr/sbin/nologin -d /var/lib/transi2p transi2p

# Set up iptables using configure.sh (as root)
RUN chmod +x /var/lib/transi2p/configure.sh
RUN /var/lib/transi2p/configure.sh

# Change ownership to transi2p user
RUN chown -R transi2p:transi2p /var/lib/transi2p

# Switch to non-root user
USER transi2p

# Make sure start.sh is executable
RUN chmod +x /var/lib/transi2p/start.sh
CMD ["/var/lib/transi2p/start.sh"]