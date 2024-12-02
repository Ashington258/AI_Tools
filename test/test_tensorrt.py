# 验证 TensorRT 安装
try:
    # 导入并验证 TensorRT
    import tensorrt

    print("TensorRT version:", tensorrt.__version__)
    assert tensorrt.Builder(tensorrt.Logger())
    print("TensorRT is working correctly.")

    # 导入并验证 tensorrt_lean
    import tensorrt_lean as trt_lean

    print("tensorrt_lean version:", trt_lean.__version__)
    assert trt_lean.Runtime(trt_lean.Logger())
    print("tensorrt_lean is working correctly.")

    # 导入并验证 tensorrt_dispatch
    import tensorrt_dispatch as trt_dispatch

    print("tensorrt_dispatch version:", trt_dispatch.__version__)
    assert trt_dispatch.Runtime(trt_dispatch.Logger())
    print("tensorrt_dispatch is working correctly.")

except Exception as e:
    print("An error occurred:", e)
