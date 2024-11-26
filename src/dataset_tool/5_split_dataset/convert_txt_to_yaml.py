import yaml


def convert_txt_to_yaml(txt_file, yaml_file, dataset_path):
    with open(txt_file, "r") as file:
        # 读取类别名称
        categories = [line.strip() for line in file if line.strip()]

    # 创建 YAML 数据结构
    data = {
        "path": dataset_path,
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",  # 可选
        "names": {
            i: category for i, category in enumerate(categories)
        },  # 使用枚举生成类别字典
    }

    # 写入 YAML 文件
    with open(yaml_file, "w") as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False)


# 使用示例
txt_file = "output_file/classification.txt"  # 输入的文本文件名
yaml_file = "dataset.yaml"  # 输出的 YAML 文件名
dataset_path = (
    "F:/16_AI_Workspace/ultralytics/datasets/2024_10_13_13_40"  # 数据集根目录
)

convert_txt_to_yaml(txt_file, yaml_file, dataset_path)
