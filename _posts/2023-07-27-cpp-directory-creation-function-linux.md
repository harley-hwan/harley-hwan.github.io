---
title: "(C++) 리눅스 환경에서 디렉토리 생성을 보장하는 함수"
description: "로그 폴더가 없으면 ofstream이 조용히 실패해서 만든 함수. stat으로 먼저 확인하는 게 왜 불필요한지, mkdir(0777)이 왜 0755가 되는지, 상대 경로가 왜 자동 실행에서 어긋나는지 정리했다."
date: 2023-07-27 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, linux, mkdir, stat, umask, filesystem]
---
## 로그가 안 남아서 시작했다

보드에 프로그램을 새로 올리고 나면 로그가 하나도 안 남았다. 코드에는 분명히 `ofstream`으로 쓰고 있는데 파일이 없다.

원인은 `../log` 디렉토리가 없어서였다. `ofstream`은 열기에 실패해도 예외를 던지지 않고 그냥 실패 상태로 남는다. 반환값을 안 보면 아무 일도 없었던 것처럼 지나간다. 개발 PC에는 폴더가 있으니 문제가 없다가, 새로 배포한 보드에서만 조용히 실패하는 상황이었다.

그래서 파일을 쓰기 전에 디렉토리를 보장하는 함수를 하나 만들었다.

## 처음 짠 함수

```c++
void ensure_directory_exists(const std::string& path, mode_t mode)
{
    struct stat st;
    if(stat(path.c_str(), &st) != 0) {
        if (mkdir(path.c_str(), mode) != 0 && errno != EEXIST) {
            std::cerr << "Could not create directory: " << path << std::endl;
            exit(EXIT_FAILURE);
        }
    } else if (!S_ISDIR(st.st_mode)) {
        errno = ENOTDIR;
        std::cerr << "Path exists but is not a directory: " << path << std::endl;
        exit(EXIT_FAILURE);
    }
}
```

```c++
// Check if log directory exists, if not, create it
ensure_directory_exists("../log", 0777);
```

동작 순서는 이렇다. `stat`으로 경로를 확인해서 아무것도 없으면(`-1` 반환) `mkdir`으로 만든다. 뭔가 있는데 디렉토리가 아니면 에러다. 이미 디렉토리면 아무 일도 안 한다.

목적은 달성했다. 다시 보니 고칠 부분이 여러 개 있다.

## stat으로 먼저 확인할 필요가 없다

`stat`과 `mkdir` 사이에는 틈이 있다. 그 사이에 다른 프로세스가 같은 디렉토리를 만들면 `mkdir`이 `EEXIST`로 실패한다. 원 코드가 `errno != EEXIST`를 검사하고 있으니 그 경우는 이미 통과한다.

그러면 `stat`은 왜 있는 걸까. 사실 없어도 된다. `mkdir`을 먼저 부르고 `EEXIST`면 이미 있는 것으로 처리하면 한 번의 시스템 콜로 끝난다.

```c++
if (mkdir(path.c_str(), mode) == 0)  return true;   // 내가 만들었다
if (errno != EEXIST)                 return false;  // 진짜 실패
// 여기 왔으면 이미 뭔가 있다 — 그게 디렉토리인지만 확인하면 된다
```

`stat`이 필요한 건 "이미 있는 게 디렉토리가 맞는지" 확인할 때뿐이다. `../log`라는 **파일**이 있으면 `mkdir`은 `EEXIST`를 주지만 그 경로에 로그를 못 쓴다. 실제로 겪었다. 이전 버전이 `log`를 디렉토리가 아니라 파일로 만들어놓은 상태에서 새 버전을 올렸더니, `mkdir`은 통과하는데 파일 열기는 계속 실패했다.

## 라이브러리 함수가 프로세스를 죽이면 안 된다

`exit(EXIT_FAILURE)`가 제일 걸리는 부분이다. 디렉토리 하나 못 만들었다고 프로그램 전체가 끝난다. 호출한 쪽에서 "로그는 못 남기지만 계속 진행"을 선택할 여지가 없다.

측정 데이터를 저장할 디렉토리라면 종료가 맞을 수도 있다. 하지만 그 판단은 호출하는 쪽이 하는 게 맞다. 함수는 성공 여부만 돌려준다.

그리고 `errno = ENOTDIR;`을 설정한 직후에 `exit`을 부르는 건 아무 의미가 없다. `errno`는 호출자가 읽으라고 있는 것인데 읽을 호출자가 없다.

## mkdir(0777)이 0777이 안 된다

이건 한참 헤맸다. `0777`로 만들었는데 `ls -l`로 보면 `drwxr-xr-x`, 즉 `0755`다.

`mkdir`의 mode 인자는 **요청값**이고, 실제 권한은 `mode & ~umask`가 된다. 대부분의 시스템에서 기본 umask는 `022`라서 그룹과 기타 사용자의 쓰기 권한(`022`)이 깎인다.

```text
0777 & ~0022 = 0755
```

다른 사용자로 도는 프로세스가 같은 디렉토리에 써야 하는 상황이었는데, 권한이 없어서 실패했다. 진짜로 `0777`이 필요하면 만든 뒤 `chmod`를 따로 불러야 한다. `chmod`는 umask의 영향을 안 받는다.

```c++
mkdir(path.c_str(), 0777);
chmod(path.c_str(), 0777);   // umask 를 우회한다
```

물론 `0777`은 아무나 쓸 수 있다는 뜻이라 좋은 선택은 아니다. 같은 그룹만 쓰면 되면 `0775`에 그룹을 맞추는 쪽이 낫다.

## 중간 경로는 안 만들어진다

`mkdir`은 한 단계만 만든다. `mkdir -p`가 아니다.

```c++
ensure_directory_exists("../log/2023-07-27", 0755);   // ../log 가 없으면 ENOENT
```

로그를 날짜별 폴더로 나누기 시작하면서 바로 걸렸다. 경로를 앞에서부터 하나씩 만들어야 한다.

```c++
#include <sys/stat.h>
#include <cerrno>
#include <string>

bool make_dir_p(const std::string& path, mode_t mode)
{
    if (path.empty()) return false;

    std::string cur;
    size_t i = 0;
    if (path[0] == '/') { cur = "/"; i = 1; }       // 절대 경로

    while (i <= path.size()) {
        const size_t next = path.find('/', i);
        const size_t end  = (next == std::string::npos) ? path.size() : next;

        if (end > i) {
            cur += path.substr(i, end - i);
            if (mkdir(cur.c_str(), mode) != 0 && errno != EEXIST)
                return false;
            cur += '/';
        }
        if (next == std::string::npos) break;
        i = next + 1;
    }

    struct stat st{};
    return stat(path.c_str(), &st) == 0 && S_ISDIR(st.st_mode);
}
```

중간에 `//`가 들어가거나 끝에 `/`가 붙어도 되도록 빈 구간을 건너뛴다. 마지막에 한 번 더 `stat`으로 확인하는 이유는, 경로 마지막이 파일인 경우를 잡기 위해서다.

## 상대 경로가 자동 실행에서 어긋난다

`../log`는 **프로세스의 현재 작업 디렉토리** 기준이다. 터미널에서 `cd /home/pi/app/bin && ./program`으로 띄우면 `/home/pi/app/log`가 된다. 의도한 그대로다.

그런데 부팅 시 자동 실행으로 바꾸면서 로그가 다시 사라졌다. systemd로 띄우면 작업 디렉토리가 `/`라서 `../log`가 `/log`로 해석된다. root가 아니면 만들 수도 없다. cron도 홈 디렉토리에서 시작하니 또 다르다.

세 가지 중 하나로 해결한다.

- systemd 유닛에 `WorkingDirectory=/home/pi/app/bin`을 명시한다
- 프로그램이 시작할 때 실행 파일 위치를 읽어서 기준을 잡는다 (`readlink("/proc/self/exe", ...)`)
- 로그 경로를 설정 파일이나 환경 변수로 받는다

지금은 세 번째로 갔다. 절대 경로를 설정으로 주는 게 제일 헷갈릴 여지가 없다.

## 정리한 버전

```c++
#include <sys/stat.h>
#include <cerrno>
#include <string>

// true  : 경로에 사용 가능한 디렉토리가 있다
// false : 만들지 못했다 (errno 에 이유가 남는다)
bool ensure_directory(const std::string& path, mode_t mode = 0755)
{
    if (mkdir(path.c_str(), mode) == 0)
        return true;

    if (errno != EEXIST)
        return false;                       // 권한 없음, 상위 경로 없음 등

    struct stat st{};
    if (stat(path.c_str(), &st) != 0)
        return false;

    if (!S_ISDIR(st.st_mode)) {
        errno = ENOTDIR;                    // 파일이 자리를 차지하고 있다
        return false;
    }
    return true;
}
```

호출하는 쪽에서 정책을 정한다.

```c++
if (!ensure_directory(log_dir)) {
    // 로그는 못 남기지만 계속 간다. 대신 stderr 로 뺀다
    std::perror(("log dir: " + log_dir).c_str());
    use_stderr_only = true;
}

if (!ensure_directory(data_dir)) {
    // 측정 데이터는 못 잃는다. 여기서 끝낸다
    std::perror(("data dir: " + data_dir).c_str());
    return EXIT_FAILURE;
}
```

`stat`은 심볼릭 링크를 따라간다는 점도 알아두면 좋다. `log`가 다른 디렉토리를 가리키는 링크여도 `S_ISDIR`이 참이 되어 그대로 통과한다. 링크 자체를 봐야 하면 `lstat`을 쓴다. 여기서는 링크여도 쓸 수 있으면 되니까 `stat`이 맞다.

## C++17이면 표준으로 된다

```c++
#include <filesystem>
namespace fs = std::filesystem;

std::error_code ec;
fs::create_directories(log_dir, ec);      // 중간 경로까지 다 만든다
if (ec) { /* ec.message() */ }
```

`create_directories`가 `mkdir -p` 역할을 하고, 이미 있으면 `false`를 돌려주지만 에러는 아니다. 예외를 안 쓰려면 `error_code`를 받는 오버로드를 쓴다.

권한은 기본값(`0777 & ~umask`)이라 위의 umask 이야기가 그대로 적용된다. 다르게 주려면 만든 뒤 `fs::permissions`를 부른다.

보드 툴체인이 오래되면 못 쓰는 경우가 있다. GCC 8까지는 `-lstdc++fs`를 링크해야 하고, 그 이전 버전은 `<experimental/filesystem>`이라 헤더 이름부터 다르다. 그래서 결국 위의 POSIX 버전을 그대로 들고 다니게 됐다.

## 정리하면

- `stat` 먼저 확인할 필요 없다. `mkdir`을 부르고 `EEXIST`를 처리하는 게 짧고 경쟁 조건도 없다
- 다만 `EEXIST`일 때 그게 디렉토리인지는 확인해야 한다. 파일이 자리를 차지한 경우가 실제로 생긴다
- `mkdir(path, 0777)`의 결과는 `0777 & ~umask`다. 그대로 원하면 `chmod`를 따로 부른다
- `mkdir`은 한 단계만 만든다. 중첩 경로는 직접 쪼개거나 `create_directories`를 쓴다
- 상대 경로는 자동 실행 환경에서 기준이 달라진다. 절대 경로를 설정으로 받는 게 안전하다
- 실패를 어떻게 처리할지는 호출하는 쪽이 정한다. 함수 안에서 `exit`을 부르지 않는다
