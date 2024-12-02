from ultralytics import YOLO

model = YOLO("src/model_convert/best.pt")
path = model.export(
    format="onnx", simplify=True, device=0, opset=12, dynamic=False, imgsz=640
)
