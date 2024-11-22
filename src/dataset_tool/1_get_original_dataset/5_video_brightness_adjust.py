import cv2
import os
import concurrent.futures
import argparse


def adjust_brightness(frame, beta):
    return cv2.convertScaleAbs(frame, alpha=1, beta=beta)


def process_frame(frame, brightness_adjustment):
    return adjust_brightness(frame, brightness_adjustment)


def main(input_video, output_video, brightness_adjustment, num_workers):
    # 检查输入文件是否存在
    if not os.path.exists(input_video):
        print("输入视频文件不存在。")
        return

    # 打开视频文件
    cap = cv2.VideoCapture(input_video)

    # 获取视频的基本信息
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 创建视频写入对象
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    frames = []
    for frame_idx in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    # 处理视频并显示进度
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(process_frame, frame, brightness_adjustment): idx
            for idx, frame in enumerate(frames)
        }

        for future in concurrent.futures.as_completed(futures):
            bright_frame = future.result()
            out.write(bright_frame)

            # 显示进度
            progress = (futures[future] + 1) / total_frames * 100
            print(f"处理进度: {progress:.2f}%")

    # 释放资源
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("视频处理完成！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="视频亮度调整")
    parser.add_argument("--input", type=str, default="2.mp4", help="输入视频路径")
    parser.add_argument(
        "--output",
        type=str,
        default="5_video_brightness_adjust.mp4",
        help="输出视频路径",
    )
    parser.add_argument("--brightness", type=int, default=-100, help="亮度调整值")
    parser.add_argument("--workers", type=int, default=10, help="处理核心数量")

    args = parser.parse_args()

    main(args.input, args.output, args.brightness, args.workers)
