import time
import logging

def run_broadcast_heartbeat(server, interval=1.0):
    logging.info(f"Starting broadcast heartbeat. Interval: {interval}s")

    while True:
        with server.lock:
            devices_list = list(server.connections.items())

        for mac, conn in devices_list:
            try:
                conn.send(b'\x00')
            except (BrokenPipeError, ConnectionResetError):
                logging.warning(f"Heartbeat: Lost connection with {mac}")
            except BlockingIOError:
                pass
            except Exception as e:
                logging.error(f"Heartbeat error for {mac}: {e}")

        time.sleep(interval)