
# = "ADMIN"
#detectorWorkerPassword= "123"
#mdwIP = "0.0.0.0"
#mdwIP = "10.5.181.8"
#mdwIP = "192.168.1.100"
#mdwIP = "10.8.54.253"
mdwIP = "10.5.133.129" #used
#mdwIP = "192.168.3.16"
#mdwUserName = "mamba"
#mdwPassword = "abc123456"
mdwUserName = "mdw"
mdwPassword = "abc123456"
#mamba = "192.168.3.10"

alignWorkerIP = mdwIP
alignWorkerPort0 = 8000
alignWorkerPort1 = 8001
alignWorkerPort_fly_hama = 8002
alignWorkerPort_fly_panda = 8003
alignWorkerPort_fly_camonitor = 8004

#用于 stepscan
alignWorker2IP = mdwIP
alignWorker2Port0 = 7003


storageWorkerIP = mdwIP
storageWorkerPort = 6700

#mambaIP = "0.0.0.0"
mambaIP = "10.5.133.130" #used
mambaPort = 6668
mambaUserName = "mamba"
mambaPassword = "abc123456"

#bufferIP = "0.0.0.0"
#bufferIP = "10.5.133.130"
bufferIP = mdwIP
bufferPort = "6378"

#detectorWorkerIP = "0.0.0.0"
#detectorWorkerIP = "localhost"
#detectorWorkerIP = "10.5.181.10"
#detectorWorkerIP = "192.168.1.14"
#detectorWorkerIP = "10.8.54.254"
detectorWorkerIP = "10.5.133.137" #used
detectorWorkerPort = 6667
detectorWorkerPort_fly_hama = 6670
#detectorWorkerIP = "192.168.60.198"
#detectorWorkerUserName = "mamba"
#detectorWorkerPassword= "abc123456"
#detectorWorkerUserName = "ADMIN"
detectorWorkerUserName = "BE"
detectorWorkerPassword= "123456"

pandaWorkerIP = mambaIP
detectorWorkerPort_fly_panda = 6671
pandaUserName = mambaUserName
pandaPassword = mambaPassword

#camonitorWorkerIP = "10.5.133.155"
camonitorWorkerIP = mdwIP
camonitorWorkerPort = 6672
camonitorWorkerUserName = mdwUserName
camonitorWorkerPassword = mdwPassword
