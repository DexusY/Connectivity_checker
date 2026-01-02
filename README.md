# pings — Local Device Monitor & mDNS Announcer - IoT Device Management Server

A Python-based multi-threaded server designed to manage, discover, and monitor a fleet of networked devices (referred to as "Nameplates"). This project demonstrates the implementation of low-level TCP socket communication, service discovery (mDNS), and concurrent connection handling.

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation & Usage](#installation--usage)
- [Configuration](#configuration)


---

## Overview

This application acts as a central command unit for IoT devices. It listens for incoming TCP connections, registers devices via their MAC addresses, and maintains a "heartbeat" to ensure connection stability. It also features a console-based dashboard to visualize real-time connectivity status.

The system is designed to handle up to 45 devices (configurable) simultaneously using a threaded architecture.

---

## Key Features

* **TCP Socket Server:** Handles raw socket connections, managing binary data streams and command packets.
* **Service Discovery (mDNS):** Broadcasts the server's presence using Zeroconf (`_nameplate2._tcp.local.`), allowing devices to find the server automatically.
* **Concurrency:** Utilizes `threading` and `Locks` to handle multiple client connections, heartbeats, and UI updates safely.
* **Heartbeat Mechanism:** A background thread sends periodic keep-alive signals (`0x00` byte) to connected devices.
* **Real-time Dashboard:** A console UI that refreshes dynamically to show Connected vs. Disconnected devices and their IPs.
* **Network Diagnostics:** Includes a background "pinger" that utilizes the OS ICMP ping command to verify device reachability alongside the TCP session.
* **Binary Protocol Handling:** Implements `struct` packing/unpacking for command generation (e.g., `SetErrorTimeout`) and CRC32 verification.

---

## Architecture

The project is modularized into the following components:

1.  **`devices.py` (Entry Point):**
    * Initializes the application, loads configuration, and starts the dashboard thread.
    * Manages the main loop and coordinates the display of device statuses.
2.  **`server.py`:**
    * `Server_two`: The core class responsible for binding sockets and accepting connections.
    * Parses incoming handshakes to extract MAC addresses.
    * Handles specific command protocols (e.g., setting error timeouts via binary structs).
3.  **`mDNS.py`:**
    * Uses `zeroconf` to register the service `_nameplate2._tcp.local`, enabling automatic discovery on the local network.
4.  **`heartbeat.py`:**
    * Runs a Round-Robin routine to send keep-alive packets to all active sockets, handling broken pipes and connection resets gracefully.

---

## Installation & Usage

1. Prerequisites
 - Python 3.8+: The project utilizes f-strings and modern threading features.

 - Network Access: The server requires permission to bind to a local socket and broadcast mDNS packets.

2. Installation
Clone the repository and install the required dependencies (specifically zeroconf). For Linux environments, it is recommended to create and activate a virtual environment (venv) to keep dependencies isolated:

```bash
git clone https://github.com/DexusY/Connectivity_checker.git && cd Connectivity_checker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Usage
Execute the main script, which initializes the TCP server, mDNS broadcaster, and the console dashboard:

```bash
python devices.py
```

---

## Configuration

The application is controlled via `settings.conf`. You can adjust the network bindings and the expected number of devices.

```ini
[NETWORK]
HOST_IP = 192.168.1.100  # Must match your machine's local IPv4 address (e.g., 192.168.1.x) for mDNS to function correctly.
PORT = 8080              # The TCP listening port

[DEVICES]
COUNT = 45               # Expected number of devices for the dashboard


