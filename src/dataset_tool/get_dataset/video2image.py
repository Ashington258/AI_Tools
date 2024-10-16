import cv2
import os

# 输入视频文件路径
video_path = "1.mp4"
# 输出图像文件夹
output_folder = "output_images"

# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 打开视频文件
cap = cv2.VideoCapture(video_path)

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break
    # 保存每帧为图像
    frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
    cv2.imwrite(frame_filename, frame)
    frame_count += 1

# 释放视频对象
cap.release()
print(f"提取完成，共提取 {frame_count} 帧图像。")
