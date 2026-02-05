# 数据集整理工具使用说明

## 📋 功能简介

这是一个用于整理混合数据集的工具，可以自动识别并匹配图像文件和对应的标签文件，将它们分类输出到 `images/` 和 `labels/` 文件夹中。

### 适用场景

- 标注工具导出的混合文件夹（图像和标签在同一目录）
- 需要整理成 YOLO 标准格式的数据集
- 批量处理多个混合文件夹

### 主要特性

- ✅ **自动匹配**：基于文件名自动匹配图像和标签
- ✅ **多格式支持**：支持 .jpg、.jpeg、.png、.bmp、.tif、.tiff
- ✅ **智能过滤**：自动跳过无标签的图像
- ✅ **双模式**：支持复制模式和移动模式
- ✅ **批量处理**：可同时处理多个文件夹
- ✅ **详细统计**：显示匹配成功、无标签、孤立标签的数量

---

## 🚀 快速开始

### 环境要求

```bash
Python >= 3.7
PyQt5  # 仅图形界面版本需要
```

### 安装依赖

```bash
# 图形界面版本
pip install PyQt5

# 命令行版本无需额外依赖
```

---

## 📖 使用教程

### 方式一：图形界面版本（推荐）

#### 1. 启动程序

```bash
python organize_dataset_UI.py
```

#### 2. 操作步骤

1. **选择源文件夹**：点击"浏览"按钮，选择包含混合图像和标签的文件夹
2. **选择输出文件夹**：点击"浏览"按钮，选择整理后数据集的保存位置
3. **选择操作模式**：
   - **复制文件**：保留源文件（推荐）
   - **移动文件**：删除源文件，节省空间
4. **开始整理**：点击"🚀 开始整理"按钮
5. **查看结果**：在日志窗口查看处理进度和统计信息

#### 界面预览

```
┌─────────────────────────────────────────┐
│  📁 数据集整理工具                       │
│  自动匹配图像和标签文件...               │
├─────────────────────────────────────────┤
│  源文件夹: [_______________] [浏览]      │
│  输出文件夹: [_____________] [浏览]      │
│  操作模式: ○ 复制  ○ 移动               │
│  [🚀 开始整理]                           │
├─────────────────────────────────────────┤
│  处理日志:                               │
│  ┌─────────────────────────────────┐   │
│  │ 正在扫描...                      │   │
│  │ 找到 100 个图像文件              │   │
│  │ 找到 95 个标签文件               │   │
│  │ ✓ 成功匹配: 95 对文件            │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

### 方式二：命令行版本

#### 基本用法

```bash
# 复制模式（默认）
python organize_dataset.py -s E:/mixed_data -o E:/organized_data

# 移动模式
python organize_dataset.py -s E:/mixed_data -o E:/organized_data --move
```

#### 批量处理多个文件夹

```bash
python organize_dataset.py -s E:/data1 E:/data2 E:/data3 -o E:/output
```

#### 命令行参数说明

| 参数           | 说明                       | 必需 |
| -------------- | -------------------------- | ---- |
| `-s, --source` | 源文件夹路径（可指定多个） | 是   |
| `-o, --output` | 输出文件夹路径             | 是   |
| `--move`       | 移动文件而不是复制         | 否   |

---

## 📁 输入输出格式

### 输入格式（混合文件夹）

```
source_folder/
├── img001.jpg          # 图像文件
├── img001.txt          # 对应的标签文件
├── img002.jpg
├── img002.txt
├── img003.png
├── img003.txt
├── photo_001.jpg
├── photo_001.txt
└── ...
```

### 输出格式（标准 YOLO 格式）

```
output_folder/
├── images/             # 所有图像文件
│   ├── img001.jpg
│   ├── img002.jpg
│   ├── img003.png
│   ├── photo_001.jpg
│   └── ...
└── labels/             # 所有标签文件
    ├── img001.txt
    ├── img002.txt
    ├── img003.txt
    ├── photo_001.txt
    └── ...
```

---

## 🔧 使用示例

### 示例 1：整理标注工具导出的数据

**场景**：使用 LabelImg 标注后，图像和标签在同一文件夹

```bash
# 源文件夹结构
E:/labelimg_output/
├── dog_001.jpg
├── dog_001.txt
├── cat_002.jpg
├── cat_002.txt
└── ...

# 执行命令
python organize_dataset_UI.py

# 或命令行
python organize_dataset.py -s E:/labelimg_output -o E:/yolo_dataset

# 输出结果
E:/yolo_dataset/
├── images/
│   ├── dog_001.jpg
│   ├── cat_002.jpg
│   └── ...
└── labels/
    ├── dog_001.txt
    ├── cat_002.txt
    └── ...
```

### 示例 2：批量整理多个文件夹

**场景**：有多个不同来源的混合数据集需要整理

```bash
python organize_dataset.py \
  -s E:/dataset1 E:/dataset2 E:/dataset3 \
  -o E:/organized_datasets

# 输出结构
E:/organized_datasets/
├── dataset1/
│   ├── images/
│   └── labels/
├── dataset2/
│   ├── images/
│   └── labels/
└── dataset3/
    ├── images/
    └── labels/
```

### 示例 3：移动模式（节省空间）

**场景**：磁盘空间不足，需要移动而不是复制

```bash
python organize_dataset.py -s E:/mixed_data -o E:/organized_data --move
```

⚠️ **警告**：移动模式会删除源文件，请确保已备份！

---

## ⚠️ 常见问题

### Q1: 提示"没有找到匹配的文件"
**A:** 检查以下几点：
- 图像和标签文件名是否一致（除扩展名外）
- 标签文件是否为 `.txt` 格式
- 源文件夹中是否真的包含图像和标签文件

### Q2: 有些图像没有被复制
**A:** 这是正常的。工具只会复制有对应标签的图像。无标签的图像会在日志中显示警告。

### Q3: 支持哪些图像格式？
**A:** 支持以下格式：
- `.jpg` / `.jpeg`
- `.png`
- `.bmp`
- `.tif` / `.tiff`

### Q4: 标签文件格式有要求吗？
**A:** 标签文件必须是 `.txt` 格式，内容格式不限（YOLO、COCO 等都可以）。

### Q5: 可以处理子文件夹吗？
**A:** 当前版本不支持递归处理子文件夹。如需处理，请使用批量模式分别指定每个子文件夹。

### Q6: 复制模式和移动模式有什么区别？
**A:** 
- **复制模式**：保留源文件，适合需要备份的情况
- **移动模式**：删除源文件，适合磁盘空间不足的情况

---

## 📊 统计信息说明

处理完成后会显示三类统计：

| 类型         | 说明               | 处理方式              |
| ------------ | ------------------ | --------------------- |
| ✓ 成功匹配   | 找到对应标签的图像 | 已复制/移动到输出目录 |
| ⚠ 无标签图像 | 没有对应标签的图像 | 跳过，不处理          |
| ⚠ 孤立标签   | 没有对应图像的标签 | 跳过，不处理          |

**示例输出：**
```
✓ 成功匹配: 95 对文件
⚠ 无标签图像: 5 个
⚠ 孤立标签: 2 个
```

---

## 🛠️ 高级用法

### 在 Python 脚本中调用

```python
from organize_dataset import organize_dataset

# 整理单个文件夹
matched, no_label, orphan = organize_dataset(
    source_dir="E:/mixed_data",
    output_dir="E:/organized_data",
    copy_mode=True  # True=复制, False=移动
)

print(f"成功: {matched}, 无标签: {no_label}, 孤立: {orphan}")
```

### 批量处理

```python
from organize_dataset import batch_organize_datasets

source_dirs = [
    "E:/dataset1",
    "E:/dataset2",
    "E:/dataset3"
]

batch_organize_datasets(
    source_dirs=source_dirs,
    output_base_dir="E:/organized_datasets",
    copy_mode=True
)
```

---

## 📝 注意事项

1. 💾 **备份数据**：使用移动模式前请务必备份原始数据
2. 📛 **文件命名**：确保图像和标签文件名一致（除扩展名）
3. 🗂️ **文件夹纯净**：源文件夹中只应包含图像和标签文件
4. 💿 **磁盘空间**：复制模式需要足够的磁盘空间
5. 🔄 **重复运行**：可以多次运行，已存在的文件会被覆盖

---

## 🔗 与其他工具配合使用

### 工作流程示例

```
1. 标注工具（LabelImg/CVAT）
   ↓ 导出混合文件夹
2. organize_dataset.py（本工具）
   ↓ 整理成标准格式
3. split_dataset.py
   ↓ 划分训练/验证/测试集
4. YOLO 训练
```

### 完整命令示例

```bash
# 步骤1: 整理数据集
python organize_dataset.py -s E:/labelimg_output -o E:/organized_data

# 步骤2: 划分数据集
python split_dataset_UI.py
# 在界面中选择:
#   图片文件夹: E:/organized_data/images
#   标签文件夹: E:/organized_data/labels
#   保存文件夹: E:/yolo_dataset

# 步骤3: 训练 YOLO
yolo train data=E:/yolo_dataset/dataset.yaml model=yolov8n.pt epochs=100
```

---

## 🎉 更新日志

### v1.0.0 (2026-02-05)
- ✨ 初始版本发布
- ✅ 支持图形界面和命令行两种模式
- ✅ 自动匹配图像和标签文件
- ✅ 支持复制/移动两种操作模式
- ✅ 支持批量处理多个文件夹
- ✅ 详细的统计信息和日志输出

---

## 📧 反馈与支持

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [提交问题](https://github.com/Ashington258/AI_Tools/issues)
- 项目地址: https://github.com/Ashington258/AI_Tools

---

## 📄 许可证

MIT License
