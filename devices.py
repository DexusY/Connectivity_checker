import logging
import queue
import sys
import threading
import time
import os
import subprocess
import configparser

from mDNS import start_mdns
from server import Server_two as Server
from heartbeat import run_broadcast_heartbeat

config = configparser.ConfigParser()
config.read('settings.conf')
try:
    LOCAL_IP = config['NETWORK']['HOST_IP']
    PORT = int(config['NETWORK']['PORT'])
    PASSWORD = config['SERVER']['PASSWORD'].encode('utf-8')
    logging.info(f"Loaded config: ip={LOCAL_IP}, port={PORT}")
except KeyError as e:
    logging.error(f"Configuration file error: missing key {e}")
    sys.exit(1)

ping_results = {}
ping_results_lock = threading.Lock()


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


def background_pinger(server):
    while True:
        devices = list(server.connections.items())
        if not devices:
            time.sleep(2)
            continue

        for device_key, conn in devices:
            ip = _get_ip_from_conn(conn, device_key)
            try:
                param = '-n' if os.name == 'nt' else '-c'
                timeout_param = '-w' if os.name == 'nt' else '-W'
                timeout_val = '500' if os.name == 'nt' else '1'
                args = ['ping', param, '1', timeout_param, timeout_val, ip]

                result = subprocess.run(args, capture_output=True, text=True, timeout=2)
                is_online = (result.returncode == 0)
            except Exception:
                is_online = False

            with ping_results_lock:
                ping_results[device_key] = is_online
        time.sleep(1)


def server_two_menu(server):
    pinger_thread = threading.Thread(target=background_pinger, args=(server,), daemon=True)
    pinger_thread.start()

    while True:
        connected = []
        not_connected = []

        with ping_results_lock:
            for device_key, conn in list(server.connections.items()):
                ip = _get_ip_from_conn(conn, device_key)
                is_online = ping_results.get(device_key, False)
                entry = f"{device_key} ({ip})"
                if is_online:
                    connected.append(entry)
                else:
                    not_connected.append(entry)

        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*60)
        print(f"{'CONNECTED (' + str(len(connected)) + ')':<30} | {'NOT CONNECTED (' + str(len(not_connected)) + ')':<25}")
        print("="*60)
        max_rows = max(len(connected), len(not_connected))
        for i in range(max_rows):
            left = connected[i] if i < len(connected) else ""
            right = not_connected[i] if i < len(not_connected) else ""
            print(f"{left:<30} | {right:<25}")
        print("="*60)
        time.sleep(0.5)


def start_mdns_service(started_event):
    start_mdns(LOCAL_IP, PORT)
    started_event.set()


def start_server_two(server, started_event):
    server.start_server()
    started_event.set()


def main(server):
    threading.Thread(target=server_two_menu, args=(server,), daemon=True).start()
    threading.Thread(target=run_broadcast_heartbeat, args=(server, 1.0), daemon=True).start()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    connection_queue = queue.Queue()
    server = Server(LOCAL_IP, PORT, connection_queue, PASSWORD)

    mdns_started = threading.Event()
    server_started = threading.Event()

    threading.Thread(target=start_mdns_service, args=(mdns_started,), daemon=True).start()
    threading.Thread(target=start_server_two, args=(server, server_started,), daemon=True).start()

    main(server)
