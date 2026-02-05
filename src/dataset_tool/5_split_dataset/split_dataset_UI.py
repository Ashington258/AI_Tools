"""YOLO 数据集划分工具

功能说明：
将标注好的图像数据集按指定比例划分为训练集(train)、验证集(val)和测试集(test)，
并自动生成 YOLO 格式的 dataset.yaml 配置文件。

主要特性：
- 图形化界面操作，简单易用
- 支持自定义训练/验证/测试集比例
- 自动匹配图像和标签文件
- 生成标准 YOLO 格式的目录结构
- 自动生成 dataset.yaml 配置文件

目录结构：
输出目录/
├── images/
│   ├── train/    # 训练集图像
│   ├── val/      # 验证集图像
│   └── test/     # 测试集图像
├── labels/
│   ├── train/    # 训练集标签
│   ├── val/      # 验证集标签
│   └── test/     # 测试集标签
└── dataset.yaml  # YOLO 配置文件
"""

import os
import shutil
import random
import yaml
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QFileDialog,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QWidget,
    QApplication,
)


def mkdir(path):
    """创建目录（如果不存在）

    Args:
        path: 要创建的目录路径
    """
    if not os.path.exists(path):
        os.makedirs(path)


def generate_yaml(txt_file, save_dir):
    """生成 YOLO 格式的 dataset.yaml 配置文件

    Args:
        txt_file: 类别文件路径，每行一个类别名称
        save_dir: 数据集保存目录

    YAML 文件格式：
        path: 数据集根目录
        train: 训练集相对路径
        val: 验证集相对路径
        test: 测试集相对路径
        names: {类别ID: 类别名称} 字典
    """
    # 使用 os.path.normpath 确保路径为系统标准格式（Windows/Linux 兼容）
    normalized_save_dir = os.path.normpath(save_dir)

    yaml_file = os.path.join(normalized_save_dir, "dataset.yaml")

    # 读取类别文件，每行一个类别名称
    try:
        with open(txt_file, "r", encoding="utf-8") as file:
            categories = [line.strip() for line in file if line.strip()]
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "错误", f"读取类别文件失败: {e}")
        return

    # 构建 YAML 数据结构
    yaml_data = {
        "path": normalized_save_dir,  # 数据集根目录（绝对路径）
        "train": "images/train",  # 训练集图像相对路径
        "val": "images/val",  # 验证集图像相对路径
        "test": "images/test",  # 测试集图像相对路径
        "names": {
            i: category for i, category in enumerate(categories)
        },  # 类别映射 {0: 'class1', 1: 'class2', ...}
    }

    try:
        with open(yaml_file, "w", encoding="utf-8") as file:
            # 将数据写入 YAML 文件，避免转义
            yaml.dump(
                yaml_data,
                file,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "错误", f"生成 YAML 文件失败: {e}")
        return

    QtWidgets.QMessageBox.information(None, "完成", "YAML 文件生成成功！")


def split_dataset(
    image_dir, txt_dir, save_dir, train_percent, val_percent, test_percent
):
    """将数据集按比例划分为训练集、验证集和测试集

    Args:
        image_dir: 原始图像文件夹路径
        txt_dir: 标签文件夹路径（YOLO 格式 .txt 文件）
        save_dir: 输出数据集保存路径
        train_percent: 训练集比例（0-1）
        val_percent: 验证集比例（0-1）
        test_percent: 测试集比例（0-1）

    工作流程：
        1. 创建标准 YOLO 目录结构
        2. 获取所有标签文件
        3. 按比例随机划分数据集
        4. 复制图像和标签到对应目录
    """
    # 1. 创建保存数据集的目录结构
    mkdir(save_dir)
    # 定义 YOLO 标准目录结构
    images_dir = os.path.join(save_dir, "images")  # 图像根目录
    labels_dir = os.path.join(save_dir, "labels")  # 标签根目录

    # 图像子目录
    img_train_path = os.path.join(images_dir, "train")
    img_val_path = os.path.join(images_dir, "val")
    img_test_path = os.path.join(images_dir, "test")

    # 标签子目录
    label_train_path = os.path.join(labels_dir, "train")
    label_val_path = os.path.join(labels_dir, "val")
    label_test_path = os.path.join(labels_dir, "test")

    # 批量创建所有必需的文件夹
    for path in [
        img_train_path,
        img_val_path,
        img_test_path,
        label_train_path,
        label_val_path,
        label_test_path,
    ]:
        mkdir(path)

    # 2. 支持的图像格式（可根据需要扩展）
    image_extensions = [".png", ".jpg", ".jpeg"]

    # 获取所有标签文件（YOLO 格式 .txt 文件）
    total_txt = [f for f in os.listdir(txt_dir) if f.endswith(".txt")]

    # 验证标签文件是否存在
    if not total_txt:
        QtWidgets.QMessageBox.critical(
            None, "错误", "标签文件夹中没有有效的标签文件（.txt）"
        )
        return

    num_txt = len(total_txt)

    # 3. 根据比例计算各数据集的样本数量
    num_train = int(num_txt * train_percent)  # 训练集数量
    num_val = int(num_txt * val_percent)  # 验证集数量
    num_test = num_txt - num_train - num_val  # 测试集数量（剩余全部）

    # 4. 随机划分数据集（无放回抽样，确保数据不重复）
    train_files = random.sample(total_txt, num_train)  # 随机抽取训练集
    remaining_files = [f for f in total_txt if f not in train_files]  # 剩余文件
    val_files = random.sample(remaining_files, num_val)  # 从剩余中抽取验证集
    test_files = [
        f for f in remaining_files if f not in val_files
    ]  # 剩余全部作为测试集

    # 输出划分结果统计
    print(
        f"训练集数量: {len(train_files)}, 验证集数量: {len(val_files)}, 测试集数量: {len(test_files)}"
    )

    # 5. 定义文件复制函数
    def copy_files(txt_files, img_path, label_path):
        """复制图像和标签文件到指定目录

        Args:
            txt_files: 标签文件列表
            img_path: 图像目标目录
            label_path: 标签目标目录
        """
        for txt_file in txt_files:
            # 获取标签文件的完整路径
            txt_full_path = os.path.abspath(os.path.join(txt_dir, txt_file))

            # 根据标签文件名查找对应的图像文件（支持多种格式）
            img_file = None
            for ext in image_extensions:
                potential_img_file = os.path.join(
                    image_dir, txt_file.replace(".txt", ext)
                )
                if os.path.exists(potential_img_file):
                    img_file = potential_img_file
                    break

            # 如果找不到对应图像，跳过该标签文件
            if img_file is None:
                print(f"警告：未找到对应的图像文件: {txt_file}")
                continue

            # 复制图像和标签文件到目标目录
            shutil.copy(img_file, os.path.join(img_path, os.path.basename(img_file)))
            shutil.copy(txt_full_path, os.path.join(label_path, txt_file))

    # 6. 批量复制训练集、验证集和测试集文件
    print("正在复制训练集...")
    copy_files(train_files, img_train_path, label_train_path)
    print("正在复制验证集...")
    copy_files(val_files, img_val_path, label_val_path)
    print("正在复制测试集...")
    copy_files(test_files, img_test_path, label_test_path)
    print("文件复制完成！")


class SplitDatasetApp(QWidget):
    """YOLO 数据集划分工具的图形界面类

    提供友好的图形界面，用于：
    - 选择图像和标签文件夹
    - 设置数据集划分比例
    - 选择类别文件
    - 执行数据集划分和 YAML 生成
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """初始化用户界面"""
        # 创建垂直布局
        layout = QVBoxLayout()

        # 设置深色主题样式（GitHub 风格）
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2d2d2d;
                color: white;
                font-family: Arial;
            }
            QLineEdit, QPushButton {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #3c3c3c;
                padding: 5px;
            }
            QPushButton {
                border: 1px solid #ffffff;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """
        )

        # Image directory
        self.imageDirLabel = QLabel("选择图片文件夹:")
        self.imageDirInput = QLineEdit()
        self.imageDirButton = QPushButton("浏览")
        self.imageDirButton.clicked.connect(self.browse_image_dir)

        # Txt directory
        self.txtDirLabel = QLabel("选择标签文件夹:")
        self.txtDirInput = QLineEdit()
        self.txtDirButton = QPushButton("浏览")
        self.txtDirButton.clicked.connect(self.browse_txt_dir)

        # Save directory
        self.saveDirLabel = QLabel("选择保存文件夹:")
        self.saveDirInput = QLineEdit()
        self.saveDirButton = QPushButton("浏览")
        self.saveDirButton.clicked.connect(self.browse_save_dir)

        # Class file
        self.classFileLabel = QLabel("选择类别文件:")
        self.classFileInput = QLineEdit()
        self.classFileButton = QPushButton("浏览")
        self.classFileButton.clicked.connect(self.browse_class_file)

        # Train, Val, Test Percentages
        self.trainLabel = QLabel("训练集百分比:")
        self.trainInput = QLineEdit("0.7")
        self.valLabel = QLabel("验证集百分比:")
        self.valInput = QLineEdit("0.15")
        self.testLabel = QLabel("测试集百分比:")
        self.testInput = QLineEdit("0.15")

        # Start button
        self.startButton = QPushButton("开始划分数据集并生成 YAML")
        self.startButton.clicked.connect(self.start_splitting)

        # 将组件添加到布局中
        layout.addWidget(self.imageDirLabel)
        layout.addWidget(self.imageDirInput)
        layout.addWidget(self.imageDirButton)

        layout.addWidget(self.txtDirLabel)
        layout.addWidget(self.txtDirInput)
        layout.addWidget(self.txtDirButton)

        layout.addWidget(self.saveDirLabel)
        layout.addWidget(self.saveDirInput)
        layout.addWidget(self.saveDirButton)

        layout.addWidget(self.classFileLabel)
        layout.addWidget(self.classFileInput)
        layout.addWidget(self.classFileButton)

        layout.addWidget(self.trainLabel)
        layout.addWidget(self.trainInput)

        layout.addWidget(self.valLabel)
        layout.addWidget(self.valInput)

        layout.addWidget(self.testLabel)
        layout.addWidget(self.testInput)

        layout.addWidget(self.startButton)

        self.setLayout(layout)
        self.setWindowTitle("YOLO训练集数据集划分工具")
        self.setGeometry(300, 300, 400, 350)

    def browse_image_dir(self):
        dir_ = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if dir_:
            self.imageDirInput.setText(dir_)

    def browse_txt_dir(self):
        dir_ = QFileDialog.getExistingDirectory(self, "选择标签文件夹")
        if dir_:
            self.txtDirInput.setText(dir_)

    def browse_save_dir(self):
        dir_ = QFileDialog.getExistingDirectory(self, "选择保存文件夹")
        if dir_:
            self.saveDirInput.setText(dir_)

    def browse_class_file(self):
        file_, _ = QFileDialog.getOpenFileName(
            self, "选择类别文件", "", "文本文件 (*.txt)"
        )
        if file_:
            self.classFileInput.setText(file_)

    def start_splitting(self):
        image_dir = self.imageDirInput.text()
        txt_dir = self.txtDirInput.text()
        save_dir = self.saveDirInput.text()
        class_file = self.classFileInput.text()
        train_percent = float(self.trainInput.text())
        val_percent = float(self.valInput.text())
        test_percent = float(self.testInput.text())

        if not class_file:
            QtWidgets.QMessageBox.critical(self, "错误", "请选择类别文件")
            return

        if train_percent + val_percent + test_percent != 1.0:
            QtWidgets.QMessageBox.critical(
                self, "错误", "训练、验证、测试集百分比之和必须等于1"
            )
            return

        split_dataset(
            image_dir, txt_dir, save_dir, train_percent, val_percent, test_percent
        )
        generate_yaml(class_file, save_dir)
        QtWidgets.QMessageBox.information(
            self, "完成", "数据集划分和 YAML 文件生成完成！"
        )


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = SplitDatasetApp()
    window.show()
    sys.exit(app.exec_())
