---
title: "(C++) 함수 내부에 함수 정의하기: 지역 함수와 람다 표현식"
description: "코드 구조화와 가독성 향상을 위한 내부 함수 활용법"
date: 2024-09-02 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, programming, lambda, local-functions, code-structure]
---
<br/>

## 소개

함수 내부에 다른 함수를 정의하고 호출하는 방식은 코드의 구조화와 가독성 향상에 도움이 된다. C++에서는 이를 주로 람다 함수를 통해 구현한다.

<br/>

## 지역 함수의 개념

지역 함수(또는 내부 함수)는 다른 함수 내부에 정의된 함수를 말한다. 이 함수들은 정의된 함수의 범위 내에서만 사용할 수 있다.

주요 특징:
- 범위가 외부 함수로 제한된다.
- 외부 함수의 변수에 접근 가능하다. (클로저)
- 코드 구조화와 가독성 향상에 도움을 준다.

<br/>

## C++에서의 구현: 람다 표현식

C++에서는 람다 표현식을 사용하여 지역 함수를 구현한다. 람다 표현식의 기본 구조는 다음과 같다:

```cpp
[캡처 목록](매개변수 목록) -> 반환 타입 {
    // 함수 본문
};
```

- 캡처 목록: 외부 변수를 람다 함수 내부로 가져올 때 사용한다.
- 매개변수 목록: 일반 함수의 매개변수와 동일하다.
- 반환 타입: 생략 가능하다. (컴파일러가 추론)
- 함수 본문: 실제 실행될 코드를 작성한다.

<br/>

## 장점과 사용 사례

- 복잡한 로직을 작은 단위로 분할하고, 관련 기능을 근접하게 배치해 가독성을 높일 수 있다.
- 함수의 사용을 특정 컨텍스트로 제한해 전역 네임스페이스 오염을 방지한다.
- 외부 함수의 상태를 캡처(클로저)할 수 있어 컨텍스트에 따른 동작을 구현하기 쉽다.
- 동일한 외부 함수 내에서 여러 번 호출해 재사용할 수 있다.

<br/>

## 주의사항

- 너무 많은 내부 함수는 오히려 코드를 복잡하게 만들 수 있으므로 적절한 균형이 필요하다.
- 내부 함수는 디버깅이 상대적으로 어려울 수 있어 명확한 이름과 주석을 쓰는 것이 좋다.
- 람다 함수의 과도한 사용은 미세한 성능 저하를 일으킬 수 있으므로 성능이 중요한 부분에서는 주의한다.

<br/>

## 예제 코드

다음은 내부 함수를 활용한 간단한 예제 코드다:

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

void processNumbers(const std::vector<int>& numbers) {
    // 내부 함수 정의: 숫자 출력
    auto printNumber = [](int num) {
        std::cout << num << " ";
    };

    // 내부 함수 정의: 짝수 여부 확인
    auto isEven = [](int num) {
        return num % 2 == 0;
    };

    // 모든 숫자 출력
    std::cout << "All numbers: ";
    std::for_each(numbers.begin(), numbers.end(), printNumber);
    std::cout << std::endl;

    // 짝수만 출력
    std::cout << "Even numbers: ";
    std::for_each(numbers.begin(), numbers.end(), 
                  [&](int num) {
                      if (isEven(num)) {
                          printNumber(num);
                      }
                  });
    std::cout << std::endl;
}

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    processNumbers(numbers);
    return 0;
}
```

이 예제에서:
- `printNumber`와 `isEven`은 `processNumbers` 함수 내부에 정의된 람다 함수다.
- 이들은 `processNumbers` 함수 내에서만 사용되며, 코드의 가독성과 구조를 개선한다.
- `std::for_each`를 사용하여 내부 함수들을 효과적으로 활용하고 있다.

<br/>

## 결론

C++에서는 람다 표현식으로 함수 내부에 지역 함수를 정의할 수 있고, 잘 쓰면 코드 구조화와 가독성에 도움이 되지만 과하면 오히려 복잡해진다.
