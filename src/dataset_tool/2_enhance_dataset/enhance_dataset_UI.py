import sys
import os
import cv2
import numpy as np
import random
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QCheckBox,
    QHBoxLayout,
    QGraphicsScene,
    QGraphicsView,
)

from PyQt5.QtGui import QImage, QPixmap


class AugmentationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.original_image = None  # 保存原图
        self.current_image_path = None  # 当前预览图像路径

    def initUI(self):
        # 设置黑色主题
        self.setStyleSheet("background-color: #2d2d2d; color: white;")

        layout = QVBoxLayout()

        self.input_dir = ""
        self.output_dir = "enhance"  # 默认输出文件夹

        self.input_button = QPushButton("选择输入文件夹")
        self.input_button.clicked.connect(self.select_input_dir)
        layout.addWidget(self.input_button)

        self.output_button = QPushButton("选择输出文件夹")
        self.output_button.clicked.connect(self.select_output_dir)
        layout.addWidget(self.output_button)

        # 批量增强选项
        self.operations = {
            "scale": QCheckBox("缩放"),
            "rotate": QCheckBox("旋转"),
            "flip": QCheckBox("翻转"),
            "brightness": QCheckBox("亮度调整"),
            "translate": QCheckBox("平移"),
            "noise": QCheckBox("噪声添加"),
        }
        for op, checkbox in self.operations.items():
            layout.addWidget(checkbox)

        # 预览功能部分
        self.preview_layout = QHBoxLayout()
        self.preview_options = {}

        for op in self.operations.keys():
            checkbox = QCheckBox(op)
            checkbox.stateChanged.connect(self.update_preview)
            self.preview_options[op] = checkbox
            self.preview_layout.addWidget(checkbox)

        self.preview_button = QPushButton("预览增强效果")
        self.preview_button.clicked.connect(self.select_random_image)
        layout.addLayout(self.preview_layout)
        layout.addWidget(self.preview_button)

        self.preview_label = QLabel("预览:")
        layout.addWidget(self.preview_label)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        self.enhance_button = QPushButton("开始增强")
        self.enhance_button.clicked.connect(self.enhance_images)
        layout.addWidget(self.enhance_button)

        self.setLayout(layout)
        self.setWindowTitle("图像增强工具")
        self.show()

    def select_input_dir(self):
        self.input_dir = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        print(f"输入文件夹: {self.input_dir}")

    def select_output_dir(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        print(f"输出文件夹: {self.output_dir}")

    def augment_image(self, image, operations):
        if operations.get("scale"):
            scale_factor = random.uniform(0.5, 1.5)
            image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor)

        if operations.get("rotate"):
            angle = random.randint(0, 360)
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            image = cv2.warpAffine(image, M, (w, h))

        if operations.get("flip"):
            image = cv2.flip(image, 1)

        if operations.get("brightness"):
            brightness_change = random.randint(-50, 50)
            image = cv2.convertScaleAbs(image, alpha=1, beta=brightness_change)

        if operations.get("translate"):
            tx = random.randint(-30, 30)
            ty = random.randint(-30, 30)
            M = np.float32([[1, 0, tx], [0, 1, ty]])
            image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))

        if operations.get("noise"):
            noise = np.random.normal(0, 25, image.shape).astype(np.uint8)
            image = cv2.add(image, noise)

        return image

    def enhance_dataset(self, input_dir, output_dir, operations):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename in os.listdir(input_dir):
            if filename.endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(input_dir, filename)
                image = cv2.imread(img_path)
                augmented_image = self.augment_image(image, operations)

                output_path = os.path.join(output_dir, f"aug_{filename}")
                cv2.imwrite(output_path, augmented_image)

    def enhance_images(self):
        operations = {
            op: checkbox.isChecked() for op, checkbox in self.operations.items()
        }
        self.enhance_dataset(self.input_dir, self.output_dir, operations)

    def select_random_image(self):
        if self.input_dir:
            self.current_image_path = os.path.join(
                self.input_dir, random.choice(os.listdir(self.input_dir))
            )
            self.original_image = cv2.imread(self.current_image_path)

            self.update_preview()  # 初始化预览

    def update_preview(self):
        if self.original_image is not None:
            # 收集选择的预览选项
            preview_operations = {
                op: checkbox.isChecked()
                for op, checkbox in self.preview_options.items()
            }
            augmented_image = self.augment_image(
                self.original_image.copy(), preview_operations
            )

            height, width, channel = augmented_image.shape
            bytes_per_line = 3 * width
            qt_image = QImage(
                augmented_image.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_RGB888,
            ).rgbSwapped()
            self.scene.clear()
            self.scene.addPixmap(QPixmap.fromImage(qt_image))
            self.view.setScene(self.scene)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AugmentationApp()
    sys.exit(app.exec_())
