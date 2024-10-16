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
    QComboBox,
    QGraphicsScene,
    QGraphicsView,
)
from PyQt5.QtGui import QImage, QPixmap


class AugmentationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

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

        self.preview_button = QPushButton("预览增强效果")
        self.preview_button.clicked.connect(self.preview_image)
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
        augmented_images = []

        if operations.get("scale", False):
            scales = [0.8, 1.2]
            for scale in scales:
                h, w = image.shape[:2]
                new_h, new_w = int(h * scale), int(w * scale)
                augmented_images.append(cv2.resize(image, (new_w, new_h)))

        if operations.get("rotate", False):
            angles = [45, 90, 180, 270]
            for angle in angles:
                center = (image.shape[1] // 2, image.shape[0] // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                augmented_images.append(
                    cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
                )

        if operations.get("flip", False):
            augmented_images.append(cv2.flip(image, 1))  # 水平翻转
            augmented_images.append(cv2.flip(image, 0))  # 垂直翻转

        if operations.get("brightness", False):
            for value in [50, -50]:
                augmented_images.append(cv2.convertScaleAbs(image, alpha=1, beta=value))

        if operations.get("translate", False):
            translations = [(10, 0), (0, 10)]
            for tx, ty in translations:
                M = np.float32([[1, 0, tx], [0, 1, ty]])
                augmented_images.append(
                    cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
                )

        if operations.get("noise", False):
            noisy_image_sp = image.copy()
            num_salt = np.ceil(0.02 * image.size * 0.5)
            coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
            noisy_image_sp[coords[0], coords[1], :] = 255

            num_pepper = np.ceil(0.02 * image.size * 0.5)
            coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
            noisy_image_sp[coords[0], coords[1], :] = 0
            augmented_images.append(noisy_image_sp)

            gauss = np.random.normal(0, 1, image.shape).astype("uint8")
            augmented_images.append(cv2.add(image, gauss))

        return augmented_images

    def enhance_dataset(self, input_dir, output_dir, operations):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename in os.listdir(input_dir):
            if filename.endswith((".png", ".jpg", ".jpeg", ".bmp")):
                image_path = os.path.join(input_dir, filename)
                image = cv2.imread(image_path)

                for i in range(1):  # 每张图片增强1次
                    augmented_images = self.augment_image(image, operations)
                    for j, augmented_image in enumerate(augmented_images):
                        output_path = os.path.join(
                            output_dir,
                            f"{os.path.splitext(filename)[0]}_aug_{i}_{j}.png",
                        )
                        cv2.imwrite(output_path, augmented_image)

    def enhance_images(self):
        operations = {
            op: checkbox.isChecked() for op, checkbox in self.operations.items()
        }
        self.enhance_dataset(self.input_dir, self.output_dir, operations)

    def preview_image(self):
        if self.input_dir:
            random_image_path = os.path.join(
                self.input_dir, random.choice(os.listdir(self.input_dir))
            )
            image = cv2.imread(random_image_path)
            operations = {
                op: checkbox.isChecked() for op, checkbox in self.operations.items()
            }
            augmented_images = self.augment_image(image, operations)

            if augmented_images:
                preview_image = augmented_images[0]  # 预览第一个增强图像
                height, width, channel = preview_image.shape
                bytes_per_line = 3 * width
                qt_image = QImage(
                    preview_image.data,
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
