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
    QSlider,
    QProgressBar,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, input_dir, output_dir, operations, sliders):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.operations = operations
        self.sliders = sliders

    def augment_image(self, image):
        if self.operations.get("scale"):
            scale_factor = self.sliders["scale"].value() / 100.0
            image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor)

        if self.operations.get("rotate"):
            angle = self.sliders["rotate"].value()
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            image = cv2.warpAffine(image, M, (w, h))

        if self.operations.get("flip"):
            image = cv2.flip(image, 1)

        if self.operations.get("brightness"):
            brightness_change = self.sliders["brightness"].value() - 50
            image = cv2.convertScaleAbs(image, alpha=1, beta=brightness_change)

        if self.operations.get("translate"):
            tx = self.sliders["translate"].value() - 50
            ty = self.sliders["translate"].value() - 50
            M = np.float32([[1, 0, tx], [0, 1, ty]])
            image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))

        if self.operations.get("noise"):
            noise_strength = max(self.sliders["noise"].value() / 100.0, 0)
            noise = np.random.normal(0, 25 * noise_strength, image.shape).astype(
                np.uint8
            )
            image = cv2.add(image, noise)

        return image

    def enhance_dataset(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        input_files = [
            f
            for f in os.listdir(self.input_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        for i, filename in enumerate(input_files):
            file_path = os.path.join(self.input_dir, filename)
            image = cv2.imread(file_path)

            if image is None:
                print(f"Error reading image {file_path}")
                continue

            for j in range(5):
                augmented_image = self.augment_image(image.copy())
                output_path = os.path.join(self.output_dir, f"aug_{j}_{filename}")
                cv2.imwrite(output_path, augmented_image)

            self.progress.emit(int((i + 1) / len(input_files) * 100))

        self.finished.emit()


class AugmentationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.sliders = {}
        self.initUI()
        self.original_image = None
        self.current_image_path = None

    def initUI(self):
        self.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout = QVBoxLayout()

        self.input_dir = ""
        self.output_dir = "enhance"

        self.input_button = QPushButton("选择输入文件夹")
        self.input_button.clicked.connect(self.select_input_dir)
        layout.addWidget(self.input_button)

        self.output_button = QPushButton("选择输出文件夹")
        self.output_button.clicked.connect(self.select_output_dir)
        layout.addWidget(self.output_button)

        self.operations_layout = QHBoxLayout()
        self.operations = {
            "scale": QCheckBox("缩放"),
            "rotate": QCheckBox("旋转"),
            "flip": QCheckBox("翻转"),
            "brightness": QCheckBox("亮度调整"),
            "translate": QCheckBox("平移"),
            "noise": QCheckBox("噪声添加"),
        }
        for op, checkbox in self.operations.items():
            self.operations_layout.addWidget(checkbox)

        layout.addLayout(self.operations_layout)

        self.preview_label = QLabel("预览选项:")
        layout.addWidget(self.preview_label)

        self.preview_layout = QVBoxLayout()
        self.preview_options = {}

        for op in self.operations.keys():
            checkbox = QCheckBox(op)
            checkbox.stateChanged.connect(self.update_preview)
            self.preview_options[op] = checkbox
            self.preview_layout.addWidget(checkbox)

            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(50)
            self.preview_layout.addWidget(QLabel(f"{op} 参数:"))
            self.preview_layout.addWidget(slider)
            self.sliders[op] = slider

            slider_value_label = QLabel("值: 50")
            self.preview_layout.addWidget(slider_value_label)
            slider.valueChanged.connect(
                lambda value, label=slider_value_label: label.setText(f"值: {value}")
            )

        # 添加噪声强度滑动条
        self.preview_layout.addWidget(QLabel("噪声强度:"))
        noise_slider = QSlider(Qt.Horizontal)
        noise_slider.setMinimum(0)
        noise_slider.setMaximum(50)
        noise_slider.setValue(2)
        self.preview_layout.addWidget(noise_slider)
        self.sliders["noise"] = noise_slider

        noise_value_label = QLabel("值: 2")
        self.preview_layout.addWidget(noise_value_label)
        noise_slider.valueChanged.connect(
            lambda value: noise_value_label.setText(f"值: {value}")
        )

        self.preview_button = QPushButton("预览增强效果")
        self.preview_button.clicked.connect(self.select_random_image)
        self.preview_layout.addWidget(self.preview_button)

        self.preview_label_result = QLabel("预览:")
        self.preview_layout.addWidget(self.preview_label_result)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.preview_layout.addWidget(self.view)

        layout.addLayout(self.preview_layout)

        self.enhance_button = QPushButton("开始增强")
        self.enhance_button.clicked.connect(self.start_enhancement)
        layout.addWidget(self.enhance_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle("图像增强工具")
        self.show()

    def select_input_dir(self):
        self.input_dir = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        print(f"输入文件夹: {self.input_dir}")

    def select_output_dir(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        print(f"输出文件夹: {self.output_dir}")

    def augment_image_for_preview(self, image, operations):
        if operations.get("scale"):
            scale_factor = self.sliders["scale"].value() / 100.0
            image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor)

        if operations.get("rotate"):
            angle = self.sliders["rotate"].value()
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            image = cv2.warpAffine(image, M, (w, h))

        if operations.get("flip"):
            image = cv2.flip(image, 1)

        if operations.get("brightness"):
            brightness_change = self.sliders["brightness"].value() - 50
            image = cv2.convertScaleAbs(image, alpha=1, beta=brightness_change)

        if operations.get("translate"):
            tx = self.sliders["translate"].value() - 50
            ty = self.sliders["translate"].value() - 50
            M = np.float32([[1, 0, tx], [0, 1, ty]])
            image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))

        if operations.get("noise"):
            noise_strength = max(self.sliders["noise"].value() / 100.0, 0)
            noise = np.random.normal(0, 25 * noise_strength, image.shape).astype(
                np.uint8
            )
            image = cv2.add(image, noise)

        return image

    def select_random_image(self):
        if self.input_dir:
            self.current_image_path = os.path.join(
                self.input_dir, random.choice(os.listdir(self.input_dir))
            )
            self.original_image = cv2.imread(self.current_image_path)

            if self.original_image is None:
                print(f"错误：无法读取图像 {self.current_image_path}")
                return

            print(f"选择随机图像: {self.current_image_path}")
            self.update_preview()

    def update_preview(self):
        if self.original_image is not None:
            preview_operations = {
                op: checkbox.isChecked()
                for op, checkbox in self.preview_options.items()
            }
            augmented_image = self.augment_image_for_preview(
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

    def start_enhancement(self):
        if not self.input_dir:
            print("错误：未选择输入文件夹")
            return
        if not os.path.exists(self.input_dir):
            print(f"错误：输入文件夹不存在: {self.input_dir}")
            return

        if not self.output_dir:
            print("错误：未选择输出文件夹")
            return

        operations = {
            op: checkbox.isChecked() for op, checkbox in self.operations.items()
        }
        print(f"开始增强，操作: {operations}")

        self.thread = QThread()
        self.worker = Worker(self.input_dir, self.output_dir, operations, self.sliders)
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.started.connect(self.worker.enhance_dataset)
        self.worker.progress.connect(self.progress_bar.setValue)

        self.thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AugmentationApp()
    sys.exit(app.exec_())
