"""
Author: Ashington ashington258@proton.me
Date: 2024-06-15 01:04:40
LastEditors: Ashington ashington258@proton.me
LastEditTime: 2024-06-15 01:06:40
FilePath: \triandata_rename\delete_non_py_files.py
Description: 请填写简介
联系方式:921488837@qq.com
Copyright (c) 2024 by ${git_name_email}, All Rights Reserved. 
"""

import os


def delete_json_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")


if __name__ == "__main__":
    target_directory = "F:\\15_Train_data\\zebra_redlight\\train_data_2024_6_15_3_02\\data"  # 指定目标目录, '.' 表示当前目录
    delete_json_files(target_directory)
