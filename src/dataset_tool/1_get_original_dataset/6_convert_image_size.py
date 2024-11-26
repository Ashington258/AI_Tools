import os
from PIL import Image


def adjust_images_in_folder(input_folder, output_folder, new_size):
    """
    批量调整文件夹中的图像大小并保存到输出文件夹。

    :param input_folder: 输入图像文件夹路径
    :param output_folder: 输出图像文件夹路径
    :param new_size: 新的图像大小，格式为 (宽度, 高度)
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(
            (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        ):  # 支持的图像格式
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # 打开图像并调整大小
            with Image.open(input_path) as img:
                resized_img = img.resize(new_size)
                resized_img.save(output_path)
                print(f"已调整并保存图像: {output_path}")


if __name__ == "__main__":
    # 输入图像文件夹路径
    input_folder_path = (
        "output_file/2024_11_26_22_06/dataset/all"  # 替换为你的输入文件夹路径
    )

    # 输出图像文件夹路径
    output_folder_path = "output_file/6_convert_image_size"  # 替换为你的输出文件夹路径

    # 新的图像大小
    new_image_size = (640, 480)  # 640x480 像素

    # 调整图像
    adjust_images_in_folder(input_folder_path, output_folder_path, new_image_size)
