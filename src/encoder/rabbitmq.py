import logging
import threading

import pika
from encoder.config import (
    RABBITMQ_HOST,
    RABBITMQ_USER,
    RABBITMQ_PASS,
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

    def push_message(self, queue, message: str):
        self.channel.queue_declare(queue=queue, durable=False)

        self.channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),
        )

    def close(self):
        self.connection.close()


class RabbitMQConsumer:
    def __init__(self):
        self.credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        self.thread_local = threading.local()

    def _get_channel(self):
        if not hasattr(self.thread_local, "connection"):
            self.thread_local.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST, credentials=self.credentials
                )
            )
            self.thread_local.channel = self.thread_local.connection.channel()
            self.thread_local.channel.basic_qos(prefetch_count=1)
        return self.thread_local.channel

    def start(self, queue: str, on_message_receive_callback):
        self.consume_thread = threading.Thread(
            target=self._consume,
            args=(queue, on_message_receive_callback),
            name=queue,
            daemon=True,
        )

        self.consume_thread.start()

    def _consume(self, queue: str, on_message_receive_callback):
        channel = self._get_channel()
        channel.queue_declare(queue=queue)

        channel.basic_consume(
            queue=queue, on_message_callback=on_message_receive_callback
        )

        logging.info(f"Waiting for messages on {queue}")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            logging.info(f"Stopping consumer on {queue}")
            channel.stop_consuming()
        except Exception as e:
            logging.error(f"Error consuming messages: {str(e)}")
        finally:
            self._cleanup()

    def stop(self):
        channel = self._get_channel()
        try:
            channel.stop_consuming()
        finally:
            self._cleanup()

    def _cleanup(self):
        if hasattr(self.thread_local, "connection"):
            try:
                self.thread_local.connection.close()
            except Exception:
                logging.error("Error closing connection")
            del self.thread_local.connection
