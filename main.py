import os
import asyncio
import logging
import json
import socket
import win32process
import win32gui
import psutil
import datetime
import socketio
import win32api
import time
from io import BytesIO
from PIL import ImageGrab
import cloudinary
import cloudinary.uploader
from pywinauto import Application
from pywinauto.findwindows import find_windows
import pprint 
import signal
from collections import deque
data_queue = deque(maxlen=1000)



WEBSOCKET_URL = "https://kpdzcg9r-8000.inc1.devtunnels.ms/"
CLOUDINARY_CLOUD_NAME = "dqfokopo7"
CLOUDINARY_API_KEY = "748171778948956"
CLOUDINARY_API_SECRET = "s5NSVxhbGctcLbeRh1LVd_VXCgk"

# Log environment variables to check their values 
logging.debug(f"WebSocket URL: {WEBSOCKET_URL}")
print(WEBSOCKET_URL)

# Logging setup
log_dir = os.path.join(os.getenv('APPDATA'), 'PleskService')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'my_script_log.txt'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add configuration file handling
CONFIG_PATH = os.path.join(os.getenv('APPDATA'), 'PleskService', 'config.json')




# Cloudinary configuration
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

# Asynchronous WebSocket client initialization
sio = socketio.AsyncClient()
async def connect_websocket():
    while True:
        try:
            await sio.connect(WEBSOCKET_URL)
            logging.debug("WebSocket connected successfully.")
            return True
        except Exception as e:
            logging.error(f"WebSocket connection failed: {e}")
            await asyncio.sleep(5)





def save_user_id(user_id):
    """Save user ID to a configuration file"""
    config_dir = os.path.dirname(CONFIG_PATH)
    os.makedirs(config_dir, exist_ok=True)
    
    config = {'user_id': user_id}
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)

def load_user_id():
    """Load user ID from configuration file"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            return config.get('user_id')
    except FileNotFoundError:
        return None



def get_chrome_urls():
    urls = []
    try:
        chrome_windows = find_windows(title_re=".*Chrome.*")
        if not chrome_windows:
            logging.debug("No Chrome windows found.")
            return []

        for hwnd in chrome_windows:
            try:
                app = Application(backend="uia").connect(handle=hwnd)
                win = app.window(handle=hwnd)
                url_bar = win.child_window(title="Address and search bar", control_type="Edit")
                url = url_bar.get_value()
                if url:
                    urls.append(url)
            except Exception as e:
                logging.error(f"Error retrieving Chrome URL from window (handle {hwnd}): {e}")

    except Exception as e:
        logging.error(f"Error connecting to Chrome: {e}")
    return urls

def get_firefox_urls():
    urls = []
    try:
        firefox_windows = find_windows(title_re=".*Mozilla Firefox.*")
        if not firefox_windows:
            logging.debug("No Firefox windows found.")
            return []

        for hwnd in firefox_windows:
            try:
                app = Application(backend="uia").connect(handle=hwnd)
                firefox_window = app.window(handle=hwnd)
                omnibox = firefox_window.child_window(title="Search with Google or enter address", control_type="Edit")
                url = omnibox.get_value()
                if url:
                    urls.append(url)
            except Exception as e:
                logging.error(f"Error retrieving Firefox URL from window (handle {hwnd}): {e}")

    except Exception as e:
        logging.error(f"Error connecting to Firefox: {e}")
    return urls




class WindowTracker:
    def __init__(self):
        self.current_window = None
        self.current_executable = None
        self.start_time = None
        self.url_cache = {}
        self.url_update_interval = 1
        self.min_tracking_duration = 1  # Minimum seconds to track

    def update_window(self, window_info):
        """Update window information and return data only when window actually changes"""
        window_title, executable = window_info
        current_time = datetime.datetime.now()
        
        # If this is first window or window has changed
        if self.current_window is None:
            self.current_window = window_title
            self.current_executable = executable
            self.start_time = current_time
            return None, None, None
            
        # Only process if window has changed
        if self.current_window != window_title:
            old_window = self.current_window
            old_executable = self.current_executable
            old_start = self.start_time
            
            # Update current window info
            self.current_window = window_title
            self.current_executable = executable
            self.start_time = current_time
            
            # Only return data if enough time has passed
            time_spent = (current_time - old_start).total_seconds()
            if time_spent >= self.min_tracking_duration:
                return old_window, old_executable, old_start, current_time
                
        return None, None, None, None

    async def get_browser_url(self, executable):
        """Get browser URL with caching"""
        current_time = time.time()
        
        # Check cache first
        if executable in self.url_cache:
            cache_time, url = self.url_cache[executable]
            if current_time - cache_time < self.url_update_interval:
                return url

        # Update cache
        url = None
        if executable.lower() == "chrome.exe":
            urls = get_chrome_urls()
            url = urls[0] if urls else None
        elif executable.lower() == "firefox.exe":
            urls = get_firefox_urls()
            url = urls[0] if urls else None

        self.url_cache[executable] = (current_time, url)
        return url


async def send_data_to_websocket(event_name, data):
    try:
        await sio.emit(event_name, data)
        logging.debug("Data sent successfully.")
      
        while data_queue and sio.connected:
            queued_data = data_queue.popleft()
            await sio.emit(event_name, queued_data)
    except Exception as e:
        logging.error(f"Error sending data: {str(e)}")
        data_queue.append(data)

def get_active_window_info() -> tuple[str, str]:
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            executable = process.name()
            window_title = win32gui.GetWindowText(hwnd)
            return window_title, executable
    except Exception as e:
        logging.error(f"Error getting active window info: {str(e)}")
    
   
    return None, None


 

def extract_application_name(window_title, executable):
    if executable and executable.lower() in ['chrome.exe', 'firefox.exe', 'msedge.exe', 'safari.exe', 'opera.exe', 'brave.exe']:
        # For browsers, extract the website or tab name
        if ' - ' in window_title:
            parts = window_title.split(' - ')
            application_name = parts[0]  # The first part usually contains the website/tab name
            browser_name = parts[-1]  # The last part usually contains the browser name
            return application_name, browser_name
        else:
            return window_title, executable
    else:
        # For other applications, use the last part of the window title
        if ' - ' in window_title:
            application_name = window_title.split(' - ')[-1]
            return application_name, ""
        else:
            return window_title, ""

def is_browser(executable_name):
    if executable_name is None:
        return False

    browser_executables = [
        "chrome.exe",
        "firefox.exe", 
        "msedge.exe",
        "safari.exe",
        "opera.exe",
        "brave.exe"
    ]
    return executable_name.lower() in browser_executables

def upload_screenshot_to_cloudinary():
    try:
        screenshot = ImageGrab.grab()
        buffer = BytesIO()
        screenshot.save(buffer, format='PNG')
        buffer.seek(0)

        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(buffer, resource_type="image")
        return upload_result["secure_url"]
    except Exception as e:
        logging.error(f"Error uploading screenshot to Cloudinary: {e}")
        return None


def validate_window_info(window_title, executable):
    if not window_title or len(window_title.strip()) == 0:
        return False
    if window_title.lower() in ['program manager', 'task switching']:
        return False
    return True

async def health_check():
    while True:
        try:
            if not sio.connected:
                logging.warning("WebSocket disconnected, attempting reconnection...")
                await connect_websocket()
        except Exception as e:
            logging.error(f"Health check error: {e}")
        await asyncio.sleep(60)

async def shutdown():
    logging.info("Shutting down service...")
    try:
        if sio.connected:
            await sio.disconnect()
        # Save any remaining queued data
        if data_queue:
            logging.info(f"Saving {len(data_queue)} queued items before shutdown")
            # Implement saving queue to disk if needed
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")
    finally:
        sys.exit(0)
        




async def main(userID=None):
    if userID is None:
        userID = load_user_id()
        if userID is None:
            logging.error("No user ID provided or found in config")
            return
    else:
        save_user_id(userID)

    if not await connect_websocket():
        logging.error("Failed to establish initial connection")
        return

    # Start health check in background
    health_check_task = asyncio.create_task(health_check())
    
    hostname = socket.gethostname()
    window_tracker = WindowTracker()

    try:
        while True:
            try:
                window_info = get_active_window_info()
                if not window_info or not validate_window_info(*window_info):
                    await asyncio.sleep(0.1)
                    continue
                    
                old_window, old_executable, old_start, end_time = window_tracker.update_window(window_info)

                # Only process and send data if we have valid window change information
                if old_window and old_start and end_time:
                    application_name, browser_name = extract_application_name(old_window, old_executable)
                    
                    # Skip Cloudinary upload while account is suspended
                    screenshot_url = None  # Temporarily disabled: upload_screenshot_to_cloudinary()
                    
                    current_url = None
                    if is_browser(old_executable):
                        current_url = await window_tracker.get_browser_url(old_executable)

                    time_spent = (end_time - old_start).total_seconds()
                    
                    data = {
                        "userID": userID,
                        'pc_name': hostname,
                        'active_window': old_window,
                        'executable': old_executable,
                        'website': application_name,
                        'browser': browser_name,
                        'url': current_url,
                        'start_time': old_start.strftime('%Y-%m-%d %H:%M:%S'),
                        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'time_spent': time_spent,
                        'productivity': 'Unidentified',
                        'screenshot_url': screenshot_url
                    }
                    await send_data_to_websocket('message', data)
                    pprint.pprint(data)

                await asyncio.sleep(0.1)

            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)
                continue

    except asyncio.CancelledError:
        logging.info("Main loop cancelled")
    finally:
        health_check_task.cancel()
        await shutdown()
if __name__ == "__main__":
    import sys
    
    # Setup Windows signal handling
    if os.name == 'nt':
        def handle_windows_signal(sig):
            if sig in (signal.SIGINT, signal.SIGTERM):
                asyncio.run(shutdown())
            return True
        win32api.SetConsoleCtrlHandler(handle_windows_signal, True)
    
    userID = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(main(userID))



# pyinstaller --clean --onefile --windowed --hidden-import=comtypes.stream service.py  