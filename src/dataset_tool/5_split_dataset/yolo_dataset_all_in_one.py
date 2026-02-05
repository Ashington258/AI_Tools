"""YOLO 数据集一键整理与划分工具

功能说明：
从混合文件夹（图像和标签在同一目录）中自动读取数据，
按指定比例划分为训练集/验证集/测试集，
并生成标准 YOLO 格式的目录结构和 dataset.yaml 配置文件。

主要特性：
- 一键完成：从混合文件夹到标准 YOLO 数据集
- 自动匹配图像和标签文件
- 支持自定义训练/验证/测试集比例
- 生成标准 YOLO 目录结构
- 自动生成 dataset.yaml 配置文件
- 图形化界面，操作简单

工作流程：
1. 扫描混合文件夹，识别图像和标签
2. 匹配图像和标签文件
3. 按比例随机划分数据集
4. 复制到标准 YOLO 目录结构
5. 生成 dataset.yaml 配置文件
"""

import os
import sys
import shutil
import random
import yaml
import subprocess
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QTextEdit,
    QProgressBar,
    QMessageBox,
    QGroupBox,
    QComboBox,
    QSpinBox,
    QCheckBox,
)
from PyQt5.QtCore import QThread, pyqtSignal, QProcess
from PyQt5.QtGui import QFont


class DatasetProcessor(QThread):
    """后台工作线程，执行数据集整理和划分"""

    progress = pyqtSignal(str)  # 进度信息
    finished = pyqtSignal(bool, str)  # 完成信号 (成功/失败, 消息)

    def __init__(
        self, source_dir, output_dir, class_file, train_ratio, val_ratio, test_ratio
    ):
        super().__init__()
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.class_file = class_file
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio

    def run(self):
        """执行完整的数据集处理流程"""
        try:
            # 步骤1: 扫描和匹配文件
            self.progress.emit("=" * 60 + "\n")
            self.progress.emit("步骤 1/4: 扫描源文件夹\n")
            self.progress.emit("=" * 60 + "\n")
            self.progress.emit(f"源文件夹: {self.source_dir}\n\n")

            image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
            label_extension = ".txt"

            image_files = {}  # {文件名(无扩展名): 完整路径}
            label_files = {}  # {文件名(无扩展名): 完整路径}

            for filename in os.listdir(self.source_dir):
                file_path = os.path.join(self.source_dir, filename)

                if os.path.isdir(file_path):
                    continue

                name_without_ext = os.path.splitext(filename)[0]
                ext = os.path.splitext(filename)[1].lower()

                if ext in image_extensions:
                    image_files[name_without_ext] = file_path
                elif ext == label_extension:
                    label_files[name_without_ext] = file_path

            self.progress.emit(f"✓ 找到 {len(image_files)} 个图像文件\n")
            self.progress.emit(f"✓ 找到 {len(label_files)} 个标签文件\n\n")

            # 匹配图像和标签
            matched_pairs = []
            for name in image_files:
                if name in label_files:
                    matched_pairs.append(
                        {
                            "name": name,
                            "image": image_files[name],
                            "label": label_files[name],
                        }
                    )

            if not matched_pairs:
                self.progress.emit("❌ 错误: 没有找到匹配的图像和标签对！\n")
                self.finished.emit(False, "没有找到匹配的图像和标签文件")
                return

            self.progress.emit(f"✓ 成功匹配 {len(matched_pairs)} 对图像和标签\n")

            # 统计未匹配的文件
            no_label = len(image_files) - len(matched_pairs)
            orphan_label = len(label_files) - len(matched_pairs)
            if no_label > 0:
                self.progress.emit(f"⚠ 警告: {no_label} 个图像没有对应标签\n")
            if orphan_label > 0:
                self.progress.emit(f"⚠ 警告: {orphan_label} 个标签没有对应图像\n")

            # 步骤2: 划分数据集
            self.progress.emit("\n" + "=" * 60 + "\n")
            self.progress.emit("步骤 2/4: 划分数据集\n")
            self.progress.emit("=" * 60 + "\n")

            total = len(matched_pairs)
            num_train = int(total * self.train_ratio)
            num_val = int(total * self.val_ratio)
            num_test = total - num_train - num_val

            self.progress.emit(f"总样本数: {total}\n")
            self.progress.emit(f"训练集: {num_train} ({self.train_ratio*100:.1f}%)\n")
            self.progress.emit(f"验证集: {num_val} ({self.val_ratio*100:.1f}%)\n")
            self.progress.emit(f"测试集: {num_test} ({self.test_ratio*100:.1f}%)\n\n")

            # 随机打乱并划分
            random.shuffle(matched_pairs)
            train_pairs = matched_pairs[:num_train]
            val_pairs = matched_pairs[num_train : num_train + num_val]
            test_pairs = matched_pairs[num_train + num_val :]

            # 步骤3: 创建目录结构并复制文件
            self.progress.emit("=" * 60 + "\n")
            self.progress.emit("步骤 3/4: 创建 YOLO 标准目录结构\n")
            self.progress.emit("=" * 60 + "\n")

            # 创建目录
            images_dir = os.path.join(self.output_dir, "images")
            labels_dir = os.path.join(self.output_dir, "labels")

            img_train = os.path.join(images_dir, "train")
            img_val = os.path.join(images_dir, "val")
            img_test = os.path.join(images_dir, "test")

            label_train = os.path.join(labels_dir, "train")
            label_val = os.path.join(labels_dir, "val")
            label_test = os.path.join(labels_dir, "test")

            for path in [
                img_train,
                img_val,
                img_test,
                label_train,
                label_val,
                label_test,
            ]:
                os.makedirs(path, exist_ok=True)

            self.progress.emit(f"✓ 创建目录结构完成\n\n")
            self.progress.emit("正在复制文件...\n")

            # 复制文件
            def copy_pairs(pairs, img_dest, label_dest, dataset_name):
                for i, pair in enumerate(pairs, 1):
                    img_name = os.path.basename(pair["image"])
                    label_name = os.path.basename(pair["label"])

                    shutil.copy2(pair["image"], os.path.join(img_dest, img_name))
                    shutil.copy2(pair["label"], os.path.join(label_dest, label_name))

                    if i % 50 == 0 or i == len(pairs):
                        self.progress.emit(f"  {dataset_name}: {i}/{len(pairs)}\n")

            copy_pairs(train_pairs, img_train, label_train, "训练集")
            copy_pairs(val_pairs, img_val, label_val, "验证集")
            copy_pairs(test_pairs, img_test, label_test, "测试集")

            self.progress.emit("\n✓ 文件复制完成\n")

            # 步骤4: 生成 YAML 配置文件
            self.progress.emit("\n" + "=" * 60 + "\n")
            self.progress.emit("步骤 4/4: 生成 dataset.yaml 配置文件\n")
            self.progress.emit("=" * 60 + "\n")

            # 读取类别文件
            try:
                with open(self.class_file, "r", encoding="utf-8") as f:
                    categories = [line.strip() for line in f if line.strip()]
            except Exception as e:
                self.progress.emit(f"❌ 读取类别文件失败: {e}\n")
                self.finished.emit(False, f"读取类别文件失败: {e}")
                return

            # 生成 YAML
            yaml_data = {
                "path": os.path.normpath(self.output_dir),
                "train": "images/train",
                "val": "images/val",
                "test": "images/test",
                "names": {i: cat for i, cat in enumerate(categories)},
            }

            yaml_file = os.path.join(self.output_dir, "dataset.yaml")
            with open(yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    yaml_data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )

            self.progress.emit(f"✓ YAML 文件已生成: {yaml_file}\n")
            self.progress.emit(f"\n类别数量: {len(categories)}\n")
            for i, cat in enumerate(categories):
                self.progress.emit(f"  {i}: {cat}\n")

            # 完成总结
            self.progress.emit("\n" + "=" * 60 + "\n")
            self.progress.emit("✓ 数据集处理完成！\n")
            self.progress.emit("=" * 60 + "\n")
            self.progress.emit(f"\n输出目录: {self.output_dir}\n")
            self.progress.emit(f"训练集: {num_train} 张\n")
            self.progress.emit(f"验证集: {num_val} 张\n")
            self.progress.emit(f"测试集: {num_test} 张\n")
            self.progress.emit(f"\n可以使用以下命令开始训练:\n")
            self.progress.emit(
                f"yolo train data={yaml_file} model=yolov8n.pt epochs=100\n"
            )

            self.finished.emit(True, f"成功处理 {total} 张图像")

        except Exception as e:
            self.progress.emit(f"\n❌ 错误: {str(e)}\n")
            self.finished.emit(False, str(e))


class YOLODatasetApp(QWidget):
    """YOLO 数据集一键整理与划分工具主窗口"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.train_process = None
        self.yaml_file_path = None
        self.initUI()

    def initUI(self):
        """初始化用户界面"""
        self.setWindowTitle("YOLO 数据集一键整理与划分工具")
        self.setGeometry(150, 150, 900, 850)

        # 深色主题
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2d2d2d;
                color: white;
                font-family: 'Microsoft YaHei', Arial;
                font-size: 10pt;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #555;
                padding: 6px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5f62;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
            }
            QGroupBox {
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                background-color: #3c3c3c;
            }
            QProgressBar::chunk {
                background-color: #0d7377;
            }
        """
        )

        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # 标题
        title = QLabel("🚀 YOLO 数据集一键整理与划分工具")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # 说明
        desc = QLabel("从混合文件夹自动整理、划分数据集，并生成 YOLO 训练配置文件")
        desc.setStyleSheet("color: #aaa; font-size: 9pt;")
        layout.addWidget(desc)

        # 输入配置组
        input_group = QGroupBox("📂 输入配置")
        input_layout = QVBoxLayout()

        # 源文件夹
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("混合数据文件夹:"))
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("选择包含图像和标签的混合文件夹...")
        source_layout.addWidget(self.source_input)
        self.source_btn = QPushButton("浏览")
        self.source_btn.clicked.connect(self.browse_source)
        source_layout.addWidget(self.source_btn)
        input_layout.addLayout(source_layout)

        # 类别文件
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("类别文件 (classes.txt):"))
        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("选择包含类别名称的文本文件...")
        class_layout.addWidget(self.class_input)
        self.class_btn = QPushButton("浏览")
        self.class_btn.clicked.connect(self.browse_class)
        class_layout.addWidget(self.class_btn)
        input_layout.addLayout(class_layout)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 输出配置组
        output_group = QGroupBox("📁 输出配置")
        output_layout = QVBoxLayout()

        # 输出文件夹
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(QLabel("输出文件夹:"))
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("选择 YOLO 数据集的保存位置...")
        output_dir_layout.addWidget(self.output_input)
        self.output_btn = QPushButton("浏览")
        self.output_btn.clicked.connect(self.browse_output)
        output_dir_layout.addWidget(self.output_btn)
        output_layout.addLayout(output_dir_layout)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 划分比例组
        ratio_group = QGroupBox("📊 数据集划分比例")
        ratio_layout = QHBoxLayout()

        ratio_layout.addWidget(QLabel("训练集:"))
        self.train_input = QLineEdit("0.7")
        self.train_input.setMaximumWidth(80)
        ratio_layout.addWidget(self.train_input)

        ratio_layout.addWidget(QLabel("验证集:"))
        self.val_input = QLineEdit("0.15")
        self.val_input.setMaximumWidth(80)
        ratio_layout.addWidget(self.val_input)

        ratio_layout.addWidget(QLabel("测试集:"))
        self.test_input = QLineEdit("0.15")
        self.test_input.setMaximumWidth(80)
        ratio_layout.addWidget(self.test_input)

        ratio_layout.addStretch()
        ratio_group.setLayout(ratio_layout)
        layout.addWidget(ratio_group)

        # 训练配置组
        train_group = QGroupBox("🎯 训练配置 (可选)")
        train_layout = QVBoxLayout()

        # 启用训练复选框
        self.enable_train_checkbox = QCheckBox("数据集处理完成后自动开始训练")
        self.enable_train_checkbox.setStyleSheet("font-weight: bold; color: #14a085;")
        self.enable_train_checkbox.stateChanged.connect(self.toggle_train_options)
        train_layout.addWidget(self.enable_train_checkbox)

        # 训练参数容器
        self.train_options_widget = QWidget()
        train_options_layout = QVBoxLayout()
        train_options_layout.setContentsMargins(20, 10, 0, 0)

        # 任务类型
        task_layout = QHBoxLayout()
        task_layout.addWidget(QLabel("任务类型:"))
        self.task_combo = QComboBox()
        self.task_combo.addItems(["detect", "segment", "classify", "pose"])
        self.task_combo.setCurrentText("segment")
        self.task_combo.setMaximumWidth(150)
        task_layout.addWidget(self.task_combo)
        task_layout.addStretch()
        train_options_layout.addLayout(task_layout)

        # 预训练模型选择
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("预训练模型:"))
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItems(
            [
                "yolo11n.pt",
                "yolo11s.pt",
                "yolo11m.pt",
                "yolo11l.pt",
                "yolo11x.pt",
                "yolov8n.pt",
                "yolov8s.pt",
                "yolov8m.pt",
                "yolov8l.pt",
                "yolov8x.pt",
            ]
        )
        self.model_combo.setCurrentText("yolo11s.pt")
        self.model_combo.setMaximumWidth(200)
        model_layout.addWidget(self.model_combo)

        # 浏览模型文件按钮
        self.browse_model_btn = QPushButton("浏览模型")
        self.browse_model_btn.clicked.connect(self.browse_model)
        self.browse_model_btn.setMaximumWidth(100)
        model_layout.addWidget(self.browse_model_btn)

        # 扫描文件夹按钮
        self.scan_models_btn = QPushButton("扫描文件夹")
        self.scan_models_btn.clicked.connect(self.scan_models_folder)
        self.scan_models_btn.setMaximumWidth(100)
        model_layout.addWidget(self.scan_models_btn)

        model_layout.addStretch()
        train_options_layout.addLayout(model_layout)

        # 训练参数
        params_layout = QHBoxLayout()

        params_layout.addWidget(QLabel("训练轮数:"))
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 1000)
        self.epochs_spin.setValue(100)
        self.epochs_spin.setMaximumWidth(100)
        params_layout.addWidget(self.epochs_spin)

        params_layout.addWidget(QLabel("图像大小:"))
        self.imgsz_combo = QComboBox()
        self.imgsz_combo.addItems(["320", "416", "640", "800", "1024", "1280"])
        self.imgsz_combo.setCurrentText("640")
        self.imgsz_combo.setMaximumWidth(100)
        params_layout.addWidget(self.imgsz_combo)

        params_layout.addWidget(QLabel("批次大小:"))
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(1, 128)
        self.batch_spin.setValue(16)
        self.batch_spin.setMaximumWidth(100)
        params_layout.addWidget(self.batch_spin)

        params_layout.addStretch()
        train_options_layout.addLayout(params_layout)

        self.train_options_widget.setLayout(train_options_layout)
        self.train_options_widget.setEnabled(False)
        train_layout.addWidget(self.train_options_widget)

        train_group.setLayout(train_layout)
        layout.addWidget(train_group)

        # 配置管理组
        config_group = QGroupBox("⚙️ 配置管理")
        config_layout = QHBoxLayout()

        self.export_config_btn = QPushButton("📤 导出配置到YAML")
        self.export_config_btn.clicked.connect(self.export_config_to_yaml)
        config_layout.addWidget(self.export_config_btn)

        self.import_config_btn = QPushButton("📥 从YAML导入配置")
        self.import_config_btn.clicked.connect(self.import_config_from_yaml)
        config_layout.addWidget(self.import_config_btn)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # 开始按钮
        self.start_btn = QPushButton("🚀 开始处理")
        self.start_btn.clicked.connect(self.start_process)
        self.start_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0d7377;
                font-size: 13pt;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
        """
        )
        layout.addWidget(self.start_btn)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)
        layout.addWidget(self.progress_bar)

        # 日志
        log_label = QLabel("📋 处理日志:")
        layout.addWidget(log_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("等待开始处理...")
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def toggle_train_options(self, state):
        """切换训练选项的启用状态"""
        self.train_options_widget.setEnabled(state == 2)

    def browse_model(self):
        """浏览预训练模型文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择预训练模型", "", "PyTorch 模型 (*.pt *.pth)"
        )
        if file_path:
            # 添加到下拉列表并选中
            model_name = os.path.basename(file_path)
            if self.model_combo.findText(model_name) == -1:
                self.model_combo.addItem(model_name)
            self.model_combo.setCurrentText(file_path)

    def scan_models_folder(self):
        """扫描文件夹中的所有.pt模型"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择模型文件夹")
        if dir_path:
            # 查找所有.pt和.pth文件
            model_files = []
            for file in os.listdir(dir_path):
                if file.endswith((".pt", ".pth")):
                    model_files.append(os.path.join(dir_path, file))

            if model_files:
                # 清空现有列表
                self.model_combo.clear()
                # 添加找到的模型
                for model_path in sorted(model_files):
                    self.model_combo.addItem(model_path)

                QMessageBox.information(
                    self,
                    "扫描完成",
                    f"找到 {len(model_files)} 个模型文件\n\n"
                    + "\n".join([os.path.basename(m) for m in model_files[:10]])
                    + (
                        f"\n... 还有 {len(model_files)-10} 个"
                        if len(model_files) > 10
                        else ""
                    ),
                )
            else:
                QMessageBox.warning(
                    self,
                    "未找到模型",
                    f"在文件夹中未找到 .pt 或 .pth 模型文件\n\n{dir_path}",
                )

    def export_config_to_yaml(self):
        """导出当前配置到YAML文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置", "yolo_config.yaml", "YAML 文件 (*.yaml *.yml)"
        )

        if not file_path:
            return

        try:
            # 收集所有配置
            config = {
                "dataset": {
                    "source_dir": self.source_input.text(),
                    "output_dir": self.output_input.text(),
                    "class_file": self.class_input.text(),
                },
                "split_ratio": {
                    "train": (
                        float(self.train_input.text())
                        if self.train_input.text()
                        else 0.7
                    ),
                    "val": (
                        float(self.val_input.text()) if self.val_input.text() else 0.15
                    ),
                    "test": (
                        float(self.test_input.text())
                        if self.test_input.text()
                        else 0.15
                    ),
                },
                "training": {
                    "enabled": self.enable_train_checkbox.isChecked(),
                    "task": self.task_combo.currentText(),
                    "model": self.model_combo.currentText(),
                    "epochs": self.epochs_spin.value(),
                    "imgsz": int(self.imgsz_combo.currentText()),
                    "batch": self.batch_spin.value(),
                },
            }

            # 写入YAML文件
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    config,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )

            QMessageBox.information(
                self, "导出成功", f"配置已成功导出到:\n\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出配置时出错:\n\n{str(e)}")

    def import_config_from_yaml(self):
        """从YAML文件导入配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入配置", "", "YAML 文件 (*.yaml *.yml)"
        )

        if not file_path:
            return

        try:
            # 读取YAML文件
            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # 应用数据集配置
            if "dataset" in config:
                dataset = config["dataset"]
                if "source_dir" in dataset:
                    self.source_input.setText(dataset["source_dir"])
                if "output_dir" in dataset:
                    self.output_input.setText(dataset["output_dir"])
                if "class_file" in dataset:
                    self.class_input.setText(dataset["class_file"])

            # 应用划分比例
            if "split_ratio" in config:
                ratio = config["split_ratio"]
                if "train" in ratio:
                    self.train_input.setText(str(ratio["train"]))
                if "val" in ratio:
                    self.val_input.setText(str(ratio["val"]))
                if "test" in ratio:
                    self.test_input.setText(str(ratio["test"]))

            # 应用训练配置
            if "training" in config:
                training = config["training"]
                if "enabled" in training:
                    self.enable_train_checkbox.setChecked(training["enabled"])
                if "task" in training:
                    self.task_combo.setCurrentText(training["task"])
                if "model" in training:
                    model_text = training["model"]
                    if self.model_combo.findText(model_text) == -1:
                        self.model_combo.addItem(model_text)
                    self.model_combo.setCurrentText(model_text)
                if "epochs" in training:
                    self.epochs_spin.setValue(training["epochs"])
                if "imgsz" in training:
                    self.imgsz_combo.setCurrentText(str(training["imgsz"]))
                if "batch" in training:
                    self.batch_spin.setValue(training["batch"])

            QMessageBox.information(
                self, "导入成功", f"配置已成功从以下文件导入:\n\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"导入配置时出错:\n\n{str(e)}")

    def browse_source(self):
        """浏览源文件夹"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择混合数据文件夹")
        if dir_path:
            self.source_input.setText(dir_path)

    def browse_class(self):
        """浏览类别文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择类别文件", "", "文本文件 (*.txt)"
        )
        if file_path:
            self.class_input.setText(file_path)

    def browse_output(self):
        """浏览输出文件夹"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if dir_path:
            self.output_input.setText(dir_path)

    def start_process(self):
        """开始处理数据集"""
        source_dir = self.source_input.text().strip()
        output_dir = self.output_input.text().strip()
        class_file = self.class_input.text().strip()

        # 验证输入
        if not source_dir:
            QMessageBox.warning(self, "警告", "请选择混合数据文件夹！")
            return

        if not output_dir:
            QMessageBox.warning(self, "警告", "请选择输出文件夹！")
            return

        if not class_file:
            QMessageBox.warning(self, "警告", "请选择类别文件！")
            return

        if not os.path.exists(source_dir):
            QMessageBox.critical(self, "错误", f"源文件夹不存在:\n{source_dir}")
            return

        if not os.path.exists(class_file):
            QMessageBox.critical(self, "错误", f"类别文件不存在:\n{class_file}")
            return

        # 验证比例
        try:
            train_ratio = float(self.train_input.text())
            val_ratio = float(self.val_input.text())
            test_ratio = float(self.test_input.text())

            if abs(train_ratio + val_ratio + test_ratio - 1.0) > 0.001:
                QMessageBox.critical(
                    self, "错误", "训练、验证、测试集比例之和必须等于 1.0！"
                )
                return

            if train_ratio < 0 or val_ratio < 0 or test_ratio < 0:
                QMessageBox.critical(self, "错误", "比例值不能为负数！")
                return

        except ValueError:
            QMessageBox.critical(self, "错误", "比例值必须是有效的数字！")
            return

        # 清空日志
        self.log_text.clear()

        # 禁用控件
        self.start_btn.setEnabled(False)
        self.source_btn.setEnabled(False)
        self.class_btn.setEnabled(False)
        self.output_btn.setEnabled(False)
        self.progress_bar.setVisible(True)

        # 创建并启动工作线程
        self.worker = DatasetProcessor(
            source_dir, output_dir, class_file, train_ratio, val_ratio, test_ratio
        )
        self.worker.progress.connect(self.update_log)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def update_log(self, message):
        """更新日志"""
        self.log_text.insertPlainText(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def on_finished(self, success, message):
        """处理完成"""
        # 恢复控件
        self.start_btn.setEnabled(True)
        self.source_btn.setEnabled(True)
        self.class_btn.setEnabled(True)
        self.output_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        # 显示结果
        if success:
            # 保存 YAML 文件路径
            self.yaml_file_path = os.path.join(self.output_input.text(), "dataset.yaml")

            # 检查是否需要开始训练
            if self.enable_train_checkbox.isChecked():
                reply = QMessageBox.question(
                    self,
                    "开始训练",
                    f"数据集处理完成！\n\n{message}\n\n是否立即开始训练？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )

                if reply == QMessageBox.Yes:
                    self.start_training()
                else:
                    QMessageBox.information(
                        self,
                        "完成",
                        f"数据集处理完成！\n\n{message}\n\n"
                        f"输出目录: {self.output_input.text()}",
                    )
            else:
                QMessageBox.information(
                    self,
                    "完成",
                    f"数据集处理完成！\n\n{message}\n\n"
                    f"输出目录: {self.output_input.text()}",
                )
        else:
            QMessageBox.critical(self, "错误", f"处理失败！\n\n{message}")

    def start_training(self):
        """开始 YOLO 训练"""
        if not self.yaml_file_path or not os.path.exists(self.yaml_file_path):
            QMessageBox.critical(self, "错误", "找不到 dataset.yaml 文件！")
            return

        # 获取训练参数
        task = self.task_combo.currentText()
        model = self.model_combo.currentText()
        epochs = self.epochs_spin.value()
        imgsz = int(self.imgsz_combo.currentText())
        batch = self.batch_spin.value()

        # 构建训练命令 - 使用 Python 脚本方式调用 YOLO
        # 创建临时训练脚本
        train_script = f"""
from ultralytics import YOLO

# 加载模型
model = YOLO('{model}')

# 开始训练
results = model.train(
    data='{self.yaml_file_path}',
    task='{task}',
    epochs={epochs},
    imgsz={imgsz},
    batch={batch}
)
"""

        # 保存临时脚本
        temp_script_path = os.path.join(
            os.path.dirname(self.yaml_file_path), "_temp_train.py"
        )
        with open(temp_script_path, "w", encoding="utf-8") as f:
            f.write(train_script)

        # 构建命令
        command = [sys.executable, temp_script_path]

        # 显示训练命令
        self.log_text.append("\n" + "=" * 60 + "\n")
        self.log_text.append("🚀 开始训练\n")
        self.log_text.append("=" * 60 + "\n")
        self.log_text.append(f"任务类型: {task}\n")
        self.log_text.append(f"模型: {model}\n")
        self.log_text.append(f"数据集: {self.yaml_file_path}\n")
        self.log_text.append(f"训练轮数: {epochs}\n")
        self.log_text.append(f"图像大小: {imgsz}\n")
        self.log_text.append(f"批次大小: {batch}\n\n")

        # 禁用控件
        self.start_btn.setEnabled(False)
        self.enable_train_checkbox.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        # 使用 QProcess 执行训练
        self.train_process = QProcess(self)
        self.train_process.readyReadStandardOutput.connect(self.handle_train_output)
        self.train_process.readyReadStandardError.connect(self.handle_train_error)
        self.train_process.finished.connect(self.on_train_finished)

        # 启动训练进程
        self.train_process.start(command[0], command[1:])

    def handle_train_output(self):
        """处理训练输出"""
        if self.train_process:
            data = self.train_process.readAllStandardOutput()
            text = bytes(data).decode("utf-8", errors="ignore")
            self.log_text.insertPlainText(text)
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )

    def handle_train_error(self):
        """处理训练错误输出"""
        if self.train_process:
            data = self.train_process.readAllStandardError()
            text = bytes(data).decode("utf-8", errors="ignore")
            self.log_text.insertPlainText(text)
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )

    def on_train_finished(self, exit_code, exit_status):
        """训练完成"""
        # 恢复控件
        self.start_btn.setEnabled(True)
        self.enable_train_checkbox.setEnabled(True)
        self.progress_bar.setVisible(False)

        if exit_code == 0:
            self.log_text.append("\n" + "=" * 60 + "\n")
            self.log_text.append("✓ 训练完成！\n")
            self.log_text.append("=" * 60 + "\n")
            QMessageBox.information(
                self,
                "训练完成",
                "YOLO 模型训练已成功完成！\n\n" "训练结果保存在 runs/ 目录下。",
            )
        else:
            self.log_text.append("\n" + "=" * 60 + "\n")
            self.log_text.append(f"❌ 训练失败 (退出码: {exit_code})\n")
            self.log_text.append("=" * 60 + "\n")
            QMessageBox.critical(
                self,
                "训练失败",
                f"训练过程出现错误！\n\n退出码: {exit_code}\n\n"
                "请查看日志了解详细信息。",
            )


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YOLODatasetApp()
    window.show()
    sys.exit(app.exec_())
