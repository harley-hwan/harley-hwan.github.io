---
title: "(C++) 이상치(Outlier) 데이터 처리 구현"
description: "선형 보간법과 이동 평균을 이용한 데이터 스무딩"
date: 2023-06-09 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, outlier, filtering, smoothing, interpolation]
---
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

#### 구현 특징

- windowSize로 지정된 범위의 데이터로 윈도우 평균을 구하며, 데이터의 시작과 끝에서는 범위를 잘라 처리한다.
- 값과 윈도우 평균의 차이(절대값)가 threshold를 초과하면 이상치로 판단한다.
- 이상치는 이전값과 다음값의 평균으로 대체하고, 양 끝 요소는 자기 자신을 이웃값으로 쓰도록 예외 처리한다.

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

#### 구현 특징

- 각 위치의 윈도우 평균을 미리 계산해 전체 데이터에 대한 이동 평균 배열을 만든다.
- 원본값과 이동 평균의 차이로 이상치를 판별하고, 해당 위치의 이동 평균값으로 대체한다.
- 선형 보간법보다 부드러운 결과를 얻을 수 있고 전체적인 데이터 트렌드를 잘 유지한다.

선형 보간법은 급격한 변화를 잘 처리하는 대신 부드러움이 떨어질 수 있고, 이동 평균은 더 부드럽지만 급격한 변화를 잘 반영하지 못하므로 데이터 특성에 맞게 골라 쓰면 된다.
