---
title: "(CNN) PyTorch Tensor 차원 변환"
description: "reshape, view, permute, transpose를 활용한 텐서 형태 변환"
date: 2025-05-29 10:00:00 +0900
categories: [Dev, CNN]
tags: [pytorch, tensor, reshape, view, permute, transpose, deep learning]
---

-------------------------------------------------------

# PyTorch Tensor 

* 최초 작성일: 2025년 5월 29일 (목)

## 

딥러닝에서 텐서의 차원을 이해하고 조작하는 것은 필수적이다. 각 차원은 데이터의 특정 속성을 나타낸다.

### 
- **1D 텐서**: 벡터 (예: 시계열 데이터)
- **2D 텐서**: 행렬 (예: 흑백 이미지, 텍스트 임베딩)
- **3D 텐서**: 큐브 (예: 컬러 이미지, 시퀀스 데이터)
- **4D 텐서**: 배치 포함 (예: 이미지 배치 [B, C, H, W])

```python
import torch

# 1D: 
seq = torch.arange(10)
print(f"1D tensor shape: {seq.shape}")
# : 1D tensor shape: torch.Size([10])

# 2D: 
feat_mat = torch.randn(5, 3)
print(f"2D tensor shape: {feat_mat.shape}")
# : 2D tensor shape: torch.Size([5, 3])

# 3D: RGB 
rgb_img = torch.randn(3, 224, 224)
print(f"3D tensor shape: {rgb_img.shape}")
# : 3D tensor shape: torch.Size([3, 224, 224])

# 4D: 
img_batch = torch.randn(32, 3, 224, 224)
print(f"4D tensor shape: {img_batch.shape}")
# : 4D tensor shape: torch.Size([32, 3, 224, 224])
```

---

## reshape view 

`reshape()`와 `view()` 모두 텐서의 형태를 변환하지만, 중요한 차이점이 있다.

### reshape() - 
```python
# reshape 
data = torch.arange(12)
print(f"Original: {data}")
# : Original: tensor([ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

# 2x6 
mat_2x6 = data.reshape(2, 6)
print(f"2x6 matrix:\n{mat_2x6}")
# : 2x6 matrix:
# tensor([[ 0, 1, 2, 3, 4, 5],
# [ 6, 7, 8, 9, 10, 11]])

# 3x4 
mat_3x4 = data.reshape(3, 4)
print(f"3x4 matrix:\n{mat_3x4}")
# : 3x4 matrix:
# tensor([[ 0, 1, 2, 3],
# [ 4, 5, 6, 7],
# [ 8, 9, 10, 11]])

# -1 
auto_shape = data.reshape(2, -1)
print(f"Auto-sized (2, -1): {auto_shape.shape}")
# : Auto-sized (2, -1): torch.Size([2, 6])
```

### view() - 
```python
# view contiguous 
vec = torch.arange(20)
mat = vec.view(4, 5)
print(f"View result:\n{mat}")
# : View result:
# tensor([[ 0, 1, 2, 3, 4],
# [ 5, 6, 7, 8, 9],
# [10, 11, 12, 13, 14],
# [15, 16, 17, 18, 19]])

# CNN FC 
torch.manual_seed(2025)
cnn_out = torch.rand(size=(16, 64, 8, 8))  # [배치, 채널, H, W]
fc_in = cnn_out.view(16, -1)  # Flatten
print(f"CNN output: {cnn_out.shape} -> FC input: {fc_in.shape}")
# : CNN output: torch.Size([16, 64, 8, 8]) -> FC input: torch.Size([16, 4096])
```

### Contiguous Memory 
```python
# 
t1 = torch.arange(12)
t2 = t1.view(3, 4)
t3 = t1.reshape(3, 4)

print(f"Original contiguous: {t1.is_contiguous()}")
print(f"View contiguous: {t2.is_contiguous()}")
print(f"Reshape contiguous: {t3.is_contiguous()}")
# : Original contiguous: True
# View contiguous: True
# Reshape contiguous: True
```

### 
```python
try:
    wrong_shape = torch.arange(10).reshape(3, 4)
except RuntimeError as e:
    print(f"Error: {e}")
# : Error: shape '[3, 4]' is invalid for input of size 10
```

---

## permute transpose 

차원의 순서를 바꾸는 것은 딥러닝에서 매우 중요한 작업이다.

### permute() - 
```python
# : HWC -> CHW
torch.manual_seed(2025)
img_hwc = torch.rand(size=(224, 224, 3))  # Height, Width, Channel
print(f"HWC format: {img_hwc.shape}")
# : HWC format: torch.Size([224, 224, 3])

img_chw = img_hwc.permute(2, 0, 1)  # Channel, Height, Width
print(f"CHW format: {img_chw.shape}")
# : CHW format: torch.Size([3, 224, 224])

# 
img_back = img_chw.permute(1, 2, 0)
print(f"Back to HWC: {img_back.shape}")
# : Back to HWC: torch.Size([224, 224, 3])

# 4D : NHWC -> NCHW ( )
batch_nhwc = torch.rand(size=(32, 224, 224, 3))
batch_nchw = batch_nhwc.permute(0, 3, 1, 2)
print(f"NHWC: {batch_nhwc.shape} -> NCHW: {batch_nchw.shape}")
# : NHWC: torch.Size([32, 224, 224, 3]) -> NCHW: torch.Size([32, 3, 224, 224])
```

### transpose() - 
```python
# 
feat_map = torch.rand(size=(64, 3, 128, 256))
print(f"Original shape: {feat_map.shape}")
# : Original shape: torch.Size([64, 3, 128, 256])

# 
transposed = feat_map.transpose(2, 3)
print(f"After transpose(2, 3): {transposed.shape}")
# : After transpose(2, 3): torch.Size([64, 3, 256, 128])

# transpose
double_trans = feat_map.transpose(1, 2).transpose(2, 3)
print(f"Double transpose: {double_trans.shape}")
# : Double transpose: torch.Size([64, 128, 3, 256])
```

### t() - 2D 
```python
# 2 
matrix = torch.rand(size=(3, 5))
print(f"Original matrix:\n{matrix}")
# : Original matrix:
# tensor([[0.5234, 0.3456, 0.7890, 0.1234, 0.9876],
# [0.2345, 0.6789, 0.3456, 0.8901, 0.4567],
# [0.8901, 0.2345, 0.5678, 0.3456, 0.7890]])

transposed = matrix.t()
print(f"Transposed shape: {transposed.shape}")
# : Transposed shape: torch.Size([5, 3])
```

### Contiguous 
```python
# permute contiguous 
img = torch.rand(size=(3, 64, 64))
img_perm = img.permute(1, 2, 0)
print(f"After permute, contiguous: {img_perm.is_contiguous()}")
# : After permute, contiguous: False

# view 
try:
    img_flat = img_perm.view(64, -1)
except RuntimeError as e:
    print(f"View error: {e}")
# : View error: view size is not compatible with input tensor's size and stride

# 1: reshape 
img_flat_reshape = img_perm.reshape(64, -1)
print(f"Reshape success: {img_flat_reshape.shape}")
# : Reshape success: torch.Size([64, 192])

# 2: contiguous() view 
img_flat_view = img_perm.contiguous().view(64, -1)
print(f"Contiguous + view success: {img_flat_view.shape}")
# : Contiguous + view success: torch.Size([64, 192])
```

---

## 

### 1. CNN FC 
```python
# CNN Fully Connected 
class CNNToFC(torch.nn.Module):
    def forward(self, x):
        # x shape: [batch, channels, height, width]
        batch_size = x.shape[0]
        # Flatten 방법 1: view
        x_flat_1 = x.view(batch_size, -1)
        # Flatten 방법 2: reshape
        x_flat_2 = x.reshape(batch_size, -1)
        return x_flat_1

# 
model = CNNToFC()
cnn_output = torch.randn(32, 512, 7, 7)
fc_input = model(cnn_output)
print(f"CNN output: {cnn_output.shape} -> FC input: {fc_input.shape}")
# : CNN output: torch.Size([32, 512, 7, 7]) -> FC input: torch.Size([32, 25088])
```

### 2. 
```python
# Multi-head attention 
def prepare_attention(x, num_heads=8):
    # x shape: [batch, seq_len, embed_dim]
    b, s, d = x.shape
    head_dim = d // num_heads
    
    # [batch, seq_len, num_heads, head_dim]으로 reshape
    x = x.reshape(b, s, num_heads, head_dim)
    
    # [batch, num_heads, seq_len, head_dim]으로 permute
    x = x.permute(0, 2, 1, 3)
    
    return x

# 
seq_data = torch.randn(16, 100, 512)  # [batch, seq_len, embed_dim]
attn_input = prepare_attention(seq_data, num_heads=8)
print(f"Original: {seq_data.shape} -> Attention: {attn_input.shape}")
# : Original: torch.Size([16, 100, 512]) -> Attention: torch.Size([16, 8, 100, 64])
```

### 3. 
```python
# PyTorch (NCHW) <-> TensorFlow (NHWC) 
def pytorch_to_tensorflow(img_batch):
    # NCHW -> NHWC
    return img_batch.permute(0, 2, 3, 1)

def tensorflow_to_pytorch(img_batch):
    # NHWC -> NCHW
    return img_batch.permute(0, 3, 1, 2)

# 
pytorch_batch = torch.randn(8, 3, 224, 224)  # PyTorch 형식
tf_batch = pytorch_to_tensorflow(pytorch_batch)
print(f"PyTorch: {pytorch_batch.shape} -> TensorFlow: {tf_batch.shape}")
# : PyTorch: torch.Size([8, 3, 224, 224]) -> TensorFlow: torch.Size([8, 224, 224, 3])

back_to_pytorch = tensorflow_to_pytorch(tf_batch)
print(f"Back to PyTorch: {back_to_pytorch.shape}")
# : Back to PyTorch: torch.Size([8, 3, 224, 224])
```

---

## 

### 1. 
```python
# view vs reshape 
large_tensor = torch.randn(1000, 1000)

# view ( )
view_result = large_tensor.view(100, 10000)
print(f"Same storage: {view_result.data_ptr() == large_tensor.data_ptr()}")
# : Same storage: True

# permute 
permuted = large_tensor.t()
print(f"After transpose, contiguous: {permuted.is_contiguous()}")
# : After transpose, contiguous: False
```

### 2. 
- ✅ 변환 전후 원소 개수가 동일한지 확인
- ✅ contiguous 메모리가 필요한 경우 확인
- ✅ 차원의 의미가 올바르게 유지되는지 확인
- ✅ 배치 차원은 보통 첫 번째 차원으로 유지

### 3. 
```python
def debug_tensor_shape(tensor, name="tensor"):
    print(f"{name}:")
    print(f"  Shape: {tensor.shape}")
    print(f"  Size: {tensor.numel()}")
    print(f"  Contiguous: {tensor.is_contiguous()}")
    print(f"  Device: {tensor.device}")

# 
test_tensor = torch.randn(2, 3, 4).permute(2, 0, 1)
debug_tensor_shape(test_tensor, "Permuted tensor")
# : Permuted tensor:
# Shape: torch.Size([4, 2, 3])
# Size: 24
# Contiguous: False
# Device: cpu
```

---

## 

| 함수 | 용도 | 특징 | 주의사항 |
|------|------|------|----------|
| `reshape` | 형태 변환 | 유연함, 새 메모리 할당 가능 | 상대적으로 느림 |
| `view` | 형태 변환 | 메모리 효율적 | contiguous 필요 |
| `permute` | 차원 재배열 | 모든 차원 자유롭게 | contiguous 깨짐 |
| `transpose` | 두 차원 교환 | 특정 두 차원만 | contiguous 깨짐 |
| `t` | 2D 전치 | 2차원 전용 | 간단한 행렬 전치 |

이 가이드를 통해 PyTorch 텐서의 차원 변환을 자유자재로 다룰 수 있게 되기를 바란다!
