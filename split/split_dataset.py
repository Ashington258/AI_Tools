import os
import shutil
import random
import argparse


# 创建目录
def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def split_dataset(
    image_dir, txt_dir, save_dir, train_percent, val_percent, test_percent
):
    # 创建保存数据集的目录结构
    mkdir(save_dir)
    images_dir = os.path.join(save_dir, "images")
    labels_dir = os.path.join(save_dir, "labels")

    img_train_path = os.path.join(images_dir, "train")
    img_val_path = os.path.join(images_dir, "val")
    img_test_path = os.path.join(images_dir, "test")

    label_train_path = os.path.join(labels_dir, "train")
    label_val_path = os.path.join(labels_dir, "val")
    label_test_path = os.path.join(labels_dir, "test")

    # 创建相应的文件夹
    for path in [
        img_train_path,
        img_val_path,
        img_test_path,
        label_train_path,
        label_val_path,
        label_test_path,
    ]:
        mkdir(path)

    # 获取所有标签文件
    total_txt = [f for f in os.listdir(txt_dir) if f.endswith(".txt")]
    num_txt = len(total_txt)

    # 根据比例计算数量
    num_train = int(num_txt * train_percent)
    num_val = int(num_txt * val_percent)
    num_test = num_txt - num_train - num_val

    # 随机划分数据集
    train_files = random.sample(total_txt, num_train)
    remaining_files = [f for f in total_txt if f not in train_files]
    val_files = random.sample(remaining_files, num_val)
    test_files = [f for f in remaining_files if f not in val_files]

    print(
        f"训练集数量: {len(train_files)}, 验证集数量: {len(val_files)}, 测试集数量: {len(test_files)}"
    )

    # 复制文件到相应的目录
    for txt_file in train_files:
        img_file = txt_file.replace(".txt", ".png")
        shutil.copy(
            os.path.join(image_dir, img_file), os.path.join(img_train_path, img_file)
        )
        shutil.copy(
            os.path.join(txt_dir, txt_file), os.path.join(label_train_path, txt_file)
        )

    for txt_file in val_files:
        img_file = txt_file.replace(".txt", ".png")
        shutil.copy(
            os.path.join(image_dir, img_file), os.path.join(img_val_path, img_file)
        )
        shutil.copy(
            os.path.join(txt_dir, txt_file), os.path.join(label_val_path, txt_file)
        )

    for txt_file in test_files:
        img_file = txt_file.replace(".txt", ".png")
        shutil.copy(
            os.path.join(image_dir, img_file), os.path.join(img_test_path, img_file)
        )
        shutil.copy(
            os.path.join(txt_dir, txt_file), os.path.join(label_test_path, txt_file)
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split dataset into train, val, and test sets"
    )
    parser.add_argument(
        "--image-dir", type=str, required=True, help="Directory containing the images"
    )
    parser.add_argument(
        "--txt-dir",
        type=str,
        required=True,
        help="Directory containing the label files",
    )
    parser.add_argument(
        "--save-dir",
        type=str,
        required=True,
        help="Directory to save the split dataset",
    )
    parser.add_argument(
        "--train-percent",
        type=float,
        default=0.7,
        help="Percentage of data for training set",
    )
    parser.add_argument(
        "--val-percent",
        type=float,
        default=0.15,
        help="Percentage of data for validation set",
    )
    parser.add_argument(
        "--test-percent",
        type=float,
        default=0.15,
        help="Percentage of data for test set",
    )

    args = parser.parse_args()

    # 确保比例之和为 1
    if args.train_percent + args.val_percent + args.test_percent != 1:
        raise ValueError("Train, validation, and test percentages must sum to 1.")

    split_dataset(
        args.image_dir,
        args.txt_dir,
        args.save_dir,
        args.train_percent,
        args.val_percent,
        args.test_percent,
    )
