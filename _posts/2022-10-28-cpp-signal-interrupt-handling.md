---
title: signal() - 인터럽트 신호 처리 (c++)
description: "SIGINT, SIGPIPE, SIGALRM, signal, signal()"
date: 2022-10-28 10:00:00 +0900
categories: [Dev, C++]
tags: [SIGINT, SIGPIPE, SIGALRM, signal, signal(), signal.h]
---

# signal() - 인터럽트 신호 처리
- 최초 작성일: 2022년 11월 9일 (수)
- 참조: https://www.ibm.com/docs/ko/i/7.3?topic=functions-signal-handle-interrupt-signals

## 목차



<br/>

## 내용

signal() 함수를 이용해 프로그램이 운영체제나 raise() 함수에서 인터럽트 신호를 처리할 수 있는 여러 방법 중 하나를 선택할 수 있다.

SISIFCOPT(\*ASYNCSIGNAL) 옵션으로 컴파일하는 경우 이 함수는 비동기 신호를 사용한다. 이때 이 함수의 비동기 버전은 SA_NODEFER 및 SA_RESETHAND 옵션으로 sigaction() 같이 작동한다. 비동기 신호 핸들러는 abort() 또는 exit()를 호출하지 않을 수 있다고 한다. 

### 형식

```c++
#include <signal.h>
void ( *signal (int sig, void(*func)(int)) )(int);
```
**sig 인수**는 SIGABRT, SIGALL, SIGILL, SIGINT, SIGFPE, SIGIO, SIGOTHER, SIGSEGV, SIGTERM, SIGUSR1 또는 SIGUSR2 가 있다.

**func 인수**는 SIG_DFL 또는 SIG_IGN 중 하나이며, <signal.h> 포함 파일이나 함수 주소에 정의된다.

<br/>

### sig 인수

**SIGABRT**
- 비정상 종료

**SIGALL**
- 현재 핸들링 조치가 SIG_DFL인 신호에 대한 Catch-all이다.
- SYSICOPT(*ASYNCSIGNAL)이 지정되면 SIGALL은 catch-all 신호가 아니다.
- SIGALL을 위한 신호 핸들러는 사용자 격상된 SIGALL 신호에 대해서만 호출된다.

**SIGILL**
- 유효하지 않은 함수 이미지의 발견

**SIGFPE**
- 오버플로, 0으로 나눔 및 유효하지 않은 조작과 같이 마스크되지 않은 산술 예외

**SIGINT**
- 대화식 어텐션

**SIGIO**
- 레코드 파일 I/O 오류

**SIGOTHER**
- ILE C 신호

**SIGSEGV**
- 유효하지 않은 메모리에 액세스

**SIGTERM**
- 프로그램에 전송된 요청 종료

**SIGUSR1**
- 사용자 애플리케이션용 (ANSI로 연장)

**SIGUSR2**
- 사용자 애플리케이션용 (ANSI로 연장)

<br/>

### func 인수

**SIG_DFL**
- 신호에 대한 기본 처리기가 발생한다.

**SIG_IGN**
- 신호가 무시된다.

<br/>

### 리턴 값

SIG_ERR의 리턴값은 signal()에 대한 호출에서의 오류를 표시한다.

성공의 경우, signal()에 대한 호출은 func의 최근 값을 리턴한다.

errno의 값은 EINVAL으로 설정될 수 있다. (신호가 유효하지 X)


## 예제

```c++
std::atomic_bool quit(false);
std::atomic_bool replay(false);

void handler(int sig) {
    if (sig == SIGINT) {
        quit = true;
        std::cout << "\n SIGINT" << "\n";
    } else if (sig == SIGPIPE) {
        replay = true;
        std::cout << "\n SIGPIPE" << "\n";
    } else if (sig == SIGABRT) {
        std::cout << "\n SIGABRT" << "\n";
    } else if (sig == SIGSEGV) {
        std::cout << "\n SIGSEGV" << "\n";
    }
}

int main() {
    signal(SIGINT, handler);
    signal(SIGPIPE, handler);
    // signal(SIGPIPE, SIG_IGN);
    signal(SIGABRT, handler);
    signal(SIGSEGV, handler);
    while(!quit)
    {
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    return 0;
}
```
<br/>

### 관련 정보

- abort() : 프로그램 중단
- atexit() : 프로그램 종료 함수 레코드
- exit() : 프로그램 종료
- raise() : 송신 신호
- <signal.h>
