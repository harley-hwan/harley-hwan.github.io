---
title: "(C++) RANSAC 알고리즘 구현 (Eigen)"
description: "Eigen으로 RANSAC을 구현해 위상 로그에 2차 곡선을 맞춰봤는데 결과가 이상했다. 당시엔 원인을 못 찾았고, 지금 다시 보니 짚이는 게 네 가지 있어서 같이 정리했다."
date: 2023-06-09 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, visual-studio, ransac, algorithm, eigen, curve-fitting, conditioning]
math: true
---
## 왜 최소제곱이 아니라 RANSAC인가

측정 로그에 곡선을 맞추는 작업이었다. 그냥 최소제곱으로 하면 [앞 글](/posts/cpp-outlier-handling/)에서 적었듯 크게 벗어난 점 하나가 결과를 통째로 끌고 간다. 오차를 제곱해서 더하니 벗어난 정도가 10배면 영향은 100배다.

RANSAC은 접근이 반대다. 전체를 한 번에 맞추는 대신, 최소 개수의 점만 뽑아 모델을 만들고 그 모델에 동의하는 점이 몇 개인지 센다. 이걸 여러 번 반복해서 지지자가 제일 많은 모델을 고른다. 이상치는 어느 모델에도 잘 동의하지 않으니 자연스럽게 밀려난다.

## 직선 피팅으로 먼저 확인

```c++
#include <iostream>
#include <vector>
#include <Eigen/Dense>

struct LineModel {
    double a, b;

    LineModel(double a = 0, double b = 0) : a(a), b(b) {}

    // Fit the line model using two points
    void fit(const Eigen::Vector2d& pt1, const Eigen::Vector2d& pt2) {
        a = (pt2[1] - pt1[1]) / (pt2[0] - pt1[0]);
        b = pt1[1] - a * pt1[0];
    }

    // Evaluate the line model for a given x
    double eval(double x) const {
        return a * x + b;
    }

    // Calculate the error of the point to the line model
    double error(const Eigen::Vector2d& pt) const {
        return std::abs(pt[1] - eval(pt[0]));
    }
};

int main() {
    // Create synthetic data
    std::vector<Eigen::Vector2d> data;
    for (double x = -1; x <= 1; x += 0.01) {
        double y = 2 * x + 1 + 0.1 * ((double)rand() / (RAND_MAX));
        data.push_back(Eigen::Vector2d(x, y));
    }

    // RANSAC parameters
    int max_iterations = 1000;
    double inlier_threshold = 0.1;
    int min_inliers = data.size() * 0.8;

    LineModel best_model;
    int best_inlier_count = 0;

    for (int i = 0; i < max_iterations; i++) {
        // Randomly select 2 data points and fit the model
        int idx1 = rand() % data.size();
        int idx2 = rand() % data.size();
        LineModel model;
        model.fit(data[idx1], data[idx2]);

        // Count the inliers for the current model
        int inlier_count = 0;
        for (const auto& pt : data) {
            if (model.error(pt) < inlier_threshold)
                inlier_count++;
        }

        // Update the best model if current model is better
        if (inlier_count > best_inlier_count) {
            best_model = model;
            best_inlier_count = inlier_count;
        }

        // If we already have enough inliers, stop early
        if (best_inlier_count >= min_inliers)
            break;
    }

    std::cout << "Best model: y = " << best_model.a << " * x + " << best_model.b << std::endl;
    std::cout << "Inlier count: " << best_inlier_count << std::endl;

    return 0;
}
```

```c++
Best model: y = 2.06363 * x + 1.06259
Inlier count: 193
```

`y = 2x + 1`을 넣었으니 답에 가깝게 나왔다. 그런데 이 실험은 RANSAC이 잘 도는지를 확인해주지 못한다.

**합성 데이터에 이상치가 하나도 없다.** `0.1 * (rand()/RAND_MAX)`는 0에서 0.1 사이의 값이라 노이즈가 아니라 한쪽으로만 더해지는 치우침이다. 평균 0.05가 전부 더해지니 절편이 1.05 근처로 나오는 것도 그 때문이다. 이상치가 없으면 RANSAC이 아니라 최소제곱도 같은 답을 준다.

이상치에 강한지 보려면 일부러 넣어야 한다.

```c++
// 20% 를 크게 어긋나게
for (size_t i = 0; i < data.size(); i += 5)
    data[i][1] += (i % 2 ? 5.0 : -5.0);
```

이렇게 넣고 돌려야 최소제곱과의 차이가 보인다.

`idx1 == idx2`가 되는 경우를 안 막은 것도 문제다. 같은 점이 두 번 뽑히면 `fit`에서 `pt2[0] - pt1[0]`이 0이라 기울기가 무한대가 되고, 이후 모든 `error` 비교가 거짓이라 `inlier_count`가 0이 된다. 최선 모델을 갱신하지 않으니 크래시는 안 나지만 그 회차가 버려진다.

`rand()`도 `srand()` 없이 쓰면 매번 같은 수열이라 실행 결과가 항상 같다. 디버깅에는 편한데 의도한 게 아니었다. 그리고 `rand() % n`은 모듈로 편향이 있어서 앞쪽 인덱스가 더 자주 뽑힌다.

## 실제 데이터에 2차 곡선 맞추기

측정 로그 두 개(수평, 수직)에 2차 곡선을 맞춘 코드다. 이번엔 Eigen의 최소제곱을 쓰고, 마지막에 인라이어 전체로 다시 맞춘다.

```c++
Eigen::VectorXd ransac(const Eigen::MatrixXd& A, const Eigen::VectorXd& B, int N, double T) {
    int n_data = A.rows();
    int n_sample = 3;

    int max_cnt = 0;
    Eigen::VectorXd best_model = Eigen::VectorXd::Zero(A.cols());

    std::uniform_int_distribution<> dis(0, n_data - 1);
    for (int itr = 0; itr < N; ++itr) {
        std::vector<int> k(n_sample);
        for (int i = 0; i < n_sample; ++i) {
            k[i] = dis(gen);
        }

        Eigen::MatrixXd AA(n_sample, A.cols());
        Eigen::VectorXd BB(n_sample);
        for (int i = 0; i < n_sample; ++i) {
            AA.row(i) = A.row(k[i]);
            BB(i) = B(k[i]);
        }

        Eigen::VectorXd X = AA.colPivHouseholderQr().solve(BB);

        Eigen::VectorXd residual = B - A * X;
        int cnt = (residual.array().abs() < T).count();
        if (cnt > max_cnt) {
            best_model = X;
            max_cnt = cnt;
        }
    }

    // 인라이어만 모아 다시 피팅
    Eigen::VectorXd residual = B - A * best_model;
    std::vector<int> in_k;
    for (int i = 0; i < n_data; ++i) {
        if (std::abs(residual(i)) < T) {
            in_k.push_back(i);
        }
    }

    Eigen::MatrixXd A2(in_k.size(), A.cols());
    Eigen::VectorXd B2(in_k.size());
    for (size_t i = 0; i < in_k.size(); ++i) {
        A2.row(i) = A.row(in_k[i]);
        B2(i) = B(in_k[i]);
    }

    return A2.colPivHouseholderQr().solve(B2);
}
```

행렬은 이렇게 만든다.

```c++
    Eigen::MatrixXd A1(n_data1, 3);
    Eigen::VectorXd B1(n_data1);
    for (int i = 0; i < n_data1; ++i) {
        A1(i, 0) = i * i;
        A1(i, 1) = i;
        A1(i, 2) = 1;
        B1(i) = data1[i];
    }

    int N = 100;
    double T = 3 * 100; // 3 * noise_sigma
    Eigen::VectorXd X1 = ransac(A1, B1, N, T);
```

결과는 이랬다.

```c++
Result H: 0.00547198   0.292524   -80.6625
Result W: -0.00291597     1.01354    -70.4702
```

원하는 답이 아니었다. 당시엔 원인을 못 찾고 넘어갔다.

## 지금 보면 짚이는 것들

정리하면서 다시 보니 의심되는 게 네 가지다.

### 1. 위상 데이터를 언랩하지 않았다

입력이 위상 로그다. 위상은 ±180°(또는 ±π)에서 접히는 값이라, 실제로는 연속적으로 증가해도 데이터상으로는 한 바퀴 돌 때마다 반대편으로 점프한다.

그 점프를 그대로 두고 2차 곡선을 맞추면 곡선은 점프를 평균 내려고 엉뚱한 곳에 놓인다. 데이터가 "이상치가 많은 곡선"이 아니라 "톱니 모양"이 되기 때문에, RANSAC으로 이상치를 걸러도 해결되지 않는다.

언랩을 먼저 해야 한다. 인접 값의 차이가 π를 넘으면 2π를 더하거나 빼서 연속으로 만든다. 코드는 [이상치 처리](/posts/cpp-outlier-handling/) 쪽에 적어뒀다.

이걸 안 하고 어떤 강건 추정을 붙여도 결과가 안 나온다. 데이터를 잘못 해석하고 있는 것이지 알고리즘 문제가 아니다.

### 2. 행렬의 조건수가 나쁘다

```c++
A1(i, 0) = i * i;
A1(i, 1) = i;
A1(i, 2) = 1;
```

`i`가 데이터 인덱스라 수천까지 간다. 그러면 첫 열은 $10^7$ 규모, 둘째 열은 $10^3$, 셋째 열은 1이다. 열끼리 스케일이 $10^7$배 차이 난다.

이런 행렬은 조건수가 매우 커서, QR 분해로 풀어도 계수의 유효 자릿수가 크게 깎인다. 특히 2차항 계수가 $0.005$ 같은 작은 값으로 나온 걸 보면 이 영향이 의심된다.

입력을 정규화하면 해결된다.

```c++
// i 를 [-1, 1] 로 옮긴다
const double c = (n_data - 1) / 2.0;
const double s = (n_data - 1) / 2.0;
for (int i = 0; i < n_data; ++i) {
    const double t = (i - c) / s;         // -1 ~ 1
    A(i, 0) = t * t;
    A(i, 1) = t;
    A(i, 2) = 1.0;
}
```

이러면 세 열의 크기가 비슷해진다. 나온 계수는 정규화된 좌표 기준이니, 원래 좌표로 되돌리려면 치환을 풀어야 한다. 곡선 값만 필요하면 정규화된 좌표에서 그대로 평가하면 되니 되돌릴 필요도 없다.

### 3. 표본을 중복해서 뽑는다

```c++
for (int i = 0; i < n_sample; ++i)
    k[i] = dis(gen);
```

같은 인덱스가 두 번 이상 뽑힐 수 있다. 3점 중 2점이 같으면 방정식이 사실상 2개뿐이라 미지수 3개를 결정할 수 없다. `colPivHouseholderQr`는 이때 에러를 내지 않고 해 하나를 돌려주는데, 그게 의미 있는 곡선이라는 보장이 없다.

데이터가 1000개면 3개 중 중복이 생길 확률은 0.3% 정도라 크진 않다. 100번 반복이면 몇 번은 나온다는 뜻이다. 최선 모델을 고르는 구조라 치명적이진 않지만 그만큼 시행이 낭비된다.

중복을 막는 건 간단하다.

```c++
std::vector<int> k;
while (k.size() < n_sample) {
    int idx = dis(gen);
    if (std::find(k.begin(), k.end(), idx) == k.end()) k.push_back(idx);
}
```

한 가지 더, 3점이 서로 너무 가까우면 그 구간에서만 맞는 곡선이 나와 나머지 구간으로 크게 외삽된다. 인덱스가 일정 간격 이상 떨어지도록 강제하는 편이 결과가 안정적이었다.

### 4. T가 데이터와 무관하다

```c++
double T = 3 * 100; // 3 * noise_sigma
```

노이즈 σ를 100으로 가정하고 3σ를 임계값으로 잡았다. 그런데 이 100이 어디서 나온 값인지 근거가 없다. 데이터의 실제 잔차 분포와 안 맞으면 인라이어를 너무 많이 받거나 너무 적게 받는다.

너무 크면 이상치까지 인라이어로 세니 RANSAC을 쓸 이유가 없어지고, 너무 작으면 어떤 모델도 지지자를 못 얻어 결과가 무작위에 가까워진다.

데이터에서 뽑는 게 낫다. 잔차의 MAD로 σ를 추정하고 그 배수를 쓴다.

```c++
Eigen::VectorXd r = (B - A * X).cwiseAbs();
std::vector<double> v(r.data(), r.data() + r.size());
std::nth_element(v.begin(), v.begin() + v.size()/2, v.end());
const double sigma = 1.4826 * v[v.size()/2];
const double T = 2.5 * sigma;
```

## 반복 횟수는 계산할 수 있다

`N = 100`도 감으로 정한 값이었는데, 필요한 횟수는 공식으로 나온다.

인라이어 비율을 $w$, 모델에 필요한 최소 점 수를 $s$, 원하는 성공 확률을 $p$라고 하면

$$
N = \frac{\log(1 - p)}{\log\!\left(1 - w^{s}\right)}
$$

한 번에 $s$개를 다 인라이어로 뽑을 확률이 $w^s$이고, $N$번 모두 실패할 확률이 $(1-w^s)^N$이다. 그게 $1-p$ 이하가 되게 하는 $N$이다.

$s=3$, $p=0.99$일 때 인라이어 비율에 따라 이렇게 된다.

| 인라이어 비율 $w$ | 필요한 $N$ |
| ---: | ---: |
| 0.9 | 6 |
| 0.7 | 11 |
| 0.5 | 35 |
| 0.3 | 169 |
| 0.2 | 574 |

인라이어가 70%만 돼도 11번이면 충분하다. 100번은 넉넉했던 셈이라, 이쪽은 원인이 아니었다.

실전에서는 $w$를 미리 모르니, 도는 중에 지금까지 찾은 최선 인라이어 비율로 $N$을 계속 갱신하는 방식을 쓴다. 좋은 모델을 빨리 찾으면 일찍 끝난다.

```c++
const double w = double(max_cnt) / n_data;
if (w > 0) {
    const double denom = std::log(1.0 - std::pow(w, n_sample));
    if (denom < 0) N = std::min<int>(N, int(std::log(1.0 - 0.99) / denom) + 1);
}
```

## 정리하면

- 합성 데이터에 이상치가 없으면 RANSAC이 도는지 확인이 안 된다. 일부러 넣어야 한다
- 표본을 중복 없이 뽑아야 한다. 같은 점이 두 번 뽑히면 그 시행이 버려진다
- 다항 피팅에서 $x$를 그대로 쓰면 열 스케일 차이 때문에 조건수가 나빠진다. $[-1, 1]$로 정규화한다
- 임계값 $T$는 데이터에서 추정한다. 잔차 MAD의 배수가 무난하다
- 반복 횟수는 $\log(1-p)/\log(1-w^s)$로 계산되고, 도는 중에 갱신할 수 있다
- 무엇보다, 위상처럼 접히는 데이터는 언랩을 먼저 해야 한다. 알고리즘을 바꿔서 해결될 문제가 아니다

## 입력과 출력 로그

[maxAmplitudePhasesH.log](https://github.com/harley-hwan/harley-hwan.github.io/files/11705761/maxAmplitudePhasesH.log)
[maxAmplitudePhasesW.log](https://github.com/harley-hwan/harley-hwan.github.io/files/11705762/maxAmplitudePhasesW.log)

[outputH.log](https://github.com/harley-hwan/harley-hwan.github.io/files/11705756/outputH.log)
[outputW.log](https://github.com/harley-hwan/harley-hwan.github.io/files/11705758/outputW.log)
