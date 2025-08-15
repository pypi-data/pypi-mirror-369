from typing import Callable
import pika
import json


class AsyncConsumer:

    def __init__(self, host: str, queue_name: str, callback: Callable[[dict], None]):
        self.host = host
        self.queue_name = queue_name
        self.callback = callback
        self.__connection: pika.adapters.blocking_connection.BlockingConnection = None
        self.__channel: pika.adapters.blocking_connection.BlockingChannel = None
        self.__connect()

    def __connect(self):
        try:
            self.__connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
            self.__channel = self.__connection.channel()
        except Exception as e:
            print(f"Error while connecting to RabbitMQ : {e}")
            return

    def __callback(self, channel, method, properties, body):
        try:
            print(f"Consuming message : {body.decode('utf-8')}")
            self.callback(json.loads(body.decode('utf-8')))
        except Exception as e:
            print(f"Error while consuming message : {body.decode('utf-8')} error : {e}")
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        try:
            self.__channel.basic_consume(queue=self.queue_name, on_message_callback=self.__callback, auto_ack=False)
            print('[*] Waiting for messages. To exit press CTRL+C')
            self.__channel.start_consuming()
        except KeyboardInterrupt as e:
            print("Exiting consumer...")
            self.__channel.stop_consuming()
            self.__connection.close()
        except Exception as e:
            print(f"Error occurred while consuming messages : {e}")
            self.__connection.close()

