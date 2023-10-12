import socket
import threading
import json
import sys
import signal
import os
import base64

HOST = "127.0.0.1"
PORT = 6090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(25)
print(f"Server is listening on {HOST}:{PORT}")


def del_folder(folder):
    for fname in os.listdir(folder):
        path = os.path.join(folder, fname)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            del_folder(path)
    os.rmdir(folder)


# Inform the client of the size of the incoming message
# Add padding afterwards to fit the agreed-upon 64 byte size of this message
def send_msg(target, reply):
    payload = json.dumps(reply).encode('utf-8')
    msglen = str(len(payload))
    lenstr = 21 - len(msglen)
    msg = {
        "type": "msglen",
        "payload": {
            "size": msglen + ' '*lenstr
        }
    }
    target.send(json.dumps(msg).encode('utf-8'))
    target.send(payload)


def handle_client(client, addr):
    print(f"{addr[0]}:{addr[1]} connected")
    status = 0
    reply = ""

    while True:
        # Read the first message indicating the size of the 2nd
        # This 1st msg will always be 64 bytes long
        data = client.recv(64).decode("utf-8")
        if data:
            msg = json.loads(data)

            # Keep reading the 2nd msg until it reaches the expected length
            message = ""
            expected_len = int(msg["payload"]["size"])

            while expected_len > 0:
                data = client.recv(1024).decode("utf-8")
                message += data
                expected_len -= 1024

            msg = json.loads(message)

            # If someone connects, add them to user list & corresponding room
            if msg["type"] == "connect":
                name = msg["payload"]["name"]
                room = msg["payload"]["room"]

                if name in users:
                    # Username already in use!
                    reply = "Username in use!"
                    status = 1
                else:
                    users[name] = client
                    reply = f"Joined room {room}\n"
                    if room in rooms:
                        rooms[room].append(name)
                        # Notify users of new members upon join
                        if len(rooms[room]) == 1:
                            os.mkdir("./server/"+room)
                            reply += "SERVER: \u001b[33mYou're the only one here!\u001b[0m"
                        else:
                            reply += f"\u001b[32m{len(rooms[room])} users connected\u001b[0m"
                            response = {
                                "type": "notice",
                                "payload": {
                                    "msg": f"\u001b[34mUser \u001b[37m{name}\u001b[34m joined the room\u001b[0m"
                                }
                            }
                            for uname in rooms[room]:
                                if uname != name:
                                    send_msg(users[uname], response)
                    else:
                        # If new room, place user in it, make media folder
                        rooms[room] = [name]
                        if not os.path.exists("./server/"+room):
                            os.mkdir("./server/"+room)
                        reply += "SERVER: \u001b[33mYou're the only one here!\u001b[0m"

                response = {
                    "type": "connect_ack",
                    "payload": {
                        "status": status,
                        "msg": reply
                    }
                }
                send_msg(client, response)
            # If someone sends a regular message, relay it to the rest in room
            elif msg["type"] == "msg":
                name = msg["payload"]["name"]
                room = msg["payload"]["room"]

                for uname in rooms[room]:
                    if uname != name:
                        send_msg(users[uname], msg)

            # If user disconnects, notify all others in the room, remove user
            elif msg["type"] == "disconnect":
                print(f"{addr[0]}:{addr[1]} disconnected")
                name = msg["payload"]["name"]
                room = msg["payload"]["room"]

                response = {
                    "type": "notice",
                    "payload": {
                        "msg": f"\u001b[34mUser \u001b[37m{name}\u001b[34m left the room\u001b[0m"
                    }
                }
                for uname in rooms[room]:
                    if uname != name:
                        send_msg(users[uname], response)

                rooms[room].remove(name)
                del users[name]
                # If room is empty (all users left) delete the room's folder
                if len(rooms[room]) == 0:
                    del_folder("./server/"+room)
                break

            # If someone sends media, copy it byte by byte thru connection
            elif msg["type"] == "media":
                name = msg["payload"]["name"]
                room = msg["payload"]["room"]
                fname = msg["payload"]["filename"]

                file = base64.b64decode(msg["payload"]["content"])
                location = "./server/"+room + "/" + msg["payload"]["filename"]
                with open(location, 'wb') as out_file:
                    out_file.write(file)

                response = {
                    "type": "notice",
                    "payload": {
                        "msg": f"\u001b[36mUser \u001b[37m{name} \u001b[36muploaded \u001b[0m{fname}"
                    }
                }
                for uname in rooms[room]:
                    send_msg(users[uname], response)

            # If someone requests a file, send it to them if it exists
            elif msg["type"] == "filereq":
                fname = msg["payload"]["filename"]
                src = "./server/"+msg["payload"]["room"] + "/" + fname
                response = {}
                if os.path.exists(src):
                    with open(src, 'rb') as file:
                        data = base64.b64encode(file.read()).decode("utf-8")

                    response = {
                        "type": "media",
                        "payload": {
                            "fname": fname,
                            "content": data,
                            "format": fname.rsplit('.', 1)[-1]
                        }
                    }
                else:
                    response = {
                        "type": "notice",
                        "payload": {
                            "msg": "\u001b[33mRequested file does not exist!\u001b[0m"
                        }
                    }

                send_msg(client, response)
        else:
            break

    client.close()


# Handling ^C and other signals
def signal_handler(sig, frame):
    response = {
        "type": "alert",
        "payload": {
            "msg": "\u001b[31mServer's shutting down!\u001b[0m"
        }
    }

    for room in rooms.keys():
        for uname in rooms[room]:
            send_msg(users[uname], response)
            users[uname].close()

    del_folder("server")
    print("\nServer shutting down...")
    server.close()
    sys.exit(0)


# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

users = {}
rooms = {}

# Make a media folder if it doesn't exist (it shouldn't, anyway)
if not os.path.exists("./server"):
    os.mkdir("./server")

while True:
    client, addr = server.accept()
    client_thread = threading.Thread(target=handle_client, args=(client, addr))
    client_thread.start()
