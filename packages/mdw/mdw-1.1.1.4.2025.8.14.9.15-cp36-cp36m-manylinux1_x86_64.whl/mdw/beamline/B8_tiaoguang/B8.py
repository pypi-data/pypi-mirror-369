import os.path

def collect_start(*arg,**args):
    filepath_store_dir = args["filepath_store_dir"]
    #filepath_store_dir = "/home/mamba/mdw_result/experiment"
    filename = args["filepath_store_filename"]
    #gui
    filepath_store_dir = args["filepath_store_dir"]
    # if directory not exist, create it
    if not os.path.exists(filepath_store_dir):
        os.makedirs(filepath_store_dir)
    #filename = filename.split(".")[0]+"_"+CTType+".nxs" #只需要打开这句，文件名即可加上 _CTType 信息
    filelist_dir_name = [[filepath_store_dir,filename]]
    args["filelist_dir_name"] = filelist_dir_name
    print("zcl collect_start args",args)
    return args
