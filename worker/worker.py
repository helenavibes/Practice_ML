import time, os, json
import traceback
from ml_model.predict import make_prediction
from rabbitmq import get_rabbitmq_connection
import psycopg2
from datetime import datetime


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )


def update_task_in_db(task_id, status, result=None):
    conn = get_db_connection()
    cur = conn.cursor()

    if result:
        # Обновляем статус задачи
        cur.execute(
            "UPDATE prediction_tasks SET status = %s, completed_at = NOW() WHERE id = %s",
            (status, task_id)
        )

        # Сохраняем результат предсказания
        cur.execute(
            """
            INSERT INTO prediction_results 
            (task_id, predictions, cost, created_at) 
            VALUES (%s, %s, %s, %s)
            """,
            (task_id, json.dumps(result), 10.0, datetime.now())
        )

    else:
        cur.execute(
            "UPDATE prediction_tasks SET status = %s WHERE id = %s",
            (status, task_id)
        )

    conn.commit()
    cur.close()
    conn.close()


def validate_data(data):
    required_fields = ['task_id', 'user_id', 'input_data']
    return all(field in data for field in required_fields)


def process_task(task):
    worker_id = os.getenv('WORKER_ID', 'worker')
    print(f"[{worker_id}] Processing task: {task['task_id']}", flush=True)

    if not validate_data(task):
        raise ValueError("Invalid task format")

    try:
        # Обновляем статус на "processing"
        update_task_in_db(task['task_id'], 'processing')

        # Выполняем предсказание
        result = make_prediction(task['input_data'])

        # Сохраняем результат
        update_task_in_db(task['task_id'], 'completed', result)

        print(f"[{worker_id}] Result: {result}", flush=True)
        return result

    except Exception as e:
        print(f"[{worker_id}] Error processing task {task['task_id']}: {e}", flush=True)
        update_task_in_db(task['task_id'], 'failed')
        raise


def main():
    print("Worker is starting...", flush=True)

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
                    traceback.print_exc()
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='ml_tasks', on_message_callback=callback)
            channel.start_consuming()

        except Exception as e:
            print(f"Connection error: {e}, retrying in 5 seconds...", flush=True)
            traceback.print_exc()
            time.sleep(5)


if __name__ == "__main__":
    main()