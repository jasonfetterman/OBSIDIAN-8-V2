# swarm_comms.py
# OBSIDIAN-8 V3 — REV D
# Handles mesh network communications for swarm coordination

import socket
import json
import threading
import time

class SwarmComms:
    def __init__(self, node_id, multicast_group="224.1.1.1", port=5007):
        self.node_id = node_id
        self.group = multicast_group
        self.port = port

        # Setup UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))

        # Join multicast group
        mreq = socket.inet_aton(self.group) + socket.inet_aton('0.0.0.0')
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.received_messages = []
        self.running = True

        # Start listener thread
        self.listener_thread = threading.Thread(target=self._listen)
        self.listener_thread.start()

    def _listen(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = json.loads(data.decode())
                message['from'] = addr[0]
                self.received_messages.append(message)
            except Exception as e:
                print(f"[SwarmComms] Error receiving: {e}")

    def send(self, payload):
        """
        Send a JSON payload to the multicast group
        """
        try:
            message = json.dumps(payload).encode()
            self.sock.sendto(message, (self.group, self.port))
        except Exception as e:
            print(f"[SwarmComms] Error sending: {e}")

    def get_messages(self):
        """
        Retrieve and clear received messages
        """
        msgs = self.received_messages.copy()
        self.received_messages.clear()
        return msgs

    def shutdown(self):
        self.running = False
        self.listener_thread.join()
        self.sock.close()


# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    swarm = SwarmComms(node_id="OB8-Node1")
    try:
        while True:
            # Example: broadcast heartbeat
            swarm.send({"type": "heartbeat", "node_id": "OB8-Node1", "timestamp": time.time()})
            time.sleep(1)
            messages = swarm.get_messages()
            for msg in messages:
                print("Received:", msg)
    finally:
        swarm.shutdown()
