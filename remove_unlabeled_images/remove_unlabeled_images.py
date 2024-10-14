'''
Author: Ashington ashington258@proton.me
Date: 2024-06-22 00:53:13
LastEditors: Ashington ashington258@proton.me
LastEditTime: 2024-06-22 00:53:19
FilePath: \AI_Tools\remove_unlabeled_images.py\remove_unlabeled_images.py
Description: 请填写简介
联系方式:921488837@qq.com
Copyright (c) 2024 by ${git_name_email}, All Rights Reserved. 
'''
import os

# 定义图片和JSON文件的目录
image_dir = 'F:/15_Train_data/zebra_redlight/train_data_2024_6_21_21_30/data'  # 请替换为你的图片目录
json_dir = 'F:/15_Train_data/zebra_redlight/train_data_2024_6_21_21_30/data'    # 请替换为你的JSON文件目录

# 获取所有图片文件的列表
image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]

# 获取所有JSON文件的列表
json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

# 生成JSON文件名列表（不带扩展名）
json_file_basenames = [os.path.splitext(f)[0] for f in json_files]

# 遍历图片文件列表，删除没有对应JSON文件的图片
for image_file in image_files:
    image_basename = os.path.splitext(image_file)[0]
    if image_basename not in json_file_basenames:
        image_path = os.path.join(image_dir, image_file)
        os.remove(image_path)
        print(f'Deleted {image_path}')

print("Completed removing unlabeled images.")
