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
)


class AugmentationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
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
            # 添加椒盐噪声
            noisy_image_sp = image.copy()
            num_salt = np.ceil(0.02 * image.size * 0.5)
            coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
            noisy_image_sp[coords[0], coords[1], :] = 255

            num_pepper = np.ceil(0.02 * image.size * 0.5)
            coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
            noisy_image_sp[coords[0], coords[1], :] = 0
            augmented_images.append(noisy_image_sp)

            # 添加高斯噪声
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AugmentationApp()
    sys.exit(app.exec_())
