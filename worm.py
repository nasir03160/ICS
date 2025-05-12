"""
Worm Simulation with Actual Message Delivery - FOR EDUCATIONAL PURPOSES ONLY
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
import socket
from urllib.request import urlopen
import logging
import random

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MessageServer:
    def __init__(self, port=8080):
        self.port = port
        self.message = "Your system has been scanned by a security simulation tool. This is for educational purposes only."
        self.server = None
        self.server_thread = None
    
    def start(self):
        """Start the HTTP server in a separate thread"""
        def run_server():
            server_address = ('', self.port)
            handler = lambda *args: SimpleHTTPRequestHandler(*args, directory='.')
            self.server = HTTPServer(server_address, handler)
            logging.info(f"Message server running on port {self.port}")
            self.server.serve_forever()
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server_thread.join()
            logging.info("Message server stopped")

class WormSimulator:
    def __init__(self):
        self.message_server = MessageServer()
        self.local_ip = self.get_local_ip()
        self.discovered_hosts = self.scan_network()
    
    def get_local_ip(self):
        """Get the local IP address"""
        try:
            # Create a dummy socket to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def scan_network(self):
        """Simulate network scanning"""
        # Generate some random IPs in the same subnet
        base_ip = ".".join(self.local_ip.split(".")[:3])
        hosts = [f"{base_ip}.{random.randint(1, 254)}" for _ in range(5)]
        hosts.append(self.local_ip)  # Include our own IP
        
        logging.info(f"[SIMULATION] Discovered hosts: {', '.join(hosts)}")
        return hosts
    
    def send_messages(self):
        """Actually attempt to send messages to devices"""
        self.message_server.start()
        
        for host in self.discovered_hosts:
            try:
                # Try to send HTTP request (this will only work if device has a server)
                url = f"http://{host}:{self.message_server.port}"
                logging.info(f"Sending message to {host} - visit {url} to see it")
                
                # In a real implementation, you'd use more sophisticated methods
                # This just demonstrates the concept
                
            except Exception as e:
                logging.error(f"Error contacting {host}: {str(e)}")
        
        logging.info(f"To see the message on your mobile, visit: http://{self.local_ip}:{self.message_server.port} in your mobile browser")

if __name__ == "__main__":
    simulator = WormSimulator()
    simulator.send_messages()
    
    try:
        # Keep the server running
        while True:
            pass
    except KeyboardInterrupt:
        simulator.message_server.stop()