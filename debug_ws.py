import asyncio
import websockets
import json
import sys

async def hello():
    uri = "ws://localhost:8000/api/v1/projects/3c36f50b-3064-47fb-9ebe-9fc86453b98e/chat"
    async with websockets.connect(uri) as websocket:
        # Simulate DeepChat format
        msg = {"text": "Hello from debug script"}
        print(f"Sending: {msg}")
        await websocket.send(json.dumps(msg))
        
        response = await websocket.recv()
        print(f"Received: {response}")

if __name__ == "__main__":
    asyncio.run(hello())
