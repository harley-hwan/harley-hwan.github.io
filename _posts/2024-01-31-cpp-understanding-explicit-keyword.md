---
title: "(c++) Understanding 'explicit'"
description: "Preventing Implicit Conversions"
date: 2024-01-31 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, programming, explicit keyword]
---

# Understanding 'explicit' in C++

- 최초 작성일: 2024년 1월 31일 (수)

## 목차



<br/>

## 내용

`explicit` 키워드는 C++ 프로그래밍에서 중요한 역할을 한다. 이는 주로 생성자에서 사용되며, 코드에서의 암시적 형변환을 방지한다. 이러한 기능은 코드의 명확성을 높이고, 예기치 않은 변환으로 인한 버그를 방지하는 데 도움을 준다.

### explicit이란 무엇인가?

C++에서 생성자가 하나의 인자만 받는 경우, 컴파일러는 해당 생성자를 이용한 암시적 변환을 허용할 수 있다. 이는 때때로 예상치 못한 결과를 초래할 수 있다. `explicit` 키워드를 생성자 앞에 붙이면, 이러한 암시적 변환을 막을 수 있다. 즉, 타입 변환을 명시적으로만 허용한다.

### explicit 사용 예

```cpp
class MyClass {
public:
    explicit MyClass(int x) { ... }
};
```

이 예제에서 `MyClass`의 생성자는 `explicit`으로 선언된다. 따라서 `MyClass` 객체를 초기화하기 위해서는 명시적인 형변환이 필요하다.

### explicit 없이 선언한 경우

```cpp
class MyClass {
public:
    MyClass(int x) { ... }
};
```

이 경우, `MyClass` 생성자는 암시적 형변환을 허용한다. 예를 들어, `MyClass obj = 10;` 같은 코드가 가능하다. 여기서 `10`은 자동으로 `MyClass` 타입으로 변환된다.

### explicit 사용의 장점

`explicit`을 사용하면 코드의 의도를 더 명확하게 표현할 수 있다. 이는 타입 변환의 오류를 줄이는 데 도움을 준다. 또한, 코드의 가독성과 유지보수성이 향상된다.

### 결론

`explicit` 키워드는 C++ 프로그래밍에서 타입 변환의 오류를 방지하고 코드의 명확성을 높이는 데 중요한 역할을 한다. 생성자에 `explicit`을 사용하는 것은 좋은 프로그래밍 습관이다.

<br/>

---
