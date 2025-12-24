---
title: (c++) FFT 알고리즘 구현
description: "C++, Visual Studio, FFT, Cooley-Tukey, 복소수, 재귀"
date: 2023-09-19 10:00:00 +0900
categories: [Dev, C++]
tags: [C++, Visual Studio, FFT, Cooley-Tukey, 복소수, 재귀]
---

# Fast Fourier Transform (FFT) 

Fast Fourier Transform (FFT)는 Discrete Fourier Transform (DFT) 및 그 역변환을 계산하기 위한 효율적인 알고리즘이다.

필터링, 컨볼루션, 오디오 또는 이미지 압축과 같은 디지털 신호 처리 분야에서 다양한 응용 분야가 있다.

가장 일반적인 FFT 알고리즘은 Cooley-Tukey 알고리즘으로, 이는 분할 정복 알고리즘디다.

<br/>

## Cooley-Tukey FFT 

Cooley-Tukey 알고리즘은 크기 N의 DFT를 크기 N/2의 두 개의 작은 DFT로 재귀적으로 나누어 계산 속도를 향상시킨다. 

이 알고리즘은 N이 2의 거듭제곱이라고 가정한다.

<br/>

DFT는 다음 공식으로 정의된다:

![image](https://github.com/harley-hwan/harley-hwan.github.io/assets/68185569/0fb4aeb2-fdff-4b37-8656-2e4e9ffe4a0f)

여기서:
- \( X(k) \)는 k번째 복소 DFT 계수.
- \( x(n) \)은 n번째 복소 입력 샘플.
- \( j \)는 허수 단위 (\( j^2 = -1 \)).
- \( N \)은 샘플의 총 개수.

<br/>

## C++ 

### 1. 

```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <complex>
```

<br/>

### 2. 

```cpp
typedef complex<double> Complex;
const double PI = 3.14159265358979323846;
```

<br/>

### 3. FFT 

```cpp
vector<Complex> fft(vector<Complex>& a) {
    int n = a.size();
    if (n == 1)
        return a;
    
    vector<Complex> a_even(n / 2), a_odd(n / 2);
    for (int i = 0; i < n / 2; i++) {
        a_even[i] = a[i * 2];
        a_odd[i] = a[i * 2 + 1];
    }
    vector<Complex> y_even = fft(a_even);
    vector<Complex> y_odd = fft(a_odd);
    vector<Complex> y(n);
    for (int k = 0; k < n / 2; k++) {
        Complex t = polar(1.0, -2.0 * PI * k / n) * y_odd[k];
        y[k] = y_even[k] + t;
        y[k + n / 2] = y_even[k] - t;
    }
    return y;
}
```

1. 입력 벡터 a의 크기 n을 구함.
2. n이 1이면 a를 반환. 재귀의 기본 조건.
3. a의 짝수 인덱스와 홀수 인덱스의 원소들을 각각 a_even과 a_odd 벡터에 저장합니다.
4. a_even과 a_odd에 대해 재귀적으로 fft 함수를 호출하여 y_even과 y_odd를 계산합니다.
5. y_even과 y_odd를 사용하여 최종 결과 y를 반환.

<br/>

### 4. IFFT 

```cpp
vector<Complex> ifft(vector<Complex>& a) {
    int n = a.size();
    for (int i = 0; i < n; i++) {
        a[i] = conj(a[i]);
    }
    vector<Complex> y = fft(a);
    for (int i = 0; i < n; i++) {
        y[i] = conj(y[i]) / double(n);
    }
    return y;
}
```

1. 입력 벡터 a의 모든 원소에 대해 켤레 복소수를 계산.
2. 변환된 a에 대해 fft 함수를 호출하여 y를 계산.
3. y의 모든 원소에 대해 켤레 복소수를 계산하고 n으로 나누어 최종 결과를 반환.

<br/>

### 5. Main 

```cpp
int main() {
    vector<Complex> a = {1, 2, 3, 4};
    vector<Complex> y = fft(a);
    for (int i = 0; i < y.size(); i++)
        cout << y[i] << " ";
    cout << endl;
    vector<Complex> x = ifft(y);
    for (int i = 0; i < x.size(); i++)
        cout << x[i] << " ";
    cout << endl;
    return 0;
}
```

- `a`의 FFT 결과 `y`와, `y`의 IFFT 결과 `x`를 출력한다. 
- `x`는 원래의 `a`와 같아야 한다.

<br/>

<br/>

Cooley-Tukey 알고리즘이 가장 널리 사용되는 FFT 알고리즘 중 하나이지만, 다른 여러 가지 FFT 알고리즘이 있다. 

이 중 일부는 특정 애플리케이션에 대해 더 효율적일 수 있다. 

<br/>

#### 

- Radix-2 FFT: Cooley-Tukey 알고리즘의 특별한 경우로, 입력 크기 N이 2의 거듭제곱일 때만 작동. 일반적으로 매우 효율적이지만, 2의 거듭제곱 크기의 입력에만 제한된다.
- Mixed-Radix FFT: Cooley-Tukey 알고리즘의 일반화이며, 여러 기수(radix)를 사용하여 계산을 수행한다. 2의 거듭제곱이 아닌 입력 크기에 대해 효율적일 수 있다.
- Prime Factor Algorithm (PFA): 입력 크기 N이 소수의 곱으로 표현될 수 있을 때 효과적이다.
- Rader's Algorithm: 입력 크기 N이 소수일 때 사용.
- Bluestein's Algorithm: 어떤 크기의 입력에 대해서도 사용.
- Winograd Fourier Transform Algorithm (WFTA): 작은 크기의 DFT를 계산하기 위해 특별히 최적화된 알고리즘. 일반적으로 큰 DFT를 작은 크기의 DFT로 분해하는 데 사용되는 다른 알고리즘과 함께 사용.

<br/>

위의 각 알고리즘은 특정 상황에서 최적의 성능을 제공하기 위해 설계되었다. 따라서 어떤 알고리즘이 "최선"인지는 응용 프로그램 및 입력 데이터의 특성에 따라 달라질 수 있다.
