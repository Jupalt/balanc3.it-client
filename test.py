import asyncio
import websockets

async def test_websocket():
    uri = "ws://127.0.0.1:8000/ws"  # WebSocket-URL
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server")
        await websocket.send("Hello Server!")  # Sende eine Nachricht
        response = await websocket.recv()  # Empfange eine Nachricht
        print(f"Received from server: {response}")

# Starte das Testen
asyncio.run(test_websocket())