---
title: "(C++) Windows 소켓 에러 메시지 출력 구현"
description: ""FormatMessage를 이용한 시스템 에러 코드 해석""
date: 2023-02-10 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, windows, socket, error, mfc]
---

# Windows 소켓 에러 메시지 출력 구현
- 최초 작성일: 2023년 2월 10일 (금)

<br/>

## 목차
1. [소개](#소개)
2. [구현 코드](#구현-코드)
3. [함수 설명](#함수-설명)

<br/>

## 소개
Windows 소켓 프로그래밍에서 발생하는 에러 코드를 사용자가 이해하기 쉬운 메시지로 변환하여 출력한다. FormatMessage API를 사용하여 시스템 에러 코드에 대한 상세 설명을 획득한다.

<br/>

## 구현 코드
시스템 에러 코드를 해석하여 출력하는 함수이다.

```cpp
void displayerror(int nErrorCode)
{
    LPVOID lpMsgBuf;
    FormatMessage(
        FORMAT_MESSAGE_ALLOCATE_BUFFER |
            FORMAT_MESSAGE_FROM_SYSTEM |
            FORMAT_MESSAGE_IGNORE_INSERTS,
        NULL,
        nErrorCode,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // 기본 시스템 언어 사용
        (LPTSTR)&lpMsgBuf,
        0,
        NULL);
    printf("%d %s\n", nErrorCode, (LPCTSTR)lpMsgBuf);
    LocalFree(lpMsgBuf);
}
```

<br/>

## 함수 설명

1. **FormatMessage 매개변수 설명**
   - FORMAT_MESSAGE_ALLOCATE_BUFFER
     - 시스템이 메시지 버퍼를 자동으로 할당한다
     - LocalFree로 해제해야 한다
   
   - FORMAT_MESSAGE_FROM_SYSTEM
     - 시스템 메시지 테이블에서 메시지를 찾는다
     - Windows 시스템 에러 메시지를 사용한다

   - FORMAT_MESSAGE_IGNORE_INSERTS
     - 인자 삽입을 무시한다
     - 메시지를 있는 그대로 반환한다

2. **언어 설정**
   - MAKELANGID 매크로를 사용한다
   - LANG_NEUTRAL: 중립 언어 설정
   - SUBLANG_DEFAULT: 시스템 기본 서브 언어 사용

3. **메모리 관리**
   - lpMsgBuf: 시스템이 할당한 메시지 버퍼
   - LocalFree로 버퍼를 해제한다
   - 메모리 누수 방지를 위해 반드시 호출해야 한다

4. **사용 예시**
```cpp
// 소켓 함수 호출 후 에러 발생 시
int error = WSAGetLastError();
displayerror(error);

// 일반 시스템 함수 호출 후 에러 발생 시
int error = GetLastError();
displayerror(error);
```

이 함수는 Windows 네트워크 프로그래밍에서 발생하는 다양한 에러 상황을 디버깅할 때 유용하게 사용할 수 있다. 에러 코드를 사람이 읽을 수 있는 형태로 변환하여 문제 해결을 돕는다.
