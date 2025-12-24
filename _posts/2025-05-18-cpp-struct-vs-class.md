---
title: "(C++) 구조체(struct)와 클래스(class)의 차이 명확히 이해하기"
description: ""C++에서 struct와 class의 개념적, 기술적 차이와 사용법""
date: 2025-05-18 10:00:00 +0900
categories: [Dev, C++]
---

# (C++) 구조체(struct)와 클래스(class)의 차이 명확히 이해하기

* 최초 작성일: 2025년 5월 18일 (일)

## 목차

1. [구조체(struct)의 개념과 특징](#구조체struct의-개념과-특징)
2. [클래스(class)의 개념과 특징](#클래스class의-개념과-특징)
3. [구조체와 클래스의 주요 차이점](#구조체와-클래스의-주요-차이점)
4. [접근 지정자 이해하기](#접근-지정자-이해하기)
5. [언제 struct를 쓰고 언제 class를 쓸까?](#언제-struct를-쓰고-언제-class를-쓸까)
6. [실무 활용 예제](#실무-활용-예제)
7. [요약](#요약)

---

## 구조체(struct)의 개념과 특징

**구조체(struct)** 는 여러 데이터를 묶어 하나의 그룹으로 관리할 수 있도록 해주는 자료구조다. 기본적으로 데이터를 묶어서 표현할 때 주로 사용한다.

```cpp
struct Point {
    int x;
    int y;
};

Point p;
p.x = 10;
p.y = 20;
```

구조체는 멤버 변수와 멤버 함수를 모두 가질 수 있으며, 상속도 가능하다.

## 클래스(class)의 개념과 특징

**클래스(class)** 는 객체지향 프로그래밍(OOP)의 핵심으로, 데이터와 기능(메서드)을 묶어 캡슐화하는 역할을 한다.

```cpp
class Point {
private:
    int x;
    int y;

public:
    void set(int a, int b) {
        x = a;
        y = b;
    }

    int getX() { return x; }
    int getY() { return y; }
};

Point p;
p.set(10, 20);
```

클래스는 캡슐화, 상속, 다형성 등 OOP의 주요 개념을 지원한다.

## 구조체와 클래스의 주요 차이점

| 항목         | struct           | class                 |
| ---------- | ---------------- | --------------------- |
| 기본 접근 지정자  | public           | private               |
| 용도         | 단순 데이터 묶음 위주     | 데이터와 메서드를 묶는 객체지향적 설계 |
| 상속 가능 여부   | 가능               | 가능                    |
| 캡슐화와 정보 은닉 | 지원하지만 주로 사용하지 않음 | 적극적으로 사용함             |

가장 중요한 차이는 **기본 접근 지정자**다.

## 접근 지정자 이해하기

구조체는 기본 접근 지정자가 **public**이다. 따라서 따로 지정하지 않으면 모든 멤버가 외부에서 접근 가능하다.

```cpp
struct Person {
    std::string name;  // 기본 public
    int age;           // 기본 public
};
```

클래스는 기본 접근 지정자가 **private**이다. 즉, 따로 지정하지 않으면 모든 멤버는 클래스 외부에서 접근 불가능하다.

```cpp
class Person {
    std::string name;  // 기본 private
    int age;           // 기본 private

public:
    void setName(const std::string& n) { name = n; }
};
```

## 언제 struct를 쓰고 언제 class를 쓸까?

* **struct**:

  * 데이터 위주로 간단하게 묶어서 사용할 때
  * 주로 자료 전달이나 POD(Plain Old Data) 타입 정의할 때

* **class**:

  * 데이터와 기능을 함께 묶어 객체지향적으로 설계할 때
  * 캡슐화, 상속, 다형성을 활용할 때

## 실무 활용 예제

### 구조체 예시

```cpp
struct Color {
    int r, g, b;
};

Color c = {255, 0, 0};  // 빨간색 데이터 표현
```

### 클래스 예시

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

Account acc(1000.0);
acc.deposit(500.0);
```

## 요약

* **struct**는 데이터를 간단히 묶는 용도로, 기본 접근 지정자는 **public**이다.
* **class**는 데이터와 기능을 함께 묶어 객체지향적으로 관리하는 용도로, 기본 접근 지정자는 **private**이다.
* 구조체와 클래스 모두 상속이 가능하지만, 주로 설계 목적에 따라 적합한 쪽을 선택해 사용한다.
