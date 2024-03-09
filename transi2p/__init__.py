from twisted.internet import protocol, reactor
from twisted.internet.endpoints import clientFromString, connectProtocol
from twisted.names import client, dns, error
from twisted.internet import defer
# from twisted.names.client import createResolver
import socket
import struct
import re
# import asyncio
import logging
from twisted.python import log

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


ip_re = re.compile(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$')
socket.SO_ORIGINAL_DST = 80

class AddressMap(object):
    def __init__(self, addr_map, default_mappings):
        self.base_addr = struct.unpack('>I', socket.inet_aton(addr_map))[0]
        self.addr_index = 0

        self.names = {}
        self.addresses = {}

        for addr in default_mappings:
            name = str(default_mappings[addr])
            addr = str(addr)

            if ip_re.match(addr):
                self.names[name] = addr
                self.addresses[addr] = name
            else:
                self.names[addr] = name
                self.addresses[name] = addr

    def map(self, name):
        if name in self.names:
            return self.names[name]
        else:
            addr = None
            while not addr or addr in self.addresses:
                self.addr_index += 1
                addr = socket.inet_ntoa(struct.pack('>I', self.base_addr + self.addr_index))

            self.names[name] = addr
            self.addresses[addr] = name
            return addr

    def get_name(self, addr):
        if addr in self.addresses:
            return self.addresses[addr]
        else:
            return None

class EepNS(object):
    def __init__(self, resolvers):
        # Initialize a Twisted Resolver with the specified external DNS resolvers
        self.external_resolver = client.Resolver(servers=resolvers, resolv='/var/lib/transi2p/etc/resolv.conf')  # Increased timeout

    def map_address(self, query):
        name = query.name.name
        addr = address_map.map(name)
        answer = dns.RRHeader(name=name, payload=dns.Record_A(address=addr))
        return [answer], [], []

    def query(self, query, timeout=None):
        domain_name = query.name.name.decode('utf-8')
        logging.debug("Query is for %s", domain_name)
        logging.debug("Domain name is type %s", type(domain_name))
        if query.type == dns.A and domain_name.endswith('.i2p'):
            return defer.succeed(self.map_address(query))
        elif domain_name.endswith('.onion'):
            # Handle .onion domains (Return a dummy IP or similar approach, as actual resolution happens via Tor)
            dummy_ip = "172.24.0.2"  # Placeholder IP, adjust as needed
            answer = dns.RRHeader(name=query.name.name, payload=dns.Record_A(address=dummy_ip))
            return defer.succeed(([answer], [], []))
        else:
            # Forward other queries to the external resolver
            d = self.external_resolver.query(query)
            d.addCallback(self.handleResponse)
            d.addErrback(self.handleError)
            return d
    # def query(self, query, timeout=None):
    #     domain_name = query.name.name.decode('utf-8')
    #     if query.type == dns.A and domain_name.endswith('.i2p'):
    #         return defer.succeed(self.map_address(query))
    #     else:
        d = self.external_resolver.query(query)
    #         d.addCallback(self.handleResponse)
    #         d.addErrback(self.handleError)
    #         return d
    #         

    def handleResponse(self, response):
        if response:
            ans, auth, add = response
            return ans, auth, add
        else:
            logging.error("Received empty response from external resolver")
            return [], [], []

    def handleError(self, failure):
        logging.error("Error in DNS query: %s", failure)
    # def query(self, query, timeout=None):
    #     domain_name = query.name.name.decode('utf-8')
    #     logging.debug("Received DNS query: %s", domain_name)
    #     if query.type == dns.A and domain_name.endswith('.i2p'):
    #         logging.debug("Query is for .i2p domain. Handling internally.")
    #         return defer.succeed(self.map_address(query))
    #     else:
    #         logging.debug("Query is for non-.i2p domain. Forwarding to external resolver.")
    #         d = self.external_resolver.query(query)
    #         d.addErrback(log.err)  # Log any errors during the query
    #         return d

class EepConnection(protocol.Protocol):
    def __init__(self, proxy):
        self.proxy = proxy

    def dataReceived(self, data):
        self.proxy.transport.write(data)

    def connectionLost(self, reason):
        self.proxy.i2p_error(reason)

class TransPort(protocol.Protocol):
    async def connectionMade(self):
        self.pending = b''
        self.i2p = None

        addr = self.transport.socket.getsockopt(socket.SOL_IP, socket.SO_ORIGINAL_DST, 16)
        _, self.dst_port, self.dst_addr, _ = struct.unpack('>HH4s8s', addr)
        self.dst_addr = socket.inet_ntoa(self.dst_addr)

        logging.debug("Connection made with destination: %s:%s", self.dst_addr, self.dst_port)

        name = address_map.get_name(self.dst_addr)
        if not name:
            self.transport.loseConnection()
            return

        endpoint = clientFromString(reactor, 'i2p:' + name)
        i2p_connection = await connectProtocol(endpoint, EepConnection(self))
        
        self.i2p_connected(i2p_connection)

    def dataReceived(self, data):
        if self.i2p:
            self.i2p.transport.write(data)
        else:
            self.pending += data

    def connectionLost(self, reason):
        if self.i2p:
            self.i2p.transport.loseConnection()    

    def i2p_error(self, reason):
        self.transport.loseConnection()

    def i2p_connected(self, i2p):
        self.i2p = i2p
        if self.pending:
            self.i2p.transport.write(self.pending)

address_map = AddressMap('10.18.0.0', {'10.18.0.1': 'stats.i2p'})
