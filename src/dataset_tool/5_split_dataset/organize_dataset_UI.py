"""数据集整理工具 - 图形界面版本

功能说明：
从混合文件夹中自动识别并匹配图像文件和对应的标签文件，
将它们分类复制到 images/ 和 labels/ 文件夹中。

图形界面特性：
- 可视化文件选择
- 实时进度显示
- 详细统计信息
- 支持复制/移动模式切换
"""

import os
import sys
import shutil
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QRadioButton,
    QButtonGroup,
    QTextEdit,
    QProgressBar,
    QMessageBox,
)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont


class OrganizeWorker(QThread):
    """后台工作线程，用于执行文件整理任务"""

    progress = pyqtSignal(str)  # 进度信息
    finished = pyqtSignal(int, int, int)  # 完成信号 (成功, 无标签, 孤立)

    def __init__(self, source_dir, output_dir, copy_mode):
        super().__init__()
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.copy_mode = copy_mode

    def run(self):
        """执行文件整理"""
        try:
            # 创建输出目录
            images_dir = os.path.join(self.output_dir, "images")
            labels_dir = os.path.join(self.output_dir, "labels")
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(labels_dir, exist_ok=True)

            # 支持的格式
            image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
            label_extension = ".txt"

            # 扫描文件
            self.progress.emit(f"正在扫描源文件夹: {self.source_dir}\n")

            image_files = {}
            label_files = {}

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

            self.progress.emit(f"找到 {len(image_files)} 个图像文件\n")
            self.progress.emit(f"找到 {len(label_files)} 个标签文件\n\n")

            # 匹配和复制/移动
            matched_count = 0
            no_label_count = 0
            orphan_label_count = 0

            operation = shutil.copy2 if self.copy_mode else shutil.move
            operation_name = "复制" if self.copy_mode else "移动"

            self.progress.emit(f"开始{operation_name}文件...\n")

            total = len(image_files)
            for idx, (name, image_path) in enumerate(image_files.items(), 1):
                if name in label_files:
                    label_path = label_files[name]

                    # 复制/移动文件
                    dest_image = os.path.join(images_dir, os.path.basename(image_path))
                    dest_label = os.path.join(labels_dir, os.path.basename(label_path))

                    operation(image_path, dest_image)
                    operation(label_path, dest_label)

                    matched_count += 1

                    if matched_count % 50 == 0:
                        self.progress.emit(
                            f"进度: {idx}/{total} - 已处理 {matched_count} 对文件\n"
                        )
                else:
                    no_label_count += 1
                    self.progress.emit(
                        f"⚠ 警告: '{os.path.basename(image_path)}' 没有对应标签\n"
                    )

            # 统计孤立标签
            for name in label_files:
                if name not in image_files:
                    orphan_label_count += 1
                    self.progress.emit(f"⚠ 警告: '{name}.txt' 没有对应图像\n")

            self.progress.emit(f"\n{'='*50}\n")
            self.progress.emit(f"整理完成！\n")
            self.progress.emit(f"{'='*50}\n")
            self.progress.emit(f"✓ 成功匹配: {matched_count} 对文件\n")
            self.progress.emit(f"⚠ 无标签图像: {no_label_count} 个\n")
            self.progress.emit(f"⚠ 孤立标签: {orphan_label_count} 个\n")
            self.progress.emit(f"\n输出目录:\n")
            self.progress.emit(f"  - 图像: {images_dir}\n")
            self.progress.emit(f"  - 标签: {labels_dir}\n")

            self.finished.emit(matched_count, no_label_count, orphan_label_count)

        except Exception as e:
            self.progress.emit(f"\n❌ 错误: {str(e)}\n")
            self.finished.emit(0, 0, 0)


class OrganizeDatasetApp(QWidget):
    """数据集整理工具主窗口"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        """初始化用户界面"""
        # 设置窗口
        self.setWindowTitle("数据集整理工具 - 图像标签分类器")
        self.setGeometry(200, 200, 800, 600)

        # 深色主题样式
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
                padding: 5px;
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
            QRadioButton {
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
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
        title = QLabel("📁 数据集整理工具")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # 说明文字
        desc = QLabel("自动匹配图像和标签文件，分类输出到 images/ 和 labels/ 文件夹")
        desc.setStyleSheet("color: #aaa; font-size: 9pt;")
        layout.addWidget(desc)

        # 源文件夹选择
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("源文件夹:"))
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("选择包含混合图像和标签的文件夹...")
        source_layout.addWidget(self.source_input)
        self.source_btn = QPushButton("浏览")
        self.source_btn.clicked.connect(self.browse_source)
        source_layout.addWidget(self.source_btn)
        layout.addLayout(source_layout)

        # 输出文件夹选择
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出文件夹:"))
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("选择整理后数据集的保存位置...")
        output_layout.addWidget(self.output_input)
        self.output_btn = QPushButton("浏览")
        self.output_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_btn)
        layout.addLayout(output_layout)

        # 操作模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("操作模式:"))
        self.mode_group = QButtonGroup()
        self.copy_radio = QRadioButton("复制文件（保留源文件）")
        self.move_radio = QRadioButton("移动文件（删除源文件）")
        self.copy_radio.setChecked(True)
        self.mode_group.addButton(self.copy_radio)
        self.mode_group.addButton(self.move_radio)
        mode_layout.addWidget(self.copy_radio)
        mode_layout.addWidget(self.move_radio)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # 开始按钮
        self.start_btn = QPushButton("🚀 开始整理")
        self.start_btn.clicked.connect(self.start_organize)
        self.start_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0d7377;
                font-size: 12pt;
                padding: 12px;
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
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        layout.addWidget(self.progress_bar)

        # 日志输出
        log_label = QLabel("处理日志:")
        layout.addWidget(log_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("等待开始...")
        layout.addWidget(self.log_text)

        # 统计信息
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        layout.addWidget(self.stats_label)

        self.setLayout(layout)

    def browse_source(self):
        """浏览源文件夹"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择源文件夹")
        if dir_path:
            self.source_input.setText(dir_path)

    def browse_output(self):
        """浏览输出文件夹"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if dir_path:
            self.output_input.setText(dir_path)

    def start_organize(self):
        """开始整理数据集"""
        source_dir = self.source_input.text().strip()
        output_dir = self.output_input.text().strip()

        # 验证输入
        if not source_dir:
            QMessageBox.warning(self, "警告", "请选择源文件夹！")
            return

        if not output_dir:
            QMessageBox.warning(self, "警告", "请选择输出文件夹！")
            return

        if not os.path.exists(source_dir):
            QMessageBox.critical(self, "错误", f"源文件夹不存在:\n{source_dir}")
            return

        # 清空日志
        self.log_text.clear()
        self.stats_label.setText("")

        # 禁用按钮
        self.start_btn.setEnabled(False)
        self.source_btn.setEnabled(False)
        self.output_btn.setEnabled(False)
        self.progress_bar.setVisible(True)

        # 获取操作模式
        copy_mode = self.copy_radio.isChecked()

        # 创建并启动工作线程
        self.worker = OrganizeWorker(source_dir, output_dir, copy_mode)
        self.worker.progress.connect(self.update_log)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def update_log(self, message):
        """更新日志"""
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def on_finished(self, matched, no_label, orphan):
        """处理完成"""
        # 恢复按钮
        self.start_btn.setEnabled(True)
        self.source_btn.setEnabled(True)
        self.output_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        # 显示统计
        if matched > 0:
            self.stats_label.setText(
                f"✓ 整理完成！成功: {matched} 对 | 无标签: {no_label} 个 | 孤立标签: {orphan} 个"
            )
            QMessageBox.information(
                self,
                "完成",
                f"数据集整理完成！\n\n"
                f"✓ 成功匹配: {matched} 对文件\n"
                f"⚠ 无标签图像: {no_label} 个\n"
                f"⚠ 孤立标签: {orphan} 个",
            )
        else:
            self.stats_label.setText("❌ 处理失败或没有找到匹配的文件")
            QMessageBox.warning(self, "警告", "没有找到匹配的图像和标签文件！")


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrganizeDatasetApp()
    window.show()
    sys.exit(app.exec_())
