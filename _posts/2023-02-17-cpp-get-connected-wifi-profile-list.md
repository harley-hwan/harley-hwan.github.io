---
title: "(C++) Windows WLAN API를 이용한 WiFi 프로필 검출"
description: "현재 연결된 WiFi 사용자 프로필 정보 추출"
date: 2023-02-17 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, windows, wlan, api, profile, network]
---

# Windows WLAN API를 이용한 WiFi 프로필 검출
- 최초 작성일: 2023년 2월 17일 (금)

<br/>

## 소개
시스템 커맨드 "netsh wlan show profiles"의 기능을 프로그래밍 방식으로 구현한다. WLAN API를 사용하여 현재 연결된 Wi-Fi와 일치하는 사용자 프로필을 검출한다.

<br/>

## 기본 구현
WlanAPI를 사용하여 WiFi 프로필을 검출하는 기본 구현이다.

```cpp
#include <iostream>
#include <Windows.h>
#include <wlanapi.h>
#include <objbase.h>
#include <wtypes.h>
#include <string>
#include <vector>

#pragma comment(lib, "Wlanapi.lib")
#pragma comment(lib, "ole32.lib")

std::wstring ConvertWCharToString(const WCHAR* wstr) {
    std::wstring str(wstr);
    return str;
}

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

    // 각 인터페이스별 처리
    for (DWORD i = 0; i < ifList->dwNumberOfItems; i++) {
        PWLAN_INTERFACE_INFO pIfInfo = &ifList->InterfaceInfo[i];
        PWLAN_CONNECTION_ATTRIBUTES pConnectInfo = NULL;

        // 현재 연결 정보 획득
        ret = WlanQueryInterface(clientHandle, &pIfInfo->InterfaceGuid, 
            wlan_intf_opcode_current_connection, NULL,
            (PDWORD)&pConnectInfo, (PVOID)&pConnectInfo, NULL);
        if (ret != ERROR_SUCCESS) {
            std::cerr << "WlanQueryInterface failed with error: " << ret << std::endl;
            continue;
        }

        // 프로필 정보 출력
        std::wcout << "Currently connected to: " 
                   << ConvertWCharToString(pConnectInfo->strProfileName) << std::endl;
        std::wcout << "Other profiles available: " << std::endl;

        // 프로필 목록 획득
        PWLAN_PROFILE_INFO_LIST profileList = NULL;
        ret = WlanGetProfileList(clientHandle, &pIfInfo->InterfaceGuid, NULL, &profileList);
        if (ret != ERROR_SUCCESS) {
            std::cerr << "WlanGetProfileList failed with error: " << ret << std::endl;
            continue;
        }

        // 프로필 목록 처리
        for (DWORD j = 0; j < profileList->dwNumberOfItems; j++) {
            PWLAN_PROFILE_INFO profileInfo = &profileList->ProfileInfo[j];
            std::wstring profileName = ConvertWCharToString(profileInfo->strProfileName);

            if (profileName != ConvertWCharToString(pConnectInfo->strProfileName)) {
                std::wcout << "- " << profileName << std::endl;
            }
        }

        // 메모리 해제
        WlanFreeMemory(pConnectInfo);
        WlanFreeMemory(profileList);
    }

    // 정리
    WlanFreeMemory(ifList);
    WlanCloseHandle(clientHandle, NULL);
    return 0;
}
```

#### 구현 설명:
1. **초기화 및 설정**
   - WlanOpenHandle로 WLAN 클라이언트를 초기화한다
   - WlanEnumInterfaces로 무선 인터페이스 목록을 가져온다

2. **연결 정보 획득**
   - WlanQueryInterface로 현재 연결 상태를 확인한다
   - WLAN_CONNECTION_ATTRIBUTES 구조체로 정보를 저장한다

3. **프로필 처리**
   - WlanGetProfileList로 모든 프로필을 가져온다
   - 현재 연결된 프로필과 다른 프로필을 구분하여 출력한다

#### 실행 결과:
![기본 구현 결과](https://user-images.githubusercontent.com/68185569/219573236-74c8eccc-7a33-4673-a126-c28e20bdaaa5.png)

<br/>

## 문제 해결 및 개선
WlanQueryInterface 함수 호출 시 발생하는 오류를 수정한 개선된 구현이다.

```cpp
// 수정된 WlanQueryInterface 호출
ret = WlanQueryInterface(
    clientHandle,
    &pIfInfo->InterfaceGuid,
    wlan_intf_opcode_current_connection,
    NULL,
    (PDWORD)&pConnectInfo,
    (PVOID*)&pConnectInfo,
    NULL);
```

#### 주요 수정사항:
1. **매개변수 타입 수정**
   - (PVOID)&pConnectInfo를 (PVOID*)&pConnectInfo로 수정
   - 포인터의 포인터로 올바르게 캐스팅

2. **에러 처리 개선**
   - 정확한 에러 코드 확인이 가능
   - 명확한 에러 메시지 출력

3. **문자열 출력 방식 변경**
   - std::cout에서 std::wcout으로 변경
   - 유니코드 문자열 올바르게 처리

<br/>

## 특정 프로필 검출
특정 문자열로 시작하는 프로필만 선택적으로 검출하는 구현이다.

```cpp
for (DWORD j = 0; j < pProfileList->dwNumberOfItems; j++) {
    PWLAN_PROFILE_INFO pProfileInfo = &pProfileList->ProfileInfo[j];
    std::wstring profileName = ConvertWCharToString(pProfileInfo->strProfileName);
    if (profileName == connectedProfileName) {
        std::wcout << "Matched connected WiFi profile: " << profileName << std::endl;
        // "VISION"으로 시작하는 프로필 선택
        if (profileName.compare(0, 6, L"VISION") == 0) {
            std::wcout << "Selected profile: " << profileName << std::endl;
        }
    }    
}
```

#### 구현 특징:
1. **프로필 필터링**
   - compare 함수로 문자열 시작 부분 비교
   - 특정 접두사를 가진 프로필만 선택

2. **정보 출력**
   - 매칭된 프로필 정보 출력
   - 선택된 프로필 별도 표시

#### 실행 결과:
![선택적 프로필 검출 결과](https://user-images.githubusercontent.com/68185569/219586052-a188aa65-f17a-44b0-bef6-bf65ea401082.png)

이 구현을 통해 Windows 환경에서 Wi-Fi 프로필을 효과적으로 검출하고 관리할 수 있다. WLAN API의 다양한 함수들을 활용하여 현재 연결 상태 확인, 프로필 목록 획득, 특정 프로필 선택 등의 기능을 구현했다.
