---
title: "(C++) signal() - 인터럽트 신호 처리"
description: C++에서 signal() 함수로 SIGINT, SIGPIPE 등 인터럽트 신호를 처리하는 방법과 신호 종류, 예제 코드를 정리한다.
date: 2022-10-28 10:00:00 +0900
categories: [Dev, C++]
tags: [sigint, sigpipe, signal, signal-function, signal-h]
---
- 참조: https://www.ibm.com/docs/ko/i/7.3?topic=functions-signal-handle-interrupt-signals

## 내용

signal() 함수를 이용하면 운영체제가 보내거나 raise() 함수로 발생시킨 인터럽트 신호를 프로그램이 어떻게 처리할지 지정할 수 있다.

### 형식

```c++
#include <signal.h>
void ( *signal (int sig, void(*func)(int)) )(int);
```
sig 인수에는 처리할 신호를 지정한다. 표준 C에는 SIGABRT, SIGFPE, SIGILL, SIGINT, SIGSEGV, SIGTERM이 정의되어 있고, POSIX 환경에서는 SIGPIPE, SIGUSR1, SIGUSR2 등이 추가로 제공된다.

func 인수에는 SIG_DFL, SIG_IGN 또는 신호 핸들러 함수의 주소를 지정한다.

<br/>

### sig 인수

- SIGABRT: 비정상 종료 (abort() 호출 등)
- SIGFPE: 0으로 나누기, 오버플로 등 산술 연산 예외
- SIGILL: 잘못된 명령어 실행
- SIGINT: 인터럽트 (터미널에서 Ctrl+C 입력 등)
- SIGSEGV: 잘못된 메모리 접근
- SIGTERM: 프로그램 종료 요청
- SIGPIPE: 닫힌 파이프나 소켓에 쓰기 시도 (POSIX)
- SIGUSR1, SIGUSR2: 사용자 정의 용도 (POSIX)

<br/>

### func 인수

- SIG_DFL: 신호에 대한 기본 처리를 수행한다.
- SIG_IGN: 신호를 무시한다.
- 핸들러 함수 주소: 신호가 발생하면 해당 함수가 호출된다.

<br/>

### 리턴 값

성공하면 signal()은 이전에 등록되어 있던 핸들러를 리턴한다.

오류가 발생하면 SIG_ERR를 리턴하며, 신호 번호가 유효하지 않은 경우 errno가 EINVAL로 설정될 수 있다.

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
