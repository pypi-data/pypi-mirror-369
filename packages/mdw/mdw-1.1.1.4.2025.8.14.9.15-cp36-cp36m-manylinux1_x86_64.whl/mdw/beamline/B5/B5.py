
def collect_start(*arg,**args):
    filepath_store_dir = args["filepath_store_dir"]
    filename = args["filepath_store_filename"]
    filelist_dir_name = [[filepath_store_dir,filename]]
    args["filelist_dir_name"] = filelist_dir_name
    return args


