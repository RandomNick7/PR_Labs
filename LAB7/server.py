import os
import time
import pika
import sys
import threading

class RPCReceive(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='server_queue', exchange_type='direct')

        result = self.channel.queue_declare(queue='srv', exclusive=True)
        self.queue_name = result.method.queue

        self.channel.queue_bind(exchange='server_queue', queue=self.queue_name)

        print("Server's up!")
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)

        self.user = ""
        self.group = ""
        self.msg = ""

    def callback(self, ch, method, properties, body):
        payload = body.decode().split('>',2)
        self.user = payload[0]
        self.group = payload[1]
        self.msg = payload[2]

class RPCSend(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

    def call(self, user, group, message):
        payload = user+':'+message
        self.channel.exchange_declare(exchange=group, exchange_type='fanout')
        self.channel.basic_publish(exchange=group, routing_key='', body=payload)

rpc_in = RPCReceive()
rpc_out = RPCSend()

def receive_msg():
    rpc_in.channel.start_consuming()

# Make receiving messages run in parallel with sending 'em
receive_thread = threading.Thread(target=receive_msg)
receive_thread.daemon = True
receive_thread.start()

def main():
    while True:
        # If there is a nonempty message to send, do so
        if rpc_in.msg != "":
            rpc_out.call(rpc_in.user, rpc_in.group, rpc_in.msg)
            rpc_in.msg = ""
        # Cap at 40 updates/s to prevent the PC from turning into a lawnmower
        time.sleep(0.025)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
