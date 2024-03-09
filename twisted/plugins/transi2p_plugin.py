from twisted.application import internet, service
from twisted.internet import protocol
from twisted.names import dns, server, client
from twisted.python import usage
import json
import transi2p
from zope.interface import implementer

from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker


class Options(usage.Options):
    optParameters = [['config', 'c', 'config.json', 'Path to config file']]

@implementer(IServiceMaker, IPlugin)
class TransServiceMaker(object):
    tapname = "transi2p"
    description = "I2P transparent proxy service."
    options = Options

    def makeService(self, options):
        path = options['config']

        try:
            with open(path, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f'Writing default config to {path}.')
            config = self.default_config()
            with open(path, 'w') as f:
                json.dump(config, f)
        except ValueError:
            print('Invalid JSON configuration. RM and try again?')
            quit()

        transi2p.address_map = transi2p.AddressMap(config['addr_map'], config['default_mappings'])

        i2pservice = service.MultiService()

        trans_port = protocol.ServerFactory()
        trans_port.protocol = transi2p.TransPort

        print(f'listening on transparent: {config["listen"]}:{config["trans_port"]}')
        internet.TCPServer(config['trans_port'], trans_port, interface=config['listen']).setServiceParent(i2pservice)

        eepns_resolver = transi2p.EepNS(config['resolvers'])
        ns = server.DNSServerFactory(clients=[eepns_resolver, client.Resolver(servers=config['resolvers'])])
        
        print(f'listening on DNS: {config["listen"]}:{config["dns_port"]}')
        internet.UDPServer(config['dns_port'], dns.DNSDatagramProtocol(controller=ns), interface=config['listen']).setServiceParent(i2pservice)

        return i2pservice

    def default_config(self):
        return {
            'addr_map': '10.18.0.0',
            'dns_port': 5354,
            'trans_port': 7679,
            'listen': '127.0.0.1',
            'resolvers': [('127.0.0.1', 5353)],
            'default_mappings': {'1.1.1.1': 'stats.i2p'}
        }

t = TransServiceMaker()