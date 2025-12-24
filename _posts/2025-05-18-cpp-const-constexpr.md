---
title: "(C++) const와 constexpr 명확히 이해하기"
description: "C++에서 const와 constexpr의 차이점과 활용 방법"
date: 2025-05-18 10:00:00 +0900
categories: [Dev, C++]
---

# (C++) const constexpr 

* 최초 작성일: 2025년 5월 18일 (일)

## const 

**const**는 "constant"의 약자로, 한 번 값이 정해지면 이후 변경할 수 없는 상수를 나타내는 키워드다.

```cpp
const int number = 10;  // number는 이제 10으로 고정됨
// number = 20;  // ❌ 컴파일 오류 발생
```

const는 컴파일 타임과 런타임 모두에서 사용될 수 있다. 즉, 프로그램이 실행 중에도 값을 받아 const로 지정할 수 있다.

```cpp
int input;
std::cin >> input;
const int userValue = input;  // 실행 중에 입력된 값으로 설정됨
```

* **장점**:

  * 값을 안정적으로 보호할 수 있다.
  * 의도하지 않은 수정을 방지한다.

## constexpr 

**constexpr**은 "constant expression"의 약자로, 반드시 컴파일 타임에 값이 결정되는 상수를 의미한다. 컴파일 시점에서 미리 값이 계산되어 확정된다.

```cpp
constexpr int fixedValue = 100;  // 컴파일 단계에서 100으로 확정됨
```

런타임 중 값이 결정되는 경우 constexpr로 지정할 수 없다.

```cpp
int input;
std::cin >> input;
constexpr int userValue = input;  // ❌ 컴파일 오류 발생
```

* **장점**:

  * 프로그램 성능 향상(실행 시 추가 연산 없음)
  * 컴파일 타임에 미리 오류를 찾을 수 있음

## const constexpr 

| 항목           | const              | constexpr          |
| ------------ | ------------------ | ------------------ |
| 초기화 시점       | 런타임, 컴파일 타임 둘 다 가능 | 컴파일 타임에만 가능        |
| 값 변경 가능 여부   | 변경 불가능             | 변경 불가능             |
| 함수에 사용 가능 여부 | 일반 함수로는 불가능        | 컴파일 타임 함수로 가능      |
| 성능 영향        | 미미함                | 성능 최적화 (런타임 연산 없음) |

**즉,** 런타임에 값이 정해진다면 const를, 컴파일 타임에 반드시 결정할 수 있다면 constexpr을 사용한다.

## constexpr 

constexpr은 변수뿐만 아니라 함수에도 사용할 수 있다. constexpr 함수는 컴파일 시점에 미리 실행되어 결과가 확정된다.

```cpp
constexpr int multiply(int x, int y) {
    return x * y;
}

constexpr int result = multiply(4, 5);  // 컴파일 시점에 20으로 결정됨
```

이 함수는 실행 시점에 다시 호출될 필요 없이 컴파일 단계에서 결과가 계산된다.

## const constexpr 

### const 

```cpp
const int maxConnections = 100;  // 런타임에서 변하지 않을 설정 값
const std::string filePath = "config.json";  // 변경할 필요 없는 설정 경로
```

### constexpr 

```cpp
constexpr double PI = 3.14159265358979323846;  // 수학 상수로 미리 정의
constexpr int bufferSize = 1024;  // 고정된 버퍼 사이즈

constexpr int calculateArea(int radius) {
    return PI * radius * radius;
}

constexpr int area = calculateArea(5);  // 컴파일 타임에 계산 완료
```

위와 같이 자주 쓰이는 고정 값이나 연산을 미리 constexpr로 지정하면 프로그램 성능이 향상된다.

## 

* **const**는 값이 변경되지 않도록 보호하는 키워드로, 런타임 및 컴파일 타임 모두에서 사용 가능하다.
* **constexpr**는 반드시 컴파일 타임에 값이 확정되어야 하며, 성능 최적화를 위한 컴파일 타임 계산을 지원한다.
* 간단히 말해, 일반적인 상수 보호는 const를, 성능과 컴파일 타임 확정을 위한 상수는 constexpr을 사용하면 된다.
