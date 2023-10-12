import socket
import threading
import json
import sys
import signal
import os
import re
import base64

HOST = '127.0.0.1'
PORT = 6090

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

client.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")


def receive_msg():
    global status
    while True:
        data = client.recv(64).decode("utf-8")
        if data:
            msg = json.loads(data)

            message = ""
            expected_len = int(msg["payload"]["size"])
            while expected_len > 0:
                data = client.recv(1024).decode("utf-8")
                message += data
                expected_len -= 1024

            msg = json.loads(message)

            if msg["type"] == "connect_ack":
                print(f"SERVER: {msg['payload']['msg']}")
                if msg["payload"]["status"] == 1:
                    print("SERVER: \u001b[33mEnter to quit\u001b[0m")
                    status = 1
                    break
            elif msg["type"] == "notice":
                print(f"SERVER: {msg['payload']['msg']}")
            elif msg["type"] == "alert":
                print(f"SERVER: {msg['payload']['msg']}")
                print("SERVER: \u001b[33mEnter to quit\u001b[0m")
                del_folder(username)
                status = 1
                break
            elif msg["type"] == "msg":
                user = msg["payload"]["name"]
                content = msg["payload"]["content"]
                print(f"\u001b[35m{user}\u001b[0m: {content}")
            elif msg["type"] == "media":
                file = base64.b64decode(msg["payload"]["content"])
                fname = "./" + username + "/" + \
                    msg["payload"]["fname"]
                with open(fname, 'wb') as out_file:
                    out_file.write(file)
        else:
            break


receive_thread = threading.Thread(target=receive_msg)
receive_thread.daemon = True
receive_thread.start()


def del_folder(folder):
    for fname in os.listdir(folder):
        path = os.path.join(folder, fname)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            del_folder(path)
    os.rmdir(folder)


def disconnect():
    if status == 0:
        msg = {
            "type": "disconnect",
            "payload": {
                "name": username,
                "room": channel
            }
        }
        send_msg(msg)
        del_folder(username)
    client.close()


# Inform the server of the size of the incoming msg
# Add padding afterwards to fit the agreed-upon 64 bit size of this msg
def send_msg(reply):
    payload = json.dumps(reply).encode('utf-8')
    msglen = str(len(payload))
    lenstr = 21 - len(msglen)
    msg = {
        "type": "msglen",
        "payload": {
            "size": msglen + ' '*lenstr
        }
    }
    client.send(json.dumps(msg).encode('utf-8'))
    client.send(payload)


# Handling ^C and other signals
def signal_handler(sig, frame):
    disconnect()
    sys.exit(0)


# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)


status = 0
username = input("Enter a Username\n")
channel = input("Enter a channel name\n")
if not os.path.exists(username):
    os.mkdir(username)


msg = {
    "type": "connect",
    "payload": {
        "name": username,
        "room": channel
    }
}
send_msg(msg)

while status == 0:
    err = 0
    message = input()
    msg = {}

    if message.lower() == 'exit':
        break
    elif re.match("/upload *", message):
        src = username + "/" + message.split(" ", 1)[1]
        if os.path.exists(src):
            format = src.rsplit('.', 1)[-1]
            # if format in ["txt", "png", "jpg", "jpeg", "bmp", "svg"]:
            with open(src, "rb") as file:
                data = base64.b64encode(file.read()).decode("utf-8")

            msg = {
                "type": "media",
                "payload": {
                    "name": username,
                    "room": channel,
                    "filename": message.split(" ", 1)[1],
                    "content": data
                }
            }
        else:
            err = 1
            print("No such file exists!")
    elif re.match("/download *", message):
        msg = {
            "type": "filereq",
            "payload": {
                "room": channel,
                "filename": message.split(" ", 1)[1]
            }
        }
    else:
        msg = {
            "type": "msg",
            "payload": {
                "name": username,
                "room": channel,
                "content": message
            }
        }

    # Prevent sending data unnecessarily
    if status == 0 and err == 0:
        send_msg(msg)

disconnect()
