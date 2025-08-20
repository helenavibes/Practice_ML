from flask import Flask, request, jsonify
import os, pika
from rabbitmq import send_to_rabbitmq

app = Flask(__name__)

# ... (код send_to_rabbitmq из бота) ...

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        send_to_rabbitmq(data)
        return jsonify({"status": "processing", "message": "Task queued"}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)