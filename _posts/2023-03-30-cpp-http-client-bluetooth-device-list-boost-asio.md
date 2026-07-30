---
title: "(C++) HTTP 클라이언트 프로그램 - 블루투스 장치 목록 (Boost.Asio)"
description: "블루투스 스캔은 보드에 맡기고 PC는 HTTP로 결과만 받아오는 구조를 Boost.Asio로 짰다. 동기 API에 타임아웃이 없다는 점과 Connection: close에 기대는 방식의 한계를 정리했다."
date: 2023-03-30 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, boost, asio, boost-asio, bluetooth, ble, bluetoothscanner, http]
---
## 왜 이 구조로 갔나

주변 블루투스 장치 목록을 검사 프로그램에서 보여줘야 했다. 그런데 윈도우에서 BLE 스캔을 직접 하려니 WinRT를 끌어와야 하고 SDK 버전도 맞춰야 해서 손이 많이 갔다.

보드에는 이미 리눅스 블루투스 스택이 올라가 있고 스캔은 명령 한 줄이면 된다. 그래서 스캔은 보드가 하고, 결과를 HTTP로 내주고, PC는 그걸 받아서 화면에 뿌리는 구조로 나눴다. 나중에 스캔 방식을 바꿔도 PC 쪽 코드는 안 건드려도 된다는 점도 마음에 들었다.

그러니까 이 글의 코드는 **이름은 BluetoothScanner인데 실제로는 HTTP 클라이언트**다. 블루투스 API를 한 줄도 안 쓴다. 나중에 [윈도우에서 직접 BLE를 스캔하는 쪽](/posts/cpp-mfc-bluetooth-device-scan-and-listview/)으로 다시 갔는데, 그때도 이 클래스 이름을 그대로 둔 게 헷갈리는 원인이 됐다. 이름은 하는 일을 따라가야 한다.

## 코드

```c++
#include <boost/asio.hpp>
#include <iostream>
#include <string>

using boost::asio::ip::tcp;

class BluetoothScanner
{
public:
	BluetoothScanner(boost::asio::io_context& io_context)
		: io_context_(io_context), socket_(io_context)
	{
	}

	void start_scan()
	{
		// 로컬호스트의 2323 포트로 연결을 시도한다.
		tcp::resolver resolver(io_context_);
		boost::asio::connect(socket_, resolver.resolve("127.0.0.1", "2323"));

		// HTTP GET 요청을 구성하여 서버에 보낸다.
		std::string request =
			"GET /devices HTTP/1.1\r\n"
			"Host: 127.0.0.1:2323\r\n"
			"Accept: */*\r\n"
			"Connection: close\r\n\r\n";
		boost::asio::write(socket_, boost::asio::buffer(request));

		// 상태 라인을 읽어 응답을 확인한다.
		boost::asio::streambuf response;
		boost::asio::read_until(socket_, response, "\r\n");

		std::istream response_stream(&response);
		std::string http_version;
		unsigned int status_code;
		response_stream >> http_version >> status_code;

		std::string status_message;
		std::getline(response_stream, status_message);

		if (!response_stream || http_version.substr(0, 5) != "HTTP/") {
			std::cerr << "Invalid response" << std::endl;
			return;
		}
		if (status_code != 200) {
			std::cerr << "Response returned with status code " << status_code << std::endl;
			return;
		}

		// 응답 헤더를 읽어 넘긴다.
		boost::asio::read_until(socket_, response, "\r\n\r\n");
		std::string header;
		while (std::getline(response_stream, header) && header != "\r") {
		}

		// 응답 본문에 담긴 블루투스 장치 목록을 출력한다.
		if (response.size() > 0) {
			std::cout << &response;
		}

		boost::system::error_code error;
		while (boost::asio::read(socket_, response, boost::asio::transfer_at_least(1), error)) {
			std::cout << &response;
		}
		if (error != boost::asio::error::eof) {
			throw boost::system::system_error(error);
		}
	}

private:
	boost::asio::io_context& io_context_;
	tcp::socket socket_;
};

int main()
{
	try {
		boost::asio::io_context io_context;

		BluetoothScanner scanner(io_context);
		scanner.start_scan();
	}
	catch (std::exception& e) {
		std::cerr << "Error: " << e.what() << std::endl;
	}

	return 0;
}
```

흐름은 단순하다. 소켓을 열고, GET 요청 문자열을 그대로 밀어 넣고, 상태 줄을 읽어 200인지 확인하고, 헤더를 빈 줄까지 버리고, 나머지를 본문으로 읽는다.

`read_until(socket_, response, "\r\n\r\n")` 다음에 `if (response.size() > 0)`으로 남은 걸 먼저 출력하는 부분이 있는데, 이게 필요한 이유가 있다. `read_until`은 찾는 구분자까지만 읽는 게 아니라 **읽을 수 있는 만큼 읽어서** 버퍼에 넣는다. 헤더 끝을 찾은 시점에 본문의 앞부분이 이미 버퍼에 들어와 있을 수 있다. 그걸 먼저 꺼내지 않고 바로 소켓에서 더 읽으면 앞부분이 유실된다.

## Connection: close에 기대는 방식

이 코드는 본문의 끝을 **서버가 연결을 끊는 것**으로 판단한다. 그래서 요청에 `Connection: close`를 넣었다.

HTTP/1.1은 기본이 keep-alive라, 서버가 이 헤더를 무시하고 연결을 유지하면 마지막 `read` 루프가 영원히 안 끝난다. 내가 만든 서버라 동작을 알고 있어서 문제가 없었지만, 남이 만든 엔드포인트를 상대할 때는 쓸 수 없는 방식이다.

제대로 하려면 `Content-Length`를 읽어서 그만큼만 받거나, `Transfer-Encoding: chunked`면 청크 단위로 파싱해야 한다. 헤더를 버리지 않고 파싱하는 코드가 필요해진다.

```c++
// 헤더를 버리는 대신 파싱
std::string header;
size_t content_length = 0;
while (std::getline(response_stream, header) && header != "\r") {
    if (header.rfind("Content-Length:", 0) == 0)
        content_length = std::stoul(header.substr(15));
}
```

여기까지 오면 직접 짤 이유가 별로 없다. Boost.Beast가 HTTP 파싱을 다 해준다.

```c++
#include <boost/beast/http.hpp>
namespace http = boost::beast::http;

http::request<http::empty_body> req{http::verb::get, "/devices", 11};
req.set(http::field::host, "127.0.0.1:2323");
http::write(stream, req);

boost::beast::flat_buffer buffer;
http::response<http::string_body> res;
http::read(stream, buffer, res);      // Content-Length, chunked 다 처리된다

std::cout << res.body();
```

이걸 알고 나서 Beast로 옮겼다. 코드가 절반 이하로 줄고, 청크 응답이나 리다이렉트 같은 걸 신경 안 써도 된다.

## 동기 API에는 타임아웃이 없다

이게 실제로 제일 아팠던 부분이다.

`boost::asio::connect`와 `read`의 동기 버전에는 타임아웃 인자가 없다. 보드가 응답을 안 하면 프로그램이 그 자리에서 멈춘다. GUI 프로그램에서 이 함수를 UI 스레드에서 부르면 창이 통째로 얼어붙는다.

보드를 껐다 켜는 사이에 검사 프로그램이 스캔 버튼을 누른 상태였고, 프로그램이 응답 없음으로 표시된 채 몇 분을 기다렸다. 작업자는 프로그램이 죽은 줄 알고 강제 종료했다.

Asio에서 타임아웃을 걸려면 비동기 연산과 타이머를 같이 써야 한다.

```c++
boost::asio::steady_timer timer(io_context);
timer.expires_after(std::chrono::seconds(3));
timer.async_wait([&](const boost::system::error_code& ec) {
    if (!ec) socket_.close();          // 시간이 다 되면 소켓을 닫아 연산을 깨운다
});

boost::asio::async_connect(socket_, endpoints,
    [&](const boost::system::error_code& ec, const tcp::endpoint&) {
        timer.cancel();
        // ...
    });

io_context.run();
```

타이머가 먼저 터지면 소켓을 닫고, 그러면 진행 중인 비동기 연산이 `operation_aborted`로 깨어난다. Boost 1.74 이후에는 `socket.expires_after` 형태를 지원하는 래퍼(`beast::tcp_stream`)가 있어서 훨씬 간단해졌다.

간단하게 넘길 거면 소켓 옵션으로도 어느 정도 된다.

```c++
// 수신 타임아웃 (플랫폼 의존)
#ifdef _WIN32
    DWORD ms = 3000;
    setsockopt(socket_.native_handle(), SOL_SOCKET, SO_RCVTIMEO, (char*)&ms, sizeof(ms));
#else
    timeval tv{3, 0};
    setsockopt(socket_.native_handle(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
#endif
```

윈도우는 밀리초 `DWORD`, POSIX는 `timeval`이라 타입이 다르다. 그리고 이건 `read`에만 걸리고 `connect`에는 안 걸린다. 상대가 아예 없는 IP면 여전히 오래 기다린다.

## Boost 설정에서 걸린 것들

Boost를 처음 붙이면 헤더 경로부터 걸린다. Visual Studio 기준으로 프로젝트 속성 → C/C++ → 일반 → 추가 포함 디렉터리에 Boost 루트를 넣어야 한다. 예를 들어 `C:\boost_1_77_0`에 풀었으면 그 경로를 넣는다.

몇 가지 더 있었다.

**Boost.Asio는 헤더 온리지만 완전히는 아니다.** 1.69 이전 버전은 `Boost.System`을 링크해야 한다. `boost::system::error_code` 관련 심볼이 없다고 나오면 이 경우다. 요즘 버전은 헤더 온리로 동작한다.

**윈도우에서 `ws2_32.lib` 링크가 필요하다.** Asio가 알아서 `#pragma comment(lib, ...)`를 넣어주는 경우가 많지만, 안 될 때는 직접 넣는다.

**`io_service`가 아니라 `io_context`다.** Boost 1.66에서 이름이 바뀌었다. 인터넷의 예제는 대부분 옛날 이름이라 그대로 붙여넣으면 컴파일이 안 된다. `resolver.resolve("127.0.0.1", "2323")`처럼 호스트와 서비스를 따로 넘기는 형태도 1.66부터다. 그 전에는 `tcp::resolver::query`를 만들어야 했다.

**`WIN32_LEAN_AND_MEAN` 충돌.** MFC 프로젝트에 Asio를 넣으니 `winsock.h`와 `winsock2.h`가 중복 포함되어 재정의 에러가 났다. `<boost/asio.hpp>`를 `<windows.h>`보다 먼저 포함하거나, 미리 `WIN32_LEAN_AND_MEAN`을 정의하면 해결된다. stdafx.h 맨 위에 넣어두는 게 제일 확실했다.

## 상태 코드 검사가 200만 통과시킨다

```c++
if (status_code != 200) { ... return; }
```

리다이렉트(301, 302)나 부분 응답(206)이 오면 에러로 처리한다. 내가 만든 서버라 200만 오지만, 나중에 앞단에 프록시가 붙으면 깨질 수 있는 부분이다. 최소한 3xx는 로그에 다르게 남기는 게 나았다.

`http_version.substr(0, 5) != "HTTP/"` 검사도 응답이 5글자보다 짧으면 `substr`이 짧은 문자열을 돌려주니 실패 처리는 되는데, 그 앞의 `response_stream >> status_code`가 이미 실패 상태여서 `status_code`가 초기화되지 않은 값일 수 있다. `!response_stream` 검사가 앞에 있으면 더 안전했다.

## 정리하면

- 이름은 하는 일을 따라가야 한다. HTTP 클라이언트를 BluetoothScanner라고 부르면 나중에 자기가 헷갈린다
- `read_until`은 구분자까지만 읽지 않는다. 버퍼에 남은 걸 먼저 꺼내야 본문 앞부분이 안 날아간다
- `Connection: close`에 기대는 본문 읽기는 상대 서버가 협조할 때만 동작한다. `Content-Length`나 chunked를 처리해야 한다
- Asio의 동기 API에는 타임아웃이 없다. 비동기 + `steady_timer` 조합이 필요하다
- HTTP를 직접 파싱할 거면 Boost.Beast를 먼저 보는 게 낫다

## 참고

- [Boost.Asio 문서](https://www.boost.org/doc/libs/release/doc/html/boost_asio.html)
- [Boost 다운로드](https://www.boost.org/users/download/)
