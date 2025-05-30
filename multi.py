import socket
import ssl
import threading

HOST = '0.0.0.0'
PORT = 4443

def handle_client(connstream, addr):
    print(f"Connection from {addr}")
    try:
        while True:
            data = connstream.recv(1024)
            if not data:
                break
            print(f"Received from {addr}: {data.decode().strip()}")
            connstream.sendall(data)  # Echo back
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()
        print(f"Disconnected {addr}")

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile='config/server.pem', keyfile='config/server.key')

bindsocket = socket.socket()
bindsocket.bind((HOST, PORT))
bindsocket.listen(5)
print(f"TLS server listening on {HOST}:{PORT}")

while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = context.wrap_socket(newsocket, server_side=True)
    threading.Thread(target=handle_client, args=(connstream, fromaddr)).start()
