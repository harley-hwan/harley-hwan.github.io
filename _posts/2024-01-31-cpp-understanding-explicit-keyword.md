---
title: "(c++) Understanding 'explicit'"
description: "Preventing Implicit Conversions"
date: 2024-01-31 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, programming, explicit-keyword]
---
## 내용

`explicit` 키워드는 C++ 프로그래밍에서 중요한 역할을 한다. 이는 주로 생성자에서 사용되며, 코드에서의 암시적 형변환을 방지한다. 이러한 기능은 코드의 명확성을 높이고, 예기치 않은 변환으로 인한 버그를 방지하는 데 도움을 준다.

### 암시적 변환과 explicit

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

### explicit이 막는 실수

암시적 변환이 실제로 문제가 되는 상황은 이런 식이다.

```cpp
void PrintValue(MyClass obj) { ... }

PrintValue(10); // MyClass(int)가 explicit이 아니면 그대로 컴파일된다
```

정수를 잘못 넘겼는데도 컴파일러가 조용히 `MyClass` 임시 객체를 만들어 넘기기 때문에 실수를 알아차리기 어렵다. 생성자에 `explicit`을 붙이면 이 호출은 컴파일 에러가 되고, 변환이 필요하다면 `PrintValue(MyClass(10))`처럼 의도를 코드에 드러내야 한다.

<br/>

---
