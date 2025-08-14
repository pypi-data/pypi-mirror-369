from mdw import *

worker = None
index = 0
def mdw_start(name,doc):
    global  worker
    index = 0
    worker = Worker(DEALER,"0.0.0.0","6668")

    d = {"type":"detector_scan_start","scan_id":doc["scan_id"],"key":{"name":name},"doc":doc}
    #print("zcl: mdw_start",doc)
    worker.send_dumps(d)
    print("mdw collect start")
    pass

def mdw_event(name,doc):
    global worker
    global  index
    d = {"type":"detector_scan_collect","key":{"name":name},"doc":doc,"index":index}
    #print("zcl: ",d)
    worker.send_dumps(d)
    index = index + 1
    pass

def mdw_stop(name,doc):
    global worker
    d = {"type":"detector_scan_stop","key":{"name":name},"doc":doc}
    worker.send_dumps(d)
    data = worker.recv_string()
    if(data == "detector_scan_stop_ok"):
        print("mdw collect finished")
    worker.close()
    pass
