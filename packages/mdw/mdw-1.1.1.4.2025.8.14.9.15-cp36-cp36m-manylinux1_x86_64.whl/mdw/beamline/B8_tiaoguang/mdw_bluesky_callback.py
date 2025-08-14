from mdw import *
from mdw.beamline.B8_tiaoguang.mdw_config import *

try:
    from bluesky.callbacks.core import CallbackBase
except ImportError:
    CallbackBase = object
    print("not found CallbackBase")

class mdw_bluesky_callback_b8_tiaoguang_bluesky(CallbackBase):
    def __init__(self,D):
        super().__init__()
        self.D = D

    def start(self, doc):
        print("zcl",doc)
        self.detectors = doc["detectors"]
        self.detectors_noPrefix = [name.replace('D_', '', 1) for name in self.detectors]
        print("zcl devices_used",self.detectors_noPrefix)
        #self.names = \
        #    [self.D[det].hdf1.full_file_name.get() for det in ["WhiteFS"]]
        self.element_keep = {}
        self.element_keep = doc["md"]
        scan_id = getRunId()
        print("zcl",self.element_keep)
        self.element_keep["scan_id"] = scan_id
        self.element_keep["scan_type"] = doc["md"]["extra"]["mode"]
        doc = {**doc,**self.element_keep}
        if self.detectors_noPrefix[0] in ["WhiteFS","IntegratedFS","MonochromaticFS"]:
              self.names = [self.D[det].hdf1.full_file_name.get() for det in [self.detectors_noPrefix[0]]]
              print(self.names)
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
        elif self.detectors_noPrefix[0] == "WhiteXBPM":
              msg = {
                  "type": "detector_scan_start",
                  "scan_id":doc["scan_id"],
                  "frame_count": doc["num_points"],
                  #"file_path_list": [self.names[0]],
                  **doc
              }
              print("before worker:")
              #self.worker = Worker(DEALER, detectorWorkerIP, detectorWorkerPort)
              #self.worker.send_dumps(msg)
              #msg["type"] = "detector_scan_start"
              #print("**********zcl,",msg['scan_type'])
              self.worker1 = Worker(DEALER, alignWorkerIP, alignWorkerPort_xbpm)
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

