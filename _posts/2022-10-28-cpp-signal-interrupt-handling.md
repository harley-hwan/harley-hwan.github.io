---
title: "(C++) signal() - 인터럽트 신호 처리"
description: "SIGPIPE로 프로세스가 조용히 죽는 걸 막으려고 signal()을 붙였다가 알게 된 것들 — 핸들러 안에서 쓸 수 있는 함수의 제약, SIGSEGV를 잡으면 무한루프가 되는 이유, signal() 대신 sigaction()을 쓰는 편이 나은 이유를 정리했다."
date: 2022-10-28 10:00:00 +0900
categories: [Dev, C++]
tags: [sigint, sigpipe, signal, signal-function, signal-h, linux, socket]
---
## 시작은 SIGPIPE였다

보드에서 도는 클라이언트가 서버로 데이터를 계속 밀어 넣는 구조였는데, 서버 쪽을 재시작하면 클라이언트가 아무 로그도 안 남기고 사라졌다. 예외도 아니고 assert도 아니고, 그냥 프로세스가 없어진다.

원인은 SIGPIPE였다. 상대가 닫아버린 소켓에 `write`/`send`를 하면 커널이 SIGPIPE를 보내고, 이 시그널의 기본 동작이 프로세스 종료다. `send()`의 반환값을 아무리 잘 검사해도 소용이 없다. 반환값을 보기 전에 프로세스가 죽어 있으니까.

여기에 하나 더, Ctrl+C로 끄면 열어둔 로그 파일이 flush되지 않은 채로 날아갔다. 두 가지를 같이 해결하려고 시그널 핸들러를 붙였다.

## 형식

```c++
#include <signal.h>
void ( *signal (int sig, void(*func)(int)) )(int);
```

읽기 까다로운 선언인데, 풀어 쓰면 "int를 받고 void를 반환하는 함수 포인터"를 받아서 같은 타입을 돌려준다는 뜻이다. 돌려주는 건 **이전에 등록되어 있던 핸들러**다. 임시로 핸들러를 바꿨다가 되돌릴 때 쓴다.

`func` 자리에 올 수 있는 건 세 가지다.

- `SIG_DFL`: 기본 동작. 시그널마다 다르고, 대개는 프로세스 종료다
- `SIG_IGN`: 무시
- 핸들러 함수의 주소

실패하면 `SIG_ERR`를 돌려주고 `errno`가 `EINVAL`로 설정된다. 잡을 수 없는 시그널을 등록하려 할 때가 대표적이다. SIGKILL(9)과 SIGSTOP은 잡지도 무시하지도 못한다. 이 둘로 죽는 프로세스는 정리 코드를 실행할 기회 자체가 없다.

## 시그널 종류

표준 C가 정의한 것은 여섯 개뿐이다.

| 시그널 | 발생 상황 | 기본 동작 |
| :--- | :--- | :--- |
| SIGABRT | `abort()` 호출, `terminate()` 도달 | 종료 + 코어 |
| SIGFPE | 0으로 나누기 등 산술 예외 | 종료 + 코어 |
| SIGILL | 잘못된 명령어 실행 | 종료 + 코어 |
| SIGINT | 터미널에서 Ctrl+C | 종료 |
| SIGSEGV | 잘못된 메모리 접근 | 종료 + 코어 |
| SIGTERM | 종료 요청 (`kill` 기본값) | 종료 |

POSIX 환경에서 실제로 자주 만나는 건 오히려 표준 밖의 것들이다.

- SIGPIPE: 닫힌 파이프/소켓에 쓰기. 기본 동작이 종료라서 위에서 겪은 일이 생긴다
- SIGHUP: 터미널이 끊어짐. 데몬에서는 설정 다시 읽기로 관례상 쓴다
- SIGCHLD: 자식 프로세스 종료. 좀비 회수용
- SIGUSR1, SIGUSR2: 용도가 정해지지 않은 두 개. 외부에서 `kill -USR1 <pid>`로 로그 레벨을 바꾸는 식으로 쓴다

## 처음 짰던 코드

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

의도한 대로 동작하긴 했다. Ctrl+C를 누르면 `quit`이 서고 루프가 빠져나온다. 서버가 죽으면 `replay`가 서서 재접속을 시도한다.

그런데 이 코드에는 문제가 세 개 있다. 하나씩 알게 되는 데 시간이 좀 걸렸다.

## 문제 1: 핸들러 안에서 아무거나 쓰면 안 된다

시그널 핸들러는 실행 중인 코드를 아무 지점에서나 끊고 들어온다. 하필 `malloc`이 내부 자료구조를 갱신하는 도중에 끊고 들어와서, 핸들러가 다시 `malloc`을 부르면 그대로 꼬인다. 그래서 핸들러 안에서 부를 수 있는 함수는 **async-signal-safe**로 규정된 목록에 있는 것뿐이다.

`std::cout`은 그 목록에 없다. `printf`도 없다. 내부에서 락을 잡고 버퍼를 만지기 때문이다. 위 코드가 그럭저럭 돌았던 건 운이 좋았던 것에 가깝다. 실제로 로그를 많이 찍는 상태에서 Ctrl+C를 연타하면 락에 걸려 멈추는 경우가 생긴다.

핸들러에서 꼭 뭔가를 찍어야 한다면 `write(2)`를 직접 쓴다.

```c++
#include <unistd.h>
#include <csignal>

volatile sig_atomic_t g_quit = 0;

void handler(int sig) {
    static const char msg[] = "\n[signal] caught\n";
    ssize_t n = write(STDERR_FILENO, msg, sizeof(msg) - 1);
    (void)n;                 // 반환값 무시 경고 방지
    g_quit = 1;
}
```

플래그 타입도 마찬가지다. `volatile sig_atomic_t`가 표준이 보장하는 유일한 타입이다. `std::atomic<bool>`도 **lock-free일 때만** 안전한데, 리눅스 x86/ARM에서는 `ATOMIC_BOOL_LOCK_FREE == 2`라 실제로는 문제가 없다. 확인하려면 이렇게 박아두면 된다.

```c++
static_assert(ATOMIC_BOOL_LOCK_FREE == 2, "atomic_bool must be lock-free");
```

## 문제 2: SIGSEGV를 잡고 리턴하면 무한루프가 된다

이게 제일 크게 데인 부분이다.

SIGSEGV는 잘못된 주소에 접근한 **그 명령어**를 실행하다 발생한다. 핸들러가 아무 일도 안 하고 리턴하면, 커널은 중단된 지점으로 돌아가서 같은 명령어를 다시 실행한다. 메모리 상태는 그대로니까 또 SIGSEGV가 뜨고, 다시 핸들러로 들어온다. 로그가 초당 수천 줄씩 쏟아지면서 디스크를 채운다.

SIGABRT도 비슷하다. `abort()`는 SIGABRT를 올린 뒤 핸들러가 돌아오면 시그널을 기본 동작으로 되돌리고 다시 올린다. 그래서 무한루프까지는 안 가지만, 핸들러에서 정리 작업을 하고 그대로 리턴하면 결국 종료된다는 점은 같다.

치명적 시그널을 잡을 거면 반드시 프로세스를 끝내야 한다.

```c++
void fatal_handler(int sig) {
    static const char msg[] = "\n[fatal] signal\n";
    ssize_t n = write(STDERR_FILENO, msg, sizeof(msg) - 1);
    (void)n;

    signal(sig, SIG_DFL);   // 기본 동작으로 되돌리고
    raise(sig);             // 다시 올려서 코어를 남긴다
}
```

`_exit(1)`로 바로 끝내도 되지만, 그러면 코어 덤프가 안 남는다. 원인을 봐야 하는 상황이라면 위처럼 기본 동작에 넘겨서 코어를 받는 편이 낫다. `exit()`가 아니라 `_exit()`인 이유도 같다. `exit()`는 atexit 핸들러와 스트림 flush를 도는데, 그것들이 async-signal-safe하지 않다.

## 문제 3: SIGPIPE는 잡는 것보다 무시하는 게 낫다

주석으로 남겨뒀던 `signal(SIGPIPE, SIG_IGN)` 쪽이 사실 정답이었다.

SIGPIPE를 무시해두면 `send()`가 `-1`을 반환하고 `errno`가 `EPIPE`로 설정된다. 그러면 평범한 에러 처리 흐름으로 들어온다. 핸들러에서 전역 플래그를 세우고 나중에 검사하는 것보다, 실패한 그 자리에서 바로 아는 편이 훨씬 다루기 쉽다. 어느 소켓에서 끊어졌는지도 바로 알 수 있다.

```c++
signal(SIGPIPE, SIG_IGN);

// ...
ssize_t n = send(fd, buf, len, 0);
if (n < 0 && errno == EPIPE) {
    // 이 소켓만 닫고 재접속
}
```

프로세스 전체에 영향을 주는 게 부담스러우면 호출 단위로 끌 수도 있다. 리눅스는 `send`에 `MSG_NOSIGNAL` 플래그가 있다.

```c++
ssize_t n = send(fd, buf, len, MSG_NOSIGNAL);
```

macOS/BSD에는 이 플래그가 없고 대신 소켓 옵션 `SO_NOSIGPIPE`를 쓴다. 라이브러리를 만든다면 프로세스 전역 설정을 건드리는 대신 이 방식을 쓰는 게 맞다.

## signal() 대신 sigaction()

`signal()`은 역사적으로 두 가지 의미가 있었다. System V 계열은 핸들러가 호출되면 처리 방식을 `SIG_DFL`로 되돌린다. 즉 한 번만 잡히고, 핸들러 안에서 다시 등록해야 한다. BSD 계열은 등록이 유지된다. glibc는 BSD 의미를 따르지만, 이식성을 생각하면 이 차이는 지뢰다.

`sigaction()`은 동작이 명확히 규정되어 있다.

```c++
#include <signal.h>
#include <cstring>

struct sigaction sa;
std::memset(&sa, 0, sizeof(sa));
sa.sa_handler = handler;
sigemptyset(&sa.sa_mask);
sa.sa_flags = SA_RESTART;      // 끊긴 시스템 콜을 자동 재시작
sigaction(SIGINT, &sa, nullptr);
```

`sa_mask`는 핸들러가 도는 동안 추가로 막을 시그널 집합이다. 비워두면 처리 중인 시그널만 자동으로 막힌다. `SA_RESTART`가 다음 항목과 이어진다.

## EINTR: 시그널이 들어오면 블로킹 콜이 깨진다

`read`, `recv`, `accept`, `sleep` 같은 블로킹 호출은 시그널이 들어오면 도중에 `-1`을 반환하고 `errno`를 `EINTR`로 설정한다. 이걸 처리 안 하면, Ctrl+C를 눌렀을 때 종료가 아니라 엉뚱한 "read fail" 로그가 찍힌다.

```c++
ssize_t n;
do {
    n = recv(fd, buf, len, 0);
} while (n < 0 && errno == EINTR);
```

`SA_RESTART`를 주면 커널이 알아서 재시작해주는 호출이 많지만, 전부는 아니다. 타임아웃이 걸린 호출(`poll`, `select`, `SO_RCVTIMEO`가 설정된 `recv`)은 `SA_RESTART`가 있어도 `EINTR`로 돌아온다. 재시작하면 타임아웃이 처음부터 다시 계산되기 때문이다. 결국 `EINTR` 루프는 어차피 필요하다.

## 멀티스레드에서는 이야기가 달라진다

시그널은 프로세스 단위로 전달되고, 핸들러가 **어느 스레드에서 도는지는 정해져 있지 않다**. 시그널을 막지 않은 아무 스레드에서나 실행될 수 있다. 그래서 "수신 스레드가 SIGINT를 처리한다" 같은 가정은 성립하지 않는다.

깔끔한 방법은 시그널을 전용 스레드 하나에서만 받게 만드는 것이다. 메인에서 모든 스레드가 상속받도록 먼저 막아두고, 전용 스레드에서 `sigwait`으로 기다린다.

```c++
sigset_t set;
sigemptyset(&set);
sigaddset(&set, SIGINT);
sigaddset(&set, SIGTERM);
pthread_sigmask(SIG_BLOCK, &set, nullptr);   // 이후 생성되는 스레드가 상속

std::thread([set]() mutable {
    int sig = 0;
    sigwait(&set, &sig);      // 여기서 대기 — 핸들러 제약이 없다
    request_shutdown();       // 평범한 함수를 마음껏 부를 수 있다
}).detach();
```

`sigwait` 안쪽은 시그널 핸들러 컨텍스트가 아니라 그냥 스레드다. async-signal-safe 제약이 없어서 로그도 찍고 락도 잡을 수 있다. 리눅스만 대상이라면 `signalfd`로 시그널을 파일 디스크립터로 받아 `epoll`에 그대로 물리는 방법도 있다. 이벤트 루프가 이미 있으면 이쪽이 제일 자연스럽다.

## 지금 다시 짠다면

```c++
volatile sig_atomic_t g_quit = 0;

void on_term(int) { g_quit = 1; }

int main() {
    signal(SIGPIPE, SIG_IGN);          // 무시하고 EPIPE 로 받는다

    struct sigaction sa{};
    sa.sa_handler = on_term;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    sigaction(SIGINT,  &sa, nullptr);
    sigaction(SIGTERM, &sa, nullptr);  // kill 기본값도 같이 받는다

    while (!g_quit) {
        // ... EINTR 재시도를 포함한 작업
    }

    cleanup();                          // 여기서 정리한다
    return 0;
}
```

핵심은 핸들러에서 플래그만 세우고, 실제 정리는 루프를 빠져나온 뒤 평범한 코드로 한다는 것이다. SIGSEGV나 SIGABRT는 애초에 잡지 않고 코어 덤프를 받아서 분석하는 쪽으로 방향을 잡았다. 잡아서 살려보려는 시도는 대개 상태가 이미 망가진 뒤라서 의미가 없다.

## 관련 함수

- `abort()`: SIGABRT를 올려 프로그램 중단
- `raise(sig)`: 자기 자신에게 시그널 전송
- `kill(pid, sig)`: 다른 프로세스에 시그널 전송
- `atexit()`: 정상 종료 시 실행할 함수 등록. 시그널로 죽을 때는 호출되지 않는다
- `alarm()`, `setitimer()`: 일정 시간 뒤 SIGALRM 발생

## 참고

- [IBM Docs: signal() — 인터럽트 신호 처리](https://www.ibm.com/docs/ko/i/7.3?topic=functions-signal-handle-interrupt-signals)
- `man 7 signal-safety` — async-signal-safe 함수 전체 목록
- `man 2 sigaction`, `man 2 signalfd`
