---
title: "(C++) explicit 키워드 이해하기"
description: "숫자를 잘못 넘겼는데 컴파일이 되어버린 일을 겪고 나서 정리한 내용. explicit이 막는 것과 못 막는 것, 인자가 둘 이상인 생성자에도 필요한 이유, explicit operator bool까지."
date: 2024-01-31 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, programming, explicit-keyword, implicit-conversion, type-safety]
---
## 컴파일이 되면 안 되는 코드가 컴파일됐다

설정값을 담는 작은 클래스를 만들어 쓰고 있었다. 대략 이런 모양이다.

```cpp
class SampleCount {
public:
    SampleCount(int n) : n_(n) {}
    int value() const { return n_; }
private:
    int n_;
};

void SetFrameLength(SampleCount n);
```

그리고 어느 날 이렇게 썼다.

```cpp
SetFrameLength(512);      // 샘플 수를 넘긴 것
```

여기까진 의도한 대로다. 문제는 다른 자리에서 실수로 초 단위 값을 넘겼을 때도 그대로 컴파일됐다는 것이다. 타입을 따로 만든 이유가 이런 실수를 막으려는 것이었는데 정작 그 역할을 못 하고 있었다.

원인은 인자 하나짜리 생성자가 **암시적 변환 통로**로 쓰였기 때문이다. 컴파일러가 `int`를 보고 "이걸로 `SampleCount`를 만들 수 있네"라고 판단해서 임시 객체를 만들어 넘긴다. 경고도 없다.

## explicit은 그 통로를 막는다

```cpp
class SampleCount {
public:
    explicit SampleCount(int n) : n_(n) {}
    // ...
};

SetFrameLength(512);                 // 컴파일 에러
SetFrameLength(SampleCount(512));    // 이렇게 써야 한다
```

이제 변환을 원하면 코드에 드러내야 한다. 타이핑이 늘어난 만큼, 읽는 사람이 "여기서 타입이 바뀐다"는 걸 알 수 있다.

이걸 알고 나서 표준 라이브러리를 다시 보니 곳곳에 쓰여 있었다.

```cpp
std::vector<int> a(10);      // 원소 10개. 이건 된다
std::vector<int> b = 10;     // 컴파일 에러. size 생성자가 explicit 이다
```

`std::vector`의 크기 생성자가 `explicit`이 아니었다면 `= 10`이 통과했을 것이고, 그건 아무도 원하지 않는 동작이다.

`std::chrono`도 마찬가지다.

```cpp
void SetTimeout(std::chrono::seconds t);

SetTimeout(5);                        // 에러
SetTimeout(std::chrono::seconds(5));  // 단위가 코드에 보인다
```

숫자 5가 초인지 밀리초인지 헷갈릴 여지를 없앤다. 타임아웃을 잘못 넣어서 하루를 날려본 뒤로는 이 설계가 왜 이런지 이해가 됐다.

## explicit이 막는 것과 못 막는 것

정확히 어디에 적용되는지 알아둘 필요가 있다. 막는 건 **복사 초기화** 문맥이다.

```cpp
class C { public: explicit C(int) {} };

C a(10);                 // 직접 초기화 - 된다
C b{10};                 // 직접 초기화 - 된다
C c = 10;                // 복사 초기화 - 에러
C d = {10};              // 복사 초기화 - 에러

void f(C);
f(10);                   // 인자 전달은 복사 초기화 - 에러
f(C(10));                // 명시했으니 된다

C g() { return 10; }     // 반환도 복사 초기화 - 에러
C h() { return C(10); }  // 된다

C i = static_cast<C>(10);  // 캐스팅은 직접 초기화 - 된다
```

`static_cast`가 통과한다는 게 중요하다. `explicit`은 변환을 금지하는 게 아니라 **말없이 일어나는 것을 금지**한다. 필요하면 언제든 명시해서 할 수 있다.

## 인자가 둘 이상이어도 필요하다

"인자가 하나일 때만 신경 쓰면 된다"고 알고 있었는데 C++11부터는 아니다. 중괄호 초기화 때문이다.

```cpp
struct Point { Point(int x, int y); };

void Draw(Point p);
Draw({10, 20});          // 생성자가 explicit 이 아니면 통과한다
```

중괄호로 인자 목록을 그대로 넘길 수 있어서, 인자가 몇 개든 암시적 변환이 일어난다. `Draw({10, 20})`가 읽기 편해서 일부러 허용하는 경우도 많지만, 그건 선택이어야 한다.

기본값을 가진 생성자도 조심해야 한다.

```cpp
class Buffer {
public:
    Buffer(int size, bool zero_fill = true);   // 사실상 인자 하나로 호출 가능
};
```

`Buffer b = 1024;`가 통과한다. 인자가 둘로 보이지만 하나만 줘도 되니 변환 생성자다.

## 언제 안 붙이나

전부 붙이는 게 답은 아니다. 변환이 자연스럽고 의도된 경우가 있다.

```cpp
std::string s = "hello";        // const char* -> string, 당연히 허용
std::complex<double> z = 1.0;   // 실수 -> 복소수, 수학적으로 자연스럽다
```

`std::string`의 `const char*` 생성자가 `explicit`이었다면 문자열 리터럴을 쓸 때마다 캐스팅을 해야 한다. 아무도 그걸 원하지 않는다.

기준은 이렇게 잡았다. **변환이 값의 표현만 바꾸는 것이면 허용하고, 의미가 달라지면 막는다.** `"hello"`와 `std::string("hello")`는 같은 값이다. 반면 `512`와 `SampleCount(512)`는 다르다. 앞은 그냥 숫자고 뒤는 "샘플 수"라는 의미가 붙는다.

그런데 허용해서 사고가 나는 경우도 있다.

```cpp
std::vector<std::string> v;
v.push_back(nullptr);      // 컴파일된다
```

`std::string(const char*)`가 `explicit`이 아니라서 `nullptr`로 `std::string`을 만들려 하고, 그 자리에서 정의되지 않은 동작이다. 컴파일러는 아무 말도 안 한다. 편의를 위해 열어둔 통로가 다른 곳에서 구멍이 되는 예다.

## explicit operator bool

생성자 말고 변환 연산자에도 붙는다. 이쪽이 오히려 더 자주 쓴다.

```cpp
class Connection {
public:
    explicit operator bool() const { return fd_ >= 0; }
private:
    int fd_ = -1;
};

Connection c;
if (c) { }               // 된다
while (c) { }            // 된다
int n = c;               // 에러 - 이게 막고 싶었던 것
bool b = c;              // 에러
```

`explicit`을 안 붙이면 `if (c)`를 위해 열어둔 통로로 `int n = c;`나 `c + 1` 같은 것까지 들어온다. 두 `Connection`을 `==`로 비교했는데 둘 다 bool로 변환되어 "둘 다 유효함"이 참으로 나오는 식의 버그가 생긴다.

`if`, `while`, `&&`, `!` 같은 자리는 문맥상 bool이 필요한 곳이라 `explicit`이어도 자동으로 변환된다. 표준에서 이 자리를 따로 정해뒀다. `std::ifstream`이나 `std::unique_ptr`이 `if`에서는 되는데 `int`에 대입은 안 되는 이유가 이것이다.

C++11 이전에는 이 동작을 흉내 내려고 멤버 포인터를 반환하는 기법(safe bool idiom)을 썼다. `explicit operator bool`이 생기면서 필요 없어졌다.

## C++20의 조건부 explicit

템플릿을 쓰다 보면 "어떤 타입일 때는 암시적 변환을 허용하고 어떤 타입일 때는 막고 싶은" 상황이 나온다.

```cpp
template <class T>
class Wrapper {
public:
    template <class U>
    explicit(!std::is_convertible_v<U, T>) Wrapper(U&& u);
};
```

`explicit(조건)`으로 컴파일 타임에 결정한다. `U`가 `T`로 자연스럽게 변환되는 타입이면 암시적 변환을 허용하고, 아니면 막는다. `std::optional`이나 `std::pair` 같은 표준 타입들이 이런 규칙을 쓴다.

직접 쓸 일은 드문데, 표준 라이브러리 문서에서 `explicit(see below)`이라고 적힌 걸 볼 때 이 얘기라는 걸 알면 된다.

## 실제로 정한 규칙

한동안 헤매다가 이렇게 정리했다.

- 인자 하나로 호출 가능한 생성자는 **기본적으로 `explicit`**을 붙인다
- 변환이 의도된 설계면 뺀다. 대신 왜 뺐는지 주석을 남긴다
- 복사 생성자와 이동 생성자에는 안 붙인다. 붙이면 값 전달과 반환이 안 된다
- `operator bool`은 항상 `explicit`
- 그 외 변환 연산자(`operator int` 같은 것)는 웬만하면 만들지 않는다. 만들면 어디서 불리는지 추적이 어려워진다

정적 분석 도구도 도움이 된다. clang-tidy의 `google-explicit-constructor`는 `explicit`이 빠진 변환 생성자를 전부 지적해준다. 기존 코드에 처음 돌리면 지적이 쏟아지는데, 그중 진짜 문제인 것을 골라내는 것만으로도 볼 만하다.

## 정리하면

- 인자 하나짜리 생성자는 암시적 변환 통로가 된다. 타입을 나눠 만든 의미가 사라진다
- `explicit`은 복사 초기화만 막는다. 직접 초기화와 `static_cast`는 그대로 된다
- C++11의 중괄호 초기화 때문에 인자가 둘 이상인 생성자에도 필요하다
- 기본값이 있는 생성자는 인자가 여러 개로 보여도 변환 생성자일 수 있다
- `if (obj)`만 허용하고 산술 연산은 막고 싶으면 `explicit operator bool`
