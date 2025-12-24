---
title: "(CNN) NumPy 배열과 PyTorch 텐서 간 상호 변환 방법"
description: "쉽고 빠르게 NumPy 배열과 PyTorch 텐서 변환하기"
date: 2025-05-29 10:00:00 +0900
categories: [Dev, CNN]
tags: [pytorch, tensor, numpy, deep learning, python]
---

------------------------------------------------

# NumPy 배열과 PyTorch 텐서 간 상호 변환 방법

* 최초 작성일: 2025년 5월 29일 (목)

## 목차

1. [NumPy 배열을 텐서로 변환하기](#numpy-배열을-텐서로-변환하기)
2. [텐서를 NumPy 배열 또는 리스트로 변환하기](#텐서를-numpy-배열-또는-리스트로-변환하기)
3. [GPU에 있는 텐서를 NumPy 배열로 변환하기](#gpu에-있는-텐서를-numpy-배열로-변환하기)
4. [메모리 공유와 복제(clone)](#메모리-공유와-복제clone)

---

## NumPy 배열을 텐서로 변환하기

NumPy 배열을 PyTorch 텐서로 변환하는 방법은 두 가지가 있다. 첫 번째는 `torch.tensor()` 함수를 사용하는 방법이고, 두 번째는 `torch.from_numpy()` 함수를 사용하는 방법이다. 아래의 예를 통해 쉽게 이해할 수 있다.

```python
import numpy as np
import torch

arr_01 = np.array([1, 2])
ts_01 = torch.tensor(arr_01)
ts_02 = torch.from_numpy(arr_01)

print(type(arr_01), ts_01, ts_02)
```

위 코드를 실행하면 NumPy 배열이 PyTorch 텐서로 변환되었음을 확인할 수 있다.

## 텐서를 NumPy 배열 또는 리스트로 변환하기

PyTorch 텐서를 다시 NumPy 배열이나 파이썬 리스트로 변환할 때는 `.numpy()` 메서드와 `.tolist()` 메서드를 사용한다.

```python
arr_01_1 = ts_01.numpy()
list_01 = ts_01.tolist()

print(arr_01_1, type(arr_01_1), list_01, type(list_01))
```

코드를 실행하면 텐서가 NumPy 배열과 파이썬 리스트로 변환된 것을 확인할 수 있다.

## GPU에 있는 텐서를 NumPy 배열로 변환하기

PyTorch 텐서가 GPU 상에 위치한 경우 바로 NumPy 배열로 변환할 수 없다. GPU에 있는 텐서를 NumPy 배열로 변환하려면 먼저 CPU로 이동한 후 변환해야 한다.

다음의 예는 GPU에 있는 텐서를 바로 NumPy 배열로 변환하려 할 때 발생하는 오류를 보여준다.

```python
ts_01 = torch.tensor([1, 2])
ts_01_1 = ts_01.to('cuda')

# 오류 발생 예시
arr_01_1 = ts_01_1.numpy()
```

이 코드는 다음과 같은 오류를 발생시킨다:

```text
TypeError: can't convert cuda:0 device type tensor to numpy. Use Tensor.cpu() to copy the tensor to host memory first.
```

올바른 방법은 아래와 같이 GPU 텐서를 먼저 CPU로 이동한 후 NumPy 배열로 변환하는 것이다.

```python
arr_01_1 = ts_01_1.cpu().numpy()
```

## 메모리 공유와 복제(clone)

`torch.from_numpy()`로 생성된 텐서는 원본 NumPy 배열과 메모리를 공유한다. 따라서 원본 배열의 값이 변경되면 텐서의 값도 함께 바뀐다.

```python
arr_01 = np.array([1, 2])
ts_01 = torch.from_numpy(arr_01)
print('변경 전 arr_01:', arr_01, '| ts_01:', ts_01)

arr_01[0] = 0
print('변경 후 arr_01:', arr_01, '| ts_01:', ts_01)
```

실행 결과에서 원본 배열이 변경되었을 때 텐서도 함께 변경된 것을 확인할 수 있다.

이를 방지하기 위해 텐서를 복제하려면 `.clone()` 메서드를 사용하면 된다.

```python
ts_02 = ts_01.clone()
arr_01[0] = 100
print('최종 변경 후 arr_01:', arr_01, '| ts_01:', ts_01, '| ts_02(복제):', ts_02)
```

복제된 텐서 `ts_02`는 원본 배열의 변경에 영향을 받지 않는 것을 확인할 수 있다.
