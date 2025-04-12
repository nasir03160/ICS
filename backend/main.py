# main.py
import socketio
from fastapi import FastAPI

sio = socketio.AsyncServer(async_mode="asgi")
app = FastAPI()
app.mount("/", socketio.ASGIApp(sio))

@sio.event
async def connect(sid, environ):
    print(f"✅ Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")

@sio.event
async def log_data(sid, data):
    print(f"📝 Received data: {data}")

    
# uvicorn main:app --host 0.0.0.0 --port 8000
