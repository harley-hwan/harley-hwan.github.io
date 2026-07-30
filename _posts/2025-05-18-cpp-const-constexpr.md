---
title: "(C++) const와 constexpr 명확히 이해하기"
description: "상수를 어디에 어떻게 선언할지 정리하면서 알게 된 것들. const의 위치가 바꾸는 의미, constexpr 함수가 런타임에도 불린다는 것, 헤더에 상수를 두면 사본이 여러 개 생긴다는 것."
date: 2025-05-18 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, const, constexpr, compile-time, modern-cpp, linkage, inline-variable]
---
## const

`const`는 한 번 정해지면 그 이름으로는 바꿀 수 없다는 뜻이다.

```cpp
const int number = 10;
// number = 20;  // 컴파일 오류
```

값이 언제 정해지는지는 상관없다. 실행 중에 받은 값으로도 만들 수 있다.

```cpp
int input;
std::cin >> input;
const int userValue = input;  // 실행 중에 정해진다
```

이게 `constexpr`과 갈리는 지점이다.

## const의 위치가 의미를 바꾼다

포인터에 붙일 때가 헷갈린다. 규칙은 **`const`가 왼쪽에 있는 것을 수식한다. 왼쪽에 아무것도 없으면 오른쪽을 수식한다.**

```cpp
const int* p;        // 가리키는 값이 const. p 는 다른 곳을 가리킬 수 있다
int const* p;        // 위와 같다
int* const p;        // p 자체가 const. 가리키는 값은 바꿀 수 있다
const int* const p;  // 둘 다 const
```

읽는 요령은 오른쪽에서 왼쪽으로 읽는 것이다. `int* const p`는 "p는 const인 포인터, int를 가리키는"이 된다.

함수 인자로 받을 때 `const char* s`와 `char* const s`를 헷갈려서 컴파일이 안 되는 경우가 종종 나온다. 대부분 필요한 건 앞쪽이다. "내가 이 문자열을 안 바꾼다"는 약속이다.

## 멤버 함수의 const

```cpp
class Frame {
public:
    int Size() const { return n_; }        // 객체 상태를 안 바꾼다
    void Resize(int n) { n_ = n; }
private:
    int n_ = 0;
};
```

`const` 객체나 `const` 참조로는 `const` 멤버 함수만 부를 수 있다. 그래서 읽기만 하는 함수에는 붙여두는 게 맞다. 안 붙여두면 나중에 `const Frame&`로 받는 함수를 만들 때 전부 고쳐야 한다.

`const` 멤버 함수 안에서도 바꿔야 하는 멤버가 있으면 `mutable`을 쓴다. 캐시나 뮤텍스가 대표적이다.

```cpp
class Table {
public:
    double Get(int i) const {
        std::lock_guard<std::mutex> lock(m_);   // const 함수에서 뮤텍스를 잠근다
        return data_[i];
    }
private:
    mutable std::mutex m_;
    std::vector<double> data_;
};
```

논리적으로는 객체 상태가 안 바뀌지만 비트 수준에서는 뮤텍스가 바뀐다. 이럴 때 쓰라고 있는 게 `mutable`이다.

## const가 보장하는 것과 아닌 것

한 가지 오해가 있었다. `const int&`로 받으면 그 값이 함수 실행 중에 안 바뀐다고 생각했는데 아니다.

```cpp
int x = 1;
const int& r = x;
x = 2;              // r 을 통해 보면 값이 바뀌어 있다
```

`const`는 "이 이름으로는 못 바꾼다"는 것이지 "이 값이 안 변한다"는 게 아니다. 다른 참조나 다른 스레드가 바꿀 수 있다.

`const_cast`로 벗겨서 수정하는 것도 조심해야 한다. 원본이 진짜 `const` 객체면 정의되지 않은 동작이다. 컴파일러가 그 값을 읽기 전용 영역에 넣었을 수 있어서 쓰는 순간 죽는다. 원본이 원래 비-const였고 참조만 const였던 경우에만 안전하다.

## constexpr

`constexpr`은 컴파일 타임에 값이 정해진다는 뜻이다.

```cpp
constexpr int fixedValue = 100;  // 컴파일 시점에 확정
```

실행 중에 정해지는 값은 못 쓴다.

```cpp
int input;
std::cin >> input;
constexpr int userValue = input;  // 컴파일 오류
```

배열 크기, 템플릿 인자, `case` 라벨처럼 컴파일 타임 상수가 필요한 자리에 쓸 수 있다는 게 실질적인 차이다.

```cpp
constexpr int kFftSize = 512;
double buf[kFftSize];              // 된다

const int n = get_size();          // 런타임 값
double buf2[n];                    // 표준 C++ 에서는 안 된다
```

`constexpr` 변수는 자동으로 `const`이기도 하다. 따로 붙일 필요가 없다.

## 두 키워드 비교

| 항목 | const | constexpr |
| :--- | :--- | :--- |
| 값이 정해지는 시점 | 런타임/컴파일 타임 둘 다 | 컴파일 타임만 |
| 값 변경 | 불가 | 불가 |
| 배열 크기 등에 사용 | 경우에 따라 | 항상 가능 |
| 함수에 붙일 때 | 멤버 함수가 상태를 안 바꿈 | 컴파일 타임 평가가 가능함 |

## constexpr 함수는 런타임에도 불린다

여기서 오해가 하나 있었다. `constexpr`을 붙이면 항상 컴파일 타임에 계산되는 줄 알았다.

```cpp
constexpr int multiply(int x, int y) {
    return x * y;
}

constexpr int a = multiply(4, 5);   // 컴파일 타임에 20
int n = read_input();
int b = multiply(n, 5);             // 런타임에 계산된다
```

`constexpr` 함수는 "인자가 상수식이면 컴파일 타임에 계산할 수 있다"는 뜻이다. 아니면 평범한 함수로 동작한다. 그래서 `constexpr`을 붙였다고 성능이 좋아지는 게 아니다. 상수식 문맥에서 쓸 때만 계산이 사라진다.

반드시 컴파일 타임에만 실행되게 하려면 C++20의 `consteval`을 쓴다.

```cpp
consteval int must_be_compile_time(int x) { return x * 2; }

int n = read_input();
int y = must_be_compile_time(n);    // 컴파일 오류
```

컴파일 타임에 계산됐는지 확인하고 싶으면 `static_assert`에 넣어보면 된다. 통과하면 상수식으로 평가된 것이다.

```cpp
static_assert(multiply(4, 5) == 20);
```

`constexpr` 함수에 걸리는 제약은 표준 버전마다 완화됐다. C++11에서는 `return` 문 하나만 가능했고, C++14부터 지역 변수와 반복문이 되고, C++20에서는 동적 할당과 `try`/`catch`까지 허용된다. 오래된 컴파일러에서 `constexpr` 함수가 안 되는 경우는 대개 이 제약 때문이다.

## 헤더에 상수를 두면 사본이 여러 개 생긴다

이건 실제로 겪기 전에는 몰랐다.

```cpp
// Constants.h
const double kPi = 3.14159265358979323846;
constexpr int kFftSize = 512;
```

이 헤더를 여러 cpp가 포함해도 링크 에러가 안 난다. C++에서 네임스페이스 스코프의 `const` 변수는 기본적으로 **내부 링키지**를 갖기 때문이다. 즉 cpp마다 자기만의 사본을 하나씩 갖는다.

`constexpr`도 `const`를 함의하므로 마찬가지다.

값이 같으니 결과는 문제없다. 다만 두 가지가 걸린다. 사본만큼 공간을 쓰고, **주소가 서로 다르다**. 상수의 주소를 비교하거나 참조를 저장하는 코드가 있으면 cpp마다 다른 값이 나온다.

C++17부터 `inline`을 붙이면 하나로 합쳐진다.

```cpp
// Constants.h
inline constexpr double kPi = 3.14159265358979323846;
inline constexpr int    kFftSize = 512;
```

지금은 헤더의 상수에 습관적으로 `inline constexpr`을 붙인다. [static 멤버](/posts/cpp-static-members-in-classes/)에서 `inline static`을 쓰는 것과 같은 이야기다.

## #define 대신 constexpr

예전 코드에는 상수가 매크로로 되어 있는 경우가 많다.

```cpp
#define FFT_SIZE 512
```

`constexpr`이 나은 이유가 몇 가지 있다.

- **타입이 있다.** 매크로는 그냥 토큰 치환이라 타입 검사가 없다
- **스코프가 있다.** 매크로는 파일 끝까지 유효하고 네임스페이스도 무시한다. 남의 헤더에 있는 같은 이름과 충돌한다
- **디버거에서 보인다.** 매크로는 전처리 단계에서 사라져서 디버거가 모른다
- **주소를 가질 수 있다.** 참조로 넘기거나 컨테이너에 담을 수 있다

매크로 이름이 짧고 흔하면 진짜로 충돌한다. `MAX`, `MIN`, `ERROR` 같은 이름은 윈도우 헤더와 부딪히는 걸로 유명하다. `windows.h`가 정의하는 `min`/`max` 매크로 때문에 `std::min`이 안 되는 문제는 `NOMINMAX`를 정의해서 막는다.

## if constexpr

C++17에 들어온 것인데 템플릿을 쓸 때 유용하다.

```cpp
template <class T>
void Print(const T& v) {
    if constexpr (std::is_floating_point_v<T>) {
        printf("%f\n", v);
    } else {
        printf("%d\n", v);
    }
}
```

조건이 거짓인 가지는 **컴파일조차 되지 않는다**. 일반 `if`였다면 `T`가 `int`일 때도 `%f` 쪽 코드가 컴파일되어야 해서, 타입에 따라 유효하지 않은 코드가 있으면 에러가 난다.

## 실제로 정한 규칙

- 안 바꿀 변수는 일단 `const`. 지역 변수도 마찬가지다. 나중에 읽을 때 "이건 안 변한다"가 바로 보인다
- 읽기만 하는 멤버 함수에는 `const`. 나중에 `const&`로 받는 코드가 생길 때 고칠 일이 없다
- 컴파일 타임에 정할 수 있는 상수는 `constexpr`. 배열 크기나 템플릿 인자로 쓸 수 있는지가 갈린다
- 헤더에 두는 상수는 `inline constexpr`
- 매크로 상수는 `constexpr`로 바꾼다

## 정리하면

- `const`는 값이 언제 정해지든 상관없고, `constexpr`은 컴파일 타임에만 정해진다
- `const`의 위치가 포인터를 수식하는지 값을 수식하는지 바꾼다. 오른쪽에서 왼쪽으로 읽는다
- `const`는 "이 이름으로는 못 바꾼다"는 뜻이지 값이 안 변한다는 보장이 아니다
- `constexpr` 함수는 인자가 상수식일 때만 컴파일 타임에 계산된다. 붙였다고 항상 빨라지는 게 아니다
- 헤더의 `const`/`constexpr` 변수는 cpp마다 사본이 생긴다. C++17의 `inline`으로 하나로 만든다
