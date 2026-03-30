# mesh_setup.py
# OBSIDIAN-8 V3 — REV D
# Initializes and configures the swarm mesh network

import subprocess
import socket
import time

# -------------------- CONFIG --------------------
NODE_NAME = "OBSIDIAN8_01"
NODE_IP = "192.168.50.101"  # static or DHCP-assigned
MESH_PORT = 5000
PING_TIMEOUT = 1.0  # seconds

# List of known swarm node IPs (example)
SWARM_NODES = [
    "192.168.50.101",
    "192.168.50.102",
    "192.168.50.103",
]

# -------------------- FUNCTIONS --------------------
def check_ip_reachable(ip: str) -> bool:
    try:
        response = subprocess.run(
            ["ping", "-c", "1", "-W", str(int(PING_TIMEOUT)), ip],
            stdout=subprocess.DEVNULL
        )
        return response.returncode == 0
    except Exception as e:
        print(f"Ping error for {ip}: {e}")
        return False

def initialize_mesh():
    reachable_nodes = []
    print(f"[Mesh Setup] Initializing mesh for {NODE_NAME}...")
    for node in SWARM_NODES:
        if check_ip_reachable(node):
            reachable_nodes.append(node)
            print(f"[Mesh Setup] Node reachable: {node}")
        else:
            print(f"[Mesh Setup] Node NOT reachable: {node}")
    print(f"[Mesh Setup] Total reachable nodes: {len(reachable_nodes)}")
    return reachable_nodes

# -------------------- MAIN --------------------
if __name__ == "__main__":
    nodes = initialize_mesh()
    print(f"[Mesh Setup] Mesh initialization complete: {nodes}")
