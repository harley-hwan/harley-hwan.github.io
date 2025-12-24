---
title: "(C++) WlanAPI를 이용한 Wi-Fi MAC 주소 검출"
description: ""Windows 환경에서의 Wi-Fi 연결 MAC 주소 추출""
date: 2023-02-17 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, windows, wlan, mac, network, wlanapi]
---

# WlanAPI를 이용한 Wi-Fi MAC 주소 검출
- 최초 작성일: 2023년 2월 17일 (금)

<br/>

## 목차
1. [소개](#소개)
2. [구현 코드](#구현-코드)
3. [주요 기능 설명](#주요-기능-설명)

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

        // 현재 연결 속성 획득
        ret = WlanQueryInterface(
            clientHandle,
            &pIfInfo->InterfaceGuid,
            wlan_intf_opcode_current_connection,
            NULL,
            (PDWORD)&pConnectInfo,
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

1. **WLAN 클라이언트 초기화**
   - WlanOpenHandle 함수로 WLAN 서비스에 연결한다
   - 버전 2를 지정하여 최신 기능을 사용한다
   - 성공 시 클라이언트 핸들을 반환한다

2. **인터페이스 열거**
   - WlanEnumInterfaces로 무선 인터페이스 목록을 가져온다
   - WLAN_INTERFACE_INFO_LIST 구조체에 정보를 저장한다
   - 각 인터페이스에 대해 순차적으로 처리한다

3. **연결 정보 획득**
   - WlanQueryInterface로 현재 연결 상태를 조회한다
   - wlan_intf_opcode_current_connection 옵션으로 현재 연결 정보를 요청한다
   - WLAN_CONNECTION_ATTRIBUTES 구조체로 정보를 받는다

4. **MAC 주소 추출**
   - wlanAssociationAttributes.dot11Bssid에서 MAC 주소를 읽는다
   - 6바이트 길이의 MAC 주소를 16진수 형태로 변환한다
   - 각 바이트 사이에 콜론(:)을 삽입하여 표준 형식으로 출력한다

#### 실행 결과:
![MAC 주소 출력 결과](https://user-images.githubusercontent.com/68185569/219561425-804218a4-137d-47aa-a0be-6c993f9e0ba7.png)

이 구현을 통해 현재 연결된 Wi-Fi AP의 MAC 주소를 쉽게 확인할 수 있다. WlanAPI의 다양한 함수들을 활용하여 네트워크 연결 상태와 관련된 상세 정보를 획득할 수 있다.
