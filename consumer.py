import os
import json
import requests
from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv

# Đọc các biến môi trường từ file .env
load_dotenv()

# Hàm gửi record đến server Flask
def send_record_to_server(record):
    url = "http://127.0.0.1:5000/"
    try:
        response = requests.post(url, json=record)
        if response.status_code == 200:
            print("Record sent successfully!")
        else:
            print(f"Failed to send record. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending record: {e}")

# Đường dẫn lưu trữ dữ liệu
output_path = os.getenv('ROOT_PATH', '.') + "/database/"
if not os.path.exists(output_path):
    os.makedirs(output_path, exist_ok=True)

# Đường dẫn checkpoint
checkpoint_location = os.getenv('ROOT_PATH', '.') + "/database/checkpoint/"

# Cấu hình Kafka Consumer
conf = {
    'bootstrap.servers': '127.0.0.1:9092',  # Địa chỉ Kafka broker
    'group.id': 'shopee-consumer-group',    # Nhóm consumer
    'auto.offset.reset': 'earliest'         # Đọc từ đầu nếu chưa có offset
}

# Khởi tạo Kafka Consumer
consumer = Consumer(conf)
topic_name = 'ryhjlimi-shopee-2'
consumer.subscribe([topic_name])

print(f'Listening for messages on topic: {topic_name}')

try:
    while True:
        msg = consumer.poll(timeout=1.0)  # Lắng nghe tin nhắn từ Kafka
        
        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print("Reached end of partition, waiting for new messages...")
                continue
            else:
                print(f'Kafka Error: {msg.error()}')
                break

        try:
            # Giải mã dữ liệu JSON
            data = json.loads(msg.value().decode('utf-8'))
            print("Received Message:")
            print(f"CMT_ID: {data.get('cmtid', 'N/A')}")
            print(f"Rating Star: {data.get('rating_star', 'N/A')}")
            print(f"Comment: {data.get('comment', 'N/A')}")
            print("-" * 30)

            # Xác định sentiment từ rating_star
            rating_star = data.get('rating_star', 3)  # Mặc định là 3 (neutral) nếu không có
            if rating_star >= 4:
                sentiment = "positive"
            elif rating_star == 3:
                sentiment = "neutral"
            else:
                sentiment = "negative"

            # Chuẩn bị dữ liệu gửi đến Flask server
            record = {
                "cmtid": data.get("cmtid", "unknown_id"),
                "sentiment": sentiment,
                "comment": data.get("comment"),
                "begin": 0,  # Giá trị mặc định nếu không có
                "end": len(data.get("comment", "")),  # Độ dài comment
                "label": "review"  # Gán nhãn mặc định
            }

            # Gửi record về server Flask
            send_record_to_server(record)

        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw Message: {msg.value().decode('utf-8')}")  # Hiển thị nội dung lỗi để debug

except KeyboardInterrupt:
    print("Stopping consumer...")

finally:
    print("Closing consumer...")
    consumer.close()  # Đóng consumer khi thoát

