from mdw import *

worker = None
worker2 = None
index = 0
def mdw_start(name,doc):
    global  worker
    global worker2
    index = 0
    worker = Worker(DEALER,storageParser.ip,storageParser.port)
    worker2 = Worker(DEALER,"0.0.0.0","6668")

    d = {"type":"detector_scan_start","scan_id":doc["scan_id"],"key":{"name":name},"doc":doc}
    #print("zcl: mdw_start",doc)
    worker.send_dumps(d)
    worker2.send_dumps(d)
    print("mdw collect start")
    pass

def mdw_event(name,doc):
    global worker
    global worker2
    global  index
    d = {"type":"detector_scan_collect","key":{"name":name},"doc":doc,"index":index}
    #print("zcl: ",d)
    worker.send_dumps(d)
    worker2.send_dumps(d)
    index = index + 1
    pass

def mdw_stop(name,doc):
    global worker
    global worker2
    d = {"type":"detector_scan_stop","key":{"name":name},"doc":doc}
    worker.send_dumps(d)
    worker2.send_dumps(d)
    data = worker.recv_string()
    if(data == "detector_scan_stop_ok"):
        print("dw finished")
    data = worker2.recv_string()
    if (data == "detector_scan_stop_ok_gui"):
        print("gui finished")
    worker.close()
    worker2.close()
    pass
