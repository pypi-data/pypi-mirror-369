#!/usr/bin/python3
import fileservice.fileServiceProcess
import mdw
from mdw import *
from mdw.node.detector.detectorWorker_be.detectorWorker import *
from mdw.node.detector.detectorWorker_autoroi.detectorWorker import *
from mdw.node.storage.storageWorker import *
from mdw.node.buffer.bufferWorker import *
from multiprocessing import Process

from mdw.beamline.BD.mdw_config import *


workers = []

detectorWorkerEntity = { "worker_name" : "detectorWorker_autoroi",
                         "command": "detectorWorker_autoroi",
                         "args": f"--name detectorWorker --ip {detectorWorkerIP} --port {detectorWorkerPort}  --outputs {alignWorkerIP}:{alignWorkerPort0}",
                         #"args": f"--name detectorWorker --ip {detectorWorkerIP} --port {detectorWorkerPort}  --outputs {alignWorkerIP}",
                         "hostname": detectorWorkerIP,
                         "username": detectorWorkerUserName,
                         "password": detectorWorkerPassword,
                         "function": mdw.node.detector.detectorWorker_autoroi.detectorWorker.main
                         }
workers.append(detectorWorkerEntity)


alignWorkerEntity = { "worker_name" : "alignWorkerStop",
                         "command": "alignWorkerStop",
                         #"args": f"--name detectorWorker --input {alignWorkerIP}:{alignWorkerPort0} {alignWorkerIP}:{alignWorkerPort1} --outputs {storageWorkerIP}:{storageWorkerPort} {mambaIP}:{mambaPort}",
                         "args": f"--name alignWorkerStop --log-level=DEBUG --input {alignWorkerIP}:{alignWorkerPort0} {alignWorkerIP}:{alignWorkerPort1} --outputs {storageWorkerIP}:{storageWorkerPort}:['Tomography'] {mambaIP}:{mambaPort} {bufferIP}:{bufferPort} --process ~/.mdw:average",
                         #"args": f"--name detectorWorker --input {alignWorkerIP}:{alignWorkerPort0} {alignWorkerIP}:{alignWorkerPort1} --outputs {storageWorkerIP}:{storageWorkerPort} ",
                         "hostname": mdwIP,
                         "username": mdwUserName,
                         "password": mdwPassword,
                         "function": mdw.core.mdw_network.AlignWorkerStopRun
                         }
workers.append(alignWorkerEntity)

# 启动 storageWorker
storageWorkerEntiry = { "worker_name" : "storageWorker",
                        "command": "storageWorker --log-level=DEBUG",
                        #"command": "storageWorker",
                        "args": "",
                        "hostname": mdwIP,
                        "username": mdwUserName,
                        "password": mdwPassword,
                        "function": mdw.node.storage.storageWorker.main
                        }
workers.append(storageWorkerEntiry)


# 启动 fileservice
fileserviceWorkerEntiry = { "worker_name" : "fileserviceWorker",
                            "command": "fileservice --log-level=DEBUG",
                            #"command": "fileservice",
                            "args": "",
                            "hostname": mdwIP,
                            "username": mdwUserName,
                            "password": mdwPassword,
                            "function": fileservice.fileServiceProcess.main
                            }
workers.append(fileserviceWorkerEntiry)
#"""

bufferWorkerEntiry = { "worker_name" : "bufferWorker",
                            "command": "bufferWorker",
                            "args": f"--name bufferWorker --ip {bufferIP} --port {bufferPort} --outputs {storageWorkerIP}:{storageWorkerPort}",
                            "hostname": bufferIP,
                            #"username": mambaUserName,
                            "username": mdwUserName,
                            "password": mdwPassword,
                            "function": mdw.node.buffer.bufferWorker.main
                            }
#workers.append(bufferWorkerEntiry)

def main(argv=sys.argv[1:]):
    d = Dispatcher(workers,RemoteWorkEntity)
    d.dispatch()
    d.monitor()
    input()

if __name__ == "__main__":
    d = Dispatcher(workers,RemoteWorkEntity)
    d.dispatch()
    d.monitor()
    input()
pass






