---
title: "(C++) SFTP 접속 및 XML 파일 읽기"
description: "보드의 설정 XML을 PC 프로그램이 읽어야 해서 SFTP를 붙였다. 30일 뒤 갑자기 멈춘 상용 라이브러리, libssh2로 옮기며 놓친 소켓 정리와 호스트 키 검증, pugixml의 실패 검사가 항상 통과하던 문제를 정리했다."
date: 2023-06-29 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, visual-studio, sftp, ftp, cksftp, xml, pugi, pugixml, libssh2]
---
## 보드의 설정 파일을 PC에서 읽어야 했다

보드에 캘리브레이션 값이 XML로 저장되어 있고, PC의 검사 프로그램이 그 값을 읽어서 화면에 보여줘야 했다. 통신 프로토콜에 조회 명령을 하나 더 만들 수도 있었지만, 파일은 이미 있으니 그냥 가져오는 게 빠르다고 봤다. 보드에 SSH가 열려 있으니 SFTP를 쓰면 된다.

## 상용 라이브러리로 시작했다가 멈췄다

처음 고른 건 CkSFtp였다. 예제가 잘 되어 있고 API가 단순해서 금방 붙었다.

그런데 한 달쯤 지나서 갑자기 접속이 안 됐다. 코드는 하나도 안 건드렸는데 어느 날부터 실패한다. 원인을 찾다가 알았는데, **30일 평가 기간이 끝난 것**이었다. 유료 라이선스를 사야 계속 쓸 수 있다.

라이선스 조건을 제대로 안 보고 붙인 내 잘못이다. 무료로 보이는 걸 가져다 쓸 때는 라이선스 파일부터 확인해야 한다는 걸 이때 배웠다. 특히 이 경우처럼 "시간이 지나면 멈추는" 방식은, 개발 중에는 멀쩡하다가 배포하고 한참 뒤에 현장에서 터진다.

기록을 위해 CkSFtp 버전 코드도 남겨둔다.

```c++
bool CExampleDlg::connectToServer(CkSFtp& sftp, const char* hostname, int port) {
	if (sftp.Connect(hostname, port) != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	if (sftp.AuthenticatePw("root", "fa") != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	if (sftp.InitializeSftp() != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	return true;
}

bool CExampleDlg::downloadRemoteFile(CkSFtp& sftp, const char* remoteFilePath, const char* localFilePath) {
	const char* handle = sftp.openFile(remoteFilePath, "readOnly", "openExisting");
	if (sftp.get_LastMethodSuccess() != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	if (sftp.DownloadFile(handle, localFilePath) != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	if (sftp.CloseHandle(handle) != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	return true;
}
```

`lastErrorText()`가 실패 원인을 자세히 알려주는 건 확실히 편했다. libssh2는 에러 코드만 주기 때문에 원인 파악에 손이 더 간다.

## libssh2로 옮기기

libssh2는 BSD 라이선스라 상업용 프로그램에 그냥 쓸 수 있다. 대신 저수준이라 소켓부터 직접 만든다.

```c++
bool CExampleDlg::connectToServer(LIBSSH2_SESSION*& session, const char* hostname, int port, const char* username, const char* password) {
	SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
	sockaddr_in sin;
	sin.sin_family = AF_INET;
	sin.sin_port = htons(port);

	// Use inet_pton instead of inet_addr
	if (inet_pton(AF_INET, hostname, &sin.sin_addr) <= 0) {
		std::cerr << "Invalid address format\n";
		return false;
	}

	if (connect(sock, (struct sockaddr*)(&sin), sizeof(struct sockaddr_in)) != 0) {
		std::cerr << "Failed to connect to " << hostname << "\n";
		return false;
	}

	session = libssh2_session_init();
	if (libssh2_session_handshake(session, sock)) {
		std::cerr << "Failed to establish SSH session\n";
		return false;
	}

	if (libssh2_userauth_password(session, username, password)) {
		std::cerr << "Authentication failed\n";
		return false;
	}

	return true;
}
```

```c++
bool CExampleDlg::downloadRemoteFile(LIBSSH2_SESSION*& session, const char* remoteFilePath, const char* localFilePath)
{
	LIBSSH2_SFTP* sftp_session = libssh2_sftp_init(session);
	if (!sftp_session) {
		std::cerr << "Failed to initialize SFTP session\n";
		return false;
	}
	unsigned int filename_len = static_cast<unsigned int>(strlen(remoteFilePath));
	LIBSSH2_SFTP_HANDLE* sftp_handle = libssh2_sftp_open_ex(sftp_session, remoteFilePath, filename_len, LIBSSH2_FXF_READ, 0, LIBSSH2_SFTP_OPENFILE);

	if (!sftp_handle) {
		std::cerr << "Failed to open file with SFTP\n";
		libssh2_sftp_shutdown(sftp_session);
		return false;
	}

	FILE* localFile;
	errno_t err = fopen_s(&localFile, localFilePath, "wb");
	if (err != 0 || !localFile) {
		std::cerr << "Failed to open local file\n";
		libssh2_sftp_close(sftp_handle);
		libssh2_sftp_shutdown(sftp_session);
		return false;
	}

	char buffer[1024];
	while (true) {
		ssize_t amount = libssh2_sftp_read(sftp_handle, buffer, static_cast<unsigned int>(sizeof(buffer)));
		if (amount > 0) {
			size_t result = fwrite(buffer, 1, static_cast<size_t>(amount), localFile);
			if (result != static_cast<size_t>(amount)) {
				std::cerr << "Failed to write to local file\n";
				fclose(localFile);
				libssh2_sftp_close(sftp_handle);
				libssh2_sftp_shutdown(sftp_session);
				return false;
			}
		}
		else if (amount == 0) {
			break; // EOF reached
		}
		else {
			std::cerr << "Failed to read from remote file\n";
			fclose(localFile);
			libssh2_sftp_close(sftp_handle);
			libssh2_sftp_shutdown(sftp_session);
			return false;
		}
	}

	fclose(localFile);
	libssh2_sftp_close(sftp_handle);
	libssh2_sftp_shutdown(sftp_session);

	return true;
}
```

동작은 했다. 실패 경로마다 정리 코드를 늘어놓는 게 눈에 거슬리는데, 이게 나중에 실제 문제로 이어졌다.

## 소켓이 샌다

`connectToServer`에서 만든 `sock`은 지역 변수다. 함수를 나가면 변수는 사라지지만 **소켓은 안 닫힌다**. 성공하든 실패하든 마찬가지다.

`libssh2_session_free`를 불러도 소켓은 안 닫힌다. libssh2는 소켓을 자기가 만들지 않았으니 정리도 안 한다. 넘겨받은 디스크립터를 쓸 뿐이다.

검사 프로그램이 장비마다 한 번씩 이 함수를 부르니, 검사할 때마다 소켓이 하나씩 쌓인다. [예전에 리눅스에서 fd 한도로 데인 것](/posts/cpp-get-connected-ip-list-with-arp/)과 같은 종류의 문제다.

세션과 소켓을 같이 들고 다니는 구조로 바꿨다.

```c++
struct SshConn {
    SOCKET sock = INVALID_SOCKET;
    LIBSSH2_SESSION* session = nullptr;

    ~SshConn() { close(); }
    void close() {
        if (session) {
            libssh2_session_disconnect(session, "bye");
            libssh2_session_free(session);
            session = nullptr;
        }
        if (sock != INVALID_SOCKET) {
            closesocket(sock);
            sock = INVALID_SOCKET;
        }
    }
};
```

순서가 중요하다. 세션을 먼저 정리하고 소켓을 닫아야 한다. 소켓을 먼저 닫으면 `libssh2_session_disconnect`가 종료 패킷을 못 보낸다.

`libssh2_init(0)`을 안 부른 것도 빠뜨린 부분이다. 이 함수는 프로그램 전체에서 한 번, 다른 libssh2 호출보다 먼저 불러야 한다. 안 불러도 첫 호출에서 알아서 초기화되는 경우가 있지만, 멀티스레드에서는 경쟁이 생긴다. 짝이 되는 `libssh2_exit()`도 프로그램 끝에 한 번 부른다.

윈도우에서는 `WSAStartup`도 필요하다. 이 코드에는 없는데, MFC 프로그램이라 다른 곳에서 이미 불러서 동작했다. 이 함수만 떼어서 콘솔 프로그램에 붙이면 `socket()`이 바로 실패한다.

## 호스트 키를 검증하지 않는다

이 코드는 서버가 누구인지 확인하지 않는다. 핸드셰이크 직후에 바로 비밀번호를 보낸다.

터미널에서 `ssh`로 처음 접속하면 지문을 보여주고 계속할지 물어보는 그 단계가 통째로 빠져 있는 것이다. 중간에 누가 끼어 있어도 알 방법이 없고, 그 상대에게 비밀번호를 그대로 넘긴다.

폐쇄된 사내망이라 실질적 위험은 낮았지만, 넣는 비용도 낮다.

```c++
const char* fp = libssh2_hostkey_hash(session, LIBSSH2_HOSTKEY_HASH_SHA1);
if (!fp) return false;

// 처음 접속 시 저장해둔 지문과 비교
if (memcmp(fp, saved_fingerprint, 20) != 0) {
    // 서버가 바뀌었다 — 사용자에게 알리고 중단
    return false;
}
```

SHA-1은 요즘 기준으로 약하니 `LIBSSH2_HOSTKEY_HASH_SHA256`을 쓰는 게 낫다. 지문 길이가 32바이트로 바뀐다.

비밀번호가 소스에 박혀 있는 것도 그대로 두면 안 되는 부분이다. 실행 파일에서 문자열만 뽑아도 나온다. 설정 파일로 빼거나, 가능하면 공개키 인증으로 바꾸는 게 맞다. libssh2는 `libssh2_userauth_publickey_fromfile`을 제공한다.

## 파일로 안 내려도 된다

XML을 로컬 디스크에 저장하고 다시 읽는 구조인데, 크기가 몇 KB밖에 안 되니 메모리에서 바로 파싱해도 된다.

```c++
std::string read_remote(LIBSSH2_SFTP_HANDLE* h)
{
    std::string data;
    char buf[4096];
    for (;;) {
        ssize_t n = libssh2_sftp_read(h, buf, sizeof(buf));
        if (n > 0)      data.append(buf, n);
        else if (n == 0) break;
        else if (n == LIBSSH2_ERROR_EAGAIN) continue;   // 논블로킹이면 재시도
        else            return {};
    }
    return data;
}

// pugixml 은 메모리 버퍼를 바로 받는다
pugi::xml_document doc;
pugi::xml_parse_result r = doc.load_buffer(data.data(), data.size());
```

임시 파일이 없어지니 `./xml/` 디렉토리를 미리 만들 필요도 없고(없으면 `fopen_s`가 실패한다), 여러 인스턴스가 같은 파일명을 쓰는 문제도 없다.

`LIBSSH2_ERROR_EAGAIN` 처리를 넣어둔 건, 나중에 타임아웃을 걸려고 논블로킹 모드로 바꿀 가능성 때문이다. 원 코드는 `amount < 0`을 전부 에러로 보는데, 논블로킹에서는 `EAGAIN`이 "지금은 데이터가 없다"는 정상 상태다.

## pugixml의 실패 검사가 항상 통과했다

```c++
pugi::xml_document CExampleDlg::loadAndParseXml(const char* xmlFilePath) {
	pugi::xml_document doc;
	pugi::xml_parse_result result = doc.load_file(xmlFilePath);
	if (!result) {
		std::cerr << "Parsing failed with description: " << result.description() << "\n";
		return {};
	}
	return doc;
}
```

```c++
pugi::xml_document doc = loadAndParseXml("./xml/test.xml");
if (!doc) {
    return { "", "" };
}
```

여기서 `if (!doc)`가 문제다.

`xml_document`는 `xml_node`를 상속하고, `xml_node::operator!`는 내부 노드 포인터가 널인지 본다. 그런데 **기본 생성된 `xml_document`도 항상 루트 노드를 가진다.** 내용이 비어 있을 뿐 노드 자체는 있다. 그러니 `!doc`는 언제나 거짓이고, 이 검사는 아무것도 안 잡는다.

함수 안에서는 `result`로 제대로 검사하고 로그도 찍는데, 반환 시점에 그 정보가 사라진다. 호출한 쪽은 파싱이 실패했는지 알 수 없고, 빈 문서에서 노드를 찾다가 "노드 없음"이라는 다른 이유의 에러를 보게 된다. 원인이 한 단계 가려진다.

성공 여부를 같이 돌려주는 게 맞다.

```c++
bool loadXml(const std::string& data, pugi::xml_document& out)
{
    pugi::xml_parse_result r = out.load_buffer(data.data(), data.size());
    if (!r) {
        Log("XML 파싱 실패: %s (offset %td)", r.description(), r.offset);
        return false;
    }
    return true;
}
```

`r.offset`이 유용하다. 파일 어디서 깨졌는지 바이트 위치를 알려줘서, 보드가 파일을 쓰다 말았을 때 그걸 바로 확인할 수 있었다.

문서가 비었는지 보고 싶으면 `doc.first_child()`가 있는지 확인한다.

## 노드 값 검증

```c++
std::string CExampleDlg::findAndValidateNode(pugi::xml_document& doc, const char* nodeName) {
	pugi::xml_node node = doc.child("Root").child(nodeName);

	if (!node) {
		std::cerr << nodeName << " node not found." << std::endl;
		return "";
	}

	std::string nodeValue = node.text().get();

	try {
		if (std::stoi(nodeValue) >= 100 || std::stoi(nodeValue) <= -100) {
			std::cerr << "Invalid value for " << nodeName << ": " << nodeValue << std::endl;
			return "";
		}
	}
	catch (std::exception& e) {
		std::cerr << "Exception caught trying to convert " << nodeName << " to integer: " << e.what() << std::endl;
		return "";
	}

	return nodeValue;
}
```

여기서 `!node`는 제대로 동작한다. `xml_node`는 못 찾으면 실제로 널 노드가 되기 때문이다. `xml_document`와 달라서 헷갈렸던 부분이다.

`std::stoi`를 두 번 부르는 건 고쳤다. 예외가 두 곳에서 날 수 있고 파싱도 두 번 한다.

값을 문자열로 돌려주면서 실패도 빈 문자열로 표현하는 것도 애매했다. 값이 진짜로 빈 문자열인 경우와 구분이 안 된다. pugixml에는 기본값을 주는 API가 있어서 이쪽이 깔끔했다.

```c++
// 없거나 숫자가 아니면 기본값
int v = doc.child("Root").child(nodeName).text().as_int(INT_MIN);
if (v == INT_MIN) { /* 값 없음 */ }
```

`as_int`, `as_double`, `as_bool` 모두 기본값 인자를 받는다. 예외도 안 던진다.

## 정리하면

- 라이브러리를 붙이기 전에 라이선스를 확인한다. 시간이 지나면 멈추는 종류는 배포 뒤에 터진다
- libssh2는 소켓을 자기가 닫지 않는다. 세션과 소켓을 같이 관리하고, 세션 → 소켓 순으로 정리한다
- `libssh2_init`은 다른 호출보다 먼저 한 번, 윈도우에서는 `WSAStartup`도 필요하다
- 호스트 키를 확인하지 않으면 `ssh`가 처음 접속에서 물어보는 그 단계가 통째로 빠진 것이다
- 작은 파일은 디스크를 거치지 말고 `load_buffer`로 바로 파싱한다
- `xml_document`는 항상 루트를 가지므로 `!doc`로는 파싱 실패를 못 잡는다. `xml_parse_result`를 봐야 한다

같은 보드에 명령을 실행하는 쪽은 [SSH를 이용한 원격 명령 실행](/posts/cpp-remote-command-execution-with-ssh-windows/)에 정리했다.

## 참고

- [libssh2 API](https://www.libssh2.org/docs.html)
- [pugixml — Loading document](https://pugixml.org/docs/manual.html#loading)
