---
title: "(C++) WlanAPI를 이용한 Wi-Fi MAC 주소 검출"
description: "Windows 환경에서의 Wi-Fi 연결 MAC 주소 추출"
date: 2023-02-17 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, windows, wlan, mac, network, wlanapi]
---
<br/>

## 소개
Windows 환경에서 WlanAPI를 사용하여 현재 연결된 Wi-Fi의 MAC 주소(BSSID)를 추출한다. WLAN_CONNECTION_ATTRIBUTES 구조체를 통해 AP의 MAC 주소 정보에 접근한다.

<br/>

## 구현 코드
WlanAPI를 사용하여 현재 연결된 Wi-Fi의 MAC 주소를 추출하는 구현이다.

```cpp
#include <iostream>
#include <Windows.h>
#include <wlanapi.h>
#include <objbase.h>
#include <wtypes.h>

#pragma comment(lib, "Wlanapi.lib")
#pragma comment(lib, "ole32.lib")

int main() {
    DWORD negotiatedVersion;
    HANDLE clientHandle = NULL;

    // WLAN 클라이언트 초기화
    DWORD ret = WlanOpenHandle(2, NULL, &negotiatedVersion, &clientHandle);
    if (ret != ERROR_SUCCESS) {
        std::cerr << "WlanOpenHandle failed with error: " << ret << std::endl;
        return 1;
    }

    // 인터페이스 목록 획득
    PWLAN_INTERFACE_INFO_LIST ifList = NULL;
    ret = WlanEnumInterfaces(clientHandle, NULL, &ifList);
    if (ret != ERROR_SUCCESS) {
        std::cerr << "WlanEnumInterfaces failed with error: " << ret << std::endl;
        return 1;
    }

    // 각 인터페이스의 연결 정보 처리
    for (DWORD i = 0; i < ifList->dwNumberOfItems; i++) {
        PWLAN_INTERFACE_INFO pIfInfo = &ifList->InterfaceInfo[i];
        PWLAN_CONNECTION_ATTRIBUTES pConnectInfo = NULL;
        DWORD connectInfoSize = 0;

        // 현재 연결 속성 획득
        ret = WlanQueryInterface(
            clientHandle,
            &pIfInfo->InterfaceGuid,
            wlan_intf_opcode_current_connection,
            NULL,
            &connectInfoSize,
            (PVOID*)&pConnectInfo,
            NULL);

        if (ret != ERROR_SUCCESS) {
            std::cerr << "WlanQueryInterface failed with error: " << ret << std::endl;
            continue;
        }

        // MAC 주소 출력
        std::cout << "MAC address: ";
        for (DWORD j = 0; j < sizeof(pConnectInfo->wlanAssociationAttributes.dot11Bssid); j++) {
            if (j > 0) std::cout << ":";
            printf("%02X", pConnectInfo->wlanAssociationAttributes.dot11Bssid[j]);
        }
        std::cout << std::endl;

        WlanFreeMemory(pConnectInfo);
    }

    WlanFreeMemory(ifList);
    WlanCloseHandle(clientHandle, NULL);
    return 0;
}
```

<br/>

## 주요 기능 설명

먼저 WlanOpenHandle로 WLAN 서비스에 연결한다. 버전 2를 지정해 최신 기능을 사용하고, 성공하면 클라이언트 핸들을 얻는다.

WlanEnumInterfaces는 무선 인터페이스 목록을 WLAN_INTERFACE_INFO_LIST 구조체로 돌려준다. 이 목록을 순회하면서 인터페이스별로 연결 정보를 조회한다.

연결 정보 조회에는 WlanQueryInterface를 사용한다. wlan_intf_opcode_current_connection 옵션으로 현재 연결 정보를 요청하면 WLAN_CONNECTION_ATTRIBUTES 구조체를 받는다. 이때 다섯 번째 인자에는 반환 데이터의 크기를 받을 DWORD 변수를 따로 넘겨야 한다.

MAC 주소는 wlanAssociationAttributes.dot11Bssid에 6바이트로 들어 있다. 각 바이트를 16진수로 변환하고 사이에 콜론(:)을 넣어 표준 형식으로 출력한다.

#### 실행 결과:
![MAC 주소 출력 결과](/assets/img/posts/cpp-detecting-wifi-mac-address/001-219561425-804218a4-137d-47aa-a0be-6c993f9e0ba7.png)

WlanAPI의 다른 함수들을 활용하면 네트워크 연결 상태와 관련된 상세 정보도 같은 방식으로 얻을 수 있다.
