import os
from PIL import Image
from tqdm import tqdm  # 导入 tqdm 库


def adjust_images_in_folder(input_folder, output_folder, new_size):
    """
    批量调整文件夹中的图像大小并保存到输出文件夹。

    :param input_folder: 输入图像文件夹路径
    :param output_folder: 输出图像文件夹路径
    :param new_size: 新的图像大小，格式为 (宽度, 高度)
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取所有支持的图像文件
    image_files = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))
    ]

    # 使用 tqdm 显示进度条
    for filename in tqdm(image_files, desc="处理图像", unit="个"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # 打开图像并调整大小
        with Image.open(input_path) as img:
            resized_img = img.resize(new_size)
            resized_img.save(output_path)


if __name__ == "__main__":
    # 输入图像文件夹路径
    input_folder_path = "1_test"  # 替换为你的输入文件夹路径

    # 输出图像文件夹路径
    output_folder_path = "output_file/6_convert_image_size"  # 替换为你的输出文件夹路径

    # 新的图像大小
    new_image_size = (640, 480)  # 640x480 像素

    # 调整图像
    adjust_images_in_folder(input_folder_path, output_folder_path, new_image_size)
