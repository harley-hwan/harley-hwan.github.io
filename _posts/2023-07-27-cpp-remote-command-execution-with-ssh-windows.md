---
title: "(C++) SSH를 이용한 원격 명령 실행 (Windows)"
description: "검사 프로그램에서 보드의 버전을 읽으려고 libssh2로 원격 명령을 실행했다. 실패 경로에서 자원이 전부 새던 문제, stderr와 종료 코드를 안 봐서 실패를 놓치던 문제, 읽기 에러 시 무한 루프를 정리했다."
date: 2023-07-27 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, visual-studio, windows, libssh2, ssh, remote-command-execution, networking]
---
## 버튼 하나로 보드 버전 읽기

검사 결과에 보드의 소프트웨어 버전을 같이 기록해야 했다. 보드에서 `./launch_jig -v`를 실행하면 `Version: 1.2.3` 형태로 나온다.

작업자가 매번 터미널을 열어 확인하고 손으로 적을 수는 없으니, 검사 프로그램의 버튼 하나로 처리하기로 했다. [SFTP로 파일을 내려받는 것](/posts/cpp-sftp-connect-and-read-xml/)과 같은 libssh2를 쓴다. 이번엔 파일이 아니라 명령이다.

## 흐름

1. 소켓을 만들어 22번 포트에 연결한다
2. libssh2 세션을 만들고 핸드셰이크를 한다
3. 사용자/비밀번호로 인증한다
4. 채널을 열고 명령을 실행한다
5. 출력을 읽는다
6. 채널과 세션을 닫고 소켓을 정리한다

## 처음 짠 코드

```c++
#include <libssh2/include/libssh2.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <string>

#define MAX_BUFFER_SIZE 4096

void CRadarCalibrationDlg::OnBnClickedBtnTest()
{
	const char* ip = "";
	const char* username = "";
	const char* password = "";
	const char* command = "cd /path && ./command";
	int port = 22;

	// init winsock
	WSADATA wsaData;
	if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
		std::cerr << "Failed to initialize winsock!" << std::endl;
		return;
	}

	// socket 
	SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
	sockaddr_in sin;
	sin.sin_family = AF_INET;
	sin.sin_port = htons(port);

	// Use inet_pton instead of deprecated inet_addr
	inet_pton(AF_INET, ip, &(sin.sin_addr));

	if (connect(sock, (struct sockaddr*)(&sin), sizeof(struct sockaddr_in)) != 0) {
		std::cerr << "Failed to connect to server!" << std::endl;
		return;
	}

	// init libssh2
	if (libssh2_init(0) != 0) {
		std::cerr << "Failed to initialize libssh2!" << std::endl;
		return;
	}

	// create session
	LIBSSH2_SESSION* session = libssh2_session_init();
	if (libssh2_session_handshake(session, (int)sock) != 0) {
		std::cerr << "Failed to establish SSH session!" << std::endl;
		return;
	}

	// authenticate
	if (libssh2_userauth_password(session, username, password) != 0) {
		std::cerr << "Failed to authenticate user!" << std::endl;
		return;
	}

	// open channel and execute command
	LIBSSH2_CHANNEL* channel = libssh2_channel_open_session(session);
	if (channel == NULL) {
		std::cerr << "Failed to open channel!" << std::endl;
		return; 
	}

	if (libssh2_channel_exec(channel, command) != 0) {
		std::cerr << "Failed to execute command!" << std::endl;
		return;
	}

	std::string output;
	char buffer[MAX_BUFFER_SIZE];
	while (true) {
		ssize_t bytecount = libssh2_channel_read(channel, buffer, sizeof(buffer) - 1);
		if (bytecount > 0) {
			buffer[bytecount] = '\0';
			output += buffer;
		}
		else if (bytecount < 0) {
			std::cerr << "Error reading data!" << std::endl;
		}
		else {
			break;
		}
	}

	std::cout << "Command output: " << output << std::endl;

	// cleanup
	libssh2_channel_free(channel);
	libssh2_session_disconnect(session, "Finished session");
	libssh2_session_free(session);
	libssh2_exit();

	closesocket(sock);
	WSACleanup();
}
```

정상 경로에서는 잘 돌았다. 문제는 정상이 아닐 때다.

## 실패하면 전부 샌다

`return`이 일곱 군데 있는데, 그중 어느 것도 앞에서 잡은 자원을 정리하지 않는다.

- 연결 실패 → 소켓과 WSA가 남는다
- 인증 실패 → 소켓, 세션, WSA가 남는다
- 채널 열기 실패 → 거기에 세션까지

버튼 클릭 핸들러라 사용자가 몇 번이고 누른다. 보드가 꺼져 있으면 누를 때마다 실패하고, 누를 때마다 자원이 쌓인다. 작업자가 "안 되네" 하면서 열 번쯤 누르면 소켓이 열 개 남는다.

`goto`로 정리 지점을 모으는 것이 C에서 흔한 방식이지만, C++이니 RAII로 갔다.

```c++
struct WsaScope {
    bool ok = false;
    WsaScope()  { WSADATA d; ok = (WSAStartup(MAKEWORD(2,2), &d) == 0); }
    ~WsaScope() { if (ok) WSACleanup(); }
};

struct Sock {
    SOCKET s = INVALID_SOCKET;
    ~Sock() { if (s != INVALID_SOCKET) closesocket(s); }
};

struct Session {
    LIBSSH2_SESSION* s = nullptr;
    ~Session() {
        if (s) { libssh2_session_disconnect(s, "bye"); libssh2_session_free(s); }
    }
};

struct Channel {
    LIBSSH2_CHANNEL* c = nullptr;
    ~Channel() { if (c) libssh2_channel_free(c); }
};
```

소멸 순서가 선언의 역순이라, 위에서부터 `WsaScope`, `Sock`, `Session`, `Channel` 순으로 선언하면 채널 → 세션 → 소켓 → WSA 순으로 정리된다. 필요한 순서와 정확히 맞는다.

## WSAStartup과 libssh2_init을 매번 부르면 안 된다

두 함수 다 프로세스 전체에 한 번씩만 부르는 게 맞다.

`WSACleanup`은 특히 위험하다. 참조 카운트가 있어서 짝만 맞으면 되긴 하는데, 이 프로그램에는 장비와 통신하는 다른 소켓 코드가 같이 돌고 있었다. 그쪽이 `WSAStartup`을 부르지 않고 이 함수가 초기화해둔 걸 쓰고 있었다면, 여기서 `WSACleanup`을 부르는 순간 그쪽 소켓이 끊긴다.

`libssh2_init`/`libssh2_exit`도 같다. 문서에 다른 libssh2 호출보다 먼저 한 번만 부르라고 되어 있다. 세션이 살아 있는 상태에서 `libssh2_exit`을 부르면 정의되지 않은 동작이다.

둘 다 프로그램 시작과 종료로 옮겼다.

```c++
BOOL CMyApp::InitInstance() {
    WSADATA d;
    WSAStartup(MAKEWORD(2,2), &d);
    libssh2_init(0);
    // ...
}
int CMyApp::ExitInstance() {
    libssh2_exit();
    WSACleanup();
    return CWinApp::ExitInstance();
}
```

## 읽기 에러에서 무한 루프

```c++
else if (bytecount < 0) {
    std::cerr << "Error reading data!" << std::endl;
}
```

에러를 찍고 나서 `break`가 없다. 다음 회차에도 같은 에러가 나면 또 찍고, 계속 돈다. 연결이 끊긴 상태면 CPU를 하나 다 쓰면서 로그를 무한히 뱉는다.

`LIBSSH2_ERROR_EAGAIN`은 예외로 두고 나머지는 빠져나가야 한다.

```c++
if (n == LIBSSH2_ERROR_EAGAIN) continue;   // 논블로킹에서 정상
if (n < 0) { /* 로그 */ break; }
```

## stderr를 안 읽으면 실패 이유를 못 본다

`libssh2_channel_read`는 스트림 0, 즉 표준 출력만 읽는다. 명령이 실패하면 메시지는 대부분 표준 에러로 나온다.

그래서 명령 경로가 틀렸을 때 이런 상황이 됐다. 보드에서는 `bash: ./launch_jig: No such file or directory`가 나오는데, 프로그램이 보는 `output`은 빈 문자열이다. "버전을 못 읽었다"까지는 아는데 왜인지는 모른다.

표준 에러는 확장 스트림으로 따로 읽는다.

```c++
char buf[4096];
std::string out, err;

for (;;) {
    ssize_t n = libssh2_channel_read(channel, buf, sizeof(buf));
    if (n > 0)      { out.append(buf, n); continue; }
    if (n == LIBSSH2_ERROR_EAGAIN) continue;

    ssize_t m = libssh2_channel_read_ex(channel, SSH_EXTENDED_DATA_STDERR,
                                        buf, sizeof(buf));
    if (m > 0)      { err.append(buf, m); continue; }
    if (m == LIBSSH2_ERROR_EAGAIN) continue;

    break;                                   // 양쪽 다 끝났다
}
```

`libssh2_channel_read`는 사실 `libssh2_channel_read_ex(channel, 0, ...)`의 축약이다. 스트림 번호만 바꾸면 표준 에러가 나온다.

## 종료 코드를 봐야 성공을 안다

출력이 비었다고 실패는 아니다. 반대로 출력이 있어도 명령은 실패했을 수 있다. 확실한 건 종료 코드다.

```c++
libssh2_channel_send_eof(channel);
libssh2_channel_wait_eof(channel);
libssh2_channel_wait_closed(channel);

int exit_code = libssh2_channel_get_exit_status(channel);
```

`wait_eof`와 `wait_closed`를 부르는 이유가 하나 더 있다. 이걸 안 하고 바로 `libssh2_channel_free`를 하면 **출력의 마지막 부분이 잘릴 수 있다**. 버퍼에 남아 있던 데이터를 못 받고 채널을 닫는 것이다. 짧은 출력에서는 티가 안 나다가 출력이 길어지면 뒤가 사라진다.

## 응답이 없으면 창이 멈춘다

버튼 클릭 핸들러에서 동기로 처리하니, 보드가 응답을 안 하면 UI 스레드가 그대로 막힌다. `connect`에는 타임아웃이 없어서 대상이 없는 IP면 수십 초를 기다린다.

libssh2 쪽 타임아웃은 함수 하나로 걸린다.

```c++
libssh2_session_set_timeout(session, 5000);   // ms, 블로킹 호출에 적용
```

TCP 연결 자체의 타임아웃은 별개다. 소켓을 논블로킹으로 만들고 `select`로 기다리는 방법이 표준적이다.

```c++
u_long nb = 1;
ioctlsocket(sock, FIONBIO, &nb);
connect(sock, ...);                            // 즉시 반환

fd_set w; FD_ZERO(&w); FD_SET(sock, &w);
timeval tv{3, 0};
if (select(0, nullptr, &w, nullptr, &tv) <= 0) { /* 타임아웃 */ }

nb = 0;
ioctlsocket(sock, FIONBIO, &nb);               // 다시 블로킹으로
```

그래도 몇 초는 UI가 멈춘다. 결국 별도 스레드에서 돌리고 결과를 `PostMessage`로 받는 구조로 바꿨다. [BLE 스캔](/posts/cpp-mfc-bluetooth-device-scan-and-listview/)에서 쓴 것과 같은 방식이다.

## 버전 문자열 다듬기

원래 목적이었던 부분이다.

```c++
	// Extract version
	std::string prefix = "Version: ";
	std::size_t pos = output.find(prefix);
	if (pos != std::string::npos) {
		std::string version = output.substr(pos + prefix.size());
		JIGVer = version;
		m_stStatus1.SetWindowText(("Jig Ver: " + version).c_str());
		return "Version is: " + version;
	}
	else {
		return output;
	}
```

```c++
void CRadarCalibrationDlg::OnBnClickedBtnTest()
{
	const char* command = "cd /home/pi/test && ./launch_jig -v";
	std::string result = executeRemoteSshCommand(command);
	std::cout << result << std::endl;
}
```

`substr(pos + prefix.size())`는 **줄 끝까지가 아니라 문자열 끝까지** 가져간다. 출력이 한 줄이면 뒤에 `\n`이 붙고, 여러 줄이면 그 뒤 줄까지 전부 들어온다. 화면에 그대로 찍으면 줄바꿈이 남아서 레이블이 이상해진다.

줄 단위로 자르고 공백을 정리해야 한다.

```c++
std::string extract_version(const std::string& out)
{
    const std::string key = "Version:";
    const size_t p = out.find(key);
    if (p == std::string::npos) return {};

    size_t b = p + key.size();
    size_t e = out.find_first_of("\r\n", b);
    if (e == std::string::npos) e = out.size();

    std::string v = out.substr(b, e - b);
    // 앞뒤 공백 제거
    const size_t s = v.find_first_not_of(" \t");
    const size_t t = v.find_last_not_of(" \t");
    return (s == std::string::npos) ? std::string{} : v.substr(s, t - s + 1);
}
```

`\r`을 같이 찾는 이유는, 보드가 CRLF로 출력하는 경우가 있어서다. `\n`만 잘라내면 `\r`이 남아서 화면에서는 안 보이는데 문자열 비교가 계속 실패한다.

`SetWindowText(("Jig Ver: " + version).c_str())`도 유니코드 빌드에서는 안 된다. `std::string::c_str()`은 `const char*`인데 `SetWindowText`는 `LPCTSTR`을 받는다. MBCS 빌드에서만 컴파일된다. `CString`으로 만들어 넘기는 게 맞다.

## 캐스팅 하나

```c++
libssh2_session_handshake(session, (int)sock)
```

윈도우의 `SOCKET`은 `UINT_PTR`이라 64비트에서 8바이트다. `int`로 자르면 상위 4바이트가 날아간다. 실제로 윈도우가 주는 소켓 값이 작아서 대부분 문제가 안 되지만, 보장된 게 아니다.

libssh2는 `libssh2_socket_t`라는 타입을 정의해두고 윈도우에서는 `SOCKET`으로 매핑한다. 캐스팅 없이 그냥 넘기면 된다.

```c++
libssh2_session_handshake(session, sock);
```

## 정리하면

- 실패 경로마다 `return`이 있는 함수에서 자원을 손으로 정리하면 반드시 빠뜨린다. RAII로 감싸고 선언 순서로 정리 순서를 맞춘다
- `WSAStartup`/`WSACleanup`, `libssh2_init`/`libssh2_exit`은 프로그램 전체에서 한 번씩이다
- 읽기 에러에서 `break`가 없으면 무한 루프가 된다
- `libssh2_channel_read`는 표준 출력만 준다. 실패 이유는 `SSH_EXTENDED_DATA_STDERR`에 있다
- `wait_eof`/`wait_closed` 없이 채널을 닫으면 출력 끝이 잘린다. 성공 여부는 `get_exit_status`로 본다
- 원격 호출을 UI 스레드에서 동기로 하면 창이 멈춘다. 타임아웃을 걸고 스레드로 뺀다

## 참고

- [libssh2_channel_read_ex](https://www.libssh2.org/libssh2_channel_read_ex.html)
- [libssh2 예제 — ssh2_exec.c](https://www.libssh2.org/examples/ssh2_exec.html)
