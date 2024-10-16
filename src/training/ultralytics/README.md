# Train Platform

## 0 dataset structure

please use the standard dataset structure

dataset/
    ├── images/
    │   ├── train/
    │   ├── val/
    └── labels/
        ├── train/
        ├── val/
    dataset.yaml


## 1 Run code in Terminal

yolo task=segment mode=train model=yolov8s-seg.pt data=data.yaml epochs=100 imgsz=640
yolo task=segment mode=train model=yolo11s-seg.pt data=dataset/dataset.yaml epochs=100 imgsz=640

## 2 Use train.py to train

set your configuration in train.py

