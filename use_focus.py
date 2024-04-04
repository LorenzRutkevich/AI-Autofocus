import os
import cv2
import socket
import json
import sys

def give_image(path: str = "path/to/microscopes/images"):
    #print("Path: ", path)
    files = [f for f in os.listdir(path) if f.endswith((".jpg", ".png", ".jpeg"))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
    #print("File:", files[0])
    return os.path.join(path, files[0])

def send_file_and_receive_adjustment(client_socket):
    # Send file
    path = give_image()
    #print("Path: ", path)
    try:
        with open(path, "rb") as file:
            client_socket.sendall(file.read())
        client_socket.sendall(b"END_OF_FILE")
        #print("File sent")
    except Exception as e:
        #print(f"Failed to send file: {e}")
        return

    # Receive adjustments
    adjustments = receive_data(client_socket)
    #print("Adjustments received: ", adjustments)
    return adjustments

def receive_data(client_socket):
    data = b""
    while True:
        part = client_socket.recv(1024)
        data += part
        if b"END_OF_FILE" in part:
            break
    return data.rstrip(b"END_OF_FILE").decode("utf-8")

def main():
    # ethernet ip address
    server_host = 'xxx.xxx.xxx.xxx'
    server_port = 23456

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_host, server_port))
            #print("Connected to server")
            adjustments = send_file_and_receive_adjustment(s)
            print(adjustments)
            return adjustments
    except Exception as e:
        #print(f"Failed to connect to server: {e}")
        return

if __name__ == "__main__":
    adjustments = main()
    if adjustments:
        print(adjustments)
    else:
        print("No adjustments received")
    