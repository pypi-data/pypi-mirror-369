import zmq
import json
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://0.0.0.0:5557")

while True:
    data = socket.recv().decode('utf-8')
    print(data)