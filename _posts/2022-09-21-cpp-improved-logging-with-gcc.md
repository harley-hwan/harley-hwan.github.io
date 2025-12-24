---
title: 로그를 좀더 보기쉽게 찍기(g++)
description: "__FILE__, __LINE__, __func__, __PRETTY_FUNCTION__"
date: 2022-09-21 10:00:00 +0900
categories: [Dev, C++]
tags: [__FILE__, __func__, __LINE__, __PRETTY_FUNCTION__, 로그, 매크로, C++, g++, log, typeid, typeid(T t).name()]
---

# 로그를 좀더 보기쉽게 찍기(g++)
- 최초 작성일: 2022년 9월 21일 (수)
- 참조: http://dev-crazybird.blogspot.com/2014/04/g.html

## 목차

[TOC]

<br/>

## 내용

로그를 작성할 때 해당 파일명과 소스라인 위치의 함수명까지 확인할 수 있는 방법이다.

- \_\_FILE\_\_ : 소스코드가 포함된 파일 이름을 return
- \_\_LINE\_\_ : 소스코드의 줄 번호 return
- \_\_func\_\_ : 소스코드가 포함된 함수 이름 return
- \_\_PRETTY_FUNCTION\_\_ : 소스코드가 포함된 클래스명과 타입명 return
- typeid(T t).name() : 맹글링된 클래스명이나 타입명 return

<br/>

위 매크로들은 g++ 기준이며, MSVC나 clang에서는 이와 같거나 같은 역할을 하는 다른 이름의 매크로가 있을 것이다.

<br/>

## 예제

```c++
#include <iostream>
#include <typeinfo>

class CPrettyLog
{
public:
    void Print(void)
    {
        std::cout
            << "__PRETTY_FUNCTION__ = " << __PRETTY_FUNCTION__ << std::endl
            << "__func__ = " << __func__ << std::endl
            << "__LINE__ = " << __LINE__ << std::endl
            << "__FILE__ = " << __FILE__ << std::endl
            << "typeid(this).name() = " << typeid(this).name() << std::endl
            << std::endl;
    }
};

void Print(void)
{
    std::cout
        << "__PRETTY_FUNCTION__ = " << __PRETTY_FUNCTION__ << std::endl
        << "__func__ = " << __func__ << std::endl
        << "__LINE__ = " << __LINE__ << std::endl
        << "__FILE__ = " << __FILE__ << std::endl
        << std::endl;
}
 
 
int main(int argc, char** argv)
{
    CPrettyLog pl;
    pl.Print();
 
    Print();
 
    std::cout
        << "__PRETTY_FUNCTION__ = " << __PRETTY_FUNCTION__ << std::endl
        << "__func__ = " << __func__ << std::endl
        << "__LINE__ = " << __LINE__ << std::endl
        << "__FILE__ = " << __FILE__ << std::endl
        << std::endl;
 
    return 0;
}
```

<br/>

## 결과

```c++
__PRETTY_FUNCTION__ = void CPrettyLog::Print()
__func__ = Print
__LINE__ = 13
__FILE__ = main.cpp
typeid(this).name() = P10CPrettyLog

__PRETTY_FUNCTION__ = void Print()
__func__ = Print
__LINE__ = 26
__FILE__ = main.cpp

__PRETTY_FUNCTION__ = int main(int, char**)
__func__ = main
__LINE__ = 42
__FILE__ = main.cpp
```
