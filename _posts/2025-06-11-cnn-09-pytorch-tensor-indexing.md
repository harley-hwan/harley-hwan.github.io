---
title: "(CNN) Pytorch Tensor - Indexing"
description: "텐서의 다양한 인덱싱 기법과 numpy array와의 차이점까지"
date: 2025-06-11 10:00:00 +0900
categories: [Dev, CNN]
---

--------------------------------------------------------

# (CNN) Pytorch Tensor - Indexing

* 최초 작성일: 2025년 6월 11일 (수)

## 목차

1. [기본 indexing](#기본-indexing)
2. [슬라이싱(slicing) indexing](#슬라이싱slicing-indexing)
3. [Fancy(List) indexing](#fancylist-indexing)
4. [Boolean indexing](#boolean-indexing)
5. [torch.where 활용](#torchwhere-활용)

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
random_indexes: tensor([4, 2, 4, 0])
ts_01:
 tensor([[...], [...], [...], [...], [...]])
Fancy indexing 결과 ts_01_1:
 tensor([[...], [...], [...], [...]])
```

---

## Boolean indexing

Boolean indexing은 조건에 따라 원소를 선택한다. NumPy 배열과 다르게 PyTorch는 Boolean indexing 결과가 1차원 텐서로 반환된다.

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

---

이 문서를 통해 PyTorch 텐서의 다양한 indexing 방법과 NumPy 배열과의 차이를 명확하게 이해할 수 있다.
