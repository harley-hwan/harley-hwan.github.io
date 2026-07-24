---
title: 현재 연결중인 WiFi 이름 확인
description: "Windows Native WiFi API(WlanOpenHandle, WlanEnumInterfaces)를 사용해 현재 연결 중인 WiFi 이름을 C++로 확인하는 방법을 정리한다."
date: 2023-02-08 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, wifi, connect, wlan, msdn]
---
- 참조: https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/nf-wlanapi-wlanopenhandle

## 내용

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
