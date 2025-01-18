import asyncio
import json
import paho.mqtt.client as mqtt

max_messages = 5

def message(type, data=None):
    json_object = {
        "type": type,
        "data": data
    }
    return json.dumps(json_object)


async def disconnect_model(client, model_name):
    client.publish(f"{model_name}_topic", message("disconnect", "loading"))

async def prediction(client, model_name):
    client.publish(f"{model_name}_topic", message("prediction", "loading"))

async def preprocess_model(client, model_name):
    client.publish(f"{model_name}_topic", message("preprocessing", "loading"))

async def load_model(client, model_name):
    client.publish(f"{model_name}_topic", message("load_model", "loading"))

def on_message(client, userdata, message):
    json_message = json.loads(message.payload.decode())
    print(f"[receiver] Received message on main_topic: {json_message.get('data')}")

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[sender] Connected with code {reason_code}")
    client.subscribe("main_topic")

async def send_messages(client):
    for i in range(max_messages):
        print(f"[sender] Sending message {i+1}")
        await prediction(client, "yolo")
        await asyncio.sleep(3)
    await disconnect_model(client, "yolo")
    await disconnect_model(client, "detectron")
    await disconnect_model(client, "efficientdet")

async def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("broker", 1883, 60)
    client.loop_start()

    try:
        await send_messages(client)
    finally:
        client.loop_stop()

asyncio.run(main())