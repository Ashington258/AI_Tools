import os
import random
import shutil


def monte_carlo_image_sampling(image_folder, sample_ratio, output_folder):
    # 获取文件夹中的所有图像文件
    all_images = [
        f
        for f in os.listdir(image_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    # 计算样本大小
    sample_size = int(len(all_images) * sample_ratio)

    # 随机抽样图像
    sampled_images = random.sample(all_images, sample_size)

    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 复制抽样的图像到输出文件夹，并显示进度
    for i, image in enumerate(sampled_images):
        shutil.copy(os.path.join(image_folder, image), output_folder)
        # 显示进度
        print(f"复制中: {i + 1}/{sample_size} ({((i + 1) / sample_size) * 100:.2f}%)")

    print(f"抽样完成，已复制 {sample_size} 张图像到 {output_folder}")


# 示例用法
image_folder = "dataset/new"
output_folder = "3_monte_carlo_sampling"
sample_ratio = 0.1  # 10%

monte_carlo_image_sampling(image_folder, sample_ratio, output_folder)
