# mesh_heartbeat.py
# OBSIDIAN-8 V3 — REV D
# Periodically checks the health of swarm nodes

import socket
import time

# -------------------- CONFIG --------------------
HEARTBEAT_INTERVAL = 5.0  # seconds
MESH_PORT = 5000
SWARM_NODES = [
    "192.168.50.101",
    "192.168.50.102",
    "192.168.50.103",
]

# -------------------- FUNCTIONS --------------------
def send_heartbeat(node_ip: str):
    """Send UDP heartbeat packet to node"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.0)
        message = b"HEARTBEAT"
        sock.sendto(message, (node_ip, MESH_PORT))
        sock.close()
        return True
    except Exception as e:
        print(f"[Heartbeat] Failed to send to {node_ip}: {e}")
        return False

# -------------------- MAIN --------------------
if __name__ == "__main__":
    while True:
        for node in SWARM_NODES:
            if send_heartbeat(node):
                print(f"[Heartbeat] Node alive: {node}")
            else:
                print(f"[Heartbeat] Node offline: {node}")
        time.sleep(HEARTBEAT_INTERVAL)
