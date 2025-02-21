

from confluent_kafka import Consumer, KafkaError
import json

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
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw Message: {msg.value().decode('utf-8')}")  # Hiển thị nội dung lỗi để debug

except KeyboardInterrupt:
    print("Stopping consumer...")

finally:
    print("Closing consumer...")
    consumer.close()  # Đóng consumer khi thoát
