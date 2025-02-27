import os
import json
import requests
from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv


load_dotenv()


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


output_path = os.getenv('ROOT_PATH', '.') + "/database/"
if not os.path.exists(output_path):
    os.makedirs(output_path, exist_ok=True)


checkpoint_location = os.getenv('ROOT_PATH', '.') + "/database/checkpoint/"


conf = {
    'bootstrap.servers': '127.0.0.1:9092',  
    'group.id': 'shopee-consumer-group',    
    'auto.offset.reset': 'earliest'      
}


consumer = Consumer(conf)
topic_name = 'ryhjlimi-shopee-2'
consumer.subscribe([topic_name])

print(f'Listening for messages on topic: {topic_name}')

try:
    while True:
        msg = consumer.poll(timeout=1.0)  
        
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
          
            data = json.loads(msg.value().decode('utf-8'))
            print("Received Message:")
            print(f"CMT_ID: {data.get('cmtid', 'N/A')}")
            print(f"Rating Star: {data.get('rating_star', 'N/A')}")
            print(f"Comment: {data.get('comment', 'N/A')}")
            print("-" * 30)

           
            rating_star = data.get('rating_star', 3) 
            if rating_star >= 4:
                sentiment = "positive"
            elif rating_star == 3:
                sentiment = "neutral"
            else:
                sentiment = "negative"

            
            record = {
                "cmtid": data.get("cmtid", "unknown_id"),
                "sentiment": sentiment,
                "comment": data.get("comment"),
                "begin": 0, 
                "end": len(data.get("comment", "")),  
                "label": "review"  
            }

            
            send_record_to_server(record)

        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw Message: {msg.value().decode('utf-8')}") 

except KeyboardInterrupt:
    print("Stopping consumer...")

finally:
    print("Closing consumer...")
    consumer.close()  

