from mdw import *
import mdw
from mdw.node.detector.detectorWorker_ba import *
from mdw.node.storage.storageWorker import *
from multiprocessing import Process
from .mdw_config import *


workers = []

detectorWorkerEntity = { "worker_name" : "detectorWorker_ba",
                         "command": "detectorWorker_ba",
                         "function": "detectorWorker_ba",
                        "args": f"--name detectorWorker_ba --ip {detectorIP} --port {detectorPort}  --outputs {storageWorkerIP}:{storageWorkerPort}",
                         #"args": f"--log-level DEBUG --name detectorWorker_ba --ip {detectorIP} --port {detectorPort}  --outputs {storageWorkerIP}:{storageWorkerPort}",
                        "hostname": detectorIP,
                         "username": detecotrUserName,
                         "password": detecotrPassword,
                          "function": mdw.node.detector.detectorWorker_ba.main
                         }

workers.append(detectorWorkerEntity)

#"""
# 启动 storageWorker
storageWorkerEntiry = { "worker_name" : "storageWorker",
                     "command": "storageWorker",
                        "args": "",
                        "hostname": mdwIP,
                        "username": mdwUserName,
                         "password": mdwPassword,
                        "function": mdw.node.storage.storageWorker.main
                        }
workers.append(storageWorkerEntiry)

import fileservice.fileServiceProcess
# 启动 fileservice
fileserviceWorkerEntiry = { "worker_name" : "fileserviceWorker",
                        "command": "fileservice",
                        "args": "",
                        "hostname": mdwIP,
                        "username": mdwUserName,
                        "password": mdwPassword,
                        "function": fileservice.fileServiceProcess.main
                        }
workers.append(fileserviceWorkerEntiry)


if __name__ == "__main__":
    d = Dispatcher(workers,RemoteWorkEntity)
    d.dispatch()
    d.monitor()
    input()


