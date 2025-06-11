---
layout: post
title: "(CNN) 파이토치 텐서 연산 - 내적과 행렬곱(dot, matmul)"
subtitle: "torch의 dot()과 matmul() 함수의 사용법과 차이점"
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: [star, fork, follow]
tags: [pytorch, tensor, matmul, dot, deep learning]
comments: true
filename: "2025-06-11-cnn-10-pytorch-tensor-matmul.md"
---

------------------------------------------------------

# (CNN) Pytorch Tensor 연산 - 내적과 행렬곱(dot, matmul)

* 최초 작성일: 2025년 6월 11일 (수)

## 목차

1. [torch.dot() - 벡터의 내적](#torchdot---벡터의-내적)
2. [torch.matmul() - 행렬곱](#torchmatmul---행렬곱)

---

## torch.dot() - 벡터의 내적

`torch.dot()` 함수는 두 1차원 벡터 간 내적(dot product)을 계산한다. **1차원 텐서만 가능**하다.

```python
import torch

# 1차원 텐서 생성
ts_01 = torch.arange(1, 4)
ts_02 = torch.arange(4, 7)
print('ts_01:', ts_01, 'ts_02:', ts_02)

# 내적 연산 수행
ts_03 = torch.dot(ts_01, ts_02)
print('내적 결과 ts_03:', ts_03)
```

출력 결과:

```
ts_01: tensor([1, 2, 3]) ts_02: tensor([4, 5, 6])
내적 결과 ts_03: tensor(32)
```

---

## torch.matmul() - 행렬곱

`torch.matmul()` 함수는 행렬 간 곱셈 연산을 수행한다. 이 연산은 **1차원-2차원, 2차원-2차원** 및 **3차원 이상의 텐서들 간**에도 가능하다.

### 2차원 텐서 간 행렬곱

```python
ts_01 = torch.arange(1, 7).view(2, 3)
ts_02 = torch.arange(7, 13).view(3, 2)
print('ts_01:\n', ts_01, '\nts_02:\n', ts_02)

# 행렬곱 수행
ts_03 = torch.matmul(ts_01, ts_02)
print('행렬곱 결과 ts_03:\n', ts_03)
```

출력 결과:

```
ts_01:
 tensor([[1, 2, 3],
         [4, 5, 6]])
ts_02:
 tensor([[ 7,  8],
         [ 9, 10],
         [11, 12]])
행렬곱 결과 ts_03:
 tensor([[ 58,  64],
         [139, 154]])
```

### 3차원 이상 텐서 간 행렬곱 (배치 처리)

3차원 이상 텐서의 경우 맨 뒤 두 차원은 행렬로 간주하고, 그 앞의 차원은 배치(batch)로 처리한다.

```python
ts_01 = torch.arange(0, 24).view(2, 3, 4)  # [배치=2, 행=3, 열=4]
ts_02 = torch.arange(0, 40).view(2, 4, 5)  # [배치=2, 행=4, 열=5]
print('ts_01:\n', ts_01, '\nts_02:\n', ts_02)

# 배치 행렬곱 수행
ts_03 = torch.matmul(ts_01, ts_02)
print('배치 행렬곱 결과 ts_03:\n', ts_03)
print('ts_03의 shape:', ts_03.shape)
```

출력 결과:

```
ts_01:
 tensor([[[ 0,  1,  2,  3],
          [ 4,  5,  6,  7],
          [ 8,  9, 10, 11]],

         [[12, 13, 14, 15],
          [16, 17, 18, 19],
          [20, 21, 22, 23]]])
ts_02:
 tensor([[[ 0,  1,  2,  3,  4],
          [ 5,  6,  7,  8,  9],
          [10, 11, 12, 13, 14],
          [15, 16, 17, 18, 19]],

         [[20, 21, 22, 23, 24],
          [25, 26, 27, 28, 29],
          [30, 31, 32, 33, 34],
          [35, 36, 37, 38, 39]]])

배치 행렬곱 결과 ts_03:
 tensor([[[ 70,  76,  82,  88,  94],
          [190, 212, 234, 256, 278],
          [310, 348, 386, 424, 462]],

         [[1340, 1396, 1452, 1508, 1564],
          [1740, 1812, 1884, 1956, 2028],
          [2140, 2228, 2316, 2404, 2492]]])
ts_03의 shape: torch.Size([2, 3, 5])
```

> **참고:** 배치 크기는 두 텐서가 같거나, 하나가 1이면 연산 가능하다.

---

이 문서를 통해 파이토치의 내적과 행렬곱 연산을 이해하고 실제 코드 작성에 활용할 수 있다.
