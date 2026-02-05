import cv2
import os
import sys
import numpy as np
from tqdm import tqdm  # 引入进度条库


class InteractiveROISelector:
    """支持缩放和拖动的交互式ROI选择器"""

    def __init__(self, image, window_name="Select Crop Area"):
        self.original_image = image.copy()
        self.window_name = window_name
        self.scale = 1.0
        self.min_scale = 0.1
        self.max_scale = 5.0

        # ROI 选择状态
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.roi_confirmed = False
        self.roi_rect = None  # (x, y, w, h) in original image coordinates

        # 平移偏移
        self.offset_x = 0
        self.offset_y = 0
        self.panning = False
        self.pan_start = None

        # 计算初始缩放以适应屏幕
        screen_height = 1080  # 假设屏幕高度
        screen_width = 1920
        h, w = image.shape[:2]
        scale_h = (screen_height - 100) / h
        scale_w = (screen_width - 100) / w
        self.scale = min(scale_h, scale_w, 1.0)  # 不放大，只缩小

    def screen_to_image_coords(self, x, y):
        """将屏幕坐标转换为原始图像坐标"""
        img_x = int((x - self.offset_x) / self.scale)
        img_y = int((y - self.offset_y) / self.scale)
        return img_x, img_y

    def image_to_screen_coords(self, x, y):
        """将原始图像坐标转换为屏幕坐标"""
        screen_x = int(x * self.scale + self.offset_x)
        screen_y = int(y * self.scale + self.offset_y)
        return screen_x, screen_y

    def get_display_image(self):
        """获取当前缩放和偏移后的显示图像"""
        h, w = self.original_image.shape[:2]
        new_w = int(w * self.scale)
        new_h = int(h * self.scale)

        if new_w < 1 or new_h < 1:
            return self.original_image

        resized = cv2.resize(self.original_image, (new_w, new_h))

        # 创建画布
        canvas_h, canvas_w = max(new_h, 800), max(new_w, 1200)
        canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)

        # 计算放置位置
        y_start = max(0, self.offset_y)
        x_start = max(0, self.offset_x)
        y_end = min(canvas_h, self.offset_y + new_h)
        x_end = min(canvas_w, self.offset_x + new_w)

        src_y_start = max(0, -self.offset_y)
        src_x_start = max(0, -self.offset_x)
        src_y_end = src_y_start + (y_end - y_start)
        src_x_end = src_x_start + (x_end - x_start)

        if y_end > y_start and x_end > x_start:
            canvas[y_start:y_end, x_start:x_end] = resized[
                src_y_start:src_y_end, src_x_start:src_x_end
            ]

        # 绘制ROI矩形（如果正在绘制或已确认）
        if self.start_point and self.end_point:
            # 转换为屏幕坐标
            p1_screen = self.image_to_screen_coords(*self.start_point)
            p2_screen = self.image_to_screen_coords(*self.end_point)
            cv2.rectangle(canvas, p1_screen, p2_screen, (0, 255, 0), 2)

        return canvas

    def mouse_callback(self, event, x, y, flags, param):
        """鼠标事件回调"""
        # Ctrl + 滚轮缩放
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags & cv2.EVENT_FLAG_CTRLKEY:
                # 获取鼠标位置对应的图像坐标
                img_x, img_y = self.screen_to_image_coords(x, y)

                # 缩放
                old_scale = self.scale
                if flags > 0:  # 向上滚动，放大
                    self.scale = min(self.scale * 1.1, self.max_scale)
                else:  # 向下滚动，缩小
                    self.scale = max(self.scale / 1.1, self.min_scale)

                # 调整偏移，使鼠标位置保持不变
                self.offset_x = x - img_x * self.scale
                self.offset_y = y - img_y * self.scale

        # 右键拖动平移
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.panning = True
            self.pan_start = (x, y)

        elif event == cv2.EVENT_RBUTTONUP:
            self.panning = False

        elif event == cv2.EVENT_MOUSEMOVE and self.panning:
            if self.pan_start:
                dx = x - self.pan_start[0]
                dy = y - self.pan_start[1]
                self.offset_x += dx
                self.offset_y += dy
                self.pan_start = (x, y)

        # 左键绘制ROI
        elif event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            img_x, img_y = self.screen_to_image_coords(x, y)
            self.start_point = (img_x, img_y)
            self.end_point = (img_x, img_y)

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            img_x, img_y = self.screen_to_image_coords(x, y)
            self.end_point = (img_x, img_y)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            img_x, img_y = self.screen_to_image_coords(x, y)
            self.end_point = (img_x, img_y)

    def select_roi(self):
        """显示窗口并选择ROI"""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        print("\n--- 操作说明 ---")
        print("1. Ctrl + 滚轮：缩放图像")
        print("2. 右键拖动：平移图像")
        print("3. 左键拖动：绘制裁剪区域")
        print("4. 按 SPACE 或 ENTER：确认选择")
        print("5. 按 'c' 或 ESC：取消退出")
        print("6. 按 'r'：重置视图")
        print("----------------\n")

        while True:
            display_img = self.get_display_image()

            # 添加提示信息
            info_text = f"Scale: {self.scale:.2f}x | Ctrl+Wheel: Zoom | Right-drag: Pan | Left-drag: Select ROI"
            cv2.putText(
                display_img,
                info_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

            cv2.imshow(self.window_name, display_img)

            key = cv2.waitKey(1) & 0xFF

            if key == ord(" ") or key == 13:  # SPACE or ENTER
                if self.start_point and self.end_point:
                    # 计算ROI矩形
                    x1, y1 = self.start_point
                    x2, y2 = self.end_point
                    x = min(x1, x2)
                    y = min(y1, y2)
                    w = abs(x2 - x1)
                    h = abs(y2 - y1)

                    if w > 0 and h > 0:
                        self.roi_rect = (x, y, w, h)
                        self.roi_confirmed = True
                        break
                    else:
                        print("ROI区域无效，请重新选择")
                else:
                    print("请先选择ROI区域")

            elif key == ord("c") or key == 27:  # 'c' or ESC
                break

            elif key == ord("r"):  # 重置视图
                h, w = self.original_image.shape[:2]
                screen_height = 1080
                screen_width = 1920
                scale_h = (screen_height - 100) / h
                scale_w = (screen_width - 100) / w
                self.scale = min(scale_h, scale_w, 1.0)
                self.offset_x = 0
                self.offset_y = 0

        cv2.destroyWindow(self.window_name)
        return self.roi_rect if self.roi_confirmed else None


def batch_crop_images(source_folder, output_folder=None):
    """
    批量裁剪图片
    :param source_folder: 原始图片所在的文件夹路径
    :param output_folder: 裁剪后图片保存的路径。如果为 None，默认保存在当前脚本目录下的 'cropped_output' 文件夹
    """

    # --- 1. 路径与文件准备 ---
    # 如果没有指定输出路径，默认设置为当前目录下的 "cropped_output"
    if output_folder is None:
        output_folder = os.path.join(os.getcwd(), "cropped_output")

    supported_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")

    # 获取所有图片文件
    images = [
        f for f in os.listdir(source_folder) if f.lower().endswith(supported_extensions)
    ]

    if not images:
        print(f"错误：在文件夹 '{source_folder}' 中没有找到图片。")
        return

    # 按文件名排序
    images.sort()

    # --- 2. 交互式选择裁剪区域 ---
    first_image_path = os.path.join(source_folder, images[0])
    img = cv2.imread(first_image_path)

    if img is None:
        print("无法读取第一张图片，请检查文件路径或完整性。")
        return

    # 使用自定义ROI选择器（支持缩放和平移）
    selector = InteractiveROISelector(img, "Select Crop Area")
    roi = selector.select_roi()

    if roi is None:
        print("未选择区域或操作取消。程序结束。")
        return

    # 解析坐标 (x, y, w, h)
    x, y, w, h = roi

    print(f"\n选定区域: x={x}, y={y}, 宽={w}, 高={h}")

    # --- 3. 创建输出文件夹 ---
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"已创建输出文件夹: {output_folder}")
    else:
        print(f"输出文件夹已存在: {output_folder}")

    # --- 4. 批量处理 (带进度条) ---
    print(f"开始批量裁剪 {len(images)} 张图片...")

    # 使用 tqdm 创建进度条
    # desc: 进度条左边的描述文字
    # unit: 单位
    for image_name in tqdm(images, desc="Processing", unit="img"):
        full_path = os.path.join(source_folder, image_name)
        current_img = cv2.imread(full_path)

        if current_img is None:
            # 如果读图失败，tqdm会自动换行，不会破坏进度条
            print(f"警告: 无法读取 {image_name}，已跳过。")
            continue

        # 核心裁剪
        # 增加边界检查，防止偶尔有图片尺寸小于裁剪框导致报错
        img_h, img_w = current_img.shape[:2]
        if y + h > img_h or x + w > img_w:
            # 如果裁剪框超出了当前图片范围，尝试修正或跳过
            # 这里选择简单地截断到边缘
            crop_y2 = min(y + h, img_h)
            crop_x2 = min(x + w, img_w)
            cropped_img = current_img[y:crop_y2, x:crop_x2]
        else:
            cropped_img = current_img[y : y + h, x : x + w]

        # 保存图片
        save_path = os.path.join(output_folder, image_name)
        cv2.imwrite(save_path, cropped_img)

    print(f"\n全部完成！结果保存在: {output_folder}")


if __name__ == "__main__":
    # 配置源文件夹路径 (请根据实际情况修改)
    source_dir = r"output_file/3_monte_carlo_sampling"

    # 配置输出文件夹路径 (可选)
    # 选项 A: 设置为 None，默认在脚本目录下生成 cropped_output
    # target_output_dir = None

    # 选项 B: 指定一个绝对路径，例如 r"D:\MyProject\Dataset\Cropped"
    target_output_dir = r"output_file/8_cropped_images"

    # 检查源路径是否存在
    if os.path.exists(source_dir):
        batch_crop_images(source_dir, target_output_dir)
    else:
        print(f"错误：源文件夹路径不存在: {source_dir}")
