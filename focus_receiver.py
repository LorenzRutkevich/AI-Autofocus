from searcher import process, search
import socket
import threading
from PIL import Image
import io
import torch
from effnetv2_pure import effnetv2_s
import traceback
import os
import time
#from torchsummary import summary

def handle_client_connection(client_socket, address, model):
    torch.cuda.empty_cache()
    print(f"Connection from {address} has been established.")
    image_data = bytearray()  # Initialize an empty bytearray for the image data
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        image_data += data
        if b"END_OF_FILE" in image_data:
            # Remove the END_OF_FILE marker from the image data
            image_data = image_data.split(b"END_OF_FILE")[0]
            break

    print("Image data received.")
    #print(image_data)
    try:
        # Convert the received image data to a PIL Image
        image = Image.open(io.BytesIO(image_data))
        # Save the image locally
        os.makedirs("received_images", exist_ok=True)
        # save with timestamp
        image.save(f"received_images/{address[0]}_{address[1]}_{int(time.time())}.jpg")


        modified = process(image)
        print("Image modified.")
        adjustment, pred = search(model, modified, min_value=400, max_multiplier=5) 
        print(f"received adjustment (algo): {adjustment} based on class: {pred+1}")            

        adjustment_data = str(adjustment).encode("utf-8")

        # Send the modified image back to the client
        client_socket.sendall(adjustment_data)
        client_socket.sendall(b"END_OF_FILE")  # Signal end of file
        print(f"Adjustments sent back to: {address}.")
    except Exception as e:
        print(f"Error processing image: {e}")
        traceback.print_exc()
    finally:
        client_socket.close()

def start_server(host, port, model):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, address = server_socket.accept()
        thread = threading.Thread(target=handle_client_connection, args=(client_socket, address, model))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

def main():
    print(f"Initializing model... with cuda =  {torch.cuda.is_available()}.")
    model = effnetv2_s(num_classes=5)
    model.load_state_dict(torch.load("53_28.02.pth", map_location="cuda" if torch.cuda.is_available() else "cpu"))
    model.eval()
    #print(model(torch.randn(1, 3,384,384)))
    print("Model initialized.")

    host = '0.0.0.0'
    port = 23456
    start_server(host, port, model)

if __name__ == '__main__':
    main()
    """
    image  = Image.open("/home/lorenz/receiver-server/receiver_server_main/test_image.png")
    print(f"Initializing model... with cuda =  {torch.cuda.is_available()}.")
    model = effnetv2_s(num_classes=5)
    model.load_state_dict(torch.load("53_28.02.pth", map_location="cuda"))
    model.eval()
    modified = process(image)
    print("Image modified.")
    adjustment = search(model, modified) 
    print("received adjustment:", adjustment)
    """

