---
title: "(C++) 현재 연결중인 WiFi 이름 확인"
description: "Native WiFi API로 접속 중인 Wi-Fi 이름을 처음 뽑아본 기록. WlanGetAvailableNetworkList에서 dwIndex를 인덱스로 쓴 게 틀렸다는 걸 나중에 알았고, 연결된 항목을 어떻게 골라야 하는지까지 정리했다."
date: 2023-02-08 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, wifi, connect, wlan, msdn, wlanapi, windows]
---
## 왜 필요했나

장비가 자체 AP를 띄우고 PC가 거기에 붙어서 통신하는 구조라, 검사 프로그램을 켰을 때 **지금 붙어 있는 Wi-Fi가 장비 것이 맞는지** 먼저 확인해야 했다. 사무실 공용 AP에 붙은 채로 검사를 시작하면 통신이 안 되는데, 그 원인을 현장에서 찾느라 시간을 버리는 일이 반복됐다.

`netsh wlan show interfaces`를 돌려서 파싱하는 방법도 있지만, 출력 형식이 OS 언어와 버전에 따라 달라진다. 한국어 윈도우에서는 항목 이름이 한글이라 영문 윈도우용으로 짠 파싱이 그대로 깨진다. 그래서 Native WiFi API를 직접 쓰기로 했다.

## 처음 짠 코드

```c++
#ifndef UNICODE
#define UNICODE
#endif

#include <windows.h>
#include <wlanapi.h>
#include <objbase.h>
#include <wtypes.h>
#include <iostream>

// Need to link with Wlanapi.lib and Ole32.lib
#pragma comment(lib, "wlanapi.lib")
#pragma comment(lib, "ole32.lib")

using namespace std;

int wmain()
{
	HANDLE hClient = NULL;
	DWORD dwMaxClient = 2;
	DWORD dwCurVersion = 0;
	DWORD dwResult = 0;
	int iRet = 0;
	WCHAR GuidString[1000] = { 0 };
  
	PWLAN_INTERFACE_INFO_LIST pIfList = NULL;
	PWLAN_INTERFACE_INFO pIfInfo = NULL;
	PWLAN_AVAILABLE_NETWORK_LIST pBssList = NULL;
	PWLAN_AVAILABLE_NETWORK pBssEntry = NULL;
	wcout.imbue(locale("kor"));
	dwResult = WlanOpenHandle(dwMaxClient, NULL, &dwCurVersion, &hClient);

	if (dwResult != ERROR_SUCCESS) {
		wcout << L"WlanOpenHandle failed" << endl;
		return 1;
	}
  
	dwResult = WlanEnumInterfaces(hClient, NULL, &pIfList);

	if (dwResult != ERROR_SUCCESS){
    wcout << L"WlanEnumInterfaces failed" << endl;
    return 1;
	}

	else {
		pIfInfo = (WLAN_INTERFACE_INFO *)&pIfList->InterfaceInfo[pIfList->dwIndex];
		dwResult = WlanGetAvailableNetworkList(hClient, &pIfInfo->InterfaceGuid, 2, NULL, &pBssList);
		if (dwResult != ERROR_SUCCESS)
			wcout << L"failed" << endl;
		else {
			pBssEntry = (WLAN_AVAILABLE_NETWORK *)&pBssList->Network[pBssList->dwIndex];
			wcout << L"현재 연결중인 wifi :" << pBssEntry->strProfileName << endl;
		}
	}
	if (pBssList != NULL) {
		WlanFreeMemory(pBssList);
		pBssList = NULL;
	}
  
	if (pIfList != NULL) {
		WlanFreeMemory(pIfList);
		pIfList = NULL;
	}

	WlanCloseHandle(hClient, NULL);
	return 0;
}
```

내 노트북에서는 맞는 값이 나왔다. 그런데 다른 PC에서 돌려보니 접속하지도 않은 AP 이름이 찍혔다.

## dwIndex는 인덱스가 아니다

원인은 이 두 줄이었다.

```c++
pIfInfo  = &pIfList->InterfaceInfo[pIfList->dwIndex];
pBssEntry = &pBssList->Network[pBssList->dwIndex];
```

`WLAN_INTERFACE_INFO_LIST`와 `WLAN_AVAILABLE_NETWORK_LIST`에는 `dwNumberOfItems`와 `dwIndex`가 같이 들어 있다. 이름만 보면 `dwIndex`가 "현재 선택된 항목"처럼 읽히는데, 실제로는 시스템이 열거할 때 쓰는 커서 값이고 호출한 쪽에서 의미를 부여할 값이 아니다. 대부분 0으로 채워져서 나온다.

즉 위 코드는 사실상 `Network[0]`을 읽고 있었다. 목록의 첫 번째 항목이 우연히 연결된 AP였던 PC에서만 맞는 값이 나왔던 것이다. `WlanGetAvailableNetworkList`가 돌려주는 목록은 신호 강도나 접속 여부로 정렬되어 있다는 보장이 없다.

## 연결된 항목 고르기

같은 API 안에서 고치려면 `dwFlags`를 봐야 한다. 각 항목에 `WLAN_AVAILABLE_NETWORK_CONNECTED` 플래그가 붙어 있다.

```c++
for (DWORD i = 0; i < pBssList->dwNumberOfItems; ++i) {
    const WLAN_AVAILABLE_NETWORK& net = pBssList->Network[i];
    if (net.dwFlags & WLAN_AVAILABLE_NETWORK_CONNECTED) {
        std::wcout << L"연결됨: " << net.strProfileName << std::endl;
        break;
    }
}
```

`WLAN_AVAILABLE_NETWORK_HAS_PROFILE` 플래그도 같이 있는데, 이건 저장된 프로필이 있다는 뜻이지 연결됐다는 뜻이 아니다. 처음에 이 둘을 헷갈렸다.

인터페이스도 마찬가지로 순회해야 한다. 노트북에 USB Wi-Fi 어댑터를 하나 더 꽂으면 인터페이스가 두 개가 되고, 어느 쪽이 먼저 나올지 모른다. 연결 상태로 골라야 한다.

```c++
for (DWORD i = 0; i < pIfList->dwNumberOfItems; ++i) {
    if (pIfList->InterfaceInfo[i].isState == wlan_interface_state_connected) {
        // 이 인터페이스를 쓴다
    }
}
```

다만 지금 다시 짠다면 `WlanGetAvailableNetworkList` 자체를 안 쓴다. 이 함수는 "주변에 보이는 네트워크 목록"을 얻는 것이고, 그중에서 연결된 것을 찾는 건 돌아가는 길이다. 현재 연결 정보만 필요하면 전용 조회가 따로 있다. 그건 [현재 연결된 와이파이의 SSID 검출](/posts/cpp-detecting-current-wifi-ssid/)에 정리했다.

## 프로필 이름은 SSID가 아니다

또 하나 헷갈렸던 부분이다. `strProfileName`은 SSID와 대개 같지만 항상 같지는 않다.

- 사용자가 저장된 네트워크의 이름을 바꾸면 달라진다
- 숨김 SSID는 프로필 이름이 있어도 실제 SSID가 비어 있을 수 있다
- 그룹 정책으로 배포된 프로필은 관리자가 정한 이름을 쓴다

실제 SSID를 봐야 하면 `dot11Ssid`를 읽어야 한다.

```c++
const DOT11_SSID& ssid = net.dot11Ssid;
// ssid.ucSSID      : UCHAR[32], 널 종료가 아니다
// ssid.uSSIDLength : 실제 길이
std::string s(reinterpret_cast<const char*>(ssid.ucSSID), ssid.uSSIDLength);
```

`ucSSID`는 **널로 끝나지 않는 바이트 배열**이다. 802.11 규격상 SSID는 최대 32바이트의 임의 옥텟이라 널 문자가 안에 들어갈 수도 있다. `strlen`이나 `printf("%s")`로 다루면 뒤쪽 쓰레기까지 딸려 나온다. 길이를 같이 써야 한다.

인코딩도 정해져 있지 않다. 요즘 공유기는 대부분 UTF-8을 쓰는데 규격이 강제하는 건 아니라서, 한글 SSID가 CP949로 들어오는 경우도 있다. UTF-8로 변환을 시도해보고 실패하면 시스템 코드페이지로 재시도하는 식으로 처리한 얘기는 [Wi-Fi 검색 및 연결](/posts/cpp-windows-wifi-programming/) 쪽에 있다.

## 정리와 자원 해제

원 코드에는 새는 곳이 있다. `WlanEnumInterfaces`가 실패하면 `return 1`로 나가는데, 그 앞에서 연 `hClient`를 안 닫는다. 프로세스가 바로 끝나는 예제라 티가 안 나지만, GUI 프로그램에서 이 코드를 함수로 만들어 반복 호출하면 핸들이 쌓인다.

`WlanOpenHandle`의 첫 인자 `dwMaxClient`는 클라이언트 버전이다. `2`를 주면 Windows Vista 이후 버전으로 협상하고, `1`은 XP SP3 호환 모드다. `1`로 열면 `WLAN_AVAILABLE_NETWORK` 구조체의 일부 필드가 안 채워진다. 지금 환경에서는 `2`가 맞다.

`WlanFreeMemory`는 API가 할당한 모든 버퍼에 필요하다. `CoTaskMemFree`나 `free`가 아니다. 그래서 `ole32.lib`도 같이 링크한다.

```c++
struct WlanHandle {
    HANDLE h = nullptr;
    ~WlanHandle() { if (h) WlanCloseHandle(h, nullptr); }
};

template <class T>
struct WlanPtr {
    T* p = nullptr;
    ~WlanPtr() { if (p) WlanFreeMemory(p); }
    T* operator->() const { return p; }
};
```

이 정도만 감싸도 중간에 어디로 빠져나가든 정리가 된다. 조회 함수가 여러 개가 되면서 해제 코드를 매번 쓰는 게 번거로워져 결국 이렇게 정리했다.

## 정리하면

- `dwIndex`는 배열 인덱스가 아니다. 목록은 `dwNumberOfItems`만큼 직접 순회해야 한다
- 연결된 네트워크는 `dwFlags & WLAN_AVAILABLE_NETWORK_CONNECTED`로 고른다
- 인터페이스도 여러 개일 수 있다. `isState == wlan_interface_state_connected`로 거른다
- `strProfileName`은 SSID와 다를 수 있다. 실제 SSID는 `dot11Ssid`이고 널 종료가 아니다
- 실패 경로에서도 `WlanCloseHandle`과 `WlanFreeMemory`를 빠뜨리면 안 된다

## 참고

- [WlanOpenHandle](https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/nf-wlanapi-wlanopenhandle)
- [WLAN_AVAILABLE_NETWORK](https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/ns-wlanapi-wlan_available_network)
