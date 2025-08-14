from mdw import *
from mdw.beamline.BE.mdw_config import *

try:
    from bluesky.callbacks.core import CallbackBase
except ImportError:
    CallbackBase = object
    print("not found CallbackBase")

class mdw_bluesky_callback_be_bluesky(CallbackBase):
    def __init__(self,D):
        super().__init__()
        self.D = D

    def start(self, doc):
        #print("zcl",doc)
        self.names = \
            [self.D[det].hdf1.full_file_name.get() for det in ["HAMA"]]
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
        #self.worker = Worker(DEALER, "10.8.54.254", "6667")
        #self.worker = Worker(DEALER, "10.5.133.137", "6667")
        self.worker = Worker(DEALER, detectorWorkerIP, detectorWorkerPort)
        #print("worker:",self.worker)
        self.worker.send_dumps(msg)
        msg["type"] = "detector_scan_start"
        #self.scan_type = msg["md"]["extra"]["mode"]
        #msg["scan_type"] = self.scan_type
        print("**********zcl,",msg['scan_type'])
        #self.worker1 = Worker(DEALER, "10.5.181.8", "8001")
        #self.worker1 = Worker(DEALER, "10.8.54.253", "8001")
        #self.worker1 = Worker(DEALER, "10.5.133.129", "8001")
        self.worker1 = Worker(DEALER, alignWorkerIP, alignWorkerPort1)
        print("worker1:",self.worker1)
        self.worker1.send_dumps(msg)

    def descriptor(self, doc):
        #print("==== ==============zcl describe: ",doc)
        pass

    def event(self, doc):
        doc["type"] = "detector_scan_collect"
        #doc["scan_type"] = self.scan_type
        doc = {**doc,**self.element_keep}
        print("zcl event:")
        print("zcl event:",doc)
        self.worker1.send_dumps(doc)

    def stop(self, doc):
        print("zcl stop: stop begin")
        doc = {**doc,**self.element_keep}
        doc["type"] = "detector_scan_stop"
        print("zcl stop:",doc)
        #sdoc["scan_type"] = self.scan_type
        self.worker1.send_dumps(doc)
        #print("zcl after stop:",doc,self.worker1)
        import time
        #time.sleep(20)
        pass

class MdwBlueskyCallbackBeFly(CallbackBase):
    def __init__(self,D):
        super().__init__()
        self.D = D

    def start(self, doc):
        #print("zcl",doc)
        self.names = \
            {det: self.D[det].hdf1.full_file_name.get() for det in ["HAMA", "ADP"]}
        print("zcl:filename", self.names)
        self.element_keep = {}
        self.element_keep = doc["md"]
        scan_id = getRunId()
        self.element_keep["scan_id"] = scan_id
        self.element_keep["scan_type"] = doc["md"]["extra"]["mode"]
        doc = {**doc,**self.element_keep}
        print("zcl: scan_id", doc["scan_id"])
        num_points_fly = doc.get("frame_count",0)
        # 飞扫前后拍的张数
        num_points_start = doc.get("frame_count_start",0)
        num_points_end = doc.get("frame_count_end",0)
        total = num_points_fly+num_points_start+num_points_end
        """
        # used for test
        msg = {
            "type": "detector_flyscan_start",
            "scan_id":doc["scan_id"],
            "frame_count": num_points_fly,
            "frame_count_start": num_points_start, 
            "frame_count_end": num_points_end, 
            "file_path_list": [self.names["HAMA"]],
            **doc
        }
        """
        msg = {
            **doc,
            "type": "detector_flyscan_start",
            "scan_id":doc["scan_id"],
            "frame_count": total,
            "file_path_list": [self.names["HAMA"]]
            #**doc bug
        }
        self.worker = Worker(DEALER, detectorWorkerIP, detectorWorkerPort_fly_hama)
        self.worker.send_dumps(msg)

        msg = {
            **doc,
            "type": "detector_flyscan_start",
            "scan_id":doc["scan_id"],
            "frame_count": num_points_fly,
            "frame_count_start": num_points_start,
            "frame_count_end": num_points_end,
            "file_path_list": [self.names["ADP"]]
        }
        self.worker = Worker(DEALER, pandaWorkerIP, detectorWorkerPort_fly_panda)
        self.worker.send_dumps(msg)

        msg["type"] = "detector_scan_start"
        self.worker = Worker(DEALER, camonitorWorkerIP,camonitorWorkerPort)
        self.worker.send_dumps(msg)
        pass


    def descriptor(self, doc):
        #print("==== ==============zcl describe: ",doc)
        pass

    def event(self, doc):
        doc["type"] = "detector_scan_collect"
        #doc["scan_type"] = self.scan_type
        doc = {**doc,**self.element_keep}
        print("zcl event:",doc)

    def stop(self, doc):
        print("zcl stop: stop begin")
        doc = {**doc,**self.element_keep}
        doc["type"] = "detector_scan_stop"
        print("zcl stop:",doc)
        pass
