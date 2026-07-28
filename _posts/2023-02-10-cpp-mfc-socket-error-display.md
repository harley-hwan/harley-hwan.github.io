---
title: "(C++) Windows 소켓 에러 메시지 출력 구현"
description: "FormatMessage를 이용한 시스템 에러 코드 해석"
date: 2023-02-10 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, windows, socket, error, mfc]
---
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

## FormatMessage 매개변수

- FORMAT_MESSAGE_ALLOCATE_BUFFER: 시스템이 메시지 버퍼를 자동으로 할당한다. 이렇게 할당된 버퍼는 LocalFree로 해제해야 한다.
- FORMAT_MESSAGE_FROM_SYSTEM: 시스템 메시지 테이블에서 메시지를 찾는다. Windows 시스템 에러 메시지를 그대로 사용한다.
- FORMAT_MESSAGE_IGNORE_INSERTS: 인자 삽입을 무시하고 메시지를 있는 그대로 반환한다.

<br/>

## 언어 설정

MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT)는 중립 언어와 시스템 기본 서브 언어 조합으로, 시스템에 설정된 언어의 메시지를 받아온다.

<br/>

## 메모리 관리

lpMsgBuf는 시스템이 할당한 메시지 버퍼이므로 사용이 끝나면 반드시 LocalFree로 해제해야 메모리 누수가 없다.

<br/>

## 유니코드 빌드 주의점

MFC 프로젝트 기본값인 유니코드 빌드에서는 FormatMessage가 FormatMessageW로 매핑되어 lpMsgBuf가 와이드 문자열이 된다. printf의 %s는 char*를 기대하므로 이대로 출력하면 메시지가 깨지거나 첫 글자만 나올 수 있다. 이 경우 wprintf와 %ls를 쓰거나, TCHAR 매핑에 맞춰 _tprintf를 사용한다.

```cpp
wprintf(L"%d %ls\n", nErrorCode, (LPCWSTR)lpMsgBuf);
// 또는
_tprintf(_T("%d %s\n"), nErrorCode, (LPCTSTR)lpMsgBuf);
```

<br/>

## 사용 예시

```cpp
// 소켓 함수 호출 후 에러 발생 시
int error = WSAGetLastError();
displayerror(error);

// 일반 시스템 함수 호출 후 에러 발생 시
int error = GetLastError();
displayerror(error);
```

에러 코드를 사람이 읽을 수 있는 메시지로 바꿔주므로 소켓 프로그래밍 디버깅에 유용하다.
