---
title: "(c++) 클래스의 Static 멤버 변수와 Static 멤버 함수 이해하기"
description: "공유되는 멤버의 선언, 정의, 사용 방법 알아보기"
date: 2024-06-05 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, programming, static keyword, static member variable, static member function]
---
# C++에서 클래스의 Static 멤버 변수와 Static 멤버 함수 이해하기
- 최초 작성일: 2024년 6월 5일 (수)

## 목차

[TOC]

<br/>

## 내용

# C++ 클래스의 static 멤버 변수와 static 멤버 함수

C++에서 클래스의 static 멤버 변수와 static 멤버 함수는 클래스의 모든 인스턴스에서 공유되는 멤버이다.
이들은 클래스 자체에 속하며, 인스턴스와 독립적으로 존재한다. 
static 멤버 변수와 static 멤버 함수의 선언, 정의, 사용 방법에 대해 설명하겠다.

## Static 멤버 변수

### 선언

클래스 내부에서 static 멤버 변수를 선언할 때는 `static` 키워드를 사용합니다. 일반적으로 클래스의 헤더 파일(`.h`)에서 선언한다.

```cpp
class MyClass {
public:
    static int myStaticVariable;
};
```

### 정의

static 멤버 변수는 클래스 내부에서 선언만 가능하고, 정의는 클래스 외부에서 이루어져야 한다. 일반적으로 클래스의 구현 파일(`.cpp`)에서 정의한다.

```cpp
int MyClass::myStaticVariable = 0;
```

정의할 때는 클래스명과 범위 연산자(`::`)를 사용하여 static 멤버 변수를 지정한다. 이 과정에서 메모리 할당과 초기화가 이루어진다.

### 사용

static 멤버 변수는 클래스의 인스턴스와 독립적으로 사용할 수 있다. 클래스 이름과 범위 연산자(`::`)를 사용하여 직접 접근할 수 있다.

```cpp
MyClass::myStaticVariable = 10;
```

## Static 멤버 함수

### 선언

클래스 내부에서 static 멤버 함수를 선언할 때는 `static` 키워드를 사용한다. 일반적으로 클래스의 헤더 파일(`.h`)에서 선언한다.

```cpp
class MyClass {
public:
    static void myStaticFunction();
};
```

### 정의

static 멤버 함수는 클래스 외부에서 정의할 수 있다. 일반적으로 클래스의 구현 파일(`.cpp`)에서 정의한다.

```cpp
void MyClass::myStaticFunction() {
    // 함수 구현
}
```

### 사용

static 멤버 함수는 클래스의 인스턴스와 독립적으로 호출할 수 있다. 클래스 이름과 범위 연산자(`::`)를 사용하여 직접 호출할 수 있다.

```cpp
MyClass::myStaticFunction();
```

## Static 멤버 함수에서 Static 멤버 변수 사용

static 멤버 함수에서는 static 멤버 변수에 직접 접근할 수 있다. 클래스 이름과 범위 연산자(`::`)를 사용하여 접근한다.

```cpp
class MyClass {
public:
    static int myStaticVariable;
    static void myStaticFunction();
};

int MyClass::myStaticVariable = 0;

void MyClass::myStaticFunction() {
    myStaticVariable = 10; // Static 멤버 변수에 직접 접근
}
```

## 일반 멤버 함수에서 Static 멤버 변수 사용

일반 멤버 함수에서도 static 멤버 변수에 접근할 수 있다. 클래스 이름과 범위 연산자(`::`)를 사용하거나, 직접 변수 이름을 사용할 수 있다.

```cpp
class MyClass {
public:
    static int myStaticVariable;
    void myFunction();
};

int MyClass::myStaticVariable = 0;

void MyClass::myFunction() {
    myStaticVariable = 10; // 직접 변수 이름 사용
    MyClass::myStaticVariable = 20; // 클래스 이름과 범위 연산자 사용
}
```

## 정리

- static 멤버 변수는 클래스의 모든 인스턴스에서 공유된다.
- static 멤버 변수는 클래스 내부에서 선언하고, 클래스 외부에서 정의해야 한다.
- static 멤버 함수는 클래스의 인스턴스와 독립적으로 호출할 수 있다.
- static 멤버 함수에서는 static 멤버 변수에 직접 접근할 수 있다.
- 일반 멤버 함수에서도 static 멤버 변수에 접근할 수 있다.
