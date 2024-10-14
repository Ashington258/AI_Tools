import json
import numpy as np
import cv2
import os


# 读取 JSON 文件
def load_json(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    return data


# 创建掩码图像
def create_mask(json_data, image_shape):
    mask = np.zeros(
        image_shape[:2], dtype=np.uint8
    )  # 创建与原图像大小相同的黑色掩码图像

    for shape in json_data["shapes"]:
        if shape["shape_type"] == "polygon":
            points = np.array(shape["points"], dtype=np.int32)
            cv2.fillPoly(mask, [points], color=255)  # 用白色填充多边形

    return mask


# 主函数：读取 JSON 和原图像，生成掩码
def main(json_path, image_dir, save_mask_path):
    # 读取 JSON 文件数据
    json_data = load_json(json_path)

    # 读取原始图像
    image_path = os.path.join(image_dir, json_data["imagePath"])
    image = cv2.imread(image_path)

    if image is None:
        print(f"无法读取图像：{image_path}")
        return

    # 根据 JSON 标注数据创建掩码
    mask = create_mask(json_data, image.shape)

    # 保存生成的掩码图像
    cv2.imwrite(save_mask_path, mask)
    print(f"掩码图像已保存至：{save_mask_path}")


# 示例使用
json_file_path = "F:/0.Temporary_Project/Lab/generate_mask/4.json"
image_directory = "F:/0.Temporary_Project/Lab/generate_mask"
save_mask_file = "path_to_save_mask.png"

main(json_file_path, image_directory, save_mask_file)
