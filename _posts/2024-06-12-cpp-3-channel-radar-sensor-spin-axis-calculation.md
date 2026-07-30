---
title: "(C++) 3채널 레이다 센서로 물체 운동의 스핀축 계산하기"
description: "위상차 이용 스핀축 계산 원리"
date: 2024-06-12 10:00:00 +0900
categories: [Dev, Radar]
tags: [cpp, radar, radar-sensor, phase-difference, spin-axis, aoa]
math: true
---
## 내용

### 3채널 레이다 센서로 물체 운동의 스핀축 계산하기

3개 채널의 레이다 센서 수신부(RX)를 'ㄴ' 형태로 배치하고, 위 아래 채널 두 개로 상하 위상차를 구하고, 좌우 채널 두 개로 좌우 위상차를 구한 뒤, 해당 상하 위상차와 좌우 위상차 데이터를 이용해 스핀축을 계산하는 원리를 정리한다.

> [레이다 시리즈](/posts/radar-series-index/) [7장](/posts/cw-receive-chain-cpp/)의 각도 계산을 두 축으로 확장한 것이다. 위상차를 채널에서 뽑아내는 부분 — 같은 도플러 빈에서 켤레곱으로 위상차를 구하고 채널 간 오프셋을 빼는 절차 — 은 7장에 있고, 여기서는 그렇게 얻은 $\phi_v$와 $\phi_h$가 이미 있다고 두고 시작한다.
{: .prompt-tip }

<br/>

#### 레이다 센서 배치 및 위상차 측정

3개의 레이다 센서를 'ㄴ' 형태로 배치한다. 두 개의 RX 센서를 위와 아래에 배치하여 수직 위상차($\phi_v$)를 측정하고, 두 개의 RX 센서를 좌우에 배치하여 수평 위상차($\phi_h$)를 측정한다.

수직 위상차($\phi_v$)와 수평 위상차($\phi_h$)는 각각 수직 및 수평 방향에서의 공의 움직임에 따른 위상 차이를 나타내며, 안테나 간 거리와 파장을 사용하여 각도로 변환할 수 있다.

<br/>

#### 변수의 의미

1. lambda ($\lambda$): 파장
   - `lambda`는 레이다 신호의 파장을 나타낸다. 파장은 주파수와 속도의 관계를 나타내며, 특정 주파수의 신호가 공기 중에서 진행될 때의 거리이다.
   - 파장 $\lambda$는 주파수 $f$와 다음 관계를 가진다:
     
     $$\lambda = \frac{c}{f}$$
     
     여기서 $c$는 신호가 전파되는 매질의 속도 (예: 공기 중에서의 빛의 속도)이다.

2. d: 안테나 간 거리
   - `d`는 위상차를 측정하는 두 수신 안테나(RX) 사이의 간격을 나타낸다. 이 거리는 위상차를 기반으로 각도를 계산하는 데 필수적인 요소이다.
   - 안테나 간 거리가 커질수록 위상차의 변화를 더 뚜렷하게 감지할 수 있다.

<br/>

> **간격을 키우면 정밀도와 시야를 맞바꾼다.** 위상차가 $\lvert\phi\rvert \le \pi$ 안에 있어야 각도가 하나로 정해지므로, 유일하게 풀리는 구간은 $\pm\arcsin(\lambda/2d)$다. 아래 예시 값인 $\lambda = 0.03$ m, $d = 0.1$ m이면 $d/\lambda = 3.33$이라 정밀도는 좋지만 유일 구간이 **±8.6°**밖에 안 된다. 그 밖에서 들어온 표적은 접힌 각도로 읽힌다.
>
> 시야 전체를 유일하게 풀려면 $d \le \lambda/2$여야 한다. 어느 쪽을 고를지는 표적이 들어오는 원뿔이 얼마나 좁은지가 정한다. 같은 상충을 숫자로 펼친 것이 [6장](/posts/cw-vs-fmcw-radar/)에 있다.
{: .prompt-warning }

<br/>

#### 동작 원리

위상차를 이용하여 각도를 계산하는 기본 원리는 삼각법과 파동의 간섭 원리를 사용한다. 공의 움직임으로 인한 위상차를 통해 공의 운동 방향을 추정할 수 있다.

1. 위상차와 각도 간의 관계
   - 수직 위상차 $\phi_v$와 수평 위상차 $\phi_h$를 측정한 후, 이를 각도로 변환한다.
   - 위상차를 각도로 변환하는 식은 다음과 같다:
     
     $$\theta_v = \arcsin\left( \frac{\phi_v \cdot \lambda}{2 \pi d} \right)$$
     
     $$\theta_h = \arcsin\left( \frac{\phi_h \cdot \lambda}{2 \pi d} \right)$$
     
     여기서, $\theta_v$와 $\theta_h$는 각각 수직 및 수평 방향에서의 각도이다.
     
2. 각도의 계산
   - 위상차로부터 계산된 각도를 이용하여 공의 회전 벡터의 성분을 계산한다.
   - 수직 성분 $V_z$, 수평 성분 $V_x$, $V_y$를 계산한다:
     
     $$V_z = \sin(\theta_v)$$
     
     $$V_x = \cos(\theta_v) \cdot \cos(\theta_h)$$
     
     $$V_y = \cos(\theta_v) \cdot \sin(\theta_h)$$
     
3. 스핀축 각도의 계산
   - 최종적으로 회전축의 각도 $\theta_{\text{spin}}$은 다음과 같이 계산된다:
     
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

<br/>

#### 위 코드에서 고쳐야 할 두 가지

시리즈를 정리하면서 다시 보니 위 예시에 문제가 둘 있다. 남겨 두고 아래에 정정한다.

**첫째, $V_z$가 결과에 전혀 기여하지 않는다.** 대입해 보면 바로 보인다.

$$
\arctan2(V_y,\,V_x)
= \arctan2\big(\cos\theta_v \sin\theta_h,\; \cos\theta_v \cos\theta_h\big)
= \theta_h
$$

$\theta_v$는 $\arcsin$의 출력이라 항상 $\lvert\theta_v\rvert \le 90°$이고 따라서 $\cos\theta_v \ge 0$이다. 양수인 공통 인수는 $\arctan2$에서 그대로 약분되므로, 위 함수가 돌려주는 값은 **수평 각도 $\theta_h$ 그 자체**다. 수직 위상차를 재려고 채널을 하나 더 놓은 의미가 사라진다.

스핀축의 기울기를 원한다면 두 각도를 횡단면에서 합성해야 한다. 즉 $\arctan2(V_y, V_x)$가 아니라 $\arctan2(\theta_v, \theta_h)$ 꼴이다.

**둘째, `asin`의 인자가 1을 넘으면 NaN이 나온다.** 잡음이나 캘리브레이션 오차로 위상차가 조금만 튀어도 인자가 1을 넘고, NaN은 이후 계산으로 조용히 전파된다. 클램프가 필요하다.

```cpp
#include <algorithm>
#include <cmath>

// phaseV, phaseH : [rad], 켤레곱으로 구해 (−π, π] 로 접힌 값 (7장)
double calculateSpinAxisAngle(double phaseV, double phaseH,
                              double lambda = 0.0125,   // 24 GHz
                              double d      = 0.00625)  // λ/2
{
    const double kv = phaseV * lambda / (2.0 * M_PI * d);
    const double kh = phaseH * lambda / (2.0 * M_PI * d);

    // 인자가 ±1 을 넘으면 asin 이 NaN 을 낸다
    const double theta_v = std::asin(std::clamp(kv, -1.0, 1.0));
    const double theta_h = std::asin(std::clamp(kh, -1.0, 1.0));

    // 시선에 수직인 평면에서 두 각도를 합성한 것이 스핀축의 기울기다
    return std::atan2(theta_v, theta_h) * 180.0 / M_PI;
}
```

기본값도 시리즈에서 쓰는 24 GHz 설정($\lambda = 12.5$ mm, $d = \lambda/2$)으로 바꿨다. 원래 예시의 $\lambda = 0.03$ m는 10 GHz 값이라 이 시리즈의 하드웨어와 맞지 않는다.

부호와 축 방향은 안테나를 실제로 어느 쪽에 붙였는지에 따라 달라진다. 알려진 방향으로 회전하는 표적을 놓고 한 번 확인하고 부호를 고정하는 편이 안전하다.
