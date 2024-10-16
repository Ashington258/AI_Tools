"""
Author: Ashington ashington258@proton.me
Date: 2024-06-14 23:50:51
LastEditors: Ashington ashington258@proton.me
LastEditTime: 2024-06-14 23:54:34
FilePath: \zebra_redlight_detection\videocapture_train_data\train_data.py
Description: 请填写简介
联系方式:921488837@qq.com
Copyright (c) 2024 by ${git_name_email}, All Rights Reserved. 
"""

import cv2
import os
import time

# 创建保存图像的目录
save_dir = "0_capture_image"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 打开摄像头
cap = cv2.VideoCapture(0)  # 0表示默认摄像头

if not cap.isOpened():
    print("无法打开摄像头")
    exit()

interval = 0.8  # 拍照间隔时间（秒）
count = 0  # 计数器

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头画面")
            break

        # 显示画面（可选）
        cv2.imshow("Camera", frame)

        # 保存图像
        img_name = os.path.join(save_dir, f"image_{count:04d}.jpg")
        cv2.imwrite(img_name, frame)
        print(f"保存 {img_name}")

        count += 1
        time.sleep(interval)

        # 按下'q'键退出循环
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("手动中断")

# 释放资源
cap.release()
cv2.destroyAllWindows()
