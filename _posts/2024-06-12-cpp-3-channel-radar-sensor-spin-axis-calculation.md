---
title: "(c++) 3채널 레이더 센서로 물체 운동의 스핀축 계산하기"
description: "위상차 이용 스핀축 계산 원리"
date: 2024-06-12 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, programming, radar sensor, phase difference, spin axis]
---

# 3채널 레이더 센서로 물체 운동의 스핀축 계산하기

- 최초 작성일: 2024년 6월 12일 (수)
  
## 내용

### 3채널 레이더 센서로 물체 운동의 스핀축 계산하기

3개 채널의 레이더 센서 수신부(RX)를 'ㄴ' 형태로 배치하고, 위 아래 채널 두 개로 상하 위상차를 구하고, 좌우 채널 두 개로 좌우 위상차를 구한 뒤, 해당 상하 위상차와 좌우 위상차 데이터를 이용해 스핀축을 계산하는 원리를 설명한다.

<br/>

#### 레이더 센서 배치 및 위상차 측정

1. **센서 배치**:
   - 3개의 레이더 센서를 'ㄴ' 형태로 배치한다.
     - 두 개의 RX 센서를 위와 아래에 배치하여 수직 위상차($$\phi_v$$)를 측정한다.
     - 두 개의 RX 센서를 좌우에 배치하여 수평 위상차($$\phi_h$$)를 측정한다.
       
2. **위상차 측정**:
   - 수직 위상차($$\phi_v$$)와 수평 위상차($$\phi_h$$)는 각각 수직 및 수평 방향에서의 공의 움직임에 따른 위상 차이를 나타낸다.
   - 이 위상차는 안테나 간 거리와 파장을 사용하여 각도로 변환할 수 있다.
     
<br/>

#### 변수의 의미

1. **lambda ($$\lambda$$)**: 파장
   - `lambda`는 레이더 신호의 파장을 나타낸다. 파장은 주파수와 속도의 관계를 나타내며, 특정 주파수의 신호가 공기 중에서 진행될 때의 거리이다.
   - 파장 $$\lambda$$는 주파수 $$f$$와 다음 관계를 가진다:
     
     $$\lambda = \frac{c}{f}$$
     
     여기서 $$c$$는 신호가 전파되는 매질의 속도 (예: 공기 중에서의 빛의 속도)이다.

2. **d**: 안테나 간 거리
   - `d`는 레이더 시스템의 송신 안테나(TX)와 수신 안테나(RX) 사이의 거리를 나타낸다. 이 거리는 위상차를 기반으로 각도를 계산하는 데 필수적인 요소이다.
   - 안테나 간 거리가 커질수록 위상차의 변화를 더 뚜렷하게 감지할 수 있다.
     
<br/>

#### 동작 원리

위상차를 이용하여 각도를 계산하는 기본 원리는 삼각법과 파동의 간섭 원리를 사용한다. 공의 움직임으로 인한 위상차를 통해 공의 운동 방향을 추정할 수 있다.

1. **위상차와 각도 간의 관계**:
   - 수직 위상차 $$\phi_v$$와 수평 위상차 $$\phi_h$$를 측정한 후, 이를 각도로 변환한다.
   - 위상차를 각도로 변환하는 식은 다음과 같다:
     
     $$\theta_v = \arcsin\left( \frac{\phi_v \cdot \lambda}{2 \pi d} \right)$$
     
     $$\theta_h = \arcsin\left( \frac{\phi_h \cdot \lambda}{2 \pi d} \right)$$
     
     여기서, $$\theta_v$$와 $$\theta_h$$는 각각 수직 및 수평 방향에서의 각도이다.
     
2. **각도의 계산**:
   - 위상차로부터 계산된 각도를 이용하여 공의 회전 벡터의 성분을 계산한다.
   - 수직 성분 $$V_z$$, 수평 성분 $$V_x$$, $$V_y$$를 계산한다:
     
     $$V_z = \sin(\theta_v)$$
     
     $$V_x = \cos(\theta_v) \cdot \cos(\theta_h)$$
     
     $$V_y = \cos(\theta_v) \cdot \sin(\theta_h)$$
     
3. **스핀축 각도의 계산**:
   - 최종적으로 회전축의 각도 $$\theta_{\text{spin}}$$은 다음과 같이 계산된다:
     
     $$\theta_{\text{spin}} = \arctan2(V_y, V_x) \times \frac{180.0}{\pi} \quad (\text{degrees로 변환})$$
     
   - 이 각도는 공의 회전축이 XY 평면에 대해 얼마나 기울어져 있는지를 나타낸다.
     
<br/>

#### 예시 코드

```cpp
double calculateSpinAxisAngle(double phaseV, double phaseH) {
    // lambda (wavelength), d (antenna distance)
    const double lambda = 0.03; // Example value in meters
    const double d = 0.1; // Example value in meters
    double theta_v = std::asin((phaseV * lambda) / (2 * M_PI * d));
    double theta_h = std::asin((phaseH * lambda) / (2 * M_PI * d));
    double V_z = std::sin(theta_v);
    double V_x = std::cos(theta_v) * std::cos(theta_h);
    double V_y = std::cos(theta_v) * std::sin(theta_h);
    double spinAxisAngle = std::atan2(V_y, V_x) * 180.0 / M_PI; // Convert to degrees
    return spinAxisAngle;
}
```

이 코드는 주어진 수직 및 수평 위상차를 이용하여 공의 회전축 각도를 계산한다. `lambda`와 `d`는 시스템에 따라 다를 수 있으며, 정확한 값을 사용하여야 정확한 각도를 계산할 수 있다.
