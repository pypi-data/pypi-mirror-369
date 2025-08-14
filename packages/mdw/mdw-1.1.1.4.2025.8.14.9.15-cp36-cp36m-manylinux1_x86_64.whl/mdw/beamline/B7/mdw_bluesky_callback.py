from mdw import *
from mdw.beamline.B7.mdw_config import *

try:
    from bluesky.callbacks.core import CallbackBase
except ImportError:
    CallbackBase = object
    print("not found CallbackBase")

class mdw_bluesky_callback_b7_bluesky(CallbackBase):
    def __init__(self,D):
        super().__init__()
        self.D = D

    def start(self, doc):
        print("zcl",doc)
        self.detectors = doc["detectors"]
        self.detectors_noPrefix = [name.replace('D_', '', 1) for name in self.detectors]
        #union_list = list(set(self.detectors_noPrefix) & set(["TUCSEN_1"]))
        union_list = list(set(self.detectors_noPrefix) & set(["adTUCSEN"]))
        print("zcl devices_used", union_list)
        self.names = \
            [self.D[det].hdf1.full_file_name.get() for det in [union_list[0]]]
        #self.names = \
        #   [self.D[det].hdf1.full_file_name.get() for det in ["adTUCSEN"]]
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
        from datetime import datetime
        current_time = datetime.now()
        data = self.worker1.recv_loads()
        current_time1 = datetime.now()
        print(f"zcl: recv finish {data}",current_time1-current_time)
        pass


class mdw_test(CallbackBase):
    def __init__(self,D):
        super().__init__()
        self.D = D

    def start(self, doc):
        print("zcl",doc)

    def descriptor(self, doc):
        pass

    def event(self, doc):
        print("zcl event:",doc)

    def stop(self, doc):
        print("zcl stop:",doc)
        pass
