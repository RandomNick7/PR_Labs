import os
import pika
import sys
import threading
import re

class RPCReceive(object):
    def __init__(self, group):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=group, exchange_type='fanout')

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue

        self.channel.queue_bind(exchange=group, queue=self.queue_name)

        print("Client's up!")
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)

    def callback(self, ch, method, properties, body):
        print(f"{body.decode()}")

class RPCSend(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='server_queue', exchange_type='direct')

    def call(self, message):
        self.channel.basic_publish(exchange='server_queue', routing_key='srv', body=message)


# Impose an alphanumeric limit for username & group
print("Choose a username")
username = input()
if not re.match("^[\w\-\ ]+$", username):
    print("Only alphanmeric characters, spaces, dashes and underscores allowed!")
    exit()

print("Choose a group")
group = input()
if not re.match("^[\w\-\ ]+$", username):
    print("Only alphanmeric characters, spaces, dashes and underscores allowed!")
    exit()

rpc_in = RPCReceive(group)
rpc_out = RPCSend()

def receive_msg():
    rpc_in.channel.start_consuming()

# Make receiving messages run in parallel with sending 'em
receive_thread = threading.Thread(target=receive_msg)
receive_thread.daemon = True
receive_thread.start()

def main():
    while True:
        msg = input()

        if msg == "/disconnect" or msg == "/dc":
            print("Client Closed!")
            break
        else:
            # Add username & group to message with specific delimiters to be processed by server
            msg = username+'>'+group+'>'+msg
            rpc_out.call(msg)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
