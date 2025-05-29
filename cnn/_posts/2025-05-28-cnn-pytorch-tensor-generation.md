---
layout: post
title: "(CNN) 파이토치 텐서 생성 - arange, zeros, ones, random"
subtitle: "arange와 기본 텐서 생성 함수 및 난수 생성 함수 완전 정복"
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: \[star, fork, follow]
tags: \[pytorch, tensor, random, arange, deep learning]
comments: true
filename: "2025-05-28-cnn-pytorch-tensor-generation.md"
---

-------------------------------------------------------

# (CNN) 파이토치 텐서 생성 - arange, zeros, ones, random

* 최초 작성일: 2025년 5월 28일 (수)

## 목차

1. [arange를 이용한 연속 텐서 생성](#arange를-이용한-연속-텐서-생성)
2. [0 또는 1로 채워진 텐서 생성](#0-또는-1로-채워진-텐서-생성)
3. [난수 텐서 생성](#난수-텐서-생성)

---

## arange를 이용한 연속 텐서 생성

`torch.arange()`는 정수 또는 실수 범위의 연속된 숫자들을 가지는 텐서를 생성할 수 있는 함수다.

```python
torch.arange(start=0, end, step=1, *, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

* `start` (선택): 시작값 (기본값은 0)
* `end`: 종료값 (end 값은 포함되지 않음)
* `step` (선택): 증가 간격 (기본값은 1)
* `dtype`: 데이터 타입
* `device`: 생성할 장치 (CPU/GPU)

```python
seq_tensor = torch.arange(10)
seq_tensor_int = torch.arange(10, dtype=torch.int32)

print(seq_tensor)
print(seq_tensor_int)
print(seq_tensor.dtype)
print(seq_tensor.shape)
```

**출력 결과:**

```
tensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
tensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=torch.int32)
torch.int64
torch.Size([10])
```

<br>

```python
custom_range = torch.arange(start=2, end=9)
print(custom_range)
```

**출력 결과:**

```
tensor([2, 3, 4, 5, 6, 7, 8])
```

---

## 0 또는 1로 채워진 텐서 생성

`torch.zeros()`와 `torch.ones()`는 모든 원소가 각각 0 또는 1인 텐서를 생성할 때 사용된다.

```python
torch.zeros(*size, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
torch.ones(*size, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

* `size`: 텐서의 shape (튜플 또는 개별 인자)
* `dtype`: 데이터 타입 (예: torch.float32, torch.int64 등)
* `device`: 생성할 장치 (예: "cpu", "cuda")
* `requires_grad`: 자동 미분 대상 여부

```python
zero_tensor = torch.zeros(size=(3, 2), dtype=torch.int32)
print(zero_tensor)
print(zero_tensor.dtype, zero_tensor.shape)
```

**출력 결과:**

```
tensor([[0, 0],
        [0, 0],
        [0, 0]], dtype=torch.int32)
torch.int32 torch.Size([3, 2])
```

<br>

```python
one_tensor = torch.ones(3, 2, dtype=torch.int16)
print(one_tensor)
print(one_tensor.dtype, one_tensor.shape)
```

**출력 결과:**

```
tensor([[1, 1],
        [1, 1],
        [1, 1]], dtype=torch.int16)
torch.int16 torch.Size([3, 2])
```

---

## 난수 텐서 생성

난수 생성은 딥러닝에서 매우 자주 사용되며, PyTorch는 다양한 난수 생성 함수를 제공한다. 일정한 출력을 위해 `torch.manual_seed()`로 시드를 설정할 수 있다.

```python
torch.manual_seed(2025)
```

### 1. `torch.rand()` - 균일 분포 난수

```python
torch.rand(*size, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

0 이상 1 미만의 균일 분포를 따르는 float32 난수를 생성한다.

```python
uniform_tensor = torch.rand(size=(3, 4))
print(uniform_tensor)
print(uniform_tensor.dtype)
print(uniform_tensor.min(), uniform_tensor.max())
```

**출력 결과:**

```
tensor([[0.3786, 0.8113, 0.1768, 0.6552],
        [0.1755, 0.6170, 0.1070, 0.0447],
        [0.8400, 0.1595, 0.7824, 0.8486]])
torch.float32
tensor(0.0447) tensor(0.8486)
```

<br>

### 2. `torch.randint()` - 정수형 난수

```python
torch.randint(low, high, size, *, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

* `low`: 최소값 (포함)
* `high`: 최대값 (미포함)
* `size`: 생성할 텐서 크기

```python
int_random_tensor = torch.randint(low=0, high=100, size=(3, 4))
print(int_random_tensor)
print(int_random_tensor.dtype)
print(int_random_tensor.min(), int_random_tensor.max())
```

**출력 결과:**

```
tensor([[18, 85,  3, 38],
        [65, 93, 22, 95],
        [79,  9, 59, 41]])
torch.int64
tensor(3) tensor(95)
```

<br>

### 3. `torch.randn()` - 정규 분포 난수

```python
torch.randn(*size, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False)
```

평균이 0이고 분산이 1인 정규 분포를 따르는 float32 값을 생성한다.

```python
normal_tensor = torch.randn(size=(3, 4))
print(normal_tensor)
print(normal_tensor.dtype)
print(normal_tensor.min(), normal_tensor.max())
print(normal_tensor.mean(), normal_tensor.var())
```

**출력 결과:**

```
tensor([[ 0.2882, -1.0877, -0.2176,  1.2556],
        [-0.2681, -0.3065,  0.4733,  0.2659],
        [-0.0685, -0.5889,  0.7427, -0.3033]])
torch.float32
tensor(-1.0877) tensor(1.2556) tensor(0.0084) tensor(0.4382)
```
