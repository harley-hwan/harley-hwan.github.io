---
title: (c++) 현재 연결된 와이파이의 SSID 검출
description: "윈도우 WLAN API의 WlanEnumInterfaces와 WlanQueryInterface를 이용해 현재 연결된 와이파이의 SSID를 C++로 검출하는 방법을 정리한다."
date: 2023-02-17 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, wifi, ssid, wlanopenhandle, wlan-enum-interfaces, wlan-query-interface, windows, wlan-intf-opcode-current-connection]
---
## 내용

```c++
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

    // Initialize the handle to the WLAN client.
    DWORD ret = WlanOpenHandle(2, NULL, &negotiatedVersion, &clientHandle);
    if (ret != ERROR_SUCCESS) {
        std::cerr << "WlanOpenHandle failed with error: " << ret << std::endl;
        return 1;
    }

    PWLAN_INTERFACE_INFO_LIST ifList = NULL;
    ret = WlanEnumInterfaces(clientHandle, NULL, &ifList);
    if (ret != ERROR_SUCCESS) {
        std::cerr << "WlanEnumInterfaces failed with error: " << ret << std::endl;
        return 1;
    }

    for (DWORD i = 0; i < ifList->dwNumberOfItems; i++) {
        PWLAN_INTERFACE_INFO pIfInfo = &ifList->InterfaceInfo[i];
        PWLAN_CONNECTION_ATTRIBUTES pConnectInfo = NULL;

        // Get the current connection attributes.
        DWORD connectInfoSize = 0;
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

        std::wcout << L"SSID: " << pConnectInfo->strProfileName << std::endl;

        WlanFreeMemory(pConnectInfo);
    }

    WlanFreeMemory(ifList);
    WlanCloseHandle(clientHandle, NULL);
    return 0;
}

```

<br/>

## 결과

![image](/assets/img/posts/cpp-detecting-current-wifi-ssid/001-219562755-0a57223c-955d-483e-8061-9f8a0e5227df.png)
