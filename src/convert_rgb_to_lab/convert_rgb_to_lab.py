import cv2
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
import numpy as np

# 支持中文
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号


def rgb_to_lab(image_rgb):
    """
    将 RGB 图像转换为 Lab 色彩空间
    """
    image_lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
    return image_lab


def on_click(event, image_rgb, image_lab, lab_values):
    """
    处理鼠标点击事件，保存点击点的 Lab 数值
    """
    if (
        event.button is MouseButton.LEFT
        and event.xdata is not None
        and event.ydata is not None
    ):
        x = int(event.xdata)
        y = int(event.ydata)
        # 获取 RGB 值
        rgb = image_rgb[y, x]
        # 获取 Lab 值
        lab = image_lab[y, x]
        print(f"点击位置: ({x}, {y})")
        print(f"RGB 值: R={rgb[0]}, G={rgb[1]}, B={rgb[2]}")
        print(f"Lab 值: L={lab[0]}, a={lab[1]}, b={lab[2]}\n")
        # 保存 Lab 值
        lab_values.append(lab)


def filter_lab_values(lab_values):
    """
    过滤掉不合理的 Lab 数据（例如，离群点）
    """
    lab_values = np.array(lab_values)
    mean_lab = np.mean(lab_values, axis=0)
    std_lab = np.std(lab_values, axis=0)
    # 计算每个点到平均值的欧氏距离
    distances = np.linalg.norm(lab_values - mean_lab, axis=1)
    mean_distance = np.mean(distances)
    std_distance = np.std(distances)
    # 设置距离阈值（过滤掉超出平均距离两倍标准差的点）
    threshold_distance = mean_distance + 2 * std_distance
    # 保留在阈值内的点
    good_indices = distances <= threshold_distance
    filtered_lab_values = lab_values[good_indices]
    return filtered_lab_values, good_indices


def main():
    # 获取用户输入的图像路径
    image_path = input("请输入图像的路径: ")

    # 读取图像 (使用 OpenCV 读取，默认是 BGR 格式)
    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        print("无法读取图像。请检查路径是否正确。")
        return

    # 转换为 RGB 格式
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    # 转换为 Lab 色彩空间
    image_lab = rgb_to_lab(image_rgb)

    # 初始化列表来保存点击的 Lab 值
    lab_values = []

    # 使用 Matplotlib 显示图像
    fig, ax = plt.subplots()
    ax.imshow(image_rgb)
    ax.set_title("点击图像查看 RGB 和 Lab 数值")
    ax.axis("off")  # 隐藏坐标轴

    # 连接鼠标点击事件
    fig.canvas.mpl_connect(
        "button_press_event",
        lambda event: on_click(event, image_rgb, image_lab, lab_values),
    )

    plt.show()

    # 如果没有点击任何点
    if len(lab_values) == 0:
        print("未检测到任何点击。")
        return

    # 过滤掉不合理的数据
    filtered_lab_values, good_indices = filter_lab_values(lab_values)

    # 计算最终的 Lab 值（取平均）
    final_lab_value = np.mean(filtered_lab_values, axis=0)
    print(
        f"最终的 Lab 值: L={final_lab_value[0]}, a={final_lab_value[1]}, b={final_lab_value[2]}"
    )

    # 绘制每次点击的 Lab 值曲线图
    # 获取点击次数（对应于点击的序号）
    click_indices = np.arange(1, len(lab_values) + 1)

    # 将 lab_values 转换为 numpy 数组
    lab_values = np.array(lab_values)

    # 对于过滤后的数据，获取对应的点击次数
    filtered_click_indices = click_indices[good_indices]

    # 绘制 L、a、b 对应点击次数的曲线图
    plt.figure()
    plt.plot(filtered_click_indices, filtered_lab_values[:, 0], "r-", label="L* 值")
    plt.plot(filtered_click_indices, filtered_lab_values[:, 1], "g-", label="a* 值")
    plt.plot(filtered_click_indices, filtered_lab_values[:, 2], "b-", label="b* 值")

    # 在曲线图上绘制最终的 Lab 值（水平线）
    plt.axhline(y=final_lab_value[0], color="r", linestyle="--", label="最终 L* 值")
    plt.axhline(y=final_lab_value[1], color="g", linestyle="--", label="最终 a* 值")
    plt.axhline(y=final_lab_value[2], color="b", linestyle="--", label="最终 b* 值")

    plt.xlabel("点击次数")
    plt.ylabel("Lab 值")
    plt.title("每次点击的 Lab 值曲线图")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
