import logging
import queue
import threading
import time
import os
from mDNS import start_mdns
from server import Server
import subprocess

LOCAL_IP = '192.168.130.209'
dev_num = 45    

def _get_ip_from_conn(conn, key=None):
    try:
        if isinstance(conn, tuple) and len(conn) >= 1 and isinstance(conn[0], str):
            return conn[0]

        if hasattr(conn, "getpeername"):
            try:
                peer = conn.getpeername()
                if isinstance(peer, tuple) and len(peer) >= 1:
                    return peer[0]
            except Exception:
                pass
       
        if isinstance(conn, dict):
            for k in ("ip", "address", "host"):
                if k in conn:
                    return conn[k]
        for attr in ("ip", "address", "host", "remote_addr", "remote_address"):
            if hasattr(conn, attr):
                return getattr(conn, attr)
    except Exception:
        pass

    if isinstance(key, str) and any(c.isdigit() for c in key):
        return key
    return "unknown"

def send_display_updates_after_delay(server, per_device_pause=0.05):
    def _worker():
        logging.info(f"Sending display updates to all {dev_num} devices...")
        for mac in list(server.connections.keys()):
            try:
                if hasattr(server, "DisplayUpdate"):
                    server.DisplayUpdate(mac, 0)
                logging.info(f"Display update sent to {mac}")
            except Exception:
                logging.exception("Failed to send display update to %s", mac)
            time.sleep(per_device_pause)
    threading.Thread(target=_worker, daemon=True).start()

def server_two_menu(server):
        while True:
            devices = list(server.connections.keys())
            if not devices:
                logging.info("No devices connected")
                time.sleep(1)
                continue
            if len(devices) == dev_num:
                logging.info(f"Exactly {dev_num} devices connected")

                while len(server.connections) == dev_num:
                    connected = []
                    not_connected = []
                    
                    for device_key, conn in list(server.connections.items()):
                        ip = _get_ip_from_conn(conn, device_key)
                        
                        try:
                            result = subprocess.run(
                            ['ping', '-c', '1', '-W', '1000', ip], 
                            capture_output=True, 
                            text=True, 
                            timeout=2
                            )
                            if result.returncode == 0:
                                connected.append(f"{device_key} ({ip})")
                            else:
                                not_connected.append(f"{device_key} ({ip})")
                        except subprocess.TimeoutExpired:
                            not_connected.append(f"{device_key} ({ip})")
                        except Exception as e:
                            not_connected.append(f"{device_key} ({ip})")
                    
                    print("\n" + "="*60)
                    print(f"{'CONNECTED (' + str(len(connected)) + ')':<30} | {'NOT CONNECTED (' + str(len(not_connected)) + ')':<25}")
                    print("="*60)
                    
                    max_rows = max(len(connected), len(not_connected))
                    for i in range(max_rows):
                        left = connected[i] if i < len(connected) else ""
                        right = not_connected[i] if i < len(not_connected) else ""
                        print(f"{left:<30} | {right:<25}")
                    
                    print("="*60)
                    
                    time.sleep(1)
                    os.system('clear' if os.name == 'posix' else 'cls')
                logging.info("Device count changed, exiting ping loop")
                break
   

def main(server):
    threading.Thread(target=server_two_menu, args=(server,), daemon=True).start()

    while True:
        time.sleep(1)
    
def start_mdns_service(started_event):
    start_mdns(LOCAL_IP)
    started_event.set()


def start_server_one(server, started_event):
    server.start_server()
    started_event.set()


def start_server_two(server, started_event):
    server.start_server()
    started_event.set()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    connection_queue = queue.Queue()
    server = Server(LOCAL_IP, 8088, connection_queue)

    mdns_started = threading.Event()
    server_started = threading.Event()

    threading.Thread(target=start_mdns_service, args=(mdns_started,), daemon=True).start()
    threading.Thread(target=start_server_two, args=(server, server_started,), daemon=True).start()

    main(server)        
        
 
        
