from mdw import *
from mdw.beamline.BD.mdw_config import *

try:
    from bluesky.callbacks.core import CallbackBase
except ImportError:
    CallbackBase = object
    print("not found CallbackBase")

class mdw_bluesky_callback_bd_bluesky(CallbackBase):
    def __init__(self,D):
        super().__init__()
        self.D = D

    def start(self, doc):
        #print("zcl",doc)
        self.names = \
            [self.D[det].hdf1.full_file_name.get() for det in ["xsp3_1"]]
        #self.names = \
            #[D[det].hdf1.full_file_name.get() for det in ["SIM"]]
        self.element_keep = {}
        self.element_keep = doc["md"]
        scan_id = getRunId()
        self.element_keep["scan_id"] = scan_id
        self.element_keep["scan_type"] = doc["md"]["extra"]["mode"]
        doc = {**doc,**self.element_keep}
        print("zcl:name", self.names)
        print("zcl: scan_id", doc["scan_id"])
        #print("zcl: start", doc)
        print("zcl: filename",self.names)
        msg = {
            "type": "detector_flyscan_start",
            "scan_id":doc["scan_id"],
            "frame_count": doc["num_points"],
            "file_path_list": [self.names[0]],
            **doc
        }
        print("before worker:")
        self.worker = Worker(DEALER, detectorWorkerIP, detectorWorkerPort)
        self.worker.send_dumps(msg)
        msg["type"] = "detector_scan_start"
        print("**********zcl,",msg['scan_type'])
        self.worker1 = Worker(DEALER, alignWorkerIP, alignWorkerPort1)
        print("worker1:",self.worker1)
        self.worker1.send_dumps(msg)

    def descriptor(self, doc):
        pass

    def event(self, doc):
        doc["type"] = "detector_scan_collect"
        doc = {**doc,**self.element_keep}
        print("zcl event:")
        print("zcl event:",doc)
        self.worker1.send_dumps(doc)

    def stop(self, doc):
        print("zcl stop: stop begin")
        doc = {**doc,**self.element_keep}
        doc["type"] = "detector_scan_stop"
        print("zcl stop:",doc)
        self.worker1.send_dumps(doc)
        pass

