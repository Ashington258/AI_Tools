import os
from PIL import Image
from tqdm import tqdm  # 导入 tqdm 库以显示进度条


def convert_jpg_to_png(input_folder, output_folder):
    """
    批量将 JPG 图像转换为 PNG 格式并保存到输出文件夹。

    :param input_folder: 输入 JPG 图像文件夹路径
    :param output_folder: 输出 PNG 图像文件夹路径
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取所有 JPG 文件
    jpg_files = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith(".jpg") or f.lower().endswith(".jpeg")
    ]

    # 使用 tqdm 显示进度条
    for filename in tqdm(jpg_files, desc="转换图像", unit="个"):
        input_path = os.path.join(input_folder, filename)

        # 构造输出文件名
        output_filename = os.path.splitext(filename)[0] + ".png"
        output_path = os.path.join(output_folder, output_filename)

        # 打开 JPG 图像并转换为 PNG
        with Image.open(input_path) as img:
            img.convert("RGBA")  # 确保图像在转换时处理透明度
            img.save(output_path, "PNG")


if __name__ == "__main__":
    # 输入 JPG 图像文件夹路径
    input_folder_path = "output_file/test/image"  # 替换为你的输入文件夹路径

    # 输出 PNG 图像文件夹路径
    output_folder_path = "output_file/7_jpg2png"  # 替换为你的输出文件夹路径

    # 执行转换
    convert_jpg_to_png(input_folder_path, output_folder_path)
