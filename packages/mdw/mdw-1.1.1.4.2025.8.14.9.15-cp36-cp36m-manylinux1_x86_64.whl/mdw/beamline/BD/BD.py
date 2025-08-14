import os.path

def collect_start(*arg,**args):
    filepath_store_dir = args["filepath_store_dir"]
    filename = args["filepath_store_filename"]
    #gui
    CTType = args["CTType"]
    filepath_store_dir = args["filepath_store_dir"]
    # if directory not exist, create it
    if not os.path.exists(filepath_store_dir):
        os.makedirs(filepath_store_dir)
    #filename = filename.split(".")[0]+"_"+CTType+".nxs" #只需要打开这句，文件名即可加上 _CTType 信息
    filelist_dir_name = [[filepath_store_dir,filename]]
    args["filelist_dir_name"] = filelist_dir_name
    #det
    """
    scan_id = args.get("scan_id","none")

    filename1 = "ID21_%s_%s.nxs" % (CTType,str(scan_id))
    filename2 = "ID21_Dhyana_%s_%s_master.h5" % (CTType,str(scan_id))
    filelist_dir_name = [[filepath_store_dir,filename1],[filepath_store_dir,filename2]]
    args["filelist_dir_name"] = filelist_dir_name
    identify = filepath_store_dir.split("/")[-1] #sample info
    args["identify"] = identify
    """
    return args

from multiprocessing import Process
import h5py
from PIL import Image
def transform_nxs_to_tiff(filepath):
    if os.fork() != 0:
        return
    f = h5py.File(filepath,"r")
    # get filename filepath
    basename = os.path.basename(filepath).split(".")[0]
    filedir = os.path.dirname(filepath) + "/" + basename+"_tiff"
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    data = f["/entry/data/data"]
    for i in range(data.shape[0]):
        A = data[i,:,:]
        filepath = filedir + "/" + str(i) + ".tiff"
        im = Image.fromarray(A)
        im.save(filepath)

def collect_stop(*arg,**args):
    # to tiff
    filepath = args["filepath"]
    # create a process and transform nxs to tiff
    p = Process(target=transform_nxs_to_tiff,args=(filepath,))
    p.start()
    p.join()

    pass