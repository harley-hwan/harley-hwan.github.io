---
title: (c++) C++에서 파이썬 스크립트 불러오기
description: "c, c++, python, Py_SetProgramName, Py_Initialize, PyRun_SimpleString, Py_Finalize, PyMem_RawFree"
date: 2023-06-08 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, shellapi, windowsapi, system, command, exe, execute, HWND, windows.h, Shellapi.h, DT1-Remote]
---

# C++ 

## 
C++ 프로그램 내에서 파이썬 스크립트를 실행하는 방법을 설명한다. C++의 성능과 파이썬의 유연성을 결합할 수 있다.

<br/>

## 
- C++ 컴파일러
- Python 개발 라이브러리 (예: Python.h)

<br/>

## 

```c++
#include <Python.h>

int main(int argc, char* argv[])
{
    // 1. 프로그램 이름 디코딩
    wchar_t* program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    // 2. 파이썬 인터프리터 초기화
    Py_SetProgramName(program);  // 선택적이지만 권장됨
    Py_Initialize();

    // 3. 파이썬 코드 실행
    PyRun_SimpleString("from time import time,ctime\n"
        "print('Today is',ctime(time()))\n");

    // 4. 파이썬 인터프리터 종료
    Py_Finalize();

    // 5. 메모리 정리
    PyMem_RawFree(program);
    return 0;
}
```

<br/>

## 

1. **프로그램 이름 디코딩**
   - `Py_DecodeLocale` 함수를 사용해 프로그램 이름(argv[0])을 디코딩한다.
   - 이는 파이썬 인터프리터가 프로그램의 위치를 정확히 알 수 있게 해준다.

2. **파이썬 인터프리터 초기화**
   - `Py_SetProgramName`: 파이썬 인터프리터에 프로그램 이름을 설정한다.
   - `Py_Initialize`: 파이썬 인터프리터를 초기화한다.

3. **파이썬 코드 실행**
   - `PyRun_SimpleString`: 문자열로 된 파이썬 코드를 실행한다.
   - 이 예제에서는 현재 날짜와 시간을 출력하는 간단한 파이썬 스크립트를 실행한다.

4. **파이썬 인터프리터 종료**
   - `Py_Finalize`: 파이썬 인터프리터를 종료하고 사용된 리소스를 정리한다.

5. **메모리 정리**
   - `PyMem_RawFree`: 디코딩된 프로그램 이름에 할당된 메모리를 해제한다.

<br/>

## 
- 이 코드를 컴파일할 때는 파이썬 개발 라이브러리를 링크해야 한다.
- 시스템에 설치된 파이썬 버전과 호환되는 헤더 파일을 사용해야 한다.

<br/>

## 
이런 식으로 C++ 프로그램 내에서 파이썬 스크립트를 쉽게 실행할 수 있다. 이는 두 언어의 장점을 결합하여 더 강력하고 유연한 프로그램을 만들 수 있게 해준다.
