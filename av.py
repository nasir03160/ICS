"""
Anti-Virus Evasion Techniques Simulator - FOR EDUCATIONAL PURPOSES ONLY
This module demonstrates common evasion techniques used by malware
"""
import os
import sys
import time
import base64
import random
import string
import logging
import platform
import ctypes
import subprocess
from cryptography.fernet import Fernet

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AVEvasionSimulator:
    def __init__(self):
        self.techniques = {
            "string_obfuscation": self.demonstrate_string_obfuscation,
            "sleeping_code": self.demonstrate_sleeping_code,
            "environment_awareness": self.demonstrate_environment_awareness,
            "anti_vm_detection": self.demonstrate_anti_vm_detection,
            "code_encryption": self.demonstrate_code_encryption,
            "process_injection": self.demonstrate_process_injection
        }
    
    @staticmethod
    def random_string(length=8):
        """Generate a random string"""
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))
    
    def demonstrate_string_obfuscation(self):
        """Demonstrate string obfuscation techniques"""
        logging.info("Demonstrating string obfuscation techniques")
        
        # Original strings that might trigger AV
        sensitive_strings = [
            "keylogger",
            "password stealer",
            "C:\\Windows\\System32\\cmd.exe",
            "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        ]
        
        results = {}
        
        # Technique 1: Base64 Encoding
        results["base64_encoding"] = {}
        for s in sensitive_strings:
            encoded = base64.b64encode(s.encode()).decode()
            results["base64_encoding"][s] = encoded
            logging.info(f"Base64 encoded: {s} -> {encoded}")
        
        # Technique 2: Character Splitting
        results["char_splitting"] = {}
        for s in sensitive_strings:
            split_string = " + ".join([f"'{c}'" for c in s])
            results["char_splitting"][s] = split_string
            logging.info(f"Character split: {s} -> {split_string}")
        
        # Technique 3: XOR Encoding
        results["xor_encoding"] = {}
        for s in sensitive_strings:
            key = random.randint(1, 255)
            xored = ''.join([chr(ord(c) ^ key) for c in s])
            xored_bytes = [ord(c) for c in xored]
            results["xor_encoding"][s] = (key, xored_bytes)
            logging.info(f"XOR encoded (key={key}): {s} -> {xored_bytes}")
        
        return results
    
    def demonstrate_sleeping_code(self):
        """Demonstrate sleeping/delayed execution to evade sandbox detection"""
        logging.info("Demonstrating sleeping code techniques")
        
        results = {}
        
        # Technique 1: Simple Sleep
        start_time = time.time()
        logging.info("Starting simple sleep delay (1 second)")
        time.sleep(1)  # Short for demo purposes
        elapsed = time.time() - start_time
        results["simple_sleep"] = elapsed
        logging.info(f"Simple sleep completed in {elapsed:.2f} seconds")
        
        # Technique 2: Computationally intensive operation as delay
        start_time = time.time()
        logging.info("Starting computational delay")
        # A compute-intensive operation that takes time
        result = 0
        for i in range(10000000):  # Adjust based on machine speed
            result += i
        elapsed = time.time() - start_time
        results["computational_delay"] = elapsed
        logging.info(f"Computational delay completed in {elapsed:.2f} seconds")
        
        # Technique 3: Check timestamp differences
        logging.info("Demonstrating timestamp checking")
        current_time = time.time()
        creation_time = current_time - random.randint(100, 500)
        # Would use: os.path.getctime(__file__) in real code
        
        if current_time - creation_time > 60:  # If file is older than 60 seconds
            logging.info("[SIMULATION] File is old enough, would execute payload")
            results["timestamp_check"] = True
        else:
            logging.info("[SIMULATION] File is too new, would not execute")
            results["timestamp_check"] = False
        
        return results
    
    def demonstrate_environment_awareness(self):
        """Demonstrate environment checks to avoid analysis tools"""
        logging.info("Demonstrating environment awareness techniques")
        
        results = {}
        
        # Technique 1: Check username
        username = os.getenv("USERNAME", "").lower()
        suspicious_usernames = ["sandbox", "virus", "malware", "test", "admin", "user"]
        username_suspicious = any(u in username for u in suspicious_usernames)
        results["username_check"] = not username_suspicious
        logging.info(f"Username check: {'Suspicious' if username_suspicious else 'Looks normal'}")
        
        # Technique 2: Check hostname
        hostname = platform.node().lower()
        suspicious_hostnames = ["sandbox", "virus", "analysis", "lab", "test"]
        hostname_suspicious = any(h in hostname for h in suspicious_hostnames)
        results["hostname_check"] = not hostname_suspicious
        logging.info(f"Hostname check: {'Suspicious' if hostname_suspicious else 'Looks normal'}")
        
        # Technique 3: Check for debugging
        # Simple check if a debugger is present
        is_debugged = ctypes.windll.kernel32.IsDebuggerPresent() if os.name == 'nt' else False
        results["debugger_check"] = not is_debugged
        logging.info(f"Debugger check: {'Debugger detected' if is_debugged else 'No debugger'}")
        
        # Technique 4: Check system uptime
        try:
            if os.name == 'nt':
                # In Windows, get uptime in seconds
                uptime = ctypes.windll.kernel32.GetTickCount64() / 1000
            else:
                # On Unix-like systems, get uptime from /proc/uptime
                with open('/proc/uptime', 'r') as f:
                    uptime = float(f.readline().split()[0])
            
            # Sandboxes often have short uptimes
            suspicious_uptime = uptime < 600  # Less than 10 minutes
            results["uptime_check"] = not suspicious_uptime
            logging.info(f"System uptime: {uptime:.1f} seconds ({'Suspicious' if suspicious_uptime else 'Normal'})")
        except Exception as e:
            logging.error(f"Error checking uptime: {e}")
            results["uptime_check"] = True
        
        return results
    
    def demonstrate_anti_vm_detection(self):
        """Demonstrate techniques to detect if running in a VM"""
        logging.info("Demonstrating anti-VM detection techniques")
        
        results = {}
        
        # Technique 1: Check for common VM process names
        vm_processes = ["vmtoolsd.exe", "VBoxService.exe", "vmwareuser.exe", "VGAuthService.exe"]
        process_found = False
        
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in [p.lower() for p in vm_processes]:
                    process_found = True
                    logging.info(f"VM-related process detected: {proc.info['name']}")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        results["vm_process_check"] = process_found
        logging.info(f"VM process check: {'VM detected' if process_found else 'No VM detected'}")
        
        # Technique 2: Check for VM-related registry keys (Windows only)
        if os.name == 'nt':
            vm_registry_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\VMTools"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\VBoxService"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VMware, Inc.\VMware Tools")
            ]
            
            registry_found = False
            import winreg
            
            for hkey, key_path in vm_registry_keys:
                try:
                    key = winreg.OpenKey(hkey, key_path)
                    winreg.CloseKey(key)
                    registry_found = True
                    logging.info(f"VM-related registry key found: {key_path}")
                    break
                except FileNotFoundError:
                    pass
                except Exception as e:
                    logging.error(f"Registry check error: {e}")
            
            results["vm_registry_check"] = registry_found
            logging.info(f"VM registry check: {'VM detected' if registry_found else 'No VM detected'}")
        
        # Technique 3: Check for VM-related MAC addresses
        vm_mac_prefixes = [
            '00:05:69',  # VMware
            '00:0C:29',  # VMware
            '00:1C:14',  # VMware
            '00:50:56',  # VMware
            '08:00:27',  # VirtualBox
            '00:16:3E'   # Xen
        ]
        
        mac_found = False
        
        try:
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if getattr(addr, 'family', None) == psutil.AF_LINK:
                        mac = addr.address.lower()
                        for prefix in vm_mac_prefixes:
                            if mac.startswith(prefix.lower().replace(':', '')):
                                mac_found = True
                                logging.info(f"VM-related MAC address detected: {mac} on {iface}")
                                break
                    if mac_found:
                        break
                if mac_found:
                    break
        except Exception as e:
            logging.error(f"MAC address check error: {e}")
        
        results["vm_mac_check"] = mac_found
        logging.info(f"VM MAC check: {'VM detected' if mac_found else 'No VM detected'}")
        
        return results
    
    def demonstrate_code_encryption(self):
        """Simulate encrypting and decrypting code using Fernet"""
        logging.info("Demonstrating code encryption techniques")
        
        # Simulated payload (e.g., a print statement)
        original_code = "print('This is a simulated payload')"
        
        # Generate key and encrypt the code
        key = Fernet.generate_key()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(original_code.encode())
        logging.info(f"Encrypted payload: {encrypted}")
        
        # Decrypt and execute
        decrypted_code = cipher.decrypt(encrypted).decode()
        logging.info(f"Decrypted code: {decrypted_code}")
        
        # Execute using exec (simulate; avoid running real payloads)
        logging.info("[SIMULATION] Executing decrypted code")
        exec(decrypted_code, {}, {})  # Never use exec on untrusted input
        
        return {
            "original_code": original_code,
            "encrypted_code": encrypted,
            "decrypted_code": decrypted_code
        }

    def demonstrate_process_injection(self):
        """Simulate process injection without actually doing it"""
        logging.info("Demonstrating simulated process injection")

        try:
            # Choose a target process (simulate with notepad or dummy)
            target_process = "notepad.exe" if os.name == 'nt' else "sleep"
            logging.info(f"[SIMULATION] Target process for injection: {target_process}")

            # Simulate "injection" (e.g., logging the idea)
            logging.info(f"[SIMULATION] Opening process handle for: {target_process}")
            logging.info(f"[SIMULATION] Writing payload to target process memory")
            logging.info(f"[SIMULATION] Creating remote thread to execute payload")
            
            return {
                "target_process": target_process,
                "status": "simulated_injection_complete"
            }

        except Exception as e:
            logging.error(f"Error during process injection simulation: {e}")
            return {"error": str(e)}
    
    def demonstrate_all_techniques(self):
        """Run all evasion technique demonstrations"""
        results = {}
        
        logging.info("===== STARTING AV EVASION TECHNIQUES DEMONSTRATION =====")
        
        for technique_name, technique_func in self.techniques.items():
            logging.info(f"\n===== Demonstrating {technique_name} =====")
            try:
                technique_results = technique_func()
                results[technique_name] = technique_results
            except Exception as e:
                logging.error(f"Error demonstrating {technique_name}: {e}")
                results[technique_name] = {"error": str(e)}
        
        logging.info("\n===== AV EVASION TECHNIQUES DEMONSTRATION COMPLETE =====")
        return results

def run_av_evasion_demonstration():
    """Execute all AV evasion demonstrations"""
    simulator = AVEvasionSimulator()
    return simulator.demonstrate_all_techniques()

if __name__ == "__main__":
    # Make sure to import required modules at the top
    import psutil
    import winreg
    
    run_av_evasion_demonstration()