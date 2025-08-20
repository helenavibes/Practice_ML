import pika
import os
import json


def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        os.getenv('RABBITMQ_USER', 'user'),
        os.getenv('RABBITMQ_PASSWORD', 'password')
    )
    return pika.BlockingConnection(pika.ConnectionParameters(
        host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
        credentials=credentials
    ))


def send_to_rabbitmq(message, queue='ml_tasks'):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )
    connection.close()