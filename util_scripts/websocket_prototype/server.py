import asyncio
from websockets import serve

server = None
websocket_lock = asyncio.Lock()
clients = set()

async def main():
    global server, clients

    asyncio.create_task(run_server())
    print("Waiting for client to connect...")
    while len(clients) == 0:
        await asyncio.sleep(1)

    for i in range(5):
        await send_message(f"This is server")
        await asyncio.sleep(3)
    
    print("Closing server...")
    server.close()
    await server.wait_closed()
    print("Server closed")

    print("Done!")

async def run_server():
    global server
    print("Creating server...")
    server = await serve(handle_client, "localhost", 8765)
    print("Server created")

async def handle_client(websocket):
    global clients
    print("Client connected")
    async with websocket_lock:
        clients.add(websocket)

    try:
        await receive_messages(websocket)
    except Exception as e:
        print(e)
    finally:
        async with websocket_lock:
            clients.discard(websocket)
            print("Client removed")

async def receive_messages(websocket):
    print("Listening for client messages...")
    while True:
        message = await websocket.recv()
        print(f"From client: {message}")

async def send_message(message):
    global clients

    disconnected_clients = []
    print(f"Sending message \"{message}\"...")
    async with websocket_lock:
        for websocket in clients:
            try:
                await websocket.send(message)
            except Exception as e:
                print(e)
                disconnected_clients.append(websocket)
    
    print("Message sent")
    
    async with websocket_lock:
        for websocket in disconnected_clients:
            clients.discard(websocket)
            print("Client removed")

if __name__ == "__main__":
    asyncio.run(main())
