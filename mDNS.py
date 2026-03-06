from zeroconf import ServiceInfo, Zeroconf
import socket
import time
import logging
import configparser
import sys


def start_mdns(local_ip, port):
    zeroconf = Zeroconf()

    info = ServiceInfo(
        "_nameplate2._tcp.local.",
        "server._nameplate2._tcp.local.",
        addresses=[socket.inet_aton(local_ip)],
        port=port,
        server="server.nameplate.local.",
        properties={"type": "pythonmockup"}
    )

    zeroconf.register_service(info)

    try:
        logging.info(f"mDNS service registered at {local_ip}:{port}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down mDNS service...")
    finally:
        zeroconf.unregister_service(info)
        zeroconf.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    config = configparser.ConfigParser()
    config.read('settings.conf')
    try:
        ip_to_use = config['NETWORK']['HOST_IP']
        port_to_use = int(config['NETWORK']['PORT'])
        logging.info(f"Starting mDNS on IP from config: {ip_to_use}")
    except KeyError as e:
        logging.error(f"Error reading settings.conf: missing key {e}")
        sys.exit(1)

    start_mdns(ip_to_use, port_to_use)
