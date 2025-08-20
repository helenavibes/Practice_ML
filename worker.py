import time, os, json
from ml_model.predict import make_prediction
from rabbitmq import get_rabbitmq_connection

def validate_data(data):
    required_fields = ['user_id', 'input_data']
    return all(field in data for field in required_fields)

def process_task(task):
    worker_id = os.getenv('WORKER_ID', 'worker')
    print(f"[{worker_id}] Processing task: {task['user_id']}", flush=True)

    if not validate_data(task):
        raise ValueError("Invalid task format")

    result = make_prediction(task['input_data'])
    print(f"[{worker_id}] Result: {result}", flush=True)
    return result

def main():
    print("Worker is starting...", flush=True)  # <== Вставляется здесь, перед циклом

    while True:
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            channel.queue_declare(queue='ml_tasks', durable=True)

            worker_id = os.getenv('WORKER_ID', 'worker')
            print(f"[{worker_id}] Connected to RabbitMQ. Waiting for tasks...", flush=True)

            def callback(ch, method, properties, body):
                try:
                    task = json.loads(body)
                    process_task(task)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"Error processing task: {e}", flush=True)
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='ml_tasks', on_message_callback=callback)
            channel.start_consuming()

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Connection error: {e}, retrying in 5 seconds...", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
