from zeroconf import ServiceInfo, Zeroconf
import socket
import time
import logging


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

    # Register the service
    zeroconf.register_service(info)

    try:
        logging.info(f"mDNS service registered at {local_ip}:8088.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.error("Exiting...")
    finally:
        zeroconf.unregister_service(info)
        zeroconf.close()


if __name__ == "__main__":
    start_mdns('192.168.10.10')
