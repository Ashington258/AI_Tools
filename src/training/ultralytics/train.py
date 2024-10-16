import os
import subprocess
import argparse
import ultralytics


def main(args):
    # 检查路径是否存在
    if not os.path.exists(args.dataset_root):
        print(f"错误：数据集根目录 {args.dataset_root} 不存在。")
        return

    if not os.path.exists(args.yaml_file):
        print(f"错误：YAML 文件 {args.yaml_file} 不存在。")
        return

    # 训练命令
    command = [
        "yolo",
        "task=segment",
        "mode=train",
        "model=yolo11s-seg.pt",  # 使用 YOLOv11 的分割模型
        f"data={args.yaml_file}",
        f"epochs={args.epochs}",
        f"imgsz={args.imgsz}",
    ]

    # 执行训练命令
    try:
        print("开始训练...")
        subprocess.run(" ".join(command), shell=True, check=True)
        print("训练完成！")
    except subprocess.CalledProcessError as e:
        print(f"训练过程中发生错误：{e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="训练 YOLOv11s-seg 模型的脚本")
    parser.add_argument(
        "--dataset_root",
        type=str,
        default="dataset/0-200/yolo",
        help="数据集根目录",
    )
    parser.add_argument(
        "--yaml_file",
        type=str,
        default=os.path.abspath("dataset/0-200/yolo/dataset.yaml"),
        help="YAML 配置文件路径",
    )
    parser.add_argument("--epochs", type=int, default=100, help="训练轮数")
    parser.add_argument("--imgsz", type=int, default=640, help="输入图像大小")

    args = parser.parse_args()
    main(args)
