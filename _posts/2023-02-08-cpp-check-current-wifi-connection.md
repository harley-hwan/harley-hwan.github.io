---
title: 현재 연결중인 WiFi 이름 확인
description: "wifi, connect, wlan, msdn, c++, c"
date: 2023-02-08 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, wifi, connect, wlan, msdn]
---

# 현재 연결중인 WiFi 이름 확인
- 최초 작성일: 2023년 2월 8일 (수)
- 참조: https://cpp.hotexamples.com/examples/-/-/WlanOpenHandle/cpp-wlanopenhandle-function-examples.html

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
<br/>

<br/>

```c++
void KPR_system_getWifiInfo(xsMachine* the)
{
    DWORD dwResult = 0;
    HANDLE hClient = NULL;
    DWORD dwMaxClient = 2; 
    DWORD dwCurVersion = 0;
    PWLAN_INTERFACE_INFO_LIST pIfList = NULL;
    int i;
    PWLAN_INTERFACE_INFO pIfInfo = NULL;
    DWORD connectInfoSize = sizeof(WLAN_CONNECTION_ATTRIBUTES);
    PWLAN_CONNECTION_ATTRIBUTES pConnectInfo = NULL;
    WLAN_OPCODE_VALUE_TYPE opCode = wlan_opcode_value_type_invalid;
    ULONG length;
	xsVars(1);
    dwResult = WlanOpenHandle(dwMaxClient, NULL, &dwCurVersion, &hClient); 
    if (dwResult != ERROR_SUCCESS) 
    	goto bail;
	dwResult = WlanEnumInterfaces(hClient, NULL, &pIfList); 
    if (dwResult != ERROR_SUCCESS)
    	goto bail;
    for (i = 0; i < (int) pIfList->dwNumberOfItems; i++) {
		pIfInfo = (WLAN_INTERFACE_INFO *) &pIfList->InterfaceInfo[i];
   		if (pIfInfo->isState == wlan_interface_state_connected) {
			dwResult = WlanQueryInterface(hClient, &pIfInfo->InterfaceGuid,
										  wlan_intf_opcode_current_connection,
										  NULL,
										  &connectInfoSize,
										  (PVOID *) &pConnectInfo, 
										  &opCode);
			if (dwResult != ERROR_SUCCESS)
				goto bail;
			length = pConnectInfo->wlanAssociationAttributes.dot11Ssid.uSSIDLength;
			if (length > 0) {
				xsResult = xsNewInstanceOf(xsObjectPrototype);
				xsVar(0) = xsStringBuffer(NULL, length + 1);
				FskMemCopy(xsToString(xsVar(0)), pConnectInfo->wlanAssociationAttributes.dot11Ssid.ucSSID, length);
				xsSet(xsResult, xsID("SSID"), xsVar(0));
			}
   			break;
   		}
   	}
bail:
    if (pConnectInfo != NULL) {
        WlanFreeMemory(pConnectInfo);
        pConnectInfo = NULL;
    }
    if (pIfList != NULL) {
        WlanFreeMemory(pIfList);
        pIfList = NULL;
    }
    if (hClient != NULL) {
        WlanCloseHandle(hClient, NULL);
        hClient = NULL;
    }
}
```
