import json
import pika
import uuid
import random
import time
import threading
from datetime import datetime

QUEUE = "pix"
BANKS = ["BancoA", "BancoB", "BancoC", "BancoD", "BancoE"]

def run_bank(sender_bank):
    other_banks = [b for b in BANKS if b != sender_bank]

    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    print(f"[{sender_bank}] Sending messages.")

    while True:
        message = {
            "transactionId": f"TX{uuid.uuid4().hex[:6].upper()}",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "senderBank": sender_bank,
            "receiverBank": random.choice(other_banks),
            "senderAccount": str(random.randint(10000, 99999)),
            "receiverAccount": str(random.randint(10000, 99999)),
            "amount": round(random.uniform(10, 5000), 2),
        }

        body = json.dumps(message)
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE,
            body=body,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )

        print(f"[{sender_bank}] Sent: {body}")
        time.sleep(random.uniform(1, 5))


print("Iniciando todos os bancos. Para sair, pressione CTRL+C")

threads = [threading.Thread(target=run_bank, args=(bank,), daemon=True) for bank in BANKS]
for t in threads:
    t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nEncerrando produtores...")