---
title: "(CNN) PyTorch 텐서 차원 조작: squeeze, unsqueeze, item"
description: "불필요한 차원 제거와 추가, 그리고 스칼라 값 추출하기"
date: 2025-05-30 10:00:00 +0900
categories: [Dev, CNN]
tags: [pytorch, tensor, squeeze, unsqueeze, item, dimension manipulation]
---

-------------------------------------------------------

# PyTorch : squeeze, unsqueeze, item

* 최초 작성일: 2025년 5월 30일 (금)

## 

딥러닝에서 텐서의 차원을 조작하는 것은 매우 빈번하게 발생하는 작업이다. 특히 다음과 같은 상황에서 필수적으로 사용된다.

모델이 기대하는 입력 형태와 실제 데이터의 형태가 다를 때가 많습니다. 

예를 들어, 단일 이미지를 처리하려는데 모델은 배치 입력을 기대하는 경우, 또는 배치 크기가 1인 출력을 단일 이미지로 변환해야 하는 경우가 있다. 

이때 squeeze와 unsqueeze가 핵심적인 역할을 한다.

```python
import torch

# : 
single_img = torch.rand(3, 224, 224)  # [C, H, W] 형태의 단일 이미지
print(f"단일 이미지 shape: {single_img.shape}")
# : shape: torch.Size([3, 224, 224])

# : [B, C, H, W]
# unsqueeze 
batch_img = single_img.unsqueeze(0)  # 첫 번째 위치에 차원 추가
print(f"배치 형태 shape: {batch_img.shape}")
# : shape: torch.Size([1, 3, 224, 224])
```

<img src="https://github.com/user-attachments/assets/e5600edc-16cb-4cf8-a1a7-a4d0fa9153c3" width="100%" alt="image">

---

## squeeze() - 1 

`squeeze()`는 텐서에서 크기가 1인 차원을 제거하는 함수이다. 이는 불필요한 차원을 정리하여 텐서를 더 간결하게 만들 때 유용하다.

### 

```python
torch.manual_seed(2025)

# 1 
ts_batch = tor한다.

```python
# 
t1 = torch.tensor(5.5)  # 0차원 스칼라
print(f"0D 텐서: {t1.item()}")
# : 0D : 5.5

t2 = torch.tensor([10])  # 1차원, 원소 1개
print(f"1D 단일 원소: {t2.item()}")
# : 1D : 10

# 
try:
    t3 = torch.tensor([1, 2, 3])  # 원소가 여러 개
    value = t3.item()
except ValueError as e:
    print(f"에러 발생: {e}")
# : : only one element tensors can be converted to Python scalars

# 1 
t4 = torch.tensor([[[5]]])  # 3차원이지만 원소는 1개
print(f"3D 단일 원소: {t4.item()}, shape: {t4.shape}")
# : 3D : 5, shape: torch.Size([1, 1, 1])
```

### : 

```python
# 
batch_size = 32
num_classes = 10

# 
loss_tensor = torch.tensor(0.3456)  # 손실값 (스칼라)
correct_preds = torch.tensor(28)     # 맞춘 개수
total_preds = torch.tensor(32)       # 전체 개수

# Python 
loss_value = loss_tensor.item()
accuracy = (correct_preds.float() / total_preds).item()

print(f"Epoch 5 - Loss: {loss_value:.4f}, Accuracy: {accuracy:.2%}")
# : Epoch 5 - Loss: 0.3456, Accuracy: 87.50%

# 
train_losses = []
train_accuracies = []

# 
for epoch in range(3):
    mock_loss = torch.rand(1) * 0.5  # 가상의 손실값
    mock_acc = torch.rand(1) * 0.3 + 0.7  # 70~100% 사이의 정확도
    
    # item()으로 추출하여 리스트에 저장
    train_losses.append(mock_loss.item())
    train_accuracies.append(mock_acc.item())
    
    print(f"Epoch {epoch}: Loss={train_losses[-1]:.4f}, Acc={train_accuracies[-1]:.2%}")
```

---

## 

### 1. 

```python
class ImagePreprocessor:
    """이미지 전처리를 위한 차원 조작 예제"""
    
    def prepare_single_image(self, img_path):
        # 실제로는 이미지를 로드하지만, 여기서는 더미 데이터 사용
        img_tensor = torch.rand(3, 224, 224)  # [C, H, W]
        
        # 정규화 등 전처리 수행 (생략)
        
        # 모델 입력을 위해 배치 차원 추가
        batch_input = img_tensor.unsqueeze(0)  # [1, C, H, W]
        return batch_input
    
    def postprocess_output(self, model_output):
        # 모델 출력: [1, num_classes]
        # 배치 차원 제거
        probs = model_output.squeeze(0)  # [num_classes]
        
        # 최대 확률과 클래스 추출
        max_prob, pred_class = probs.max(dim=0)
        
        # Python 값으로 변환
        return {
            'class': pred_class.item(),
            'confidence': max_prob.item()
        }

# 
processor = ImagePreprocessor()
dummy_output = torch.tensor([[0.1, 0.7, 0.2]])  # 3개 클래스 확률

result = processor.postprocess_output(dummy_output)
print(f"예측 클래스: {result['class']}, 신뢰도: {result['confidence']:.2%}")
# : : 1, : 70.00%
```

### 2. 

```python
def process_variable_batch(images_list):
    """가변 크기 배치를 처리하는 함수"""
    
    # 이미지 리스트: 각각 [C, H, W] 형태
    processed_images = []
    
    for img in images_list:
        # 필요한 경우 차원 확인 및 조정
        if img.dim() == 3:  # 단일 이미지
            img = img.unsqueeze(0)  # 배치 차원 추가
        processed_images.append(img)
    
    # 배치로 결합
    batch = torch.cat(processed_images, dim=0)
    
    # 배치 크기가 1인 경우 처리
    if batch.shape[0] == 1:
        print("단일 이미지 배치 감지")
        # 특별 처리 가능
    
    return batch

# 
img1 = torch.rand(3, 64, 64)
img2 = torch.rand(3, 64, 64)
img3 = torch.rand(3, 64, 64)

batch = process_variable_batch([img1, img2, img3])
print(f"최종 배치 shape: {batch.shape}")
# : shape: torch.Size([3, 3, 64, 64])
```

### 3. 

```python
class MetricTracker:
    """학습 중 메트릭을 추적하는 클래스"""
    
    def __init__(self):
        self.loss_history = []
        self.acc_history = []
        self.best_loss = float('inf')
    
    def update(self, loss_tensor, acc_tensor):
        # 텐서에서 스칼라 값 추출
        loss_val = loss_tensor.item() if loss_tensor.numel() == 1 else loss_tensor.mean().item()
        acc_val = acc_tensor.item() if acc_tensor.numel() == 1 else acc_tensor.mean().item()
        
        self.loss_history.append(loss_val)
        self.acc_history.append(acc_val)
        
        # 최고 성능 업데이트
        if loss_val < self.best_loss:
            self.best_loss = loss_val
            return True  # 새로운 최고 기록
        return False
    
    def get_latest_metrics(self):
        return {
            'loss': self.loss_history[-1] if self.loss_history else None,
            'accuracy': self.acc_history[-1] if self.acc_history else None,
            'best_loss': self.best_loss
        }

# 
tracker = MetricTracker()

# 
for epoch in range(5):
    # 가상의 손실과 정확도
    epoch_loss = torch.tensor(0.5 - epoch * 0.08 + torch.rand(1).item() * 0.05)
    epoch_acc = torch.tensor(0.6 + epoch * 0.07 + torch.rand(1).item() * 0.05)
    
    is_best = tracker.update(epoch_loss, epoch_acc)
    metrics = tracker.get_latest_metrics()
    
    print(f"Epoch {epoch}: Loss={metrics['loss']:.4f}, "
          f"Acc={metrics['accuracy']:.2%}, "
          f"Best={'Yes' if is_best else 'No'}")
```

---

## 

### 

| 함수 | 목적 | 필수 파라미터 | 반환값 |
|------|------|--------------|--------|
| `squeeze()` | 크기 1인 차원 제거 | dim (선택적) | 차원 축소된 텐서 |
| `unsqueeze()` | 크기 1인 차원 추가 | **dim (필수)** | 차원 확장된 텐서 |
| `item()` | 단일 값 추출 | 없음 | Python 스칼라 |

### 

**squeeze 사용 시 주의점**
```python
# 
img_batch = torch.rand(1, 3, 1, 224)  # [B=1, C, ?=1, W]

# 1 (!)
wrong = img_batch.squeeze()  # [3, 224] - 2개 차원이 사라짐!

# ()
correct = img_batch.squeeze(dim=0)  # [3, 1, 224] - 배치 차원만 제거
print(f"잘못된 방법: {wrong.shape}, 올바른 방법: {correct.shape}")
```

**unsqueeze vs reshape/view**
```python
# , 
tensor = torch.rand(3, 4)

# unsqueeze 
method1 = tensor.unsqueeze(1)  # [3, 1, 4]

# view/reshape 
method2 = tensor.view(3, 1, 4)  # [3, 1, 4]
method3 = tensor.reshape(3, 1, 4)  # [3, 1, 4]

print(f"모두 동일: {torch.allclose(method1, method2) and torch.allclose(method2, method3)}")
# : : True

# unsqueeze 
```

**item() 활용 팁**
```python
# 
batch_losses = torch.tensor([0.5, 0.3, 0.4, 0.6])

# 1: mean() item()
avg_loss1 = batch_losses.mean().item()

# 2: sum() 
avg_loss2 = (batch_losses.sum() / len(batch_losses)).item()

print(f"평균 손실: {avg_loss1:.4f}")
# : : 0.4500
```

이러한 차원 조작 함수들은 PyTorch에서 매우 자주 사용되는 핵심 도구이다. 

특히 모델의 입출력 형태를 맞추거나, 시각화를 위해 차원을 조정하거나, 학습 메트릭을 추적할 때 필수적으로 활용된다.

각 함수의 특성을 잘 이해하고 적절히 활용하면 더 효율적이고 에러가 적은 코드를 작성할 수 있다.
