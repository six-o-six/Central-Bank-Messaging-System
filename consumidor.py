import json
import pika

QUEUE = "pix"

def callback(ch, method, properties, body):
    message = json.loads(body.decode())
    
    timestamp = message["timestamp"].replace("T", " ")
    log_line = f"[{timestamp}] {message['transactionId']} | {message['senderBank']} | {message['receiverBank']} | {message['amount']:.2f}\n"
    
    with open("audit.log", "a") as f:
        f.write(log_line)
        
    print(f"Received: {log_line.strip()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

print("Esperando por mensagens. Para sair, pressione CTRL+C")
channel.queue_declare(queue=QUEUE, durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE, on_message_callback=callback)
channel.start_consuming()