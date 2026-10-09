---
title: "(C++) Windows 소켓 에러 메시지 출력 구현"
description: "WSAGetLastError가 뱉는 숫자를 사람이 읽는 문장으로 바꾸는 FormatMessage 사용법과, 유니코드 빌드에서 메시지가 깨지는 문제·메시지 끝에 붙는 개행·실패 시 LocalFree가 터지는 문제까지 정리했다."
date: 2023-02-10 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, windows, socket, error, mfc, formatmessage, winsock]
---
## 숫자만 보고는 알 수가 없다

MFC 툴에서 장비랑 소켓으로 통신하는데, 실패하면 로그에 이런 게 찍혔다.

```text
send failed: 10054
```

10054가 뭔지 알려면 MSDN을 뒤져야 한다. 몇 번 반복하다 보니 자주 보는 코드는 외워졌지만(10054는 상대가 연결을 강제로 끊은 것), 처음 보는 코드가 나오면 또 검색이다. 어차피 윈도우가 메시지 테이블을 들고 있으니 그걸 꺼내 쓰기로 했다.

## 기본 형태

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

플래그 세 개가 하는 일은 이렇다.

- `FORMAT_MESSAGE_ALLOCATE_BUFFER`: 버퍼를 내가 잡지 않고 시스템이 잡아준다. 대신 `LocalFree`로 해제해야 한다. 다섯 번째 인자가 버퍼가 아니라 **버퍼 포인터의 주소**로 바뀌는 게 헷갈리는 지점이다. 그래서 `(LPTSTR)&lpMsgBuf`처럼 캐스팅이 붙는다
- `FORMAT_MESSAGE_FROM_SYSTEM`: 시스템 메시지 테이블에서 찾는다
- `FORMAT_MESSAGE_IGNORE_INSERTS`: `%1`, `%2` 같은 삽입 자리를 그대로 둔다. 이걸 빼면 삽입할 인자를 안 넘긴 메시지에서 함수가 실패한다

부르는 쪽은 이렇게 쓴다. 소켓이든 일반 API든 에러 코드만 넘기면 된다.

```cpp
// 소켓 함수 호출 후 에러 발생 시
int error = WSAGetLastError();
displayerror(error);

// 일반 시스템 함수 호출 후 에러 발생 시
int error = GetLastError();
displayerror(error);
```

두 함수가 나뉘어 있는 게 처음엔 번거로워 보였는데, 소켓 API는 `WSAGetLastError`를, 나머지 Win32 API는 `GetLastError`를 쓰는 게 규칙이다. 실제로 두 값은 같은 저장소를 쓰지만 문서상 보장된 건 아니라서 짝을 맞춰 쓰는 게 맞다.

여기까지는 검색하면 나오는 그대로다. 문제는 이걸 실제로 붙이고 나서 하나씩 튀어나왔다.

## 함정 1: 유니코드 빌드에서 메시지가 깨진다

MFC 프로젝트 기본값이 유니코드라서 `FormatMessage`가 `FormatMessageW`로 매핑된다. `lpMsgBuf`에는 와이드 문자열이 들어오는데, `printf`의 `%s`는 `char*`를 기대한다. 그대로 넘기면 첫 글자만 나오거나 깨진 문자가 찍힌다.

와이드 문자열의 두 번째 바이트가 대개 0이라 `printf`가 거기서 문자열이 끝났다고 판단한다. "액세스가 거부되었습니다"가 한 글자만 나오는 이유가 이거다.

```cpp
wprintf(L"%d %ls\n", nErrorCode, (LPCWSTR)lpMsgBuf);
// 또는 TCHAR 매핑을 그대로 따라가려면
_tprintf(_T("%d %s\n"), nErrorCode, (LPCTSTR)lpMsgBuf);
```

`_tprintf`는 유니코드 빌드에서 `wprintf`로, 멀티바이트 빌드에서 `printf`로 매핑되고 `%s`도 같이 따라간다. 빌드 설정을 왔다 갔다 할 가능성이 있으면 이쪽이 안전하다.

## 함정 2: 메시지 끝에 개행이 붙어 있다

시스템 메시지는 대부분 `\r\n`으로 끝난다. 그래서 로그가 이렇게 나온다.

```text
[12:03:41] send failed: 10054 기존 연결이 원격 호스트에 의해 강제로 끊겼습니다.

[12:03:41] reconnecting...
```

한 줄마다 빈 줄이 하나씩 끼어서 로그 파일이 두 배가 된다. 잘라내야 한다.

```cpp
// 끝의 \r, \n, 공백 제거
size_t len = _tcslen((LPCTSTR)lpMsgBuf);
LPTSTR p = (LPTSTR)lpMsgBuf;
while (len > 0 && (p[len - 1] == _T('\r') || p[len - 1] == _T('\n') || p[len - 1] == _T(' ')))
    p[--len] = _T('\0');
```

## 함정 3: 실패했을 때 LocalFree가 터진다

메시지 테이블에 없는 코드를 넘기면 `FormatMessage`가 0을 반환한다. 이때 `lpMsgBuf`는 **아무것도 대입되지 않은 상태**로 남는다. 초기화를 안 해뒀으면 스택 쓰레기 값이고, 그걸 `LocalFree`에 넘기면 그 자리에서 죽는다.

에러를 보려고 붙인 코드가 에러를 만드는 상황이라 특히 짜증난다. 반환값을 반드시 검사해야 한다.

```cpp
LPVOID lpMsgBuf = nullptr;      // 초기화
DWORD n = FormatMessage(...);
if (n == 0) {
    // 메시지를 못 찾았다. lpMsgBuf 는 손대면 안 된다
    return;
}
// ...
LocalFree(lpMsgBuf);
```

## 함정 4: 에러 코드를 즉시 저장해야 한다

`GetLastError()`와 `WSAGetLastError()`가 돌려주는 값은 스레드마다 하나뿐인 슬롯에 들어 있다. API를 하나 더 호출하면 성공했더라도 덮어쓰일 수 있다.

```cpp
if (send(sock, buf, len, 0) == SOCKET_ERROR) {
    LogToFile("send failed");          // 이 안에서 파일 API 를 호출한다
    displayerror(WSAGetLastError());   // 여기서는 이미 다른 값일 수 있다
}
```

실패를 확인한 바로 다음 줄에서 지역 변수로 받아둬야 한다.

```cpp
if (send(sock, buf, len, 0) == SOCKET_ERROR) {
    const int err = WSAGetLastError();   // 먼저 저장
    LogToFile("send failed");
    displayerror(err);
}
```

## 함정 5: 언어를 영어로 고정하면 실패할 수 있다

로그를 영어로 통일하려고 `MAKELANGID(LANG_ENGLISH, SUBLANG_ENGLISH_US)`를 넣었다가 메시지가 아예 안 나온 적이 있다. 해당 언어의 메시지 리소스가 설치되어 있지 않으면 함수가 실패한다.

언어 인자에 `0`을 넘기면 시스템이 사용 가능한 언어를 정해진 우선순위대로 찾아준다. 특별한 이유가 없으면 `0`이 제일 무난하다.

## 다듬은 버전

위의 것들을 다 반영하면 이렇게 된다. 출력까지 하는 대신 문자열을 돌려주도록 바꿨다. 로그 파일에도 쓰고 메시지 박스에도 띄우려면 이 형태가 편하다.

```cpp
#include <windows.h>
#include <tchar.h>
#include <string>

std::basic_string<TCHAR> FormatWinError(DWORD code)
{
    LPTSTR buf = nullptr;
    const DWORD n = FormatMessage(
        FORMAT_MESSAGE_ALLOCATE_BUFFER |
        FORMAT_MESSAGE_FROM_SYSTEM |
        FORMAT_MESSAGE_IGNORE_INSERTS,
        nullptr,
        code,
        0,                          // 시스템이 알아서 언어를 고르게 둔다
        (LPTSTR)&buf,
        0,
        nullptr);

    if (n == 0 || buf == nullptr) {
        TCHAR fallback[64];
        _sntprintf_s(fallback, _countof(fallback), _TRUNCATE,
                     _T("Unknown error 0x%08X (%u)"), code, code);
        return fallback;
    }

    std::basic_string<TCHAR> msg(buf, n);
    LocalFree(buf);

    while (!msg.empty() &&
           (msg.back() == _T('\r') || msg.back() == _T('\n') || msg.back() == _T(' ')))
        msg.pop_back();

    return msg;
}
```

`std::basic_string<TCHAR> msg(buf, n)`처럼 길이를 같이 넘기는 게 포인트다. `FormatMessage`의 반환값이 널 문자를 뺀 문자 수라서, 이걸 쓰면 문자열 길이를 다시 세지 않아도 된다.

사용하는 쪽.

```cpp
// 소켓 함수 실패 시
const int err = WSAGetLastError();
Log(_T("send failed: %d %s"), err, FormatWinError(err).c_str());

// 일반 Win32 API 실패 시
const DWORD err = GetLastError();
Log(_T("CreateFile failed: %u %s"), err, FormatWinError(err).c_str());
```

## WSA 에러도 시스템 테이블에 있다

처음엔 소켓 에러가 별도 테이블에 있는 줄 알고 `FORMAT_MESSAGE_FROM_HMODULE`로 `ws2_32.dll`을 지정해봤는데, 그럴 필요가 없었다. 10000번대 WSA 에러 코드는 시스템 메시지 테이블에 그대로 들어 있어서 `FORMAT_MESSAGE_FROM_SYSTEM`만으로 풀린다.

별도 모듈을 지정해야 하는 건 다른 경우다. 네트워크 관리 함수의 에러(2100~2999)는 `netmsg.dll`, WinINet 에러(12000번대)는 `wininet.dll`, NTSTATUS 값은 `ntdll.dll`에 있다.

```cpp
// NTSTATUS 를 풀 때
HMODULE h = GetModuleHandle(_T("ntdll.dll"));
FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER |
              FORMAT_MESSAGE_FROM_HMODULE |
              FORMAT_MESSAGE_IGNORE_INSERTS,
              h, status, 0, (LPTSTR)&buf, 0, nullptr);
```

자주 보게 되는 소켓 에러는 결국 몇 개로 좁혀졌다.

| 코드 | 이름 | 상황 |
| ---: | :--- | :--- |
| 10035 | WSAEWOULDBLOCK | 논블로킹 소켓에서 지금은 처리 불가. 에러가 아니라 정상 |
| 10038 | WSAENOTSOCK | 이미 닫은 소켓 핸들을 다시 썼다 |
| 10048 | WSAEADDRINUSE | bind 하려는 포트를 누가 쓰고 있다 |
| 10054 | WSAECONNRESET | 상대가 연결을 강제로 끊었다 |
| 10060 | WSAETIMEDOUT | 응답이 없다. 장비가 꺼져 있거나 방화벽 |
| 10061 | WSAECONNREFUSED | 상대는 살아 있는데 그 포트에 아무도 없다 |

10060과 10061의 구분이 실제로 제일 쓸모 있었다. 10061이면 장비는 켜져 있고 프로그램이 안 떠 있는 것이고, 10060이면 장비 자체나 경로가 문제다. 이 한 줄 차이로 현장에서 확인할 곳이 갈린다.

## C++11 이후로는 더 짧게 쓸 수 있다

표준 라이브러리에도 같은 일을 하는 게 있다.

```cpp
#include <system_error>

std::string msg = std::system_category().message(err);
```

윈도우 표준 라이브러리 구현이 내부에서 `FormatMessageA`를 부른다. 한 줄이라 간편한데, ANSI 버전이라 한국어 윈도우에서 로그를 UTF-8로 남기면 인코딩이 꼬인다. 로그를 영어로 쓰거나 시스템 코드페이지 그대로 두는 프로젝트면 이걸로 충분하고, 인코딩을 통제해야 하면 위의 `FormatWinError` 쪽으로 간다.

예외로 던지고 싶으면 이렇게 쓴다.

```cpp
throw std::system_error(err, std::system_category(), "send");
// what() -> "send: 기존 연결이 원격 호스트에 의해 강제로 끊겼습니다."
```

## 참고

- [FormatMessageW (winbase.h)](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-formatmessage)
- [Windows Sockets Error Codes](https://learn.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes-2)
