---
title: "(C++) 로또 번호 랜덤 추출"
description: "c++, lotto, srand. algorithm, ctime"
date: 2023-02-16 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, lotto, srand, algorithm, ctime]
---
## 내용

재미로 만든거니 안됐다고 탓하지 마세요^^

<br/>

### 코드

std::random_shuffle은 C++14에서 deprecated 되었고 C++17에서 표준에서 제거되었기 때문에, std::shuffle과 &lt;random&gt;을 사용한다.

```c++
#include <iostream>
#include <vector>
#include <algorithm>
#include <random>

int main() {
    // 난수 엔진 초기화
    std::random_device rd;
    std::mt19937 gen(rd());

    // 1부터 45까지의 숫자를 저장하는 벡터 생성
    std::vector<int> numbers(45);
    for (int i = 0; i < 45; i++) {
        numbers[i] = i + 1;
    }

    // 벡터를 무작위로 섞음
    std::shuffle(numbers.begin(), numbers.end(), gen);

    // 벡터에서 첫 6개의 요소를 선택하여 로또 번호로 출력
    std::cout << "로또 추천 번호: ";
    for (int i = 0; i < 6; i++) {
        std::cout << numbers[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}

```
