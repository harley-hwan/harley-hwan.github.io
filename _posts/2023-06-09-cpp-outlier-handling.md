---
title: "(C++) 이상치(Outlier) 데이터 처리 구현"
description: "선형 보간법과 이동 평균을 이용한 데이터 스무딩"
date: 2023-06-09 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, outlier, filtering, smoothing, interpolation]
---

# 이상치(Outlier) 데이터 처리 구현
- 최초 작성일: 2023년 6월 9일 (금)

<br/>

## 소개
1차원 데이터에서 이상치(Outlier)를 효과적으로 제거하고 부드러운 데이터 피팅을 구현한다. 선형 보간법과 이동 평균 두 가지 방식을 사용하여 데이터를 처리한다.

<br/>

## 선형 보간법 구현
이웃한 데이터 값을 사용하여 이상치를 보정하는 방법이다.

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

#### 구현 특징:
1. **윈도우 기반 처리**
   - windowSize로 지정된 범위의 데이터를 사용한다
   - 데이터의 시작과 끝 부분을 고려한 범위 처리를 한다

2. **이상치 판별**
   - 평균값과의 차이가 threshold를 초과하면 이상치로 판단한다
   - 양방향 모두의 차이를 고려한다

3. **보정 방법**
   - 이전값과 다음값의 평균으로 이상치를 대체한다
   - 경계값 처리를 위한 예외 처리를 포함한다

<br/>

## 이동 평균 구현
윈도우 내의 평균값으로 이상치를 대체하는 방법이다.

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

#### 구현 특징:
1. **이동 평균 계산**
   - 각 위치에서의 윈도우 평균을 미리 계산한다
   - 전체 데이터에 대한 이동 평균 배열을 생성한다

2. **이상치 처리**
   - 원본값과 이동 평균의 차이로 이상치를 판별한다
   - 이상치를 해당 위치의 이동 평균값으로 대체한다

3. **장점**
   - 선형 보간법보다 더 부드러운 결과를 얻을 수 있다
   - 전체적인 데이터 트렌드를 잘 유지한다

이 두 가지 방법은 각각의 장단점이 있다. 선형 보간법은 급격한 변화를 잘 처리하지만 부드러움이 떨어질 수 있고, 이동 평균은 더 부드러운 결과를 제공하지만 급격한 변화를 잘 반영하지 못할 수 있다. 데이터의 특성에 따라 적절한 방법을 선택하여 사용해야 한다.
