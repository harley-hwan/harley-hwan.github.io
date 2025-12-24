---
title: "(CNN) PyTorch Tensor 집계 연산"
description: "sum, min, max, mean과 argmax를 활용한 데이터 집계"
date: 2025-05-29 10:00:00 +0900
categories: [Dev, CNN]
tags: [pytorch, tensor, aggregation, sum, mean, max, min, argmax, deep learning]
---

# PyTorch 집계 연산

* 최초 작성일: 2025년 5월 29일 (목)

## 집계 연산의 이해

집계(aggregation) 연산은 텐서의 여러 값을 하나 또는 더 적은 수의 값으로 요약하는 핵심 연산이다. 딥러닝에서는 손실 계산, 통계 분석, 특징 추출 등에 필수적으로 사용된다.

### 주요 집계 함수
- **sum**: 원소들의 합
- **mean**: 평균값
- **max/min**: 최대/최소값
- **std/var**: 표준편차/분산
- **argmax/argmin**: 최대/최소값의 인덱스

```python
import torch

# 1D 텐서 예제
scores = torch.tensor([85.5, 92.3, 78.9, 95.1, 88.7])
print(f"학생 점수: {scores}")
# 출력: 학생 점수: tensor([85.5000, 92.3000, 78.9000, 95.1000, 88.7000])

print(f"총점: {scores.sum():.1f}")
# 출력: 총점: 440.5

print(f"평균: {scores.mean():.1f}")
# 출력: 평균: 88.1

print(f"최고점: {scores.max():.1f}")
# 출력: 최고점: 95.1

print(f"최저점: {scores.min():.1f}")
# 출력: 최저점: 78.9
```

<br/>

<div align="center">
  <img src="https://github.com/user-attachments/assets/86930e98-093b-4e23-bab6-d36e1644a311" width="1800" alt="집계 연산 시각화">
</div>

---

## 기본 집계 함수 사용하기

### 2D 텐서 집계
```python
# 2D 텐서 예제: 5명 학생 x 3과목
grades = torch.tensor([
    [85, 90, 88],  # 학생 1
    [92, 88, 95],  # 학생 2
    [78, 85, 82],  # 학생 3
    [90, 92, 91],  # 학생 4
    [88, 86, 89]   # 학생 5
], dtype=torch.float32)

print("성적표:")
print(grades)
# 출력: 성적표:
# tensor([[85., 90., 88.],
#         [92., 88., 95.],
#         [78., 85., 82.],
#         [90., 92., 91.],
#         [88., 86., 89.]])

# 전체 통계
print(f"전체 평균: {grades.mean():.2f}")
# 출력: 전체 평균: 87.87

print(f"전체 최고점: {grades.max()}")
# 출력: 전체 최고점: 95.0

print(f"전체 최저점: {grades.min()}")
# 출력: 전체 최저점: 78.0

print(f"전체 합계: {grades.sum()}")
# 출력: 전체 합계: 1318.0
```

### 추가 통계 함수
```python
# 분산과 표준편차
print(f"표준편차: {grades.std():.2f}")
# 출력: 표준편차: 4.89

print(f"분산: {grades.var():.2f}")
# 출력: 분산: 23.92

# 중앙값과 분위수
print(f"중앙값: {grades.median()}")
# 출력: 중앙값: 88.0

print(f"75% 분위수: {grades.quantile(0.75)}")
# 출력: 75% 분위수: 91.0
```

---

## 차원별 집계 연산

`dim` 파라미터를 사용하면 특정 차원을 따라 집계를 수행할 수 있다. 이는 딥러닝에서 배치 통계, 채널별 정규화 등에 필수적이다.

### dim 파라미터 이해하기
```python
# 3x4 행렬
mat = torch.arange(12).reshape(3, 4)
print("원본 행렬:")
print(mat)
# 출력: 원본 행렬:
# tensor([[ 0,  1,  2,  3],
#         [ 4,  5,  6,  7],
#         [ 8,  9, 10, 11]])

# dim=0: 행 방향으로 집계 (각 열의 합)
print("\ndim=0 집계 (각 열의 합):")
print(mat.sum(dim=0))
# 출력: dim=0 집계 (각 열의 합):
# tensor([12, 15, 18, 21])

# dim=1: 열 방향으로 집계 (각 행의 합) 
print("\ndim=1 집계 (각 행의 합):")
print(mat.sum(dim=1))
# 출력: dim=1 집계 (각 행의 합):
# tensor([ 6, 22, 38])
```

### 실전 예제
```python
# 성적표 활용
print("성적표 shape:", grades.shape)  # [5 학생, 3 과목]
# 출력: 성적표 shape: torch.Size([5, 3])

# 과목별 평균 (dim=0: 학생 차원 집계)
subj_avg = grades.mean(dim=0)
print(f"과목별 평균: {subj_avg}")
# 출력: 과목별 평균: tensor([86.6000, 88.2000, 89.0000])

# 학생별 평균 (dim=1: 과목 차원 집계)
stud_avg = grades.mean(dim=1)
print(f"학생별 평균: {stud_avg}")
# 출력: 학생별 평균: tensor([87.6667, 91.6667, 81.6667, 91.0000, 87.6667])
```

### max와 min의 특별한 반환값
```python
# max와 min은 값과 인덱스를 함께 반환
print("\n과목별 최고점과 해당 학생 인덱스:")
max_vals, max_idx = grades.max(dim=0)
print(f"최고점: {max_vals}")
# 출력: 최고점: tensor([92., 92., 95.])

print(f"학생 인덱스: {max_idx}")
# 출력: 학생 인덱스: tensor([1, 3, 1])

print("\n학생별 최고 과목:")
max_vals, max_idx = grades.max(dim=1)
print(f"최고점: {max_vals}")
# 출력: 최고점: tensor([90., 95., 85., 92., 89.])

print(f"과목 인덱스: {max_idx}")
# 출력: 과목 인덱스: tensor([1, 2, 1, 1, 2])
```

---

## 다중 차원 집계

여러 차원을 동시에 집계할 수 있다. 이는 고차원 텐서를 다룰 때 특히 유용하다.

### 3D 텐서 집계
```python
# 3D 텐서: 2개 반, 4명 학생, 3과목
class_scores = torch.arange(24).reshape(2, 4, 3)
print("반별 성적 데이터:")
print(class_scores)
# 출력: 반별 성적 데이터:
# tensor([[[ 0,  1,  2],
#          [ 3,  4,  5],
#          [ 6,  7,  8],
#          [ 9, 10, 11]],
#         [[12, 13, 14],
#          [15, 16, 17],
#          [18, 19, 20],
#          [21, 22, 23]]])

# 차원별 집계 결과 형태
print(f"\n원본 shape: {class_scores.shape}")
# 출력: 원본 shape: torch.Size([2, 4, 3])

print(f"dim=0 sum shape: {class_scores.sum(dim=0).shape}")
# 출력: dim=0 sum shape: torch.Size([4, 3])

print("dim=0 sum (반 차원 집계):")
print(class_scores.sum(dim=0))
# 출력: dim=0 sum (반 차원 집계):
# tensor([[12, 14, 16],
#         [18, 20, 22],
#         [24, 26, 28],
#         [30, 32, 34]])
```
<br/>

<div align="center">
  <img src="https://github.com/user-attachments/assets/936ac5f1-b3c8-4c2a-9253-1eade3a49ac8" width="1800" alt="다중 차원 집계 시각화">
</div>

### 다중 차원 동시 집계
```python
# 여러 차원 동시 집계
print("\ndim=(1,2) 집계 (각 반의 전체 합):")
class_totals = class_scores.sum(dim=(1, 2))
print(class_totals)
# 출력: dim=(1,2) 집계 (각 반의 전체 합):
# tensor([ 66, 210])

# 순서는 상관없음
print("dim=(2,1) 집계 (동일한 결과):")
print(class_scores.sum(dim=(2, 1)))
# 출력: dim=(2,1) 집계 (동일한 결과):
# tensor([ 66, 210])

# 음수 인덱스 사용
print("\ndim=-1 집계 (마지막 차원):")
print(class_scores.sum(dim=-1))
# 출력: dim=-1 집계 (마지막 차원):
# tensor([[ 3, 12, 21, 30],
#         [39, 48, 57, 66]])

print("\ndim=(-2,-1) 집계 (마지막 두 차원):")
print(class_scores.sum(dim=(-2, -1)))
# 출력: dim=(-2,-1) 집계 (마지막 두 차원):
# tensor([ 66, 210])
```

### keepdim 파라미터
```python
# keepdim=True로 차원 유지
orig = torch.randn(3, 4, 5)
print(f"원본 shape: {orig.shape}")
# 출력: 원본 shape: torch.Size([3, 4, 5])

# keepdim=False (기본값)
reduced = orig.mean(dim=1)
print(f"keepdim=False: {reduced.shape}")
# 출력: keepdim=False: torch.Size([3, 5])

# keepdim=True
kept = orig.mean(dim=1, keepdim=True)
print(f"keepdim=True: {kept.shape}")
# 출력: keepdim=True: torch.Size([3, 1, 5])
```

---

## argmax와 argmin 활용

`argmax`와 `argmin`은 최대/최소값의 위치(인덱스)를 반환한다. 분류 문제에서 예측 클래스를 찾거나, 가장 중요한 특징을 선택할 때 필수적이다.

### 기본 사용법
```python
torch.manual_seed(2025)

# 1D 텐서에서 위치 찾기
probs = torch.rand(10)
print(f"확률 분포: {probs}")
# 출력: 확률 분포: tensor([0.1947, 0.9379, 0.0840, 0.4652, 0.7508, 0.9644, 0.8788, 0.0567,
#                         0.9274, 0.5426])

print(f"최대값: {probs.max():.4f}, 위치: {probs.argmax()}")
# 출력: 최대값: 0.9644, 위치: 5

print(f"최소값: {probs.min():.4f}, 위치: {probs.argmin()}")
# 출력: 최소값: 0.0567, 위치: 7
```

### 분류 문제에서의 활용
```python
# 배치 분류 결과: 5개 샘플, 4개 클래스
logits = torch.randn(5, 4)
print("분류 로짓:")
print(logits)
# 출력: 분류 로짓:
# tensor([[ 0.3847, -0.6459,  1.2128, -0.3121],
#         [-0.8891,  0.7265,  0.1909, -1.5430],
#         [ 0.9061, -0.3742, -0.8321,  1.0216],
#         [-0.4639,  0.5442, -1.1524,  0.8927],
#         [ 1.3589, -0.7286, -0.2446,  0.5043]])

# 각 샘플의 예측 클래스
predictions = logits.argmax(dim=1)
print(f"예측 클래스: {predictions}")
# 출력: 예측 클래스: tensor([2, 1, 3, 3, 0])

# Softmax 후 argmax
probs = torch.softmax(logits, dim=1)
print("\nSoftmax 확률:")
print(probs)
# 출력: Softmax 확률:
# tensor([[0.2286, 0.0825, 0.5246, 0.1143],
#         [0.1029, 0.5199, 0.3037, 0.0536],
#         [0.3654, 0.1023, 0.0651, 0.4072],
#         [0.1208, 0.3376, 0.0616, 0.4800],
#         [0.5544, 0.0679, 0.1125, 0.2451]])

# 확률 기반 예측 (결과 동일)
prob_predictions = probs.argmax(dim=1)
print(f"확률 기반 예측: {prob_predictions}")
# 출력: 확률 기반 예측: tensor([2, 1, 3, 3, 0])
```

### top-k 값 찾기
```python
# 상위 k개 값과 인덱스
values = torch.randn(10)
print(f"원본 값: {values}")
# 출력: 원본 값: tensor([-0.3456, 1.2345, -0.7890, 2.3456, 0.1234, -1.5678, 0.9876,
#                       1.8765, -0.4567, 0.5678])

# 상위 3개
top3_vals, top3_idx = torch.topk(values, k=3)
print(f"상위 3개 값: {top3_vals}")
# 출력: 상위 3개 값: tensor([2.3456, 1.8765, 1.2345])

print(f"상위 3개 인덱스: {top3_idx}")
# 출력: 상위 3개 인덱스: tensor([3, 7, 1])

# 하위 3개 (largest=False)
bottom3_vals, bottom3_idx = torch.topk(values, k=3, largest=False)
print(f"하위 3개 값: {bottom3_vals}")
# 출력: 하위 3개 값: tensor([-1.5678, -0.7890, -0.4567])

print(f"하위 3개 인덱스: {bottom3_idx}")
# 출력: 하위 3개 인덱스: tensor([5, 2, 8])
```

---

## 실전 활용 예제

### 1. 배치 정규화 통계 계산
```python
# 이미지 배치 정규화
# [배치, 채널, 높이, 너비] 형태의 이미지 배치
batch_imgs = torch.randn(32, 3, 64, 64)

# 채널별 평균과 표준편차 계산 (배치, 높이, 너비 차원 집계)
channel_mean = batch_imgs.mean(dim=(0, 2, 3), keepdim=True)
channel_std = batch_imgs.std(dim=(0, 2, 3), keepdim=True)

print(f"원본 shape: {batch_imgs.shape}")
# 출력: 원본 shape: torch.Size([32, 3, 64, 64])

print(f"채널별 평균 shape: {channel_mean.shape}")
# 출력: 채널별 평균 shape: torch.Size([1, 3, 1, 1])

print(f"채널별 평균값: {channel_mean.squeeze()}")
# 출력: 채널별 평균값: tensor([-0.0012,  0.0023, -0.0008])

# 정규화 수행
normalized = (batch_imgs - channel_mean) / (channel_std + 1e-5)
```

### 2. 어텐션 스코어 분석
```python
# 어텐션 가중치 분석
attn_scores = torch.randn(8, 12, 100, 100)  # [배치, 헤드, 시퀀스, 시퀀스]

# 최대 어텐션 위치 찾기
max_attn_idx = attn_scores.argmax(dim=-1)
print(f"최대 어텐션 위치 shape: {max_attn_idx.shape}")
# 출력: 최대 어텐션 위치 shape: torch.Size([8, 12, 100])

# 헤드별 평균 어텐션
attn_mean = attn_scores.mean(dim=(2, 3))
attn_max = attn_scores.max(dim=(2, 3))[0]
print(f"헤드별 평균 어텐션: {attn_mean.shape}")
# 출력: 헤드별 평균 어텐션: torch.Size([8, 12])
```

### 3. 손실 함수 계산
```python
# 배치 손실 집계
individual_losses = torch.rand(128)  # 128개 샘플의 손실

# 다양한 집계 방식
mean_loss = individual_losses.mean()
sum_loss = individual_losses.sum()
max_loss = individual_losses.max()

print(f"평균 손실: {mean_loss:.4f}")
# 출력: 평균 손실: 0.4987

print(f"총 손실: {sum_loss:.4f}")
# 출력: 총 손실: 63.8336

print(f"최대 손실: {max_loss:.4f}")
# 출력: 최대 손실: 0.9934

# 상위 10% 어려운 샘플만 선택 (Hard negative mining)
k = int(0.1 * len(individual_losses))
hard_losses, _ = torch.topk(individual_losses, k)
hard_mean = hard_losses.mean()
print(f"상위 10% 어려운 샘플 평균 손실: {hard_mean:.4f}")
# 출력: 상위 10% 어려운 샘플 평균 손실: 0.9523
```

---

## 함수 요약

| 함수 | 용도 | 반환값 | 주요 옵션 |
|------|------|--------|----------|
| `sum` | 합계 | 텐서 | dim, keepdim |
| `mean` | 평균 | 텐서 | dim, keepdim, dtype |
| `max/min` | 최대/최소 | (값, 인덱스) | dim, keepdim |
| `std/var` | 표준편차/분산 | 텐서 | dim, keepdim, unbiased |
| `argmax/argmin` | 최대/최소 인덱스 | 인덱스 텐서 | dim, keepdim |
| `topk` | 상위 k개 | (값, 인덱스) | k, dim, largest |

집계 연산은 딥러닝의 모든 단계에서 사용되는 핵심 기능이다. 이 가이드를 통해 다양한 상황에서 적절한 집계 함수를 선택하고 활용할 수 있기를 바란다!
