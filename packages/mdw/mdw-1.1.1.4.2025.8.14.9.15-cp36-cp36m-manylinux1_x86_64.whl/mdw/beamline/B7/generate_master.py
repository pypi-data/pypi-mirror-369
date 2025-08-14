import h5py
import os
import re

# autor: chenglongzhang
# date: 2021-07-15
# version: 1.0


# 设定数据的根目录
root_dir = '/home/zcl/test_b7'


# 用于生成 flat_master 文件的函数
def create_flat_master_h5():
    master_path = os.path.join(root_dir, 'flat_master.h5')
    # 创建或打开一个HDF5文件
    with h5py.File(master_path, 'w') as master_h5:
        # 在master文件中创建一个数据集组
        entry_group = master_h5.create_group('/entry/data')

        # 初始化数据集计数器
        dataset_index = 0

        # 遍历所有Flat文件夹
        flat_folders = [f for f in os.listdir(root_dir) if f.startswith('Flat')]
        for flat_folder in sorted(flat_folders,
                                  key=lambda x: int(x[4:])):  # Assumes folder names are like Flat1, Flat2, etc.
            flat_folder_path = os.path.join(root_dir, flat_folder)
            # 选取符合000x.h5模式的文件
            h5_files = sorted([f for f in os.listdir(flat_folder_path) if re.match(r'^\d{4}\.h5$', f)])

            for h5_file in h5_files:
                h5_path = os.path.join(flat_folder_path, h5_file)
                # 设置外部链接的目标数据集路径
                dataset_name = f'000{dataset_index}.h5'
                external_path = f'/entry/data/{dataset_name}'
                entry_group[external_path] = h5py.ExternalLink(h5_path, '/entry/data/data')
                dataset_index += 1


# 生成 flat_master.h5
#create_flat_master_h5()

import h5py
import os
import re

# 设定数据的根目录
root_dir = '/home/zcl/test_b7'


def create_master_h5(folder_prefix, master_filename):
    """
    创建 master H5 文件，链接指定前缀的文件夹中符合000x.h5模式的文件。

    参数:
    folder_prefix: 文件夹前缀，如 'Flat' 或 'Projection'
    master_filename: 输出的 master 文件名，如 'flat_master.h5' 或 'projection_master.h5'
    """
    master_path = os.path.join(root_dir, master_filename)
    # 创建或打开一个HDF5文件
    with h5py.File(master_path, 'w') as master_h5:
        # 在master文件中创建一个数据集组
        entry_group = master_h5.create_group('/entry/data')

        # 初始化数据集计数器
        dataset_index = 0

        # 遍历所有符合前缀的文件夹
        target_folders = [f for f in os.listdir(root_dir) if f.startswith(folder_prefix)]
        for target_folder in sorted(target_folders, key=lambda x: int(re.findall(r'\d+', x)[0])):
            target_folder_path = os.path.join(root_dir, target_folder)
            # 选取符合000x.h5模式的文件
            h5_files = sorted([f for f in os.listdir(target_folder_path) if re.match(r'^\d{4}\.h5$', f)])

            for h5_file in h5_files:
                h5_path = os.path.join(target_folder_path, h5_file)
                # 设置外部链接的目标数据集路径
                dataset_name = f'000{dataset_index}.h5'
                external_path = f'/entry/data/{dataset_name}'
                entry_group[external_path] = h5py.ExternalLink(h5_path, '/entry/data/data')
                dataset_index += 1


# 生成 flat_master.h5
#create_master_h5('Flat', 'flat_master.h5')

# 生成 projection_master.h5
#create_master_h5('Projection', 'projection_master.h5')

import h5py
import os
import re

# 设定数据的根目录
#root_dir = 'your_data_folder_path'


def create_master_h5(root_dir,folder_prefix, master_filename):
    """
    创建 master H5 文件，链接指定前缀的文件夹中符合000x.h5模式的文件。
    参数:
    folder_prefix: 文件夹前缀，如 'Flat' 或 'Projection'
    master_filename: 输出的 master 文件名，如 'flat_master.h5' 或 'projection_master.h5'
    """
    master_path = os.path.join(root_dir, master_filename)
    # 创建或打开一个HDF5文件
    with h5py.File(master_path, 'w') as master_h5:
        # 在master文件中创建一个数据集组
        entry_group = master_h5.create_group('/entry/data')

        # 初始化数据集计数器
        dataset_index = 0

        # 遍历所有符合前缀的文件夹
        target_folders = [f for f in os.listdir(root_dir) if f.startswith(folder_prefix)]
        for target_folder in sorted(target_folders, key=lambda x: int(re.findall(r'\d+', x)[0])):
            target_folder_path = os.path.join(root_dir, target_folder)
            # 选取符合000x.h5模式的文件
            h5_files = sorted([f for f in os.listdir(target_folder_path) if re.match(r'^\d{4}\.h5$', f)],
                              key=lambda x: int(x.split('.')[0]))

            for h5_file in h5_files:
                h5_path = os.path.join(target_folder_path, h5_file)
                relative_path = os.path.relpath(h5_path, start=os.path.dirname(master_path))
                # 设置外部链接的目标数据集路径
                dataset_name = f'{dataset_index:04}.h5'
                external_path = f'/entry/data/{dataset_name}'
                entry_group[external_path] = h5py.ExternalLink(relative_path, '/entry/data/data')
                dataset_index += 1


if __name__ == "__main__":
    # 生成 flat_master.h5
    #create_master_h5('Flat', 'flat_master.h5')
    create_master_h5('/beamlinefs/B7/202409/Data/GB7-240910-02/raw/test56', "Flat", 'flat_master.h5')
    
    # 生成 projection_master.h5
    #create_master_h5('Projection', 'projection_master.h5')

