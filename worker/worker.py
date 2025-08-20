import time, os, json
from ml_model.predict import make_prediction
from rabbitmq import get_rabbitmq_connection  # Импорт из нового модуля

def validate_data(data):
    required_fields = ['user_id', 'input_data']
    return all(field in data for field in required_fields)

def process_task(task):
    print(f"[{os.getenv('WORKER_ID', 'worker')}] Processing task: {task['user_id']}")

    if not validate_data(task):
        raise ValueError("Invalid task format")

    result = make_prediction(task['input_data'])
    print(f"[{os.getenv('WORKER_ID')}] Result: {result}")
    return result

def main():
    while True:
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            channel.queue_declare(queue='ml_tasks', durable=True)

            print(f"[{os.getenv('WORKER_ID')}] Connected to RabbitMQ. Waiting for tasks...")

            def callback(ch, method, properties, body):
                try:
                    task = json.loads(body)
                    process_task(task)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"Error processing task: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='ml_tasks', on_message_callback=callback)
            channel.start_consuming()

        except Exception as e:
            print(f"Connection error: {e}, retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()