---
title: "(C++) 구조체(struct)와 클래스(class)의 차이 명확히 이해하기"
description: "문법적 차이는 접근 지정자 기본값 둘뿐인데, 실제로 갈리는 건 그 뒤다. 상속 기본값 때문에 생기는 사고, 통신 패킷 구조체에서 정렬과 패딩을 챙겨야 하는 이유까지 정리했다."
date: 2025-05-18 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, struct, class, oop, memory-layout, packing, serialization]
---
## 문법적 차이는 두 개뿐이다

C++에서 `struct`와 `class`는 사실상 같은 것이다. 다른 건 두 가지다.

**멤버의 기본 접근 지정자.** `struct`는 public, `class`는 private다.

```cpp
struct Person {
    std::string name;  // 기본 public
    int age;           // 기본 public
};

class Person2 {
    std::string name;  // 기본 private
    int age;           // 기본 private
public:
    void setName(const std::string& n) { name = n; }
};
```

**상속의 기본 접근 지정자.** 이건 원래 몰랐다가 나중에 알았는데, 실제로 사고를 낸다.

```cpp
struct D1 : Base { };   // public 상속
class  D2 : Base { };   // private 상속
```

`class`로 선언하고 상속 지정자를 안 쓰면 private 상속이 된다. 그러면 `Base*`로 받는 함수에 `D2*`를 못 넘긴다. 다형성을 쓰려고 상속했는데 그게 안 되는 상황이다.

```cpp
void Process(Base* b);

D2 d;
Process(&d);            // 컴파일 오류 - private 상속이라 변환이 안 된다
```

에러 메시지가 "Base는 접근할 수 없는 기반 클래스"라고 나오는데, 처음 보면 무슨 말인지 감이 안 온다. `class D2 : public Base`로 고치면 된다.

이 두 가지 말고는 문법적으로 완전히 동일하다. `struct`도 멤버 함수, 생성자, 소멸자, 상속, 가상 함수, 템플릿 전부 된다.

## 그래서 뭘 쓰나

문법이 같으니 선택은 관례의 문제다. 이렇게 정리해서 쓴다.

**`struct`는 데이터를 묶어놓은 것.** 멤버가 전부 public이고, 서로 지켜야 할 규칙이 없다. 아무 값이나 넣어도 그 자체로 유효하다.

```cpp
struct Detection {
    double bin;
    double velocity;
    double snr_db;
};
```

**`class`는 불변 조건이 있는 것.** 멤버끼리 지켜야 할 관계가 있어서, 외부에서 아무렇게나 못 바꾸게 막아야 한다.

```cpp
class Account {
private:
    double balance;

public:
    Account(double b) : balance(b) {}

    void deposit(double amount) { balance += amount; }
    bool withdraw(double amount) {
        if (balance >= amount) {
            balance -= amount;
            return true;
        }
        return false;
    }
};
```

`balance`를 public으로 열어두면 잔액이 음수가 되는 걸 막을 수 없다. 이럴 때 `class`다.

판단 기준은 "**멤버 하나를 바꿨을 때 다른 멤버와 앞뒤가 안 맞을 수 있는가**"다. 있으면 `class`, 없으면 `struct`.

접근 지정자를 항상 명시하면 어느 쪽으로 선언했든 같아지긴 한다. 그래도 키워드 자체가 읽는 사람에게 신호를 준다. `struct`를 보면 "값 묶음이구나" 하고 지나갈 수 있다.

## 전방 선언에서 섞으면 경고가 난다

```cpp
// A.h
struct Config;      // 전방 선언

// B.h
class Config;       // 같은 타입인데 class 로 선언
```

표준상으로는 같은 타입이라 문제가 없다. 그런데 MSVC는 경고를 낸다.

```text
warning C4099: 'Config': type name first seen using 'class' now seen using 'struct'
```

프로젝트에서 경고를 에러로 처리하고 있으면 빌드가 깨진다. 전방 선언과 정의에서 같은 키워드를 쓰는 게 맞다.

## 집합체 초기화

`struct`의 실질적인 장점 하나가 중괄호 초기화다.

```cpp
struct Point { int x, y; };
Point p = {10, 20};          // 집합체 초기화
Point q{10, 20};
```

멤버 이름을 지정할 수도 있다. C++20의 지정 초기화다.

```cpp
Point p{.x = 10, .y = 20};   // C++20
```

인자가 많은 설정 구조체에서 순서를 헷갈릴 일이 없어져서 편하다.

다만 이건 **집합체**일 때만 된다. private 멤버가 하나라도 있거나, 사용자 정의 생성자가 있거나, 가상 함수가 있으면 집합체가 아니다.

```cpp
struct S {
    int a;
private:
    int b;          // private 멤버가 생기는 순간 집합체가 아니다
};
S s{1};             // 컴파일 오류
```

`struct`로 선언했다고 자동으로 집합체가 되는 게 아니다.

## 통신 구조체는 이야기가 다르다

여기부터가 실제로 시간을 많이 쓴 부분이다.

장비와 소켓으로 주고받는 패킷을 구조체로 정의하고 `memcpy`로 다루는 코드가 있었다. 여기서는 `struct`/`class` 선택보다 **메모리 배치**가 중요하다.

### 패딩

```cpp
struct Header {
    uint8_t  type;      // 1바이트
    uint32_t length;    // 4바이트
    uint16_t seq;       // 2바이트
};
// sizeof(Header) 는 7 이 아니라 12 다
```

컴파일러가 각 멤버를 자기 크기의 배수 주소에 놓으려고 사이에 빈 바이트를 넣는다. `type` 뒤에 3바이트, `seq` 뒤에 2바이트가 들어가서 12가 된다.

이걸 그대로 소켓으로 보내면 상대가 다르게 해석한다. 상대가 다른 컴파일러나 다른 아키텍처면 패딩 규칙도 다를 수 있다.

```cpp
#pragma pack(push, 1)
struct Header {
    uint8_t  type;
    uint32_t length;
    uint16_t seq;
};
#pragma pack(pop)
// sizeof(Header) == 7
```

`#pragma pack(1)`로 패딩을 없앤다. `push`/`pop`으로 감싸는 게 중요하다. 안 그러면 그 뒤에 포함되는 모든 헤더의 구조체에까지 적용된다. 표준 라이브러리 헤더가 그 영향을 받으면 아주 찾기 어려운 문제가 생긴다.

패킹된 구조체에는 대가가 있다. 정렬되지 않은 주소에서 읽게 되는데, x86은 느려질 뿐이지만 일부 ARM에서는 정렬 예외가 난다. 멤버의 주소를 받아 참조로 쓰는 것도 위험하다.

그래서 요즘은 패킹 대신 **바이트 배열로 직렬화**하는 쪽을 선호한다. 코드가 길어지지만 배치가 코드에 명시적으로 드러나고 엔디안도 같이 처리할 수 있다.

```cpp
void WriteU32BE(uint8_t* p, uint32_t v) {
    p[0] = uint8_t(v >> 24); p[1] = uint8_t(v >> 16);
    p[2] = uint8_t(v >> 8);  p[3] = uint8_t(v);
}
```

### memcpy로 다뤄도 되는 타입인가

구조체를 통째로 복사하려면 조건이 있다. 컴파일 타임에 확인할 수 있다.

```cpp
static_assert(std::is_trivially_copyable_v<Header>);
static_assert(std::is_standard_layout_v<Header>);
static_assert(sizeof(Header) == 7);
```

`is_trivially_copyable`은 `memcpy`로 복사해도 되는지, `is_standard_layout`은 멤버 배치가 예측 가능한지를 본다. `std::string`이나 가상 함수를 하나만 넣어도 둘 다 깨진다.

`sizeof` 검사를 같이 넣어두는 게 특히 유용했다. 누가 멤버를 하나 추가하면 그 자리에서 빌드가 깨진다. 안 그러면 통신이 안 되는 걸로 알게 되는데, 원인을 찾는 데 훨씬 오래 걸린다.

가상 함수가 하나라도 있으면 vtable 포인터가 앞에 붙어서 `sizeof`가 커지고 배치가 완전히 달라진다. 통신 구조체에 편의 함수를 넣다가 실수로 `virtual`을 붙이면 그대로 깨진다.

## 실제로 정한 규칙

- 데이터 묶음이고 불변 조건이 없으면 `struct`
- 멤버끼리 지켜야 할 관계가 있으면 `class`
- 상속에는 접근 지정자를 항상 명시한다. `class D : public Base`
- 전방 선언과 정의에서 키워드를 일치시킨다
- 통신 구조체는 `static_assert`로 크기와 레이아웃을 못 박아둔다

## 정리하면

- 문법적 차이는 멤버 기본 접근 지정자와 상속 기본 접근 지정자, 두 개뿐이다
- `class`로 선언하고 상속 지정자를 빼면 private 상속이 되어 다형성이 안 된다
- `struct`라고 자동으로 집합체가 되지 않는다. private 멤버나 생성자가 있으면 중괄호 초기화가 안 된다
- 통신용 구조체는 패딩 때문에 `sizeof`가 예상과 다르다. `#pragma pack`은 `push`/`pop`으로 감싼다
- `is_trivially_copyable`, `is_standard_layout`, `sizeof`를 `static_assert`로 박아두면 나중에 멤버를 추가할 때 빌드가 먼저 깨진다
