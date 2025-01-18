import time
import threading
from kombu import Connection, Exchange, Queue

NAME = "model"
RECEIVE_FROM = "pipeline"
RABBIT_URL = "amqp://user:password@rabbitmq:5672/"

task_id = 1

def main():
    connection = Connection(RABBIT_URL)
    exchange = Exchange("tasks", type="direct", durable=True)

    receive_queue = Queue(f"task_queue_{RECEIVE_FROM}", exchange, routing_key=f"task_key_{RECEIVE_FROM}", durable=True)
    receive_thread = threading.Thread(target=receive_messages, args=(connection, receive_queue), daemon=True)
    receive_thread.start()

    send_queue = Queue(f"task_queue_{NAME}", exchange, routing_key=f"task_key_{NAME}", durable=True)
    producer = connection.Producer()
    while True:
        send_message("Some data", producer, exchange, send_queue)
        # time.sleep(1)

def receive_messages(connection, queue):
    consumer = connection.Consumer(queue, callbacks=[process_message], accept=["json"])
    while True:
        try:
            connection.drain_events(timeout=0.4)
        except TimeoutError:
            pass
        except Exception as e:
            print(f"Error receiving messages: {e}")

def process_message(body, message):
    print(f"Received: {body}")
    message.ack()

def send_message(message, producer, exchange, send_queue):
    global task_id

    message = {"task_id": task_id, "data": message}
    producer.publish(
        message,
        exchange=exchange,
        routing_key=f"task_key_{NAME}",
        declare=[send_queue],
        serializer="json",
    )
    print(f"Sent: {message}")

    task_id += 1

if __name__ == "__main__":
    main()