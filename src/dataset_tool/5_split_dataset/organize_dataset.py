"""数据集整理工具

功能说明：
从混合文件夹中自动识别并匹配图像文件和对应的标签文件，
将它们分类复制到 images/ 和 labels/ 文件夹中。

主要特性：
- 自动匹配图像和标签文件（基于文件名）
- 支持多种图像格式（.jpg, .jpeg, .png, .bmp）
- 智能跳过无标签的图像
- 显示详细的处理进度和统计信息
- 支持图形界面和命令行两种模式

使用场景：
适用于标注工具导出的混合文件夹，需要整理成 YOLO 标准格式的情况。
"""

import os
import shutil
from pathlib import Path
from typing import Tuple, List


def organize_dataset(
    source_dir: str, output_dir: str, copy_mode: bool = True
) -> Tuple[int, int, int]:
    """整理数据集：将图像和标签文件分类到不同文件夹

    Args:
        source_dir: 源文件夹路径（包含混合的图像和标签文件）
        output_dir: 输出文件夹路径
        copy_mode: True=复制文件，False=移动文件

    Returns:
        (成功匹配数, 无标签图像数, 孤立标签数)

    工作流程：
        1. 扫描源文件夹中的所有文件
        2. 识别图像文件和标签文件
        3. 匹配图像和标签（基于文件名）
        4. 将匹配的文件复制/移动到对应目录
    """
    # 1. 创建输出目录结构
    images_dir = os.path.join(output_dir, "images")
    labels_dir = os.path.join(output_dir, "labels")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    # 2. 支持的图像格式
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
    label_extension = ".txt"

    # 3. 扫描源文件夹，分类文件
    print(f"\n正在扫描源文件夹: {source_dir}")

    image_files = {}  # {文件名(无扩展名): 完整路径}
    label_files = {}  # {文件名(无扩展名): 完整路径}

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)

        # 跳过目录
        if os.path.isdir(file_path):
            continue

        # 获取文件名（无扩展名）和扩展名
        name_without_ext = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1].lower()

        # 分类存储
        if ext in image_extensions:
            image_files[name_without_ext] = file_path
        elif ext == label_extension:
            label_files[name_without_ext] = file_path

    print(f"找到 {len(image_files)} 个图像文件")
    print(f"找到 {len(label_files)} 个标签文件")

    # 4. 匹配图像和标签
    matched_count = 0
    no_label_count = 0
    orphan_label_count = 0

    # 选择操作方式
    operation = shutil.copy2 if copy_mode else shutil.move
    operation_name = "复制" if copy_mode else "移动"

    print(f"\n开始{operation_name}文件...")

    # 处理图像文件
    for name, image_path in image_files.items():
        if name in label_files:
            # 找到匹配的标签
            label_path = label_files[name]

            # 复制/移动图像
            dest_image = os.path.join(images_dir, os.path.basename(image_path))
            operation(image_path, dest_image)

            # 复制/移动标签
            dest_label = os.path.join(labels_dir, os.path.basename(label_path))
            operation(label_path, dest_label)

            matched_count += 1

            # 显示进度
            if matched_count % 100 == 0:
                print(f"已处理: {matched_count} 对文件...")
        else:
            # 没有对应的标签
            no_label_count += 1
            print(f"警告: 图像 '{os.path.basename(image_path)}' 没有对应的标签文件")

    # 统计孤立的标签文件（有标签但没有图像）
    for name in label_files:
        if name not in image_files:
            orphan_label_count += 1
            print(f"警告: 标签 '{name}.txt' 没有对应的图像文件")

    # 5. 输出统计信息
    print(f"\n{'='*50}")
    print(f"整理完成！")
    print(f"{'='*50}")
    print(f"✓ 成功匹配并{operation_name}: {matched_count} 对文件")
    print(f"⚠ 无标签的图像: {no_label_count} 个")
    print(f"⚠ 孤立的标签: {orphan_label_count} 个")
    print(f"\n输出目录:")
    print(f"  - 图像: {images_dir}")
    print(f"  - 标签: {labels_dir}")
    print(f"{'='*50}\n")

    return matched_count, no_label_count, orphan_label_count


def batch_organize_datasets(
    source_dirs: List[str], output_base_dir: str, copy_mode: bool = True
):
    """批量整理多个数据集文件夹

    Args:
        source_dirs: 源文件夹路径列表
        output_base_dir: 输出基础目录
        copy_mode: True=复制文件，False=移动文件
    """
    total_matched = 0
    total_no_label = 0
    total_orphan = 0

    for i, source_dir in enumerate(source_dirs, 1):
        print(f"\n处理第 {i}/{len(source_dirs)} 个文件夹: {source_dir}")

        # 为每个源文件夹创建独立的输出目录
        folder_name = os.path.basename(source_dir.rstrip(os.sep))
        output_dir = os.path.join(output_base_dir, folder_name)

        matched, no_label, orphan = organize_dataset(source_dir, output_dir, copy_mode)

        total_matched += matched
        total_no_label += no_label
        total_orphan += orphan

    # 总体统计
    print(f"\n{'='*50}")
    print(f"批量处理完成！")
    print(f"{'='*50}")
    print(f"总计成功匹配: {total_matched} 对文件")
    print(f"总计无标签图像: {total_no_label} 个")
    print(f"总计孤立标签: {total_orphan} 个")
    print(f"{'='*50}\n")


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    import argparse

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="数据集整理工具 - 自动匹配图像和标签文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本用法（复制模式）
  python organize_dataset.py -s E:/mixed_data -o E:/organized_data
  
  # 移动模式（不保留源文件）
  python organize_dataset.py -s E:/mixed_data -o E:/organized_data --move
  
  # 批量处理多个文件夹
  python organize_dataset.py -s E:/data1 E:/data2 E:/data3 -o E:/output
        """,
    )

    parser.add_argument(
        "-s", "--source", nargs="+", required=True, help="源文件夹路径（可指定多个）"
    )

    parser.add_argument("-o", "--output", required=True, help="输出文件夹路径")

    parser.add_argument(
        "--move", action="store_true", help="移动文件而不是复制（默认为复制）"
    )

    args = parser.parse_args()

    # 验证源文件夹
    for source_dir in args.source:
        if not os.path.exists(source_dir):
            print(f"错误: 源文件夹不存在: {source_dir}")
            exit(1)
        if not os.path.isdir(source_dir):
            print(f"错误: 路径不是文件夹: {source_dir}")
            exit(1)

    # 执行整理
    copy_mode = not args.move

    if len(args.source) == 1:
        # 单个文件夹
        organize_dataset(args.source[0], args.output, copy_mode)
    else:
        # 批量处理
        batch_organize_datasets(args.source, args.output, copy_mode)
