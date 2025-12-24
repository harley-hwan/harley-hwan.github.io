---
title: "(CNN) Pytorch의 Tensor 생성, Shape, 차원, 타입"
description: ""텐서 생성 방법부터 형태, 차원 및 데이터 타입 관리까지 상세 설명""
date: 2025-05-28 10:00:00 +0900
categories: [Dev, CNN]
tags: [pytorch, tensor, numpy, deep learning, python]
---

---------------------------------------------------

# Pytorch의 Tensor 생성, Shape, 차원, 타입

* 최초 작성일: 2025년 5월 28일 (수)

## 목차

1. [텐서 생성하기](#텐서-생성하기)
2. [텐서의 형태(shape)와 차원](#텐서의-형태shape와-차원)
3. [텐서 데이터 타입(dtype)](#텐서-데이터-타입dtype)
4. [NumPy와의 차이점](#numpy와의-차이점)

---

## 텐서 생성하기

파이토치의 텐서는 스칼라, 파이썬 리스트, NumPy 배열, 기존 텐서를 기반으로 생성할 수 있다. 아래 예제를 통해 확인할 수 있다.

```python
import numpy as np
import torch

list_01 = [1, 2, 3]
ts_01 = torch.tensor(list_01)
ts_02 = torch.tensor([[1, 2, 3], [2, 3, 4]])
ts_03 = torch.tensor([[[1, 2, 3], [2, 3, 4]], [[3, 4, 5], [4, 5, 6]]])

print('ts_01:', ts_01.shape, 'ts_02 shape:', ts_02.shape, 'ts_03 shape:', ts_03.shape)
```

**출력 결과:**

```text
ts_01: torch.Size([3]) ts_02 shape: torch.Size([2, 3]) ts_03 shape: torch.Size([2, 2, 3])
```

## 텐서의 형태(shape)와 차원

파이토치 텐서의 형태(shape)는 `.shape` 속성이나 `.size()` 메서드를 사용하여 확인할 수 있다. 두 메서드는 동일한 결과를 반환한다.

```python
print(ts_02.shape, ts_02.size())
```

**출력 결과:**

```text
torch.Size([2, 3]) torch.Size([2, 3])
```

특정 차원의 크기를 확인할 때는 다음과 같이 인덱싱하거나, `.size()`의 인자를 사용할 수 있다.

```python
print(ts_02.shape[0], ts_02.shape[1], ts_02.size(0), ts_02.size(1), ts_02.size()[0])
```

**출력 결과:**

```text
2 3 2 3 2
```

텐서의 차원 수만 확인하고 싶다면 `.ndim` 속성을 이용한다.

```python
print(ts_02.ndim)
```

**출력 결과:**

```text
2
```

## 텐서 데이터 타입(dtype)

텐서 내 모든 값은 동일한 데이터 타입(dtype)을 가진다. 데이터 타입은 텐서 생성 시 지정하거나, 생성 후 변환 가능하다.

```python
ts_01 = torch.tensor([1.0, 2, 3])
print(ts_01.dtype)  # float32

# 생성 시 dtype 지정
ts_01 = torch.tensor([1, 2, 3], dtype=torch.float32)
print(ts_01.dtype)  # float32

# 타입 변환
# int32로 변환
ts_01_1 = ts_01.int()
print(ts_01_1.dtype)  # int32

# float32로 변환
ts_01_2 = ts_01.float()
print(ts_01_2.dtype)  # float32

# type() 메소드 사용
ts_01_1 = ts_01.type(torch.int64)
print(ts_01_1.dtype)  # int64

# 다른 타입으로 변환 (int8)
ts_01_2 = ts_01.type(torch.int8)
print(ts_01_2.dtype)  # int8

# to() 메소드 사용
ts_01_1 = ts_01.to(torch.int64)
print(ts_01_1.dtype)  # int64

ts_01_2 = ts_01.to(torch.int8)
print(ts_01_2.dtype)  # int8
```

**출력 결과:**

```text
torch.float32
torch.float32
torch.int32
torch.float32
torch.int64
torch.int8
torch.int64
torch.int8
```

## NumPy와의 차이점

NumPy 배열과 파이토치 텐서는 상당히 유사하지만 중요한 차이가 존재한다.

* NumPy 배열은 주로 CPU에서만 연산되며 GPU 연산을 지원하지 않는다.
* 파이토치 텐서는 CPU와 GPU 모두에서 연산 가능하며, GPU를 통해 병렬 연산을 수행하여 속도를 크게 향상시킬 수 있다.
* 텐서는 자동 미분 기능과 같은 딥러닝에 특화된 연산들을 지원한다.

이러한 차이점으로 인해 파이토치 텐서는 딥러닝 모델 구현과 학습에 널리 사용된다.

---

이번 문서에서는 파이토치의 텐서 생성 방법, shape, 차원, 데이터 타입 관리에 대해 상세히 설명하고, NumPy 배열과의 주요 차이점도 함께 살펴보았다. 다음 문서에서는 텐서의 다양한 연산들에 대해 살펴볼 예정이다.
