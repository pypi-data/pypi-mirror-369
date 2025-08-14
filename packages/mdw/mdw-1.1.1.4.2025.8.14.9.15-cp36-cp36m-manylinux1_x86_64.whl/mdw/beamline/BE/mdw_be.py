#!/usr/bin/python3
import fileservice.fileServiceProcess
import mdw
from mdw import *
from mdw.node.detector.detectorWorker_be.detectorWorker import *
from mdw.node.detector.detectorWorker_autoroi.detectorWorker import *
from mdw.node.storage.storageWorker import *
from mdw.node.buffer.bufferWorker import *
from multiprocessing import Process

from mdw.beamline.BE.mdw_config import *


workers = []

#"""
#detectorWorkerEntity = { "worker_name" : "detectorWorker_be",
#                         "command": "detectorWorker_be",
#                         "args": f"--name detectorWorker --ip {detectorWorkerIP} --port {detectorWorkerPort}  --outputs {alignWorkerIP}:{alignWorkerPort0}",
#                         #"args": f"--name detectorWorker --ip {detectorWorkerIP} --port {detectorWorkerPort}  --outputs {alignWorkerIP}",
#                         "hostname": detectorWorkerIP,
#                         "username": detectorWorkerUserName,
#                         "password": detectorWorkerPassword,
#                         "function": mdw.node.detector.detectorWorker_be.detectorWorker.main
#                         }
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
                         "args": f"--name alignWorkerStop --log-level=DEBUG --input {alignWorkerIP}:{alignWorkerPort0} {alignWorkerIP}:{alignWorkerPort1} --outputs {storageWorkerIP}:{storageWorkerPort}:['Tomography','Count','Mosaic','Tomo+bg','Focal Series','Background','Averaging','FlyCT'] {mambaIP}:{mambaPort} {bufferIP}:{bufferPort} --process ~/.mdw:average",
                         #"args": f"--name detectorWorker --input {alignWorkerIP}:{alignWorkerPort0} {alignWorkerIP}:{alignWorkerPort1} --outputs {storageWorkerIP}:{storageWorkerPort} ",
                         "hostname": mdwIP,
                         "username": mdwUserName,
                         "password": mdwPassword,
                         "function": mdw.core.mdw_network.AlignWorkerStopRun
                         }
"""
alignWorkerEntity = { "worker_name" : "alignWorkersStop",
                         "command": "alignWorkerStop",
                         #"args": f"--name alignWorker --input {alignWorkerIP}:{alignWorkerPort0} {alignWorkerIP}:{alignWorkerPort1} --outputs {storageWorkerIP}:{storageWorkerPort}:['flyscan']",
                         #"args": f"--name alignWorker --input {alignWorkerIP}:{alignWorkerPort0} {alignWorkerIP}:{alignWorkerPort1} --outputs {storageWorkerIP}:{storageWorkerPort} {bufferIP}:{bufferPort}",
                         "args": f"--name alignWorker --log-level=DEBUG --input {alignWorkerIP}:{alignWorkerPort0} {alignWorkerIP}:{alignWorkerPort1} \
                                    --outputs {storageWorkerIP}:{storageWorkerPort}:['flyscan'] {bufferIP}:{bufferPort}\
                                    --process ~/.mdw/BE:average",
                         "hostname": mdwIP,
                         "username": mdwUserName,
                         "password": mdwPassword,
                         #"function": mdw.core.mdw_network.AlignWorkerRun,
                        "function": mdw.core.mdw_network.AlignWorkerStopRun
                         }
"""
workers.append(alignWorkerEntity)
#"""

#用于 stepscan
alignWorkerEntity2 = { "worker_name" : "alignWorker_stepscan",
                      "command": "alignWorker",
                      "args": f"--name alignWorker_stepscan --input {alignWorker2IP}:{alignWorker2Port0} --outputs {storageWorkerIP}:{storageWorkerPort} {mambaIP}:{mambaPort} {bufferIP}:{bufferPort}",
                      #"args": f"--name alignWorker --input {alignWorkerIP}:{alignWorkerPort0} {alignWorkerIP}:{alignWorkerPort1} --outputs {storageWorkerIP}:{storageWorkerPort}",
                      "hostname": mdwIP,
                      "username": mdwUserName,
                      "password": mdwPassword,
                      "function": mdw.core.mdw_network.AlignWorkerRun
                      }
workers.append(alignWorkerEntity2)


#fly
detectorWorkerEntity = { "worker_name" : "detectorWorker_autoroi_fly_hama",
                         "command": "detectorWorker_autoroi",
                         "args": f"--name detectorWorker_autoroi_fly_hama --ip {detectorWorkerIP} --port {detectorWorkerPort_fly_hama}  --outputs {alignWorkerIP}:{alignWorkerPort_fly_hama}",
                         #"args": f"--name detectorWorker --ip {detectorWorkerIP} --port {detectorWorkerPort}  --outputs {alignWorkerIP}",
                         "hostname": detectorWorkerIP,
                         "username": detectorWorkerUserName,
                         "password": detectorWorkerPassword,
                         "function": mdw.node.detector.detectorWorker_autoroi.detectorWorker.main
                         }
workers.append(detectorWorkerEntity)

detectorWorkerEntity = { "worker_name" : "detectorWorker_autoroi_fly_panda",
                         "command": "detectorWorker_autoroi",
                         "args": f"--name detectorWorker_autoroi_fly_panda --ip {mambaIP} --port {detectorWorkerPort_fly_panda}  --outputs {alignWorkerIP}:{alignWorkerPort_fly_panda}",
                         #"args": f"--name detectorWorker --ip {detectorWorkerIP} --port {detectorWorkerPort}  --outputs {alignWorkerIP}",
                         "hostname": mambaIP,
                         "username": mambaUserName,
                         "password": mambaPassword,
                         "function": mdw.node.detector.detectorWorker_autoroi.detectorWorker.main
                         }
workers.append(detectorWorkerEntity)

camonitorWorkerEntity = { "worker_name" : "camonitorWorker",
                         "command": "camonitorWorker",
                         #"args": f"--name camonitorWorker --pv BL_ID30:Sample1_Sensor:dispChan1M --ip {camonitorWorkerIP} --port {camonitorWorkerPort}  --outputs {alignWorkerIP}:{alignWorkerPort_fly_camonitor}",
                          "args": f"--log-level=DEBUG --name camonitorWorker --pv BL_ID30:Sample1_Sensor:dispChan1M --ip {camonitorWorkerIP} --port {camonitorWorkerPort}  --outputs {alignWorkerIP}:{alignWorkerPort_fly_camonitor}",
                         "hostname": camonitorWorkerIP,
                         "username": camonitorWorkerUserName,
                         "password": camonitorWorkerPassword,
                         "function": mdw.node.detector.camonitorWorker.camonitorWorker.main
                         }
workers.append(camonitorWorkerEntity)


alignWorkerEntity = { "worker_name" : "alignWorkerStop_fly",
                      "command": "alignWorkerStop",
                      "args": f"--name alignWorkerStop_fly --log-level=DEBUG --input {alignWorkerIP}:{alignWorkerPort_fly_hama} {alignWorkerIP}:{alignWorkerPort_fly_panda} {alignWorkerIP}:{alignWorkerPort_fly_camonitor} --outputs {storageWorkerIP}:{storageWorkerPort}:['Tomography','Count','Mosaic','Tomo+bg','Focal Series','Background','Averaging','FlyCT'] {mambaIP}:{mambaPort} {bufferIP}:{bufferPort} --process ~/.mdw:average",
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
workers.append(bufferWorkerEntiry)

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






