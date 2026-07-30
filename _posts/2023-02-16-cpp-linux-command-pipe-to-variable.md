---
title: "(C++) Linux Command pipe로 변수값으로 끌고오기"
description: "리눅스 명령 출력을 프로그램 변수로 받는 세 가지 방법을 비교했다. popen이 간단한 이유와 그 대가, fork/exec/pipe를 직접 짤 때 빠뜨리기 쉬운 exit·버퍼 경계·strtok 문제까지 정리했다."
date: 2023-02-16 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, linux, command, pipe, arp, popen, fork, execvp]
---
## 왜 필요했나

보드에서 도는 프로그램이 같은 망에 있는 다른 장비의 IP를 알아야 했다. 터미널에서는 `arp -a` 한 줄이면 나오는데, 이걸 프로그램 안으로 가져와야 한다.

`system("arp -a")`는 안 된다. 결과가 표준 출력으로 그냥 흘러나가고 프로그램은 종료 코드만 받는다. 출력을 잡으려면 파이프가 필요하다.

세 가지를 순서대로 해봤다. 결과는 다 같지만 얻는 것과 잃는 것이 다르다.

## 방법 1: popen

가장 짧다.

```c++
#include <iostream>
#include <cstdio>
#include <string>

int main() {
    FILE* pipe = popen("arp -a", "r");
    if (!pipe) return 1;

    char buffer[128];
    std::string result = "";
    while (!feof(pipe)) {
        if (fgets(buffer, 128, pipe) != nullptr)
            result += buffer;
    }

    pclose(pipe);

    std::cout << result << std::endl;
    return 0;
}
```

```text
? (192.168.8.152) at 88:36:6c:fc:2c:4f [ether] on wlan0
? (192.168.8.114) at 5a:ff:ec:d1:cb:a4 [ether] on wlan0
```

`popen`이 내부에서 `fork` + `exec` + `pipe` + `dup2`를 다 해준다. 반환된 `FILE*`를 파일처럼 읽으면 된다.

### while (!feof(...))는 잘못된 관용구다

이 루프가 흔히 쓰이는데 정확하지 않다. `feof`는 "파일 끝에 도달했다"가 아니라 **"읽기를 시도했다가 파일 끝에 부딪혔다"** 일 때 참이 된다. 마지막 줄을 읽은 직후에는 아직 거짓이라, 루프를 한 번 더 돌아 `fgets`가 실패한 뒤에야 빠져나온다.

위 코드는 `if (fgets(...) != nullptr)`로 감싸놨기 때문에 증상이 안 보인다. 그 검사가 없었으면 마지막 줄이 두 번 들어갔을 것이다. 애초에 `fgets`의 반환값으로 도는 게 맞다.

```c++
while (fgets(buffer, sizeof(buffer), pipe) != nullptr)
    result += buffer;
```

이러면 `feof`를 부를 일이 없다. 읽기 실패와 파일 끝을 구분해야 하면 루프를 나온 뒤 `ferror`를 보면 된다.

### pclose의 반환값이 명령의 결과다

원 코드는 `pclose`의 반환값을 버린다. 이 값이 자식 프로세스의 종료 상태다. 명령이 없거나 실패해도 알 방법이 없다.

```c++
int status = pclose(pipe);
if (status == -1) {
    // pclose 자체가 실패
} else if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
    // 명령이 0 이 아닌 코드로 끝났다
}
```

`arp` 명령이 없는 최소 이미지에서 돌린 적이 있는데, 셸이 "command not found"를 표준 에러로 뱉고 `result`는 빈 문자열이 됐다. 프로그램은 "장비가 하나도 없다"로 판단하고 조용히 지나갔다. `pclose`를 봤으면 바로 알았을 일이다.

표준 에러도 같이 받고 싶으면 명령 뒤에 `2>&1`을 붙인다. 다만 에러 메시지가 결과에 섞이니 파싱하는 쪽에서 걸러야 한다.

### popen은 셸을 거친다

`popen`은 명령 문자열을 `/bin/sh -c`에 넘긴다. 편한 점이자 위험한 점이다. 파이프나 리다이렉션을 그대로 쓸 수 있는 대신, 문자열에 외부 입력이 섞이면 그대로 명령 주입이 된다.

```c++
// 이런 코드는 쓰면 안 된다
std::string cmd = "ping -c 1 " + user_input;   // user_input 이 "; rm -rf /" 라면
popen(cmd.c_str(), "r");
```

고정된 명령만 돌리면 문제없다. 인자가 바깥에서 온다면 셸을 안 거치는 방법으로 가야 한다.

## 방법 2: fork + exec + pipe 직접

셸을 안 거치려고 직접 짜본 것이다.

```c++
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <string>
#include <vector>

std::vector<std::string> getE6ServerIPpipe()
{
    std::vector<std::string> ip_list;
    int my_pipe[2];
    char* arguments[] = {"arp",NULL}; 

    if(pipe(my_pipe) == -1)
    {
        fprintf(stderr, "Error creating pipe\n");
    }

    pid_t child_id;
    child_id = fork();
    if(child_id == -1)
    {
        fprintf(stderr, "Fork error\n");
    }
    if(child_id == 0) // child process
    {
        close(my_pipe[0]); // child doesn't read
        dup2(my_pipe[1], 1); // redirect stdout

        execvp(arguments[0], arguments);

        fprintf(stderr, "Exec failed\n");
    }
    else
    {
        close(my_pipe[1]); // parent doesn't write

        char reading_buf[1024];
        char *ptr=reading_buf;
        while(read(my_pipe[0], ptr, 1) > 0)
        {
            ptr++;
        }

        (*ptr)='\0';
        char *line=strtok(reading_buf,"\n"); // skip
        line=strtok(NULL,"\n");

        while(line)
        {
            int i;
            for(i=0;!isspace(line[i]);i++);

            line[i]='\0';
            ip_list.push_back(line);

            line=strtok(NULL,"\n");
        }
        close(my_pipe[0]);
        wait(NULL);
    }
	return ip_list;
}
```

```text
192.168.8.152
192.168.8.114
```

`pipe()`로 파이프를 만들고, `fork()`로 갈라진 뒤, 자식은 읽기 끝을 닫고 `dup2`로 표준 출력을 파이프 쓰기 끝에 연결한 다음 `execvp`로 `arp`가 된다. 부모는 쓰기 끝을 닫고 읽기 끝에서 읽는다.

파이프 양쪽 끝을 각자 안 쓰는 쪽부터 닫는 게 핵심이다. 부모가 쓰기 끝을 안 닫으면 자식이 끝나도 파이프에 쓰는 쪽이 남아 있는 것으로 취급돼서 `read`가 영원히 EOF를 못 받고 멈춘다.

동작은 했지만 문제가 여러 개 있었다.

### 컴파일 경고부터

```c++
warning: ISO C++ forbids converting a string constant to 'char*' [-Wwrite-strings]
     char* arguments[] = {"arp",NULL}; 
```

문자열 리터럴은 읽기 전용이라 `char*`로 받으면 수정 가능한 것처럼 보여서 나오는 경고다.

```c++
const char* arguments[] = {"arp", NULL};
```

이렇게 고치면 이번엔 `execvp`가 `char* const[]`를 받아서 타입이 안 맞는다. `execvp`는 인자를 수정하지 않지만 시그니처가 오래된 관례를 따르고 있어서, 호출할 때 캐스팅으로 넘기는 게 관행이다.

```c++
execvp(arguments[0], const_cast<char* const*>(arguments));
```

### execvp 실패 후 exit이 없다

이게 제일 위험하다. `execvp`가 성공하면 프로세스 이미지가 통째로 바뀌니 그 아래 코드는 실행되지 않는다. 그런데 **실패하면 그냥 반환**된다. 이 코드에서는 그 뒤에 `fprintf`만 있고 `exit`이 없어서, 자식이 부모의 코드를 계속 실행한다.

즉 `getE6ServerIPpipe`에서 리턴하고, 호출한 쪽으로 돌아가고, `main`을 마저 돈다. 프로그램이 두 개가 돌게 되는 셈이다. 자식이 루프 안에서 다시 `fork`하는 구조였으면 순식간에 프로세스가 폭증한다.

```c++
if (child_id == 0) {
    close(my_pipe[0]);
    dup2(my_pipe[1], 1);
    close(my_pipe[1]);              // dup2 후 원본도 닫는다
    execvp(...);
    _exit(127);                     // 여기 오면 실패한 것
}
```

`exit`이 아니라 `_exit`을 쓰는 이유는, `fork` 직후의 자식이 `exit`을 부르면 부모와 공유하던 stdio 버퍼가 두 번 flush될 수 있어서다. 127은 셸이 "명령을 못 찾음"에 쓰는 관례적인 코드다.

### 1바이트씩 읽는다

```c++
while(read(my_pipe[0], ptr, 1) > 0)
    ptr++;
```

바이트마다 시스템 콜을 한 번씩 한다. 출력이 몇 KB만 돼도 호출이 수천 번이다. 버퍼 단위로 읽어야 한다.

```c++
std::string out;
char buf[4096];
ssize_t n;
while ((n = read(my_pipe[0], buf, sizeof(buf))) > 0)
    out.append(buf, n);
if (n < 0 && errno == EINTR) { /* 재시도 */ }
```

`read`는 시그널이 들어오면 `EINTR`로 깨질 수 있으니 재시도 처리도 필요하다.

### 버퍼 경계 검사가 없다

`reading_buf`는 1024바이트인데 몇 바이트를 읽었는지 세지 않는다. `arp` 출력이 1024를 넘으면 스택을 그대로 넘어간다. 장비가 몇 대 없을 때는 출력이 짧아서 안 걸리다가, 같은 망에 장비가 늘어나면 그때 터진다. 재현이 어려운 종류의 사고다.

`std::string`에 `append`로 붙이면 이 문제가 없어진다.

### strtok과 무한 루프

```c++
for(i=0;!isspace(line[i]);i++);
```

공백을 만날 때까지 인덱스를 올리는데, 공백이 없으면 널 문자를 지나 계속 간다. `arp` 출력 형식이 예상과 다르면 바로 범위 밖 접근이다. 종료 조건에 `line[i] != '\0'`를 같이 넣어야 한다.

`isspace`에 `char`를 그대로 넘기는 것도 정확하지 않다. `char`가 부호 있는 타입인 플랫폼에서 0x80 이상의 바이트는 음수가 되는데, `isspace`는 `unsigned char` 범위나 `EOF`만 받는다. `isspace(static_cast<unsigned char>(line[i]))`로 넘겨야 한다.

`strtok`은 내부에 정적 상태를 들고 있어서 스레드 안전하지 않다. 두 스레드에서 동시에 부르면 서로의 파싱 위치를 망친다. 리눅스에는 `strtok_r`이 있다.

## 방법 3: popen + 문자열 파싱

결국 다시 `popen`으로 돌아와서, 파싱만 정리했다.

```c++
std::vector<std::string> getIPList() {
    FILE* pipe = popen("arp -a", "r");
    if (!pipe) {
        std::cerr << "popen() failed!" << std::endl;
        exit(1);
    }

    std::vector<std::string> ip_list;
    char buffer[128];
    std::string arpOutput = "";
    while (!feof(pipe)) {
        if (fgets(buffer, 128, pipe) != nullptr) {
            arpOutput += buffer;
        }
    }
    pclose(pipe);

    size_t pos_left, pos_right;
    while ((pos_left = arpOutput.find("(")) != std::string::npos) {
        pos_right = arpOutput.find(")", pos_left);
        if (pos_right != std::string::npos) {
            std::string token = arpOutput.substr(pos_left + 1, pos_right - pos_left - 1);
            ip_list.push_back(token);
        }
        arpOutput.erase(0, pos_right + 1);
    }
    return ip_list;
}
```

`arp -a`의 출력에서 IP가 괄호 안에 있다는 점을 이용해 괄호 쌍을 찾아 잘라낸다. 코드 양으로 보면 fork 버전의 3분의 1이고 위에서 나열한 함정이 대부분 없다.

여기에도 놓친 게 있다. `pos_right`를 못 찾으면(`npos`) `arpOutput.erase(0, npos + 1)`이 되는데, `npos + 1`은 0이라 아무것도 안 지운다. 그러면 같은 위치에서 무한 루프다. 여는 괄호는 있는데 닫는 괄호가 없는 출력이 나오면 프로그램이 멈춘다.

## 세 방법 비교

| | popen | fork/exec 직접 | popen + 파싱 |
| :--- | :--- | :--- | :--- |
| 코드 양 | 짧다 | 길다 | 짧다 |
| 셸 경유 | 예 (주입 위험) | 아니오 | 예 |
| 종료 코드 | `pclose` | `waitpid` | `pclose` |
| stdin/stdout 동시 | 불가 (한 방향) | 가능 | 불가 |
| 세부 제어 | 없음 | 전부 | 없음 |

인자가 전부 프로그램 안에서 정해지고 출력만 읽으면 되는 상황이면 `popen`이 맞다. 직접 짜서 얻는 게 별로 없다. 반대로 명령에 외부 입력이 들어가거나, 표준 입력으로도 데이터를 밀어 넣어야 하거나, 타임아웃을 걸어야 하면 `fork`/`exec`를 직접 짜야 한다.

## 명령 출력을 파싱하는 것 자체가 취약하다

이건 나중에 알게 된 더 큰 문제다.

`arp -a`의 출력 형식은 배포판과 net-tools 버전에 따라 다르다. 어떤 환경에서는 호스트명이 `?` 대신 실제 이름으로 나오고, `arp -n`은 아예 괄호가 없는 표 형식이다. 로케일에 따라 헤더가 번역되기도 한다.

같은 정보를 커널이 파일로 제공한다.

```text
$ cat /proc/net/arp
IP address       HW type     Flags       HW address            Mask     Device
192.168.8.152    0x1         0x2         88:36:6c:fc:2c:4f     *        wlan0
```

열 위치가 고정이고, 프로세스를 하나도 안 띄우고, 파싱도 훨씬 단순하다. 형식이 바뀔 걱정도 없다. 결국 이쪽으로 옮겼고, 그 과정은 [현재 연결된 IP 목록 뽑아보기](/posts/cpp-get-connected-ip-list-with-arp/)에 정리했다.

## 정리하면

- `while (!feof(fp))` 대신 `while (fgets(...))`를 쓴다
- `pclose`의 반환값이 명령의 종료 상태다. 안 보면 실패를 놓친다
- `popen`은 셸을 거친다. 외부 입력이 명령에 섞이면 주입이 된다
- 직접 짤 때 `execvp` 뒤에 `_exit`이 없으면 자식이 부모 코드를 계속 실행한다
- 1바이트 `read`, 경계 검사 없는 고정 버퍼, `strtok`은 다 나중에 문제가 된다
- 명령 출력 형식에 의존하기 전에 `/proc` 아래에 같은 정보가 있는지 먼저 본다
