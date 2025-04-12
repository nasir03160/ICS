"""
Malware Simulation Framework - FOR EDUCATIONAL PURPOSES ONLY

This software is designed to simulate malware behavior in a controlled environment
for educational and research purposes. DO NOT use this in a production environment
or against systems without explicit permission.


Modes:
- Worm Simulation
Simulate a worm channel.
"""


# import scapy.all as scapy
# import socket
# import threading
# import os

# # Function to perform ARP scan and detect devices on the network
# def scan_network(ip_range):
#     # Create ARP request to get MAC address and IP of devices in the network
#     arp_request = scapy.ARP(pdst=ip_range)
#     broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
#     # Combine Ethernet frame and ARP request
#     arp_request_broadcast = broadcast/arp_request
    
#     # Send the request and capture the response
#     devices = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
#     # Store the list of devices with IP and MAC addresses
#     device_list = []
#     for device in devices:
#         device_info = {"ip": device[1].psrc, "mac": device[1].hwsrc}
#         device_list.append(device_info)
        
#     return device_list

# # Function to print the details of devices on the network
# def display_devices(devices):
#     print("Devices connected to the network:")
#     print("IP Address\t\tMAC Address")
#     print("-----------------------------------------")
#     for device in devices:
#         print(f"{device['ip']}\t\t{device['mac']}")

# # Function to send a file to a device (currently commented)
# def send_file_to_device(ip, filename):
#     # Placeholder for file sending logic, which could be implemented
#     # by sending the file over a socket connection
#     """
#     try:
#         # Create a socket connection to the device
#         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         s.connect((ip, 12345))  # Connect to the device (example port 12345)

#         # Read the file and send its content
#         with open(filename, 'rb') as f:
#             file_data = f.read()
#             s.sendall(file_data)
        
#         print(f"File sent to {ip}")
#         s.close()
#     except Exception as e:
#         print(f"Failed to send file to {ip}: {e}")
#     """
#     pass

# # Main function to initiate network scan and display connected devices
# def main():
#     ip_range = "192.168.18.66/24"  # Modify the IP range to match your network
#     print("Scanning network for connected devices...")
#     devices = scan_network(ip_range)
#     display_devices(devices)
    
#     # Example of sending a file (commented out)
#     # for device in devices:
#     #     send_file_to_device(device['ip'], "example_file.txt")

# if __name__ == "__main__":
#     main()





"""
check mac address vendor
https://api.macvendors.com/{mac}
"""



import requests

def get_mac_vendor(mac):
    url = f"https://api.macvendors.com/{mac}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Unknown vendor"

print(get_mac_vendor("c6:0c:7b:7c:d3:94"))  # replace with real MAC
