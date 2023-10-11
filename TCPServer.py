# def cameraopen():
import socket
import numpy as np
import cv2
    
# Definieer de host en poort om naar te luisteren
host = '127.0.0.1'  # localhost
port = 12345       # Kies een beschikbare poort

# Maak een socketobject
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind de socket aan het opgegeven host en poort
server_socket.bind((host, port))

# Begin met luisteren naar inkomende verbindingen
server_socket.listen(1)  # Hier kan maximaal 1 wachtende verbindingen zijn

cam = cv2.VideoCapture(0)

print(f"Server luistert op {host}:{port}")

# Wacht op een inkomende verbinding
client_socket, client_address = server_socket.accept()
print(f"Inkomende verbinding van {client_address}")

battery = 80

while True:
    ret, frame = cam.read()
    image_bytes = frame.tobytes()
    battery_bytes = battery.to_bytes(4, 'big')

    client_socket.send(battery_bytes)
    client_socket.send(image_bytes)

    try:
        socket.settimeout(300)
        data = client_socket.recv(8)
        print (data)
    except:
        print ("Fuck")