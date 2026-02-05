"""蒙特卡洛图像抽样工具

功能说明：
从指定文件夹中随机抽样指定数量的图像，并复制到输出文件夹。
适用于从大量图像中快速获取随机样本，用于数据集构建、测试等场景。

主要特性：
- 支持指定目标抽样数量
- 自动清空输出文件夹中的旧图像
- 显示实时复制进度
- 防止抽样数超过总图像数
"""

import os
import random
import shutil


def clear_images_in_folder(folder_path):
    """清空指定文件夹中的所有图像文件

    Args:
        folder_path: 要清空的文件夹路径
    """
    if not os.path.exists(folder_path):
        return

    # 获取文件夹中的所有图像文件
    image_files = [
        f
        for f in os.listdir(folder_path)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"))
    ]

    # 删除所有图像文件
    for image_file in image_files:
        file_path = os.path.join(folder_path, image_file)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"删除文件失败 {file_path}: {e}")

    if image_files:
        print(f"已清空输出文件夹，删除了 {len(image_files)} 张旧图像")


def monte_carlo_image_sampling(image_folder, target_count, output_folder):
    """使用蒙特卡洛方法随机抽样图像

    Args:
        image_folder: 源图像文件夹路径
        target_count: 期望抽样的图像数量
        output_folder: 输出文件夹路径
    """
    # 1. 获取文件夹中的所有图像文件
    all_images = [
        f
        for f in os.listdir(image_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    # 2. 确定实际抽样数量（不超过总图像数）
    sample_size = min(target_count, len(all_images))

    print(
        f"总图像数: {len(all_images)}, 目标抽样数: {target_count}, 实际抽样数: {sample_size}"
    )

    # 3. 使用蒙特卡洛方法随机抽样图像（无放回抽样）
    sampled_images = random.sample(all_images, sample_size)

    # 4. 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 5. 清空输出文件夹中的旧图像
    clear_images_in_folder(output_folder)

    # 6. 复制抽样的图像到输出文件夹，并显示实时进度
    for i, image in enumerate(sampled_images):
        source_path = os.path.join(image_folder, image)
        shutil.copy(source_path, output_folder)
        # 显示复制进度（当前进度/总数 百分比）
        print(f"复制中: {i + 1}/{sample_size} ({((i + 1) / sample_size) * 100:.2f}%)")

    print(f"\n✓ 抽样完成！已复制 {sample_size} 张图像到 {output_folder}")


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    # 配置参数
    image_folder = "output_file/2_video2image"  # 源图像文件夹路径
    output_folder = "output_file/3_monte_carlo_sampling"  # 输出文件夹路径
    target_count = 100  # 期望抽样的图像张数

    # 执行蒙特卡洛抽样
    monte_carlo_image_sampling(image_folder, target_count, output_folder)
