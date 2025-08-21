from flask import Flask, request, jsonify
import os, json
import uuid
from rabbitmq import send_to_rabbitmq
import psycopg2
from datetime import datetime

app = Flask(__name__)


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


@app.route('/predict/<model_id>', methods=['POST'])
def predict(model_id):
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    # Generate unique task ID
    task_id = str(uuid.uuid4())

    # Create message for queue
    message = {
        'task_id': task_id,
        'model_id': model_id,
        'input_data': data,
        'user_id': user_id,
        'status': 'pending'
    }

    try:
        # Save task to DB
        save_task_to_db(task_id, model_id, user_id, data, 'pending')

        # Send to RabbitMQ
        send_to_rabbitmq(message, queue='ml_tasks')

        return jsonify({
            'status': 'processing',
            'message': 'Task queued',
            'task_id': task_id
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def save_task_to_db(task_id, model_id, user_id, input_data, status):
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    cur = conn.cursor()

    cur.execute(
        'INSERT INTO prediction_tasks (id, user_id, model_name, input_data, status, created_at) VALUES (%s, %s, %s, %s, %s, %s)',
        (task_id, user_id, model_id, json.dumps(input_data), status, datetime.now())
    )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)