---
title: "(C++) 함수 내부에 함수 정의하기: 지역 함수와 람다 표현식"
description: "함수 안에서만 쓰는 보조 함수를 람다로 빼면서 알게 된 것들. 캡처 방식에 따라 갈리는 수명 문제, [=]가 멤버를 복사하지 않는다는 것, 성능 부담이 람다가 아니라 std::function에서 온다는 것을 정리했다."
date: 2024-09-02 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, programming, lambda, local-functions, code-structure, capture, std-function]
---
## 함수 하나가 너무 길어졌다

측정 데이터를 처리하는 함수를 짜다 보니 200줄이 넘어갔다. 안에 비슷한 계산이 세 번 반복되는데, 그걸 멤버 함수로 빼자니 그 함수 밖에서는 쓸 일이 없다. 헤더에 선언이 하나 늘어나고, 나중에 보는 사람이 "이건 어디서 쓰나" 하고 찾아봐야 한다.

C++에는 함수 안에 함수를 정의하는 문법이 없다. 파스칼이나 파이썬처럼 중첩 함수를 지원하지 않는다. GCC에 확장이 있긴 한데 표준이 아니고 C++에서는 안 된다.

대신 람다가 있다.

## 기본 형태

```cpp
[캡처 목록](매개변수 목록) -> 반환 타입 {
    // 본문
};
```

반환 타입은 대개 생략한다. 컴파일러가 `return` 문에서 추론한다. 다만 `return`이 여러 개인데 타입이 서로 다르면 추론이 실패하니 그때는 명시한다.

```cpp
// 에러 - int 와 double 중 어느 것인가
auto f = [](bool b) { if (b) return 1; else return 2.0; };

// 명시하면 된다
auto g = [](bool b) -> double { if (b) return 1; else return 2.0; };
```

## 실제로 쓴 예

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

`printNumber`와 `isEven`은 `processNumbers` 안에서만 존재한다. 이름이 밖으로 안 새고, 관련된 코드가 한 곳에 모인다.

세 번째 람다가 `[&]`로 앞의 두 람다를 캡처하는데, 이게 실제로 편한 점이다. 인자로 일일이 넘길 필요가 없다.

## 캡처가 핵심이고 위험한 부분이다

캡처 목록에 뭘 쓰느냐가 람다에서 제일 중요하다.

| 표기 | 뜻 |
| :--- | :--- |
| `[]` | 아무것도 캡처 안 함 |
| `[x]` | `x`를 값으로 복사 |
| `[&x]` | `x`를 참조로 |
| `[=]` | 쓰이는 변수를 모두 값으로 |
| `[&]` | 쓰이는 변수를 모두 참조로 |
| `[this]` | 객체 포인터를 캡처 (멤버 접근용) |
| `[*this]` | 객체 자체를 복사 (C++17) |
| `[p = std::move(q)]` | 초기화 캡처 (C++14) |

`[&]`는 편해서 습관처럼 쓰게 되는데, **람다가 그 자리에서만 쓰이고 끝나는 경우에만** 안전하다. 저장해두고 나중에 부르면 이미 사라진 변수를 가리킨다.

```cpp
std::function<void()> MakeHandler() {
    int count = 0;
    return [&]() { count++; };     // count 는 함수를 나가면 사라진다
}
```

컴파일은 된다. 실행하면 없는 메모리를 건드린다. 값이 이상하게 나오거나 그 자리에서 죽는다. 스택 메모리라 다른 함수가 덮어쓰기 전까지는 멀쩡해 보이기도 해서 재현이 어렵다.

기준을 이렇게 잡았다.

- 그 자리에서 소비되는 람다(`std::sort`, `std::for_each`의 비교자 등)는 `[&]`
- 저장하거나, 콜백으로 등록하거나, 스레드에 넘기는 람다는 `[=]` 또는 명시적 값 캡처

## [=]는 멤버 변수를 복사하지 않는다

이걸 몰라서 한참 헤맸다.

```cpp
class Worker {
public:
    void Start() {
        thread_ = std::thread([=]() {
            for (int i = 0; i < count_; ++i) {   // 멤버 변수
                // ...
            }
        });
    }
private:
    int count_ = 100;
    std::thread thread_;
};
```

`[=]`이니까 `count_`가 복사됐다고 생각했는데 아니다. 멤버 변수는 그 자체로 캡처되지 않는다. 실제로 캡처되는 건 `this` **포인터**이고, `count_`는 `this->count_`로 접근된다.

즉 `[=]`을 썼는데 참조 캡처와 다를 게 없다. `Worker` 객체가 스레드보다 먼저 죽으면 그대로 문제가 된다.

C++17부터는 `[*this]`로 객체 전체를 복사할 수 있다.

```cpp
thread_ = std::thread([*this]() {     // 객체 사본을 들고 간다
    for (int i = 0; i < count_; ++i) { }
});
```

또는 필요한 값만 지역 변수로 꺼내서 캡처한다. 이쪽이 의도가 더 분명하다.

```cpp
const int n = count_;
thread_ = std::thread([n]() { for (int i = 0; i < n; ++i) { } });
```

이 혼란이 컸는지, C++20에서 `[=]`이 `this`를 암묵적으로 캡처하는 동작은 폐기 예정으로 표시됐다. 컴파일러가 경고를 준다.

## mutable

값으로 캡처한 변수는 기본적으로 람다 안에서 수정할 수 없다. `operator()`가 `const`로 생성되기 때문이다.

```cpp
int n = 0;
auto f = [n]() { n++; };            // 에러
auto g = [n]() mutable { n++; };    // 된다
```

`mutable`을 붙이면 수정할 수 있는데, 수정되는 건 **람다가 들고 있는 사본**이다. 바깥의 `n`은 안 바뀐다. 호출할 때마다 사본은 유지되니 카운터처럼 쓸 수 있다.

```cpp
auto counter = [n = 0]() mutable { return ++n; };
counter();   // 1
counter();   // 2
```

## 재귀는 바로 안 된다

이름을 붙였지만 그 이름은 아직 타입이 정해지는 중이라 자기 자신을 부를 수 없다.

```cpp
auto fact = [](int n) { return n <= 1 ? 1 : n * fact(n - 1); };   // 에러
```

`std::function`을 쓰면 된다.

```cpp
std::function<int(int)> fact = [&](int n) {
    return n <= 1 ? 1 : n * fact(n - 1);
};
```

자기 자신을 인자로 받는 방법도 있다. 이쪽은 `std::function`의 오버헤드가 없다.

```cpp
auto fact = [](auto&& self, int n) -> int {
    return n <= 1 ? 1 : n * self(self, n - 1);
};
fact(fact, 5);
```

재귀가 필요하면 그냥 이름 있는 함수로 빼는 게 나은 경우가 많다.

## 성능 얘기는 std::function 얘기다

"람다를 많이 쓰면 느려진다"는 말을 어디선가 보고 그렇게 알고 있었는데 정확하지 않다.

람다는 컴파일러가 만들어주는 이름 없는 구조체다. 각 람다가 **고유한 타입**을 가지므로 호출 지점에서 어떤 코드가 불릴지 정확히 알 수 있고 대부분 인라인된다. 함수 포인터를 넘기는 것보다 오히려 빠른 경우가 많다. `std::sort`에 람다를 넘기는 것이 `qsort`에 함수 포인터를 넘기는 것보다 빠른 이유가 이것이다.

비용이 생기는 건 `std::function`에 담을 때다.

```cpp
std::function<void(int)> cb = [](int x) { };
```

`std::function`은 어떤 호출 가능 객체든 담을 수 있어야 해서 타입을 지운다. 그 대가로 간접 호출이 생기고, 캡처가 크면 힙 할당이 일어난다. 구현에 따라 작은 캡처는 내부 버퍼에 넣지만 크기 제한이 있다.

그래서 규칙은 이렇게 된다.

- 템플릿 인자로 받거나 `auto`로 받으면 오버헤드 없음
- 멤버 변수에 저장해야 하거나 타입을 통일해야 하면 `std::function`

```cpp
template <class F>
void ForEachSample(F&& f) { /* ... */ }        // 오버헤드 없음

std::vector<std::function<void()>> handlers;   // 여기는 타입 소거가 필요하다
```

## 디버깅이 조금 불편하다

콜스택에 람다가 이런 식으로 나온다.

```text
MyClass::Process::<lambda_1>::operator()
```

어느 람다인지 번호로만 구분된다. 한 함수에 람다가 여러 개 있으면 세어봐야 한다. 브레이크포인트는 정상적으로 걸린다.

중첩이 깊어지면 읽기가 급격히 어려워진다. 람다 안에 람다 안에 람다가 있으면 중괄호를 세게 된다. 세 줄 넘는 로직이나 두 단계 넘는 중첩이면 이름 있는 함수로 빼는 편이 결과적으로 나았다.

## 람다 말고 다른 방법

cpp 파일 안에서만 쓰는 보조 함수라면 익명 네임스페이스가 있다.

```cpp
namespace {
    double ToDb(double v) { return 20.0 * std::log10(v); }
}
```

이 함수는 그 번역 단위 밖에서 안 보이고, 헤더에 선언이 안 늘어난다. 이름이 있으니 콜스택에도 제대로 나오고 재귀도 된다. 함수 하나 안에서만 쓰이는 게 아니라 그 파일 여러 곳에서 쓰인다면 이쪽이 맞다.

정리하면 이런 순서로 고르게 됐다.

1. 그 자리에서 한 번만 쓰고 짧다 → 람다
2. 한 함수 안에서 여러 번 쓴다 → 이름 붙인 람다
3. 한 파일 안에서 여러 함수가 쓴다 → 익명 네임스페이스의 함수
4. 여러 파일에서 쓴다 → 평범한 함수

## 정리하면

- C++에 중첩 함수는 없다. 람다가 그 자리를 대신한다
- `[&]`는 그 자리에서 소비되는 람다에만 쓴다. 저장하거나 스레드에 넘기면 댕글링이 된다
- `[=]`은 멤버 변수를 복사하지 않는다. `this` 포인터를 캡처한다. 객체 사본이 필요하면 `[*this]`
- `mutable`로 수정하는 건 람다가 들고 있는 사본이다
- 람다 자체에는 오버헤드가 없다. 비용은 `std::function`에 담을 때 생긴다
- 길어지거나 중첩이 깊어지면 이름 있는 함수로 빼는 게 낫다
