import logging

import pika
from .config import (
    RABBITMQ_HOST,
    RABBITMQ_USER,
    RABBITMQ_PASS,
    RABBITMQ_ENCODE_QUEUE,
)


class RabbitMQProducer:
    def __init__(self):
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=credentials,
                client_properties={"connection_name": "encode-service-be"},
            )
        )
        self.channel = self.connection.channel()

    def push_message(self, message: str):
        self.channel.queue_declare(queue=RABBITMQ_ENCODE_QUEUE, durable=False)

        self.channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_ENCODE_QUEUE,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),
        )

        self.close()

    def close(self):
        self.connection.close()


class RabbitMQConsumer:
    def __init__(self, queue):
        self.queue = queue
        self.credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=self.credentials)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)
        self.channel.basic_qos(prefetch_count=1)

    def start(self, on_message_receive_callback):
        self.channel.basic_consume(
            queue=self.queue, on_message_callback=on_message_receive_callback
        )

        logging.info(f"Waiting for messages on {self.queue}")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logging.info(f"Stopping consumer on {self.queue}")
            self.channel.stop_consuming()
        except Exception as e:
            logging.error(f"Error consuming messages: {str(e)}")

    def stop(self):
        try:
            self.channel.stop_consuming()
            self.connection.close()
        except Exception:
            logging.error("Error stopping consumer")
