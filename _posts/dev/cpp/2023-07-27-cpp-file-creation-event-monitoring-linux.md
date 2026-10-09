---
title: "(C++) 파일 생성 이벤트 모니터링 (Linux)"
description: "특정 디렉토리에 파일이 올라오면 자동으로 처리하도록 inotify를 붙였다. IN_CREATE로는 다 써지지 않은 파일을 잡는다는 것, scp로 올리면 이벤트 종류가 달라진다는 것, 큐가 넘치면 조용히 놓친다는 것을 겪고 나서 정리했다."
date: 2023-07-27 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, linux, inotify, inotify-init, in-create, in-close-write, in-isdir, inotify-rm-watch, epoll]
---
## 폴링을 대체하려고 시작했다

원격에서 파일을 특정 디렉토리에 올려두면 보드가 그걸 집어서 처리하는 구조가 필요했다. 처음엔 1초마다 디렉토리를 훑어서 새 파일이 있는지 보는 폴링이었다.

폴링은 두 가지가 걸렸다. 반응이 최대 1초 늦고, 아무 일이 없어도 계속 디렉토리를 읽는다. SD 카드로 도는 보드에서 계속 읽는 게 마음에 안 들었다.

리눅스에는 커널이 알려주는 방법이 있다.

## 처음 짠 코드

```c++
#include <iostream>
#include <sys/inotify.h>
#include <sys/stat.h>
#include <cstring>
#include <unistd.h>

// Size of read buffer
#define BUF_LEN 1024
#define EVENT_SIZE (sizeof(struct inotify_event))

int main(int argc, char* argv[]) 
{
    // Create an INOTIFY instance
    int fd = inotify_init();

    // Check for error
    if (fd < 0) {
        perror("inotify_init");
        return 1;
    }

    // Add /path directory into watch list.
    int wd = inotify_add_watch(fd, "/path", IN_CREATE);

    if (wd < 0) {
        perror("inotify_add_watch");
        return 1;
    }

    char buffer[BUF_LEN];

    while (1) 
    {
        int length = read(fd, buffer, BUF_LEN);
        if (length < 0) {
            perror("read");
            continue;  // If read failed, try to continue to the next read
        }

        int i = 0;
        while (i < length) {
            struct inotify_event* event = (struct inotify_event*)&buffer[i];
            if (event->len) {
                if (event->mask & IN_CREATE) {
                    if (!(event->mask & IN_ISDIR)) {
                        std::string file_name = event->name;
                        if (file_name.substr(file_name.find_last_of(".") + 1) == "rbf")
                        {
                            // 원하는 기능 삽입
                        }
                    }
                }
            }
            i += EVENT_SIZE + event->len;
        }
    }

    // Removing the "/path" directory from the watch list.
    inotify_rm_watch(fd, wd);

    // Close the INOTIFY instance
    close(fd);

    return 0;
}
```

`inotify_init`으로 인스턴스를 만들고, `inotify_add_watch`로 감시할 디렉토리와 이벤트 종류를 등록한다. 그다음 `read`로 이벤트를 읽으면 된다.

`read` 한 번에 이벤트가 여러 개 딸려 올 수 있어서, 버퍼 안을 돌면서 하나씩 처리한다. `event->len`은 이름의 길이인데 패딩이 포함된 값이라, 다음 이벤트의 위치를 구할 때 `EVENT_SIZE + event->len`을 더하면 된다. 이름이 없는 이벤트도 있어서 `event->len`이 0인지 먼저 본다.

동작은 했다. 그런데 실제로 파일을 올려보니 문제가 줄줄이 나왔다.

## IN_CREATE는 "다 써졌다"가 아니다

이게 제일 큰 문제였다.

`IN_CREATE`는 파일이 **만들어진 순간**에 온다. 아직 내용은 0바이트다. 그 시점에 파일을 읽으면 빈 파일이거나 앞부분만 있다. 몇 MB짜리 파일을 네트워크로 올리는 중이면 몇 초 동안 계속 써지는 중인데, 프로그램은 이미 처리를 시작한다.

처음엔 이벤트를 받고 1초 기다렸다가 읽는 식으로 때웠다. 파일이 커지거나 망이 느리면 또 깨진다. 애초에 얼마를 기다려야 하는지 알 방법이 없다.

정답은 다른 이벤트를 쓰는 것이다.

```c++
int wd = inotify_add_watch(fd, "/path", IN_CLOSE_WRITE | IN_MOVED_TO);
```

`IN_CLOSE_WRITE`는 **쓰기 모드로 열었던 파일이 닫힐 때** 온다. 쓰는 쪽이 다 쓰고 닫았다는 뜻이라 이 시점에는 내용이 완성되어 있다.

## scp로 올리면 이벤트가 아예 안 온다

`IN_CLOSE_WRITE`로 바꾸고 나서도 안 잡히는 경우가 있었다. `scp`나 `rsync`로 올릴 때다.

이 도구들은 임시 이름으로 파일을 만들어 다 쓰고 나서 최종 이름으로 `rename`한다. 최종 이름으로는 쓰기가 일어난 적이 없으니 `IN_CLOSE_WRITE`가 안 온다. 대신 `IN_MOVED_TO`가 온다.

에디터도 비슷하다. vim 같은 것들은 원본을 직접 고치지 않고 새로 쓴 뒤 바꿔치기한다.

그래서 두 이벤트를 같이 등록한다. 반대로 `IN_CREATE`는 뺐다. `IN_CREATE`까지 켜두면 하나의 파일에 대해 이벤트가 두 번 오게 되어 처리가 두 번 돈다.

| 마스크 | 언제 오는가 | 파일 내용 |
| :--- | :--- | :--- |
| `IN_CREATE` | 파일이 만들어진 순간 | 비어 있다 |
| `IN_CLOSE_WRITE` | 쓰기용으로 연 파일이 닫힐 때 | 완성 |
| `IN_MOVED_TO` | 다른 이름에서 옮겨 들어올 때 | 완성 |
| `IN_DELETE` | 삭제됨 | |
| `IN_MODIFY` | 내용이 바뀜 (쓸 때마다 여러 번) | 진행 중 |

`IN_CLOSE_WRITE`가 왔다고 파일이 반드시 온전한 것도 아니다. 쓰던 프로그램이 중간에 죽으면 파일 디스크립터가 닫히면서 이벤트가 온다. 결국 처리하는 쪽에서 크기나 체크섬을 한 번 확인하는 단계를 넣었다.

## 확장자 검사가 틀렸다

```c++
file_name.substr(file_name.find_last_of(".") + 1) == "rbf"
```

점이 없는 파일명이면 `find_last_of`가 `npos`를 돌려주고, `npos + 1`은 0이 된다. 그러면 `substr(0)`이 되어 **파일명 전체**가 나온다. `rbf`라는 이름의 확장자 없는 파일이 걸린다.

흔한 상황은 아니지만, 임시 파일 이름이 점 없이 만들어지는 경우가 있어서 실제로 한 번 걸렸다.

```c++
static bool has_extension(const std::string& name, const std::string& ext)
{
    const size_t dot = name.find_last_of('.');
    if (dot == std::string::npos) return false;
    return name.compare(dot + 1, std::string::npos, ext) == 0;
}
```

숨김 파일도 걸러야 한다. `.`으로 시작하는 이름은 대개 도구가 만든 임시 파일이다.

## 버퍼 크기와 정렬

`BUF_LEN`을 1024로 잡았는데 근거가 없었다. 이벤트 하나도 못 담는 크기면 `read`가 `EINVAL`로 실패한다. 이름이 최대 `NAME_MAX`(255)까지 오니 최소한 그건 담아야 한다.

```c++
constexpr size_t kEventSize = sizeof(struct inotify_event) + NAME_MAX + 1;
constexpr size_t kBufLen    = 32 * kEventSize;      // 이벤트 여러 개를 한 번에
alignas(struct inotify_event) char buffer[kBufLen];
```

`alignas`를 붙인 이유가 있다. 버퍼를 `char[]`로 잡으면 정렬이 보장되지 않는데, 그 위에 `inotify_event*`를 얹어서 멤버를 읽는 건 정렬을 요구하는 접근이다. x86에서는 정렬이 안 맞아도 동작하지만 ARM에서는 안 될 수 있다. 보드가 ARM이라 그냥 넘길 문제가 아니었다.

버퍼를 크게 잡을수록 한 번의 `read`로 이벤트를 많이 가져와서 다음 항목이 밀릴 확률이 줄어든다.

## 큐가 넘치면 조용히 놓친다

이벤트는 커널의 큐에 쌓이고, 큐가 가득 차면 **오래된 것부터 버려진다**. 파일을 한꺼번에 여러 개 올리거나, 처리 로직이 오래 걸려서 다음 `read`가 늦으면 이 상황이 된다.

넘쳤다는 사실은 `IN_Q_OVERFLOW` 이벤트로 알려준다. 이 이벤트는 `wd`가 `-1`이고 이름이 없다.

```c++
if (event->mask & IN_Q_OVERFLOW) {
    // 놓친 이벤트가 있다 — 디렉토리를 통째로 다시 훑는다
    rescan_directory(path);
    continue;
}
```

이걸 처리 안 하면 파일이 조용히 무시된다. 로그에도 안 남으니 나중에 "왜 이 파일만 처리가 안 됐지"가 된다. 실제로 여러 개를 한 번에 올렸을 때 몇 개가 빠지는 걸 보고 알았다.

큐 크기는 `/proc/sys/fs/inotify/max_queued_events`에서 볼 수 있고 기본값이 16384다. 늘릴 수는 있지만, 근본적으로는 이벤트 처리를 빨리 끝내고 실제 작업은 다른 곳에 넘기는 구조가 맞다. 이벤트 루프에서는 파일명만 큐에 넣고, 처리는 작업 스레드가 한다.

## 종료할 방법이 없다

원 코드의 `inotify_rm_watch`와 `close`는 `while(1)` 아래에 있어서 절대 실행되지 않는다. `read`가 이벤트를 기다리며 무한정 막혀 있으니 루프를 빠져나갈 방법도 없다.

`inotify_init1(IN_NONBLOCK)`으로 논블로킹으로 열고 `epoll`이나 `poll`에 물리면 해결된다. 종료용 `eventfd`를 같이 감시하면 밖에서 깨울 수 있다.

```c++
int fd  = inotify_init1(IN_NONBLOCK | IN_CLOEXEC);
int evt = eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);   // 종료 신호용

struct pollfd fds[2] = {
    { fd,  POLLIN, 0 },
    { evt, POLLIN, 0 },
};

while (running) {
    int n = poll(fds, 2, -1);
    if (n < 0) {
        if (errno == EINTR) continue;
        break;
    }
    if (fds[1].revents & POLLIN) break;        // 종료 요청
    if (fds[0].revents & POLLIN) { /* read + 처리 */ }
}
```

`IN_CLOEXEC`을 준 것도 이유가 있다. 이 프로그램이 나중에 다른 프로세스를 띄우게 됐는데, 플래그가 없으면 자식이 inotify 디스크립터를 물려받는다. 자식이 오래 사는 프로세스면 그만큼 디스크립터가 잡혀 있게 된다. [앞에서 fd 문제로 데인](/posts/cpp-get-connected-ip-list-with-arp/) 뒤로는 fd를 만드는 자리마다 이 플래그를 챙기게 됐다.

## read 실패 처리

```c++
if (length < 0) {
    perror("read");
    continue;
}
```

모든 실패에서 `continue`하면, 회복 불가능한 에러가 났을 때 `perror`를 무한히 찍으면서 CPU를 다 쓴다. `errno`를 봐야 한다.

```c++
if (length < 0) {
    if (errno == EINTR)  continue;              // 시그널 — 재시도
    if (errno == EAGAIN) continue;              // 논블로킹 — 지금 이벤트 없음
    perror("read");
    break;                                       // 그 외에는 빠져나간다
}
```

## 그 밖에 알아둘 것

**하위 디렉토리는 따로 등록해야 한다.** inotify에 재귀 옵션이 없다. 트리 전체를 감시하려면 디렉토리마다 watch를 걸고, 새 디렉토리가 생기면 그때 추가해야 한다. 그 사이에 만들어진 파일은 놓친다.

**감시 대상이 사라지면 `IN_IGNORED`가 온다.** 디렉토리가 삭제되거나 이동하면 watch가 자동으로 제거된다. 이 이벤트를 받으면 경로가 다시 생겼는지 확인하고 재등록해야 한다.

**네트워크 파일시스템에서는 안 된다.** NFS나 CIFS로 마운트한 디렉토리는 다른 호스트에서 일어난 변경을 커널이 모르니 이벤트가 안 온다. 이 경우엔 폴링밖에 답이 없다.

**watch 개수 제한이 있다.** `/proc/sys/fs/inotify/max_user_watches`가 기본 8192다. 큰 트리를 재귀로 감시하면 부족할 수 있다.

## 정리한 형태

```c++
// 이벤트 루프에서는 파일명만 모으고, 처리는 밖에서 한다
std::vector<std::string> poll_events(int fd, int wd, bool& overflowed)
{
    alignas(struct inotify_event) char buf[32 * (sizeof(struct inotify_event) + NAME_MAX + 1)];
    std::vector<std::string> ready;
    overflowed = false;

    const ssize_t len = ::read(fd, buf, sizeof(buf));
    if (len <= 0) return ready;

    for (char* p = buf; p < buf + len; ) {
        auto* e = reinterpret_cast<struct inotify_event*>(p);

        if (e->mask & IN_Q_OVERFLOW) overflowed = true;

        if (e->len > 0 && !(e->mask & IN_ISDIR) &&
            (e->mask & (IN_CLOSE_WRITE | IN_MOVED_TO)))
        {
            const std::string name = e->name;          // 널 종료되어 있다
            if (!name.empty() && name[0] != '.' && has_extension(name, "rbf"))
                ready.push_back(name);
        }

        p += sizeof(struct inotify_event) + e->len;
    }
    return ready;
}
```

`e->name`은 널로 끝나는 게 보장되어 있어서 `std::string`에 그대로 넣어도 된다. `e->len`은 패딩까지 포함한 값이라 문자열 길이와 다르다. 이걸 길이로 써서 `std::string(e->name, e->len)`으로 만들면 뒤에 널이 여러 개 붙는다.

## 정리하면

- `IN_CREATE`는 파일이 만들어진 순간이라 내용이 없다. 완성을 알려면 `IN_CLOSE_WRITE`
- `scp`/`rsync`/에디터는 임시 파일을 rename 하므로 `IN_MOVED_TO`도 같이 등록해야 한다
- 버퍼는 `sizeof(inotify_event) + NAME_MAX + 1` 이상이어야 하고, ARM에서는 정렬도 챙겨야 한다
- `IN_Q_OVERFLOW`를 처리 안 하면 파일을 조용히 놓친다. 오버플로우가 오면 디렉토리를 다시 훑는다
- 블로킹 `read` 대신 `inotify_init1(IN_NONBLOCK)` + `poll`로 가야 종료 처리가 된다
- 하위 디렉토리는 재귀로 감시되지 않고, 네트워크 파일시스템에서는 이벤트 자체가 안 온다

## 참고

- `man 7 inotify`
- `man 2 inotify_add_watch`
