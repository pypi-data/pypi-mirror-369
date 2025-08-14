import zmq
import json
from json import JSONEncoder
import numpy

"""
#socket1 = context.socket(zmq.PULL)
#socket1.bind("tcp://0.0.0.0:5557")
class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

def collect_start(m):
    bytes = json.dumps(m,cls=NumpyArrayEncoder).encode('utf-8')
    global context
    global socket
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://besh03.ihep.ac.cn:9955")
    if (socket is not None):
        socket.send(bytes)
    else:
        print("online processing connect is failed")
    #data = socket1.recv().decode('utf-8')
    #print(data)
    pass

def collect_collect(m):
    global context
    global socket
    if socket is not None:
        bytes = json.dumps(m,cls=NumpyArrayEncoder).encode('utf-8')
        socket.send(bytes)
    pass

def collect_stop(m):
    global context
    global socket
    if socket is not None:
        bytes = json.dumps(m,cls=NumpyArrayEncoder).encode('utf-8')
        socket.send(bytes)
    pass

#collect_start({"type":"123"})
"""