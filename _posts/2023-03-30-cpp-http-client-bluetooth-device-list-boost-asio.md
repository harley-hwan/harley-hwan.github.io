---
title: (c++) HTTP 클라이언트 프로그램 - 블루투스 장치 목록 (Boost.Asio)
description: "c++, boost, asio, boost.asio, bluetooth, ble, bluetoothscanner"
date: 2023-03-30 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, boost, asio, boost.asio, bluetooth, ble, bluetoothscanner]
---

# Boost.Asio를 사용한 간단한 HTTP 클라이언트 (블루투스 장치 목록 스캔 및 출력)
- 최초 작성일: 2023년 3월 30일 (목)

## 목차

[TOC]

<br/>

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

### 소스 1

```c++
std::vector<std::tuple<std::wstring, LONG, CString>> ListAvailableWifiNetworks()
{
	std::vector<std::tuple<std::wstring, LONG, CString>> availableNetworks;

	DWORD negotiatedVersion;
	HANDLE clientHandle = NULL;

	// Initialize the handle to the WLAN client.
	DWORD ret = WlanOpenHandle(2, NULL, &negotiatedVersion, &clientHandle);
	if (ret != ERROR_SUCCESS) {
		std::cerr << "WlanOpenHandle failed with error: " << ret << std::endl;
		return availableNetworks;
	}

	PWLAN_INTERFACE_INFO_LIST ifList = NULL;
	ret = WlanEnumInterfaces(clientHandle, NULL, &ifList);
	if (ret != ERROR_SUCCESS) {
		std::cerr << "WlanEnumInterfaces failed with error: " << ret << std::endl;
		return availableNetworks;
	}

	for (DWORD i = 0; i < ifList->dwNumberOfItems; i++) {
		PWLAN_INTERFACE_INFO pIfInfo = &ifList->InterfaceInfo[i];

		PWLAN_BSS_LIST pBssList = NULL;
		ret = WlanGetNetworkBssList(clientHandle, &pIfInfo->InterfaceGuid, NULL, dot11_BSS_type_any, FALSE, NULL, &pBssList);
		if (ret != ERROR_SUCCESS) {
			std::cerr << "WlanGetNetworkBssList failed with error: " << ret << std::endl;
			return availableNetworks;
		}

		for (DWORD j = 0; j < pBssList->dwNumberOfItems; j++) {
			PWLAN_BSS_ENTRY pBssEntry = &pBssList->wlanBssEntries[j];
			DOT11_SSID ssid = pBssEntry->dot11Ssid;

			std::wstring networkName(reinterpret_cast<const wchar_t*>(ssid.ucSSID), ssid.uSSIDLength);

			LONG rssi = pBssEntry->lRssi; // RSSI 정보

			ULARGE_INTEGER ftSystemTime1970;
			ftSystemTime1970.QuadPart = 116444736000000000ULL; // 1970년 1월 1일 00:00:00 UTC와의 차이

			ULARGE_INTEGER ftTimestamp;
			ftTimestamp.QuadPart = ftSystemTime1970.QuadPart + (pBssEntry->ullHostTimestamp * 10); // 100ns 단위로 변환

			FILETIME ftFirstAvailableTime;
			ftFirstAvailableTime.dwHighDateTime = ftTimestamp.HighPart;
			ftFirstAvailableTime.dwLowDateTime = ftTimestamp.LowPart;

			SYSTEMTIME stFirstAvailableTime;
			FileTimeToSystemTime(&ftFirstAvailableTime, &stFirstAvailableTime);

			CString firstAvailableTime;
			firstAvailableTime.Format(_T("%02u:%02u:%02u"), stFirstAvailableTime.wHour, stFirstAvailableTime.wMinute, stFirstAvailableTime.wSecond);

			availableNetworks.push_back(std::make_tuple(networkName, rssi, firstAvailableTime));
		}
		WlanFreeMemory(pBssList);
	}

	WlanFreeMemory(ifList);
	WlanCloseHandle(clientHandle, NULL);

	return availableNetworks;
}

```



