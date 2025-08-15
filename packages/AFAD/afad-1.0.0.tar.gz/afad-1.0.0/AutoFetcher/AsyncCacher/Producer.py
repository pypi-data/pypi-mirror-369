import pika
import json


class AsyncProducer:

    def __init__(self, host: str, queue_name: str, message: dict):
        self.host = host
        self.queue_name = queue_name
        self.message = message
        self.__connection: pika.adapters.blocking_connection.BlockingConnection = None
        self.__channel: pika.adapters.blocking_connection.BlockingChannel = None
        self.__connect()

    @staticmethod
    def create_and_publish(host: str, queue_name: str, message: dict):
        producer = AsyncProducer(host, queue_name, message)
        producer.publish_message_and_close(message)

    def __connect(self):
        try:
            self.__connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
            self.__channel = self.__connection.channel()
        except Exception as e:
            print(f"Error while connecting to RabbitMQ : {e}")
            return

    def __close_connection(self):
        self.__connection.close()

    def publish_message_and_close(self, message: dict, close: bool = True):
        try:
            self.__channel.queue_declare(queue=self.queue_name)
            message_body = json.dumps(message).encode('utf-8')
            self.__channel.basic_publish(exchange='',
                                         routing_key=self.queue_name,
                                         body=message_body,
                                         properties=pika.BasicProperties(
                                             content_type='application/json',
                                             delivery_mode=pika.DeliveryMode.Persistent
                                         ))
        except Exception as e:
            print(f"Error while publishing message to queue {self.queue_name} : {e}")
        finally:
            if close:
                self.__close_connection()
            return

    def publish_and_close(self):
        self.publish_message_and_close(self.message)

    def publish_message(self, message: dict):
        self.publish_message_and_close(message, False)

    def publish(self):
        self.publish_message_and_close(self.message, False)
