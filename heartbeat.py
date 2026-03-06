import time
import logging

def run_round_robin_heartbeat(server, interval=0.1):
    logging.info(f"Starting Round Robin data transmission. Interval: {interval}s")
    
    while True:
        with server.lock:
            devices_list = list(server.connections.items())

        if not devices_list:
            time.sleep(5)
            continue

        for mac, conn in devices_list:
            try:
                conn.send(b'\x00')
                
                # logging.debug(f"Heartbeat sent to {mac}") #uncomment for detailed logs

            except (BrokenPipeError, ConnectionResetError):
                logging.warning(f"Heartbeat: Lost connection with {mac}")
            except BlockingIOError:
                pass 
            except Exception as e:
                logging.error(f"Heartbeat error for {mac}: {e}")

            time.sleep(interval)