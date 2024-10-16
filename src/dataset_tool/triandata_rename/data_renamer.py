"""
Author: Ashington ashington258@proton.me
Date: 2024-06-09 11:03:02
LastEditors: Ashington ashington258@proton.me
LastEditTime: 2024-06-09 23:57:35
FilePath: \triandata_rename\data_renamer.py
Description: 请填写简介
联系方式:921488837@qq.com
Copyright (c) 2024 by ${git_name_email}, All Rights Reserved. 
"""

import os
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QCheckBox,
    QHBoxLayout,
    QProgressBar,
    QLineEdit,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #2d2d2d; color: #ffffff;")

        title = QLabel("File Renamer")
        title.setFont(QFont("Arial", 12))
        layout.addWidget(title)

        layout.addStretch()

        close_button = QPushButton("X")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet(
            "background-color: #d9534f; color: #ffffff; border: none;"
        )
        close_button.clicked.connect(self.parent.close)
        layout.addWidget(close_button)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.dragPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.move(
                self.parent.pos() + event.globalPos() - self.parent.dragPos
            )
            self.parent.dragPos = event.globalPos()
            event.accept()


class RenameApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.input_path = ""
        self.output_path = ""

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.input_label = QLabel("Input Path: Not Selected")
        self.output_label = QLabel("Output Path: Not Selected")

        self.input_label.setFont(QFont("Arial", 12))
        self.output_label.setFont(QFont("Arial", 12))

        content_layout.addWidget(self.input_label)
        content_layout.addWidget(self.output_label)

        input_btn = QPushButton("Select Input Path")
        input_btn.clicked.connect(self.select_input_path)
        content_layout.addWidget(input_btn)

        output_btn = QPushButton("Select Output Path")
        output_btn.clicked.connect(self.select_output_path)
        content_layout.addWidget(output_btn)

        self.overwrite_checkbox = QCheckBox("Overwrite Original Path")
        content_layout.addWidget(self.overwrite_checkbox)

        self.start_number_label = QLabel("Start Number:")
        self.start_number_input = QLineEdit()
        self.start_number_input.setText("1")  # 默认值为 1
        content_layout.addWidget(self.start_number_label)
        content_layout.addWidget(self.start_number_input)

        rename_btn = QPushButton("Rename Files")
        rename_btn.clicked.connect(self.rename_files)
        content_layout.addWidget(rename_btn)

        self.progress_bar = QProgressBar()
        content_layout.addWidget(self.progress_bar)

        layout.addWidget(content_widget)

        self.setCentralWidget(central_widget)
        self.setWindowTitle("File Renamer")
        self.resize(400, 300)
        self.applyStyles()

        self.show()

    def applyStyles(self):
        dark_style = """
        QWidget {
            background-color: #2d2d2d;
            color: #ffffff;
            border-radius: 10px;
        }
        QLabel {
            color: #ffffff;
        }
        QPushButton {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 5px;
            padding: 5px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #5a5a5a;
        }
        QCheckBox {
            color: #ffffff;
        }
        QCheckBox::indicator {
            border: 1px solid #555555;
            width: 15px;
            height: 15px;
        }
        QCheckBox::indicator:checked {
            background-color: #3c3c3c;
            border: 1px solid #ffffff;
        }
        QProgressBar {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 5px;
            text-align: center;
            color: #ffffff;
        }
        QProgressBar::chunk {
            background-color: #5a5a5a;
        }
        """
        self.setStyleSheet(dark_style)

    def select_input_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if path:
            self.input_path = path
            self.input_label.setText(f"Input Path: {path}")

    def select_output_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_path = path
            self.output_label.setText(f"Output Path: {path}")

    def rename_files(self):
        if not self.input_path:
            self.input_label.setText("Input Path: Not Selected (Please select a path)")
            return

        if self.overwrite_checkbox.isChecked():
            self.output_path = self.input_path

        if not self.output_path:
            self.output_label.setText(
                "Output Path: Not Selected (Please select a path)"
            )
            return

        filelist = os.listdir(self.input_path)
        total_files = len(filelist)
        if total_files == 0:
            return

        start_number = int(self.start_number_input.text() or "1")  # 获取起始编号
        a = start_number  # 使用用户输入的起始编号

        for i, files in enumerate(filelist):
            old_path = os.path.join(self.input_path, files)
            if os.path.isdir(old_path):
                continue

            filetype = os.path.splitext(files)[1]
            new_path = os.path.join(self.output_path, str(a) + filetype)
            os.rename(old_path, new_path)
            a += 1
            self.progress_bar.setValue(int((i + 1) / total_files * 100))

        self.input_label.setText("Input Path: Not Selected")
        self.output_label.setText("Output Path: Not Selected")
        self.input_path = ""
        self.output_path = ""
        self.progress_bar.setValue(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = RenameApp()
    sys.exit(app.exec_())
