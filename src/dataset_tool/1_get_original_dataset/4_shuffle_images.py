import os
import random
import shutil


def shuffle_and_rename_images(image_folder, output_folder):
    # 获取文件夹中的所有图像文件
    all_images = [
        f
        for f in os.listdir(image_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 打乱图像列表并重命名
    for image in all_images:
        # 生成随机名称
        random_name = f"{random.randint(1, 1000000)}.jpg"  # 根据需要更改扩展名
        # 移动并重命名图像
        shutil.move(
            os.path.join(image_folder, image), os.path.join(output_folder, random_name)
        )

    print(f"图像已成功打乱并重命名，移动到 {output_folder}")


# 示例用法
image_folder = "shuffled_images"  # 输入文件夹路径
output_folder = "4_shuffled_images"  # 输出文件夹路径

shuffle_and_rename_images(image_folder, output_folder)
