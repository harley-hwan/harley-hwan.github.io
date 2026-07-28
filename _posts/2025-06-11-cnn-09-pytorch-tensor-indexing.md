---
title: "(CNN) Pytorch Tensor - Indexing"
description: "파이토치 텐서의 기본 인덱싱과 슬라이싱, fancy indexing, boolean indexing, torch.where 사용법을 예제 코드와 함께 정리한다."
date: 2025-06-11 10:00:00 +0900
categories: [Dev, CNN]
series: cnn
series_order: 9
tags: [pytorch, tensor, indexing, slicing, deep-learning]
---
## 기본 indexing

파이토치 텐서의 indexing 방법은 NumPy 배열과 매우 유사하다. 단일 지정 인덱싱을 하면 원본 텐서의 차원이 하나 줄어든 텐서가 반환된다.

```python
import torch

# 텐서 생성
ts_01 = torch.arange(0, 10).view(2, 5)
print(ts_01)
```

출력 결과:

```
tensor([[0, 1, 2, 3, 4],
        [5, 6, 7, 8, 9]])
```

단일 지정 인덱싱 예시:

```python
print('ts_01[0, 0]:', ts_01[0, 0], 'ts_01[0, 1]:', ts_01[0, 1])
print('ts_01[1, 0]:', ts_01[1, 0], 'ts_01[1, 2]:', ts_01[1, 2])
print(ts_01[0, 0].shape, ts_01[0, 0].ndim, ts_01[0, :].shape, ts_01[0, :].ndim)
```

출력 결과:

```
ts_01[0, 0]: tensor(0) ts_01[0, 1]: tensor(1)
ts_01[1, 0]: tensor(5) ts_01[1, 2]: tensor(7)
torch.Size([]) 0 torch.Size([5]) 1
```

---

## 슬라이싱(slicing) indexing

슬라이싱을 사용하면 원본 텐서의 차원이 유지된다.

```python
print('ts_01[0, :]은', ts_01[0, :], '\nts_01[:, 0]은', ts_01[:, 0])
print('ts_01[0, 0:3]은', ts_01[0, 0:3], '\nts_01[1, 1:4]은', ts_01[1, 1:4])
print('ts_01[:, :]\n', ts_01[:, :])
```

출력 결과:

```
ts_01[0, :]은 tensor([0, 1, 2, 3, 4])
ts_01[:, 0]은 tensor([0, 5])
ts_01[0, 0:3]은 tensor([0, 1, 2])
ts_01[1, 1:4]은 tensor([6, 7, 8])
ts_01[:, :]
 tensor([[0, 1, 2, 3, 4],
         [5, 6, 7, 8, 9]])
```

---

## Fancy(List) indexing

Fancy indexing은 지정한 인덱스 목록을 사용해 텐서의 특정 행을 추출하는 방법이다.

```python
torch.manual_seed(2025)
random_indexes = torch.randint(0, 5, size=(4,))
print('random_indexes:', random_indexes)

ts_01 = torch.rand(size=(10, 5))
print('ts_01:\n', ts_01)

ts_01_1 = ts_01[random_indexes]
print('Fancy indexing 결과 ts_01_1:\n', ts_01_1)
```

출력 결과:

```
random_indexes: tensor([1, 4, 4, 1])
ts_01:
 tensor([[0.7470, 0.0215, 0.0654, 0.7855, 0.3883],
        [0.6340, 0.9447, 0.4773, 0.2861, 0.3887],
        [0.1099, 0.3606, 0.8450, 0.8059, 0.0520],
        [0.3438, 0.5326, 0.5318, 0.0709, 0.8716],
        [0.6798, 0.2956, 0.9812, 0.9813, 0.8118],
        [0.0463, 0.9592, 0.5132, 0.3941, 0.6953],
        [0.7350, 0.0309, 0.8294, 0.3368, 0.6413],
        [0.6471, 0.5964, 0.9792, 0.8084, 0.9328],
        [0.8772, 0.1945, 0.5616, 0.6019, 0.5040],
        [0.0028, 0.2127, 0.0655, 0.0905, 0.2134]])
Fancy indexing 결과 ts_01_1:
 tensor([[0.6340, 0.9447, 0.4773, 0.2861, 0.3887],
        [0.6798, 0.2956, 0.9812, 0.9813, 0.8118],
        [0.6798, 0.2956, 0.9812, 0.9813, 0.8118],
        [0.6340, 0.9447, 0.4773, 0.2861, 0.3887]])
```

---

## Boolean indexing

Boolean indexing은 조건에 따라 원소를 선택한다. 결과는 NumPy 배열과 마찬가지로 조건을 만족하는 원소만 모은 1차원 텐서로 반환된다.

```python
ts_01 = torch.arange(0, 10).view(2, 5)
print(ts_01)
mask = ts_01 > 4
print(mask)
print('Boolean indexing 결과:', ts_01[mask])
```

출력 결과:

```
tensor([[0, 1, 2, 3, 4],
        [5, 6, 7, 8, 9]])
tensor([[False, False, False, False, False],
        [ True,  True,  True,  True,  True]])
Boolean indexing 결과: tensor([5, 6, 7, 8, 9])
```

---

## torch.where 활용

`torch.where`를 사용하면 원본 텐서의 차원을 유지하며 조건에 따라 값을 치환할 수 있다.

```python
print(torch.where(ts_01 > 4, input=ts_01, other=torch.tensor(999)))
```

출력 결과:

```
tensor([[999, 999, 999, 999, 999],
        [  5,   6,   7,   8,   9]])
```
