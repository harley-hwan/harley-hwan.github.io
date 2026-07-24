---
title: (c++) HTTP 클라이언트 프로그램 - 블루투스 장치 목록 (Boost.Asio)
description: "c++, boost, asio, boost.asio, bluetooth, ble, bluetoothscanner"
date: 2023-03-30 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, boost, asio, boost-asio, bluetooth, ble, bluetoothscanner]
---
## 내용

Boost.Asio를 사용하여 간단한 HTTP 클라이언트를 구현한 것이다.

이 클라이언트는 TCP 소켓을 사용하여 로컬호스트의 2323 포트로 연결되는 서버와 통신하려고 한다.

코드의 주요 목적은 해당 서버에서 블루투스 장치 목록을 가져오는 것이다.

하지만, 실제 블루투스 장치를 스캔하는 것이 아니라, 서버에서 반환되는 블루투스 장치 목록을 읽고 출력하는 것이다.

<br/>

### 코드 구성

1. BluetoothScanner 클래스를 정의한다. 이 클래스는 Bluetooth 장치를 스캔하는 것처럼 보이지만, 실제로는 HTTP 요청을 통해 장치 목록을 가져오는 클라이언트이다.
2. BluetoothScanner 클래스의 생성자는 io_context 객체를 받아 소켓을 초기화한다.
3. start_scan() 함수는 다음 단계를 수행한다:
    1. 로컬호스트의 2323 포트로 연결을 시도한다.
    1. HTTP GET 요청을 구성하여 해당 서버에 보낸다.
    1. 서버로부터의 응답을 읽고 처리한다. 정상적인 응답이라면 (HTTP 상태 코드가 200인 경우) 응답에서 블루투스 장치 목록을 추출하여 출력한다.
4. main() 함수는 다음 단계를 수행한다:
    1. Boost.Asio io_context 객체를 생성한다.
    1. BluetoothScanner 객체를 생성하고 start_scan() 함수를 호출한다.
    1. 예외 처리를 수행합니다. 연결 문제 등으로 인한 예외가 발생할 경우 오류 메시지를 출력한다.

<br/>

이 코드는 실제 블루투스 스캔 작업을 수행하지 않는다. 대신, HTTP 요청을 통해 블루투스 장치 목록을 가져온다. 

이 코드를 사용하려면 로컬호스트의 2323 포트에서 실행되는 서버가 필요하며, 해당 서버는 블루투스 장치를 스캔하여 목록을 반환해야 한다. 

이 코드에서 발생하는 연결 문제는 서버가 실행되지 않거나 포트가 올바르지 않은 경우이다. 

실제 블루투스 장치를 스캔하려면 플랫폼별 블루투스 API를 사용하여 코드를 수정해야 한다.

<br/>

## 참고

1. Boost 라이브러리가 올바르게 설치되었는지 확인하세요. Boost 라이브러리를 다운로드하고 설치하는 방법은 다음 페이지에서 확인할 수 있습니다: https://www.boost.org/users/download/
2. 프로젝트 설정을 열고 헤더 파일 검색 경로를 확인하세요. Boost 라이브러리 헤더 파일이 있는 디렉토리를 포함하도록 경로를 업데이트해야 합니다. Visual Studio를 사용하는 경우 다음 단계를 따르세요:
	1. 솔루션 탐색기에서 프로젝트를 마우스 오른쪽 버튼으로 클릭하고, '속성'을 선택하세요.
	1. 구성 속성 -> C/C++ -> 일반으로 이동하세요.
	1. '추가 포함 디렉터리' 항목을 찾고, Boost 라이브러리 헤더 파일이 있는 디렉토리를 추가하세요. 예를 들어, Boost 라이브러리가 __C:\boost_1_77_0__ 에 설치되어 있다면, 이 디렉토리를 추가 포함 디렉터리에 추가하세요.
	1. d. 변경 사항을 저장하고 프로젝트를 다시 빌드하세요.

<br/>

<br/>

### 소스

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

