---
title: "(C++) 이상치(Outlier) 데이터 처리 구현"
description: "측정 데이터에서 튀는 값을 걸러내려고 이동 평균과 선형 보간을 써봤다. 평균 기준이 이상치 자체에 오염되는 문제, 위상 데이터에는 평균을 그대로 쓰면 안 되는 이유를 정리했다."
date: 2023-06-09 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, outlier, filtering, smoothing, interpolation, median, hampel]
math: true
---
## 튀는 값 하나가 뒤를 다 망친다

측정 데이터를 곡선에 맞추는 작업을 하는데, 중간에 한두 개씩 크게 튀는 값이 있었다. 그대로 넣으면 피팅 결과가 그 점 쪽으로 끌려간다. 최소제곱은 오차를 제곱해서 더하니, 크게 벗어난 점 하나가 나머지 수백 개보다 큰 영향을 준다.

곡선 피팅 쪽을 강건하게 만드는 방법도 있고 그건 [RANSAC](/posts/cpp-ransac-algorithm-implementation-with-eigen/)에서 따로 다뤘다. 여기서는 데이터를 먼저 손보는 쪽이다.

## 선형 보간

이상치를 앞뒤 값의 평균으로 대체하는 방식이다.

```cpp
std::vector<float> handleOutliers(const std::vector<float>& values, 
                                int windowSize, float threshold) {
    int size = values.size();
    std::vector<float> smoothedValues = values;

    for (int i = 0; i < size; ++i) {
        // 윈도우 내 평균 계산
        float sum = 0;
        int count = 0;
        for (int j = std::max(0, i - windowSize); 
             j <= std::min(size - 1, i + windowSize); ++j) {
            sum += values[j];
            ++count;
        }
        float mean = sum / count;

        // 이상치 검출 및 처리
        if (std::abs(values[i] - mean) > threshold) {
            // 이전값과 다음값의 평균으로 대체
            float prevValue = (i > 0) ? values[i - 1] : values[i];
            float nextValue = (i < size - 1) ? values[i + 1] : values[i];
            smoothedValues[i] = (prevValue + nextValue) / 2.0f;
        }
    }
    return smoothedValues;
}
```

한 가지 잘한 부분이 있다. 판정과 대체에 모두 **원본 `values`를 참조하고**, 결과는 `smoothedValues`에만 쓴다. 제자리에서 고치면 앞에서 고친 값이 뒤의 판정 기준에 섞여서 결과가 처리 순서에 따라 달라진다. 순서 의존성이 생기면 나중에 원인 찾기가 어렵다.

## 이동 평균

이상치를 윈도우 평균값으로 대체하는 방식이다.

```cpp
std::vector<float> handleOutliers(const std::vector<float>& values, 
                                int windowSize, float threshold) {
    int size = values.size();
    std::vector<float> smoothedValues = values;
    
    // 이동 평균 계산
    std::vector<float> movingAverages(size);
    for (int i = 0; i < size; ++i) {
        float sum = 0;
        int count = 0;
        for (int j = std::max(0, i - windowSize); 
             j <= std::min(size - 1, i + windowSize); ++j) {
            sum += values[j];
            ++count;
        }
        movingAverages[i] = sum / count;
    }

    // 이상치 검출 및 대체
    for (int i = 0; i < size; ++i) {
        if (std::abs(values[i] - movingAverages[i]) > threshold) {
            smoothedValues[i] = movingAverages[i];
        }
    }
    return smoothedValues;
}
```

계산을 두 단계로 나눈 것도 같은 이유다. 이동 평균을 다 구해놓고 그다음에 판정하니 순서에 안 휘둘린다.

선형 보간은 급격한 변화를 비교적 잘 따라가고, 이동 평균은 부드럽지만 변화를 뭉갠다. 데이터 성격에 따라 골랐다.

## 평균이 이상치에 오염된다

한동안 쓰다가 알게 된 문제다. **이상치가 클수록 검출이 안 된다.**

윈도우 평균을 구할 때 그 이상치 자신이 들어간다. 윈도우 크기가 5(양쪽 2개)면 샘플이 5개인데, 그중 하나가 1000쯤 튀면 평균이 200 올라간다. 그러면 `|values[i] - mean|`이 1000이 아니라 800이 되고, 임계값이 900이었다면 안 걸린다.

값이 클수록 자기 자신이 기준을 자기 쪽으로 끌어당기는 구조다. 통계에서 마스킹이라고 부르는 현상이다. 이상치가 연달아 두세 개 있으면 더 심해진다.

평균 대신 **중앙값**을 쓰면 이 문제가 없다. 윈도우 안에 이상치가 절반 미만이면 중앙값은 꿈쩍도 안 한다.

```cpp
float median_of(std::vector<float> w)          // 복사본을 받는다
{
    const size_t m = w.size() / 2;
    std::nth_element(w.begin(), w.begin() + m, w.end());
    return w[m];
}
```

`std::nth_element`는 전체 정렬 없이 m번째 값만 제자리에 놓는다. 평균 O(n)이라 정렬보다 빠르다.

## 임계값을 데이터가 정하게

`threshold`가 절대값이라는 것도 불편했다. 위상 데이터와 진폭 데이터의 스케일이 다르니 매번 다른 값을 넣어야 하고, 그 값을 어떻게 정하느냐는 결국 눈으로 보고 맞추는 것이었다.

데이터의 흩어진 정도를 기준으로 삼으면 자동으로 맞는다. 표준편차를 쓰면 그것도 이상치에 오염되니, 중앙값과 짝이 되는 MAD(중앙값 절대편차)를 쓴다.

$$
\mathrm{MAD} = \mathrm{median}\left(\left|x_i - \mathrm{median}(x)\right|\right)
$$

정규분포일 때 표준편차와 눈금을 맞추려면 1.4826을 곱한다. 이 상수는 정규분포에서 MAD와 σ의 비율에서 나온 값이다.

이 둘을 묶은 게 Hampel 필터다.

```cpp
std::vector<float> hampel(const std::vector<float>& x, int half, float n_sigma = 3.0f)
{
    const int n = static_cast<int>(x.size());
    std::vector<float> out = x;
    std::vector<float> w;
    w.reserve(2 * half + 1);

    for (int i = 0; i < n; ++i) {
        w.clear();
        for (int j = std::max(0, i - half); j <= std::min(n - 1, i + half); ++j)
            w.push_back(x[j]);

        const float med = median_of(w);

        for (auto& v : w) v = std::abs(v - med);
        const float mad = median_of(w);
        const float sigma = 1.4826f * mad;

        if (sigma > 0 && std::abs(x[i] - med) > n_sigma * sigma)
            out[i] = med;                      // 중앙값으로 대체
    }
    return out;
}
```

`n_sigma`는 3 정도가 기본이다. 이 값은 스케일과 무관하니 데이터가 바뀌어도 그대로 쓸 수 있다. 임계값을 손으로 맞추던 일이 없어진 게 제일 컸다.

`sigma > 0` 검사가 필요하다. 윈도우 안의 값이 전부 같으면 MAD가 0이 되고, 그러면 조금이라도 다른 값이 전부 이상치가 된다. 신호가 잠깐 평평한 구간에서 실제로 이 일이 났다.

## 위상 데이터에는 평균을 그대로 쓰면 안 된다

이게 제일 크게 데인 부분이다.

위상은 원형 데이터다. −179°와 +179°는 2° 차이인데, 산술 평균을 내면 0°가 나온다. 실제 중간값인 180°와 정반대다.

위상 로그에 이 필터를 걸었더니 ±180° 경계 근처에서 멀쩡한 값이 전부 이상치로 잡히고, 대체된 값은 완전히 엉뚱한 곳을 가리켰다. 데이터가 이상한 줄 알고 측정을 다시 했다.

두 가지로 해결한다.

**언랩을 먼저 한다.** 인접한 값의 차이가 π를 넘으면 2π를 더하거나 빼서 연속으로 만든다.

```cpp
std::vector<float> unwrap(std::vector<float> p)      // 라디안
{
    constexpr float kTwoPi = 6.283185307179586f;
    for (size_t i = 1; i < p.size(); ++i) {
        float d = p[i] - p[i - 1];
        while (d >  kTwoPi / 2) { p[i] -= kTwoPi; d -= kTwoPi; }
        while (d < -kTwoPi / 2) { p[i] += kTwoPi; d += kTwoPi; }
    }
    return p;
}
```

언랩한 뒤에는 평범한 실수 수열이라 위의 필터를 그대로 쓸 수 있다. 다만 언랩 자체가 이상치에 약하다. 튀는 값 하나 때문에 그 뒤 전체가 2π만큼 밀릴 수 있다.

**복소수로 평균을 낸다.** 언랩 없이 원형 통계를 그대로 쓰는 방법이다.

```cpp
float circular_mean(const std::vector<float>& p)     // 라디안
{
    float s = 0, c = 0;
    for (float v : p) { s += std::sin(v); c += std::cos(v); }
    return std::atan2(s, c);                          // 항상 (−π, π]
}
```

각도를 단위 벡터로 바꿔 더하고 다시 각도로 되돌린다. 경계 문제가 원리적으로 없다. 벡터 합의 길이(`hypot(s, c) / n`)가 1에 가까우면 값들이 몰려 있고, 0에 가까우면 흩어져 있다는 뜻이라 흩어진 정도까지 같이 얻는다.

차이를 잴 때도 마찬가지다. 뺄셈이 아니라 켤레곱으로 구해야 경계를 넘지 않는다. 같은 이야기를 [CW 수신 체인](/posts/cw-receive-chain-cpp/) 8절에도 적어뒀다.

## 계산량

두 구현 다 모든 위치에서 윈도우를 다시 훑으니 O(n·w)다. 윈도우가 크면 눈에 띄게 느려진다.

평균이면 누적합으로 O(n)이 된다. 윈도우가 한 칸 움직일 때 들어온 값을 더하고 나간 값을 빼면 된다.

```cpp
sum += x[i + half];
sum -= x[i - half - 1];
```

중앙값은 이렇게 못 한다. 정렬 상태를 유지하는 자료구조(멀티셋 두 개나 힙 두 개)가 필요하다. 데이터가 수천 개 수준이면 `nth_element`로도 충분해서 거기까지는 안 갔다.

## 지울 것인가 표시할 것인가

마지막으로, 이상치를 조용히 고쳐버리는 게 항상 맞는 건 아니다.

이상치가 몇 개 나왔는지, 어디서 나왔는지가 그 자체로 정보였다. 특정 구간에서만 계속 튀면 그건 노이즈가 아니라 장비 쪽 문제다. 필터가 알아서 지워버리면 그 신호를 놓친다.

그래서 대체한 위치를 같이 돌려주도록 바꿨다.

```cpp
struct FilterResult {
    std::vector<float> values;
    std::vector<int>   replaced;    // 대체된 인덱스
};
```

대체 비율이 임계치를 넘으면 로그에 경고를 남기게 했다. 5%를 넘으면 필터를 신뢰할 수 없는 상태이기도 하다.

## 정리하면

- 평균 기준 검출은 이상치 자신에 오염된다. 클수록 안 걸린다
- 중앙값과 MAD를 쓰면 이 문제가 없고, 임계값을 σ 배수로 줄 수 있어 스케일에 안 휘둘린다
- MAD가 0이 되는 구간(평평한 신호)을 따로 걸러야 한다
- 위상 같은 원형 데이터에 산술 평균을 쓰면 ±180° 경계에서 정반대 값이 나온다. 언랩하거나 복소수로 평균낸다
- 판정과 대체에 원본만 참조해야 처리 순서에 안 휘둘린다
- 이상치가 얼마나 나왔는지는 그 자체로 신호다. 조용히 지우지 말고 기록한다
