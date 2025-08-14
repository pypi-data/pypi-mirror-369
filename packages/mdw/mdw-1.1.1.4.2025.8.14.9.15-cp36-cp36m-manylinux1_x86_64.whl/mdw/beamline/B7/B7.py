import os.path


def collect_start(*arg,**args):
    #gui
    CTType = args["CTType"]
    filepath_store_dir = args["filepath_store_dir"]
    # if directory not exist, create it
    #det
    scan_id = args.get("scan_id","none")

    filename1 = "ID21_%s_%s.nxs" % (CTType,str(scan_id))
    filepath1 = filepath_store_dir +"/" + CTType + str(scan_id)+"/"
    if not os.path.exists(filepath1):
        os.makedirs(filepath1)
    filename2 = "ID21_Dhyana_%s_%s_master.h5" % (CTType,str(scan_id))
    filepath2 = filepath_store_dir +"/" + CTType + str(scan_id)+"/"
    if not os.path.exists(filepath2):
        os.makedirs(filepath2)
    filelist_dir_name = [[filepath1,filename1],[filepath2,filename2]]
    args["filelist_dir_name"] = filelist_dir_name
    identify = filepath_store_dir.split("/")[-1] #sample info
    args["identify"] = identify
    return args

    pass

import h5py
import os
import re
def create_master_h5(root_dir,folder_prefix, master_filename):
    """
    ~H~[建 master H5 ~V~G件~L~S~N~L~G~Z~I~M~@~Z~D~V~G件夹中符~P~H000x.h5模~O~Z~D~V~G件~@~B
    ~O~B~U:
    folder_prefix: ~V~G件夹~I~M~@~L~B 'Flat' ~H~V 'Projection'
    master_filename: ~S~G~Z~D master ~V~G件~P~M~L~B 'flat_master.h5' ~H~V 'projection_master.h5'
    """
    master_path = os.path.join(root_dir, master_filename)
    # ~H~[建~H~V~I~S~@~@个HDF5~V~G件
    with h5py.File(master_path, 'w') as master_h5:
        # ~\master~V~G件中~H~[建~@个~U~M~[~F~D
        entry_group = master_h5.create_group('/entry/data')

        # ~H~]~K~L~V~U~M~[~F计~U~Y
        dataset_index = 0

        # ~A~M~N~F~I~@~\~I符~P~H~I~M~@~Z~D~V~G件夹
        target_folders = [f for f in os.listdir(root_dir) if f.startswith(folder_prefix)]
        for target_folder in sorted(target_folders, key=lambda x: int(re.findall(r'\d+', x)[0])):
            target_folder_path = os.path.join(root_dir, target_folder)
            # ~@~I~O~V符~P~H000x.h5模~O~Z~D~V~G件
            h5_files = sorted([f for f in os.listdir(target_folder_path) if re.match(r'^\d{4}\.h5$', f)],
                              key=lambda x: int(x.split('.')[0]))

            for h5_file in h5_files:
                h5_path = os.path.join(target_folder_path, h5_file)
                relative_path = os.path.relpath(h5_path, start=os.path.dirname(master_path))
                # 设置~V~C~S~N~Z~D~[| ~G~U~M~[~F路~D
                dataset_name = f'{dataset_index:04}.h5'
                external_path = f'/entry/data/{dataset_name}'
                entry_group[external_path] = h5py.ExternalLink(relative_path, '/entry/data/data')
                dataset_index += 1

def collect_stop(*arg,**task):
    print("mdw storage stop process")
    print("mdw storage stop process,arg:",task)
    root_dir = task.get("filepath_store_dir")
    if root_dir is not None:
        create_master_h5(root_dir,"Flat",'flat_master.h5')
        create_master_h5(root_dir,"Projection",'projection_master.h5')
    else:
        print("zcl error!!! root_dir is None")