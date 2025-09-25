# pings — Local Device Monitor & mDNS Announcer

This toolkit spins up everything you need to discover, accept, and monitor a fleet of networked devices on a local subnet. It combines an mDNS broadcast, a TCP server that registers devices by MAC address, and a dashboard loop that continuously pings each device to verify connectivity.

---

## Discovery & intake flow

When you run the scripts, the system launches three coordinated components:

- `mDNS.py` registers the service `_nameplate2._tcp.local.` so devices can auto-discover the TCP endpoint.
- `server.py` listens for inbound device connections, authenticates the first contact, and stores sockets keyed by MAC address.
- `devices.py` orchestrates the background threads, keeps track of the expected device count, and renders a live ping dashboard once everyone is online.

The modules rely almost exclusively on the Python standard library (threads, sockets, subprocess) for portability.

---

## Setup (Recommended)

Create an isolated environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If you already have Zeroconf installed globally, you can skip the final step.

---

# pings monitor

A Python trio that advertises a TCP intake over mDNS, records connected display devices, and watches their reachability.

---

## Features

- Copy-free deployment: everything runs from three small scripts.
- mDNS announcer so devices discover the server automatically.
- Threaded TCP listener that stores live sockets keyed by MAC.
- Ping-based health dashboard that splits connected vs unreachable devices.
- Optional `DisplayUpdate` broadcast worker for synchronized screen refreshes.
- Easy configuration via top-level constants (`LOCAL_IP`, `dev_num`).

---

## Prerequisites

- Python 3.10+
- [`zeroconf`](https://pypi.org/project/zeroconf/) - To implement mDNS protocol
- A reachable LAN interface matching the `LOCAL_IP` value

---

## Configuration

Before launching, open `devices.py` and adjust:

- `LOCAL_IP` — IP address the server should bind and advertise.
- `dev_num` — Number of devices expected; the monitoring loop waits until this many have connected before starting the dashboard.
- Optional: implement `Server.DisplayUpdate(mac, status)` if you plan to use the broadcast helper.

No other configuration files are required; everything else is discovered at runtime.

---

## Usage

Run the orchestrator:

```bash
python devices.py
```

What happens next:

1. `mDNS.py` registers the service and waits indefinitely.
2. `server.py` starts listening on `LOCAL_IP:8088` and logs each connection with its MAC.
3. Once `dev_num` devices are registered, the ping loop prints a split table of reachable vs unreachable hosts, refreshing every second.

Stop the stack with `Ctrl+C`; all threads are daemonized so they exit together.

---

## Examples

Sample dashboard once all devices are online:

```
============================================================
CONNECTED (44)                 | NOT CONNECTED (1)
============================================================
AA:BB:CC:DD:EE:01 (192.168...) | AA:BB:CC:DD:EE:2F (192....)
...
============================================================
```

- Connected devices respond to `ping -c 1 -W 1000` within two seconds.
- Unreachable devices either time out or return a non-zero exit code and move to the right column.
- The terminal clears between refreshes for a compact view.

---

## Troubleshooting

- **mDNS service never registers** – Confirm `zeroconf` is installed and that `LOCAL_IP` refers to an active interface.
- **Devices connect but remain “NOT CONNECTED”** – ICMP may be blocked; swap the ping call for a protocol your devices allow.
- **Display update errors** – Implement `DisplayUpdate` on the `Server` class or remove the helper thread if not needed.
- **Connections drop unexpectedly** – Check for network instability or adjust the monitoring frequency if the devices are resource constrained.

Increase verbosity by raising the logging level in `devices.py`:

```python
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
```

---


