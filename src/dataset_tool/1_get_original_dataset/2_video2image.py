import cv2
import os


def extract_frames(video_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"总帧数: {total_frames}")

    for frame_count in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_filename, frame)

        # 显示进度
        progress = (frame_count + 1) / total_frames * 100
        print(f"转换进度: {progress:.2f}%，当前帧: {frame_count + 1}/{total_frames}")

    cap.release()
    print("提取完成！")


# 输入视频文件路径和输出文件夹
video_path = "1.mp4"
output_folder = "2_video2image"
extract_frames(video_path, output_folder)
