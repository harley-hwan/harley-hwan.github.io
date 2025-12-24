---
title: "(CNN) arange, zeros, ones, random"
description: "arange와 기본 텐서 함수 및 난수 생성 함수"
date: 2025-05-29 10:00:00 +0900
categories: [Dev, CNN]
tags: [pytorch, tensor, random, arange, deep learning, initialization]
---

-------------------------------------------------------

# arange, zeros, ones와 random

* 최초 작성일: 2025년 5월 29일 (목)

## 목차

1. [개요](#개요)
2. [arange - 연속된 값으로 텐서 생성](#arange---연속된-값으로-텐서-생성)
3. [zeros & ones - 초기화된 텐서 생성](#zeros--ones---초기화된-텐서-생성)
4. [난수 텐서 생성](#난수-텐서-생성)
5. [실전 활용 팁](#실전-활용-팁)

---

## 📚 개요

PyTorch에서 텐서를 생성하는 것은 딥러닝 모델 개발의 첫걸음이다. 이 가이드에서는 가장 자주 사용되는 텐서 생성 함수들을 실용적인 예제와 함께 소개한다.

**언제 어떤 함수를 사용할까?**
- `arange`: 인덱스 생성, 시퀀스 데이터 처리
- `zeros/ones`: 가중치 초기화, 마스크 생성
- `rand/randn`: 가중치 초기화, 데이터 증강
- `randint`: 배치 샘플링, 레이블 생성

---

## 🔢 arange - 연속된 값으로 텐서 생성

`torch.arange()`는 파이썬의 `range()`와 유사하게 연속된 숫자들의 텐서를 생성한다.

### 함수 시그니처
```python
torch.arange(start=0, end, step=1, *, out=None, dtype=None, 
             layout=torch.strided, device=None, requires_grad=False)
```

### 주요 파라미터
- **start**: 시작값 (기본값: 0)
- **end**: 종료값 (**미포함**)
- **step**: 증가 간격 (기본값: 1)
- **dtype**: 데이터 타입 (자동 추론됨)

### 실전 예제

**기본 사용법**
```python
# 0부터 9까지의 정수
seq_tensor = torch.arange(10)
print(seq_tensor)
# 출력: tensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

# 특정 범위 지정
custom_range = torch.arange(start=2, end=9, step=2)
print(custom_range)
# 출력: tensor([2, 4, 6, 8])

# 실수형 텐서 생성
float_range = torch.arange(0, 1, 0.2)
print(float_range)
# 출력: tensor([0.0000, 0.2000, 0.4000, 0.6000, 0.8000])
```

**실용적 활용: 위치 인코딩 생성**
```python
# Transformer 모델의 위치 인코딩에 활용
seq_length = 100
position = torch.arange(0, seq_length).unsqueeze(1)
print(f"Position encoding shape: {position.shape}")
# 출력: Position encoding shape: torch.Size([100, 1])
print(position[:5])  # 처음 5개만 출력
# 출력: tensor([[0],
#              [1],
#              [2],
#              [3],
#              [4]])
```

---

## 🧱 zeros & ones - 초기화된 텐서 생성

특정 값으로 채워진 텐서를 생성할 때 사용한다.

### 함수 시그니처
```python
torch.zeros(*size, out=None, dtype=None, layout=torch.strided, 
            device=None, requires_grad=False)

torch.ones(*size, out=None, dtype=None, layout=torch.strided, 
           device=None, requires_grad=False)
```

### 주요 파라미터
- **size**: 텐서의 shape (튜플 또는 개별 인자)
- **dtype**: 데이터 타입 (기본값: float32)
- **device**: CPU 또는 GPU 지정

### 실전 예제

**zeros 활용: 패딩 마스크 생성**
```python
# 배치 크기 32, 최대 시퀀스 길이 50의 패딩 마스크
batch_size, max_len = 32, 50
padding_mask = torch.zeros(batch_size, max_len, dtype=torch.bool)
print(f"Padding mask shape: {padding_mask.shape}")
# 출력: Padding mask shape: torch.Size([32, 50])
print(padding_mask[0, :10])  # 첫 번째 배치의 처음 10개 값
# 출력: tensor([False, False, False, False, False, False, False, False, False, False])

# 3차원 텐서 생성
zero_3d = torch.zeros(2, 3, 4)
print(zero_3d)
# 출력: tensor([[[0., 0., 0., 0.],
#               [0., 0., 0., 0.],
#               [0., 0., 0., 0.]],
#              [[0., 0., 0., 0.],
#               [0., 0., 0., 0.],
#               [0., 0., 0., 0.]]])
```

**ones 활용: Attention 마스크 초기화**
```python
# Self-attention을 위한 초기 마스크
seq_len = 5
attention_mask = torch.ones(seq_len, seq_len)
print(attention_mask)
# 출력: tensor([[1., 1., 1., 1., 1.],
#              [1., 1., 1., 1., 1.],
#              [1., 1., 1., 1., 1.],
#              [1., 1., 1., 1., 1.],
#              [1., 1., 1., 1., 1.]])

# 정수형 ones 텐서
int_ones = torch.ones(3, 3, dtype=torch.int64)
print(int_ones)
# 출력: tensor([[1, 1, 1],
#              [1, 1, 1],
#              [1, 1, 1]])
```

**GPU 메모리 할당**
```python
# GPU가 있다면 바로 GPU에 텐서 생성
if torch.cuda.is_available():
    gpu_tensor = torch.zeros(3, 3, device='cuda')
    print(f"Tensor device: {gpu_tensor.device}")
    # 출력: Tensor device: cuda:0
else:
    cpu_tensor = torch.zeros(3, 3, device='cpu')
    print(f"Tensor device: {cpu_tensor.device}")
    # 출력: Tensor device: cpu
```

---

## 🎲 난수 텐서 생성

딥러닝에서 가중치 초기화와 데이터 증강에 필수적인 난수 생성 함수들이다.

### 재현 가능한 결과를 위한 시드 설정
```python
torch.manual_seed(42)  # CPU 시드
if torch.cuda.is_available():
    torch.cuda.manual_seed(42)  # GPU 시드
```

### 1️⃣ torch.rand() - 균일 분포 [0, 1)

**사용 시나리오**: Dropout 마스크, 확률적 샘플링

```python
# 기본 사용법
uniform_tensor = torch.rand(3, 4)
print(uniform_tensor)
# 출력: tensor([[0.8823, 0.9150, 0.3829, 0.9593],
#              [0.3904, 0.6009, 0.2566, 0.7936],
#              [0.9408, 0.1332, 0.9346, 0.5936]])

# Dropout 구현 예시
dropout_rate = 0.5
features = torch.randn(4, 5)  # 배치 크기 4, 특징 차원 5
dropout_mask = torch.rand(4, 5) > dropout_rate
print(dropout_mask)
# 출력: tensor([[ True,  True, False,  True, False],
#              [False,  True, False,  True,  True],
#              [ True, False,  True,  True, False],
#              [ True,  True, False, False,  True]])

output = features * dropout_mask
print(f"Active neurons: {dropout_mask.sum().item()}/{dropout_mask.numel()}")
# 출력: Active neurons: 12/20
```

### 2️⃣ torch.randn() - 표준 정규 분포 N(0, 1)

**사용 시나리오**: 가중치 초기화, 노이즈 추가

```python
# 기본 사용법
normal_tensor = torch.randn(3, 3)
print(normal_tensor)
# 출력: tensor([[-0.1276,  0.5846, -0.8667],
#              [-0.2233,  1.4459, -0.2951],
#              [-0.8948, -0.0125, -1.2220]])

print(f"Mean: {normal_tensor.mean():.4f}, Std: {normal_tensor.std():.4f}")
# 출력: Mean: -0.1611, Std: 0.8436

# Xavier 초기화 구현
input_dim, output_dim = 4, 3
xavier_std = (2.0 / (input_dim + output_dim)) ** 0.5
weights = torch.randn(input_dim, output_dim) * xavier_std
print(weights)
# 출력: tensor([[ 0.5456, -0.4515,  0.6135],
#              [-0.0812, -0.5416,  0.0402],
#              [ 0.4672,  0.7812, -0.2051],
#              [-0.5897, -0.1279,  0.4492]])
print(f"Xavier weight stats - Mean: {weights.mean():.4f}, Std: {weights.std():.4f}")
# 출력: Xavier weight stats - Mean: 0.0622, Std: 0.4477
```

**데이터 증강: 가우시안 노이즈 추가**
```python
# 작은 이미지에 노이즈 추가 (2x2 이미지 예시)
images = torch.rand(2, 2)
print("Original image:")
print(images)
# 출력: Original image:
#       tensor([[0.4963, 0.7682],
#               [0.0885, 0.1320]])

noise_level = 0.1
noise = torch.randn_like(images) * noise_level
noisy_images = images + noise
noisy_images = torch.clamp(noisy_images, 0, 1)  # [0, 1] 범위로 제한
print("Noisy image:")
print(noisy_images)
# 출력: Noisy image:
#       tensor([[0.5427, 0.8145],
#               [0.0943, 0.1893]])
```

### 3️⃣ torch.randint() - 정수 균일 분포

**사용 시나리오**: 클래스 레이블 생성, 인덱스 샘플링

```python
# 분류 문제를 위한 랜덤 레이블 생성
num_classes = 5
batch_size = 10
random_labels = torch.randint(0, num_classes, (batch_size,))
print(random_labels)
# 출력: tensor([4, 4, 3, 4, 4, 3, 3, 1, 3, 2])

unique_vals, counts = random_labels.unique(return_counts=True)
print(f"Label distribution: values={unique_vals.tolist()}, counts={counts.tolist()}")
# 출력: Label distribution: values=[1, 2, 3, 4], counts=[1, 1, 4, 4]

# 2차원 정수 텐서
int_matrix = torch.randint(low=10, high=20, size=(3, 4))
print(int_matrix)
# 출력: tensor([[16, 17, 10, 18],
#              [11, 14, 12, 17],
#              [18, 13, 14, 16]])

# 배치에서 랜덤 샘플 선택
total_samples = 100
batch_size = 5
batch_indices = torch.randint(0, total_samples, (batch_size,))
print(f"Selected indices: {batch_indices}")
# 출력: Selected indices: tensor([84, 26, 80, 55, 72])
```

---

## 💡 실전 활용 팁

### 1. 메모리 효율적인 텐서 생성
```python
# 큰 텐서는 dtype을 명시하여 메모리 절약
large_tensor = torch.zeros(1000, 1000, dtype=torch.float16)
memory_mb = large_tensor.element_size() * large_tensor.numel() / 1024**2
print(f"Memory usage: {memory_mb:.1f} MB")
# 출력: Memory usage: 1.9 MB

# float32와 비교
large_tensor_32 = torch.zeros(1000, 1000, dtype=torch.float32)
memory_mb_32 = large_tensor_32.element_size() * large_tensor_32.numel() / 1024**2
print(f"Memory usage (float32): {memory_mb_32:.1f} MB")
# 출력: Memory usage (float32): 3.8 MB
```

### 2. 배치 처리를 위한 브로드캐스팅 활용
```python
# 배치의 각 샘플에 다른 바이어스 추가
batch_data = torch.randn(3, 4)  # 3개 샘플, 4차원
bias = torch.arange(4).float()  # 4차원 바이어스
print("Batch data:")
print(batch_data)
# 출력: Batch data:
#       tensor([[-0.1115,  0.1204, -0.3696, -0.2404],
#               [-1.1969, -0.1097,  1.1050, -1.5701],
#               [ 0.4927,  0.7854, -0.4551,  0.7581]])

print("Bias:", bias)
# 출력: Bias: tensor([0., 1., 2., 3.])

result = batch_data + bias  # 자동 브로드캐스팅
print("Result after adding bias:")
print(result)
# 출력: Result after adding bias:
#       tensor([[-0.1115,  1.1204,  1.6304,  2.7596],
#               [-1.1969,  0.8903,  3.1050,  1.4299],
#               [ 0.4927,  1.7854,  1.5449,  3.7581]])
```

### 3. 같은 shape의 텐서 생성
```python
# 기존 텐서와 같은 shape로 생성
reference = torch.randn(2, 3)
print(f"Reference shape: {reference.shape}")
# 출력: Reference shape: torch.Size([2, 3])

zeros_like = torch.zeros_like(reference)
print("zeros_like:")
print(zeros_like)
# 출력: zeros_like:
#       tensor([[0., 0., 0.],
#               [0., 0., 0.]])

ones_like = torch.ones_like(reference)
print("ones_like:")
print(ones_like)
# 출력: ones_like:
#       tensor([[1., 1., 1.],
#               [1., 1., 1.]])

randn_like = torch.randn_like(reference)
print("randn_like:")
print(randn_like)
# 출력: randn_like:
#       tensor([[-0.5531,  1.3090, -0.2774],
#               [ 0.7712, -0.3763, -0.7993]])
```

### 4. 디바이스 간 이동 최소화
```python
# GPU에서 직접 생성하여 불필요한 복사 방지
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
# 출력: Using device: cuda (또는 cpu)

# 처음부터 올바른 디바이스에 생성
tensor = torch.randn(3, 3, device=device)
print(f"Tensor is on: {tensor.device}")
# 출력: Tensor is on: cuda:0 (또는 cpu)

# 잘못된 방법 (피해야 함)
# bad_tensor = torch.randn(3, 3)  # CPU에 생성
# bad_tensor = bad_tensor.to(device)  # GPU로 복사 (추가 시간 소요)
```

---

## 📊 함수별 사용 시나리오 요약

| 함수 | 주요 용도 | 예시 |
|------|-----------|------|
| `arange` | 인덱스, 시퀀스 생성 | 위치 인코딩, 시간 스텝 |
| `zeros` | 초기화, 마스킹 | 패딩 마스크, 누적 변수 |
| `ones` | 초기화, 마스킹 | Attention 마스크, 바이어스 초기화 |
| `rand` | 확률적 처리 | Dropout, 데이터 샘플링 |
| `randn` | 가중치 초기화 | Xavier/He 초기화, 노이즈 |
| `randint` | 이산 샘플링 | 레이블 생성, 인덱싱 |

이 가이드를 통해 PyTorch의 텐서 생성 함수들을 효과적으로 활용하여 더 나은 딥러닝 모델을 구축하기 바란다!
