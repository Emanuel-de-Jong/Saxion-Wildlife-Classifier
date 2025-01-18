import asyncio
from websockets import connect

WEBSOCKET_CONNECT_MAX_RETRIES = 3

websocket = None
is_closing = False

async def main():
    global websocket, is_closing
    
    asyncio.create_task(run_client())

    print("Waiting for server connection...")
    while websocket is None:
        await asyncio.sleep(1)
    
    while True:
        await send_message(f"This is client")

        if is_closing:
            break

        await asyncio.sleep(3.5)

    print("Done!")

async def run_client():
    global websocket, is_closing

    connect_retries = 0
    while connect_retries <= WEBSOCKET_CONNECT_MAX_RETRIES:
        try:
            print("Connecting to server...")
            async with connect("ws://localhost:8765") as websocket:
                print("Connected to server")
                await asyncio.gather(receive_messages(websocket))
        except Exception as e:
            print(e)
        finally:
            connect_retries += 1
            print("Retrying connection in a few seconds...")
            await asyncio.sleep(3)
    
    is_closing = True
    print("Max retries reached and program closing started")

async def receive_messages(websocket):
    try:
        print("Listening for server messages...")
        while True:
            message = await websocket.recv()
            print(f"From server: {message}")
    except Exception as e:
        print(e)

async def send_message(message):
    global websocket
    if not websocket:
        print("Tried to send message but not connected to server")
        return False

    try:
        print(f"Sending message \"{message}\"...")
        await websocket.send(message)
        print("Message sent")
        return True
    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
