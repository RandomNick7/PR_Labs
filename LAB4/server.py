import socket
import threading
import re
import sys
import signal

HOST = '127.0.0.1'
ADDR = 6090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST,ADDR))
server.listen(5)
print(f"Server is listening on {HOST}:{ADDR}")

def handle_request(client):
    while True:
        request = conn.recv(2048).decode('utf-8')
        print(f"Received Request:\n{request}")
        if(len(request)>0):
            path = request.strip().split()[1]

            # Initialize the response content and status code
            response_content = ''
            status_code = 200

            # Define a simple routing mechanism
            if path == '/':
                response_content = open('pages/index.html','r').read()
            elif path == '/list_products':
                response_content = open('pages/list_products.js','r').read()
            elif path == '/products/item':
                response_content = open('pages/item.js','r').read()
            elif path in ['/about','/contacts','/products']:
                response_content = open('pages/'+path[1:]+'.html', 'r').read()
            elif re.match('/products/[0-9]+', path):
                response_content = open('pages/item.html','r').read()
            elif path == '/products.json':
                response_content = open('pages/product_list.json','r').read()
            else:
                response_content = '<p>404 Page Not Found. You were not supposed to be here.</p>'
                status_code = 404

            # Prepare the HTTP response
            response = f'HTTP/1.1 {status_code} OK\n\n{response_content}'

            conn.send(response.encode('utf-8'))

            # Browser does not need more than 1 response
            if("User-Agent:" in request):
                break;
        else:
            break;

    conn.close()
    print(f"{addr[0]}:{addr[1]} disconnected.")

# Handling ^C and other signals
def signal_handler(sig, frame):
    print("\nServer shutting down...")
    server.close()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

while True:
    conn, addr = server.accept()
    print(f"{addr[0]}:{addr[1]} connected")

    client_handler = threading.Thread(target=handle_request, args=(conn,))
    client_handler.start()
