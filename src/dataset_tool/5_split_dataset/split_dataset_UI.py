import os
import shutil
import random
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QFileDialog,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QWidget,
    QApplication,
)


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

    # 获取所有标签文件，仅选择以 .txt 结尾的文件
    total_txt = [f for f in os.listdir(txt_dir) if f.endswith(".txt")]

    # 检查是否没有有效的标签文件
    if not total_txt:
        QtWidgets.QMessageBox.critical(
            None, "错误", "标签文件夹中没有有效的标签文件（.txt）"
        )
        return

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

    # 复制文件到相应的目录，处理中文路径
    for txt_file in train_files:
        img_file = txt_file.replace(".txt", ".png")
        shutil.copy(
            os.path.abspath(os.path.join(image_dir, img_file)),
            os.path.abspath(os.path.join(img_train_path, img_file)),
        )
        shutil.copy(
            os.path.abspath(os.path.join(txt_dir, txt_file)),
            os.path.abspath(os.path.join(label_train_path, txt_file)),
        )

    for txt_file in val_files:
        img_file = txt_file.replace(".txt", ".png")
        shutil.copy(
            os.path.abspath(os.path.join(image_dir, img_file)),
            os.path.abspath(os.path.join(img_val_path, img_file)),
        )
        shutil.copy(
            os.path.abspath(os.path.join(txt_dir, txt_file)),
            os.path.abspath(os.path.join(label_val_path, txt_file)),
        )

    for txt_file in test_files:
        img_file = txt_file.replace(".txt", ".png")
        shutil.copy(
            os.path.abspath(os.path.join(image_dir, img_file)),
            os.path.abspath(os.path.join(img_test_path, img_file)),
        )
        shutil.copy(
            os.path.abspath(os.path.join(txt_dir, txt_file)),
            os.path.abspath(os.path.join(label_test_path, txt_file)),
        )


class SplitDatasetApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口布局
        layout = QVBoxLayout()

        # GitHub风格字体和颜色
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

        # Train, Val, Test Percentages
        self.trainLabel = QLabel("训练集百分比:")
        self.trainInput = QLineEdit("0.7")
        self.valLabel = QLabel("验证集百分比:")
        self.valInput = QLineEdit("0.15")
        self.testLabel = QLabel("测试集百分比:")
        self.testInput = QLineEdit("0.15")

        # Start button
        self.startButton = QPushButton("开始划分数据集")
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

        layout.addWidget(self.trainLabel)
        layout.addWidget(self.trainInput)

        layout.addWidget(self.valLabel)
        layout.addWidget(self.valInput)

        layout.addWidget(self.testLabel)
        layout.addWidget(self.testInput)

        layout.addWidget(self.startButton)

        self.setLayout(layout)
        self.setWindowTitle("数据集划分工具 - GitHub 风格")
        self.setGeometry(300, 300, 400, 300)

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

    def start_splitting(self):
        image_dir = self.imageDirInput.text()
        txt_dir = self.txtDirInput.text()
        save_dir = self.saveDirInput.text()
        train_percent = float(self.trainInput.text())
        val_percent = float(self.valInput.text())
        test_percent = float(self.testInput.text())

        if train_percent + val_percent + test_percent != 1.0:
            QtWidgets.QMessageBox.critical(
                self, "错误", "训练、验证、测试集百分比之和必须等于1"
            )
            return

        split_dataset(
            image_dir, txt_dir, save_dir, train_percent, val_percent, test_percent
        )
        QtWidgets.QMessageBox.information(self, "完成", "数据集划分完成")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = SplitDatasetApp()
    window.show()
    sys.exit(app.exec_())
