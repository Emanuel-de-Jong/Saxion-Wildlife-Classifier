import paho.mqtt.client as mqtt
import json

def preprocessing(json_message):
    print("preprocessing " + json_message.get('data'))

def load_model(json_message):
    print("loading model " + json_message.get('data'))

def prediction(json_message):
    print("predicting " + json_message.get('data'))

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[receiver] Connected with code {reason_code}")
    client.subscribe("efficientdet_topic")

def on_message(client, userdata, message):
    json_message = json.loads(message.payload.decode())
    message = json_message.get('type')

    match message:
        case "preprocessing":
            preprocessing(json_message)
        case "load_model":
            load_model(json_message)
        case "prediction":
            prediction(json_message)
        case "disconnect":
            client.disconnect()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker", 1883, 60)
client.loop_forever()
