from zeroconf import ServiceInfo, Zeroconf
import socket
import time
import logging
import configparser
import os

def start_mdns(local_ip):
    zeroconf = Zeroconf()

    info = ServiceInfo(
        "_nameplate2._tcp.local.",
        "server._nameplate2._tcp.local.",
        addresses=[socket.inet_aton(local_ip)],
        port=5678,
        server="server.nameplate.local.",
        properties={"type": "pythonmockup"}
    )

    zeroconf.register_service(info)

    try:
        logging.info(f"mDNS service registered at {local_ip}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Exiting...")
    finally:
        zeroconf.unregister_service(info)
        zeroconf.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = configparser.ConfigParser()
    config_file = 'settings.conf'

    config.read(config_file)
    try:
        ip_to_use = config['NETWORK']['HOST_IP']
        logging.info(f"Starting mDNS on IP from config: {ip_to_use}")
    except KeyError:
        logging.error("Error reading IP from settings.conf.")

    start_mdns(ip_to_use)