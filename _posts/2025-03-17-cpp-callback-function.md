---
title: "(C++) 콜백 함수(Callback Function) 이해하기"
description: "C++에서 콜백 함수의 개념과 구현 방법"
date: 2025-03-17 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, callback, std-function, lambda, programming]
---

# (C++) 콜백 함수(Callback Function) 이해하기

- 최초 작성일: 2025년 3월 17일 (월)

## 목차

1. [콜백 함수의 개념](#콜백-함수의-개념)
2. [콜백 함수의 목적 및 사용 이유](#콜백-함수의-목적-및-사용-이유)
3. [콜백 함수의 종류와 구현 방법](#콜백-함수의-종류와-구현-방법)
4. [실무에서의 콜백 함수 활용 사례](#실무에서의-콜백-함수-활용-사례)
5. [콜백 함수의 장단점 분석](#콜백-함수의-장단점-분석)
6. [요약](#요약)

---

## 콜백 함수의 개념

C++에서 콜백 함수(Callback Function)는 특정 조건이나 이벤트가 발생했을 때 자동으로 호출되는 함수이다. 개발자가 직접 호출하는 함수가 아니라, 시스템이나 라이브러리가 미리 등록된 함수 포인터 또는 함수 객체를 호출하여 실행하는 방식이다.

다음과 같은 예시를 통해 보다 명확하게 이해할 수 있다.

> "택배 주문 시 '배송 완료 시 문자 알림' 옵션을 선택하면, 택배가 도착했을 때 택배 회사가 자동으로 등록된 번호로 문자를 보낸다. 이때의 문자 알림 기능이 바로 콜백 함수이다."

이 비유에서 택배 주문자는 알림을 받고자 자신의 연락처(콜백 함수)를 미리 등록하고, 택배 회사는 택배 도착(이벤트) 시 자동으로 알림을 보내는 역할을 수행한다.

- 문자 알림: 콜백 함수 (개발자가 작성한, 특정 상황에서 자동 호출되는 기능)
- 택배 회사: 콜백 함수를 호출하는 주체(메인 로직이나 라이브러리)
- 택배 도착: 특정 이벤트 또는 조건의 발생

즉, 콜백 함수는 프로그래머가 직접 호출하지 않아도, 특정 상황이나 조건이 충족되면 미리 지정된 로직에 의해 자동으로 호출되는 함수이다.

---

## 콜백 함수의 목적 및 사용 이유

- **비동기 처리**  
  특정 이벤트 발생 시 특정 기능을 실행한다 (예: UI 클릭, 네트워크 응답).

- **라이브러리와 사용자 코드 분리**  
  라이브러리가 사용자의 코드를 호출하여 유연성을 높인다.

- **확장성과 유연성**  
  호출될 동작을 실행 시점에 동적으로 변경할 수 있다.

---

## 콜백 함수의 종류와 구현 방법

### 1. 일반 함수 포인터(Function Pointer)
가장 기본적인 방식이다.

```cpp
#include <iostream>
using namespace std;

void callbackFunc(int value) {
    cout << "콜백 호출! 받은 값은: " << value << endl;
}

void executeCallback(void (*cb)(int), int val) {
    cout << "executeCallback 실행중..." << endl;
    cb(val);
}

int main() {
    executeCallback(callbackFunc, 42);
    return 0;
}
```

### 2. 클래스 멤버 함수 포인터(Class Member Function Pointer)
객체와 함께 호출한다.

```cpp
#include <iostream>
using namespace std;

class MyClass {
public:
    void memberCallback(int x) {
        cout << "멤버 콜백 호출됨: " << x << endl;
    }
};

void executeMemberCallback(MyClass* obj, void (MyClass::*cb)(int), int val) {
    cout << "executeMemberCallback 실행중..." << endl;
    (obj->*cb)(val);
}

int main() {
    MyClass myObj;
    executeMemberCallback(&myObj, &MyClass::memberCallback, 123);
    return 0;
}
```

### 3. `std::function` (C++11 이상 권장)
람다와 호환되어 현대적인 방식이다.

```cpp
#include <iostream>
#include <functional>
using namespace std;

void executeStdCallback(function<void(int)> cb, int val) {
    cout << "executeStdCallback 실행중..." << endl;
    cb(val);
}

int main() {
    executeStdCallback([](int v) {
        cout << "람다 콜백 호출됨: " << v << endl;
    }, 2025);

    return 0;
}
```

---

## 실무에서의 콜백 함수 활용 사례

- **UI 프로그래밍**  
  버튼 클릭 시 실행할 동작 등록에 사용된다.

- **네트워크 응답 처리**  
  HTTP 응답 수신 후 특정 동작을 수행한다.

- **비동기 IO 작업**  
  파일 입출력 작업 완료 후 콜백이 호출된다.

---

## 콜백 함수의 장단점 분석

| 구분          | 장점 ✅                       | 단점 ⚠️                             |
|---------------|-------------------------------|-------------------------------------|
| 일반 함수 포인터 | 빠르고 간단한 구현               | 함수 서명이 정확히 일치해야 한다.     |
| 멤버 함수 포인터 | 객체지향적 설계 가능              | 문법이 복잡하고 객체 관리가 필요하다. |
| std::function | 간편하고 람다와 호환 가능          | 약간의 성능 오버헤드가 있다.        |

성능이 중요하면 일반 함수 포인터, 유연성을 원하면 `std::function`을 권장한다.

---

## 요약

- 콜백 함수는 특정 이벤트 발생 시 자동 호출되는 함수이다.
- 함수 포인터 또는 `std::function`을 사용해 구현 가능하다.
- 현대적 C++에서는 람다와 `std::function` 활용이 권장된다.

