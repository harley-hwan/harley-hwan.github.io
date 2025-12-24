---
title: (c++) SSH를 이용한 원격 명령 실행 (windows)
description: "c, c++, vs, windows, C++, libssh2, SSH, Remote Command Execution, Networking"
date: 2023-07-27 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, vs, windows, C++, libssh2, SSH, Remote Command Execution, Networking]
---

# libssh2를 활용한 원격 SSH 연결 및 명령어 실행
- 최초 작성일: 2023년 7월 27일 (수)

## 목차



<br/>

## 내용

SSH(Secure Shell)를 사용하여 원격 서버에 접속하고, 주어진 명령어를 실행한 뒤 그 결과를 출력하는 작업을 수행하는 코드이다.

<br/>

1. 먼저, IP 주소, 사용자 이름, 비밀번호, 실행할 명령어와 SSH의 포트 번호가 선언.
2. 그 다음으로, 소켓이 생성되고, 이 소켓을 사용해 원격 서버에 연결 시도.
3. 서버에 성공적으로 연결한 후에는 libssh2 라이브러리를 초기화하고, SSH 세션을 생성.
4. 이 세션을 사용하여 사용자 이름과 비밀번호로 서버에 인증하고, 인증이 성공적으로 완료되면 SSH 채널을 연다.
5. SSH 채널이 열리면 명령어를 실행하고, 그 결과를 읽어온다.
6. 그 결과를 출력하고, SSH 채널과 세션을 정리하고 libssh2 라이브러리를 종료하고, 소켓도 닫는다.

<br/>

## 코드

```c++
#include <libssh2/include/libssh2.h>
#include <winsock2.h>

void CRadarCalibrationDlg::OnBnClickedBtnTest()
{
	const char* ip = "";
	const char* username = "";
	const char* password = "";
	const char* command = "cd /path && ./command";
	int port = 22;

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
}
```

<br/>

<br/>

나는 ./task -v 명령어로 버전 정보를 받아오되, 출력 결과가 Version: XXXXX 형태여서 prefix (Version: ") 를 제외하고 가져오도록 했다.

<br/>

```c++
std::string CRadarCalibrationDlg::executeRemoteSshCommand(const char* command) 
{
	const char* ip = "";
	const char* username = "";
	const char* password = "";
	int port = 22;

	// socket 
	SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
	sockaddr_in sin;
	sin.sin_family = AF_INET;
	sin.sin_port = htons(port);

	// Use inet_pton instead of deprecated inet_addr
	inet_pton(AF_INET, ip, &(sin.sin_addr));

	if (connect(sock, (struct sockaddr*)(&sin), sizeof(struct sockaddr_in)) != 0) {
		std::cerr << "Failed to connect to server!" << std::endl;
		return "";
	}

	// init libssh2
	if (libssh2_init(0) != 0) {
		std::cerr << "Failed to initialize libssh2!" << std::endl;
		return "";
	}

	// create session
	LIBSSH2_SESSION* session = libssh2_session_init();
	if (libssh2_session_handshake(session, (int)sock) != 0) {
		std::cerr << "Failed to establish SSH session!" << std::endl;
		return "";
	}

	// authenticate
	if (libssh2_userauth_password(session, username, password) != 0) {
		std::cerr << "Failed to authenticate user!" << std::endl;
		return "";
	}

	// open channel and execute command
	LIBSSH2_CHANNEL* channel = libssh2_channel_open_session(session);
	if (channel == NULL) {
		std::cerr << "Failed to open channel!" << std::endl;
		return "";
	}

	if (libssh2_channel_exec(channel, command) != 0) {
		std::cerr << "Failed to execute command!" << std::endl;
		return "";
	}

	// read output
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

	// cleanup
	libssh2_channel_free(channel);
	libssh2_session_disconnect(session, "Finished session");
	libssh2_session_free(session);
	libssh2_exit();

	closesocket(sock);

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
}

void CRadarCalibrationDlg::OnBnClickedBtnTest()
{
	const char* command = "cd /home/pi/test && ./launch_jig -v";
	std::string result = executeRemoteSshCommand(command);
	std::cout << result << std::endl;
}

```
