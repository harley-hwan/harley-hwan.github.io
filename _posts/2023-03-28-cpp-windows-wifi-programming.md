---
title: "(C++) WlanAPI를 이용한 Wi-Fi 검색 및 연결 기능 구현"
description: "Windows 환경에서 Wi-Fi 네트워크 검색과 연결하기"
date: 2023-03-28 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, programming, wifi, wlanapi, windows]
---
<br/>

## 소개
Windows에서는 WlanAPI를 통해 Wi-Fi 네트워크 관련 기능을 프로그래밍 방식으로 제어할 수 있다. 

이 문서에서는 주변의 Wi-Fi 네트워크를 검색하고 선택한 네트워크에 연결하는 기능의 구현 방법을 자세히 알아보겠다. 

특히 "WAVE"로 시작하는 SSID를 가진 네트워크만을 대상으로 하는 특수한 요구사항을 반영한 구현 방법을 소개한다.

<br/>

## Wi-Fi 검색 기능

### 스캔 버튼 이벤트 처리
Wi-Fi 스캔 버튼 클릭 시 실행되는 함수로, 사용자 인터페이스와 Wi-Fi 스캔 로직을 연결한다.

```cpp
void CWifiManagerDlg::OnBnClickedButtonWifiScan()
{
	std::vector<std::tuple<CString, LONG, CString>> v_Wifilist;
	m_lcWifiList.DeleteAllItems();

	v_Wifilist = ListAvailableWifiNetworks();

	// RSSI 값 기준으로 내림차순 정렬
	std::sort(v_Wifilist.begin(), v_Wifilist.end(),
		[](const auto& a, const auto& b) {
			return std::get<1>(a) > std::get<1>(b);
		});

	int nIndex = 0;
	for (const auto& item : v_Wifilist) {
		CString ssid, listItem;
		LONG rssi;
		CString linkTime;
		std::tie(ssid, rssi, linkTime) = item;

		// WAVE로 시작하는 SSID만 리스트에 추가
		if (ssid.Find(_T("WAVE")) == 0)
		{
			listItem.Format(_T("%s - RSSI: %d - First Connect: %s"),
				ssid, rssi, linkTime);
			m_lcWifiList.InsertItem(nIndex, listItem);
			nIndex++;
		}
	}
}

```

각 네트워크의 SSID, 신호 강도, 첫 연결 시간을 `std::tuple<CString, LONG, CString>`로 묶어 다루며, 스캔 전에 기존 리스트 항목을 모두 지워 새 결과를 표시할 준비를 한다. 실제 스캔은 `ListAvailableWifiNetworks()`가 WlanAPI를 통해 수행하고, 결과는 람다 표현식으로 RSSI 기준 내림차순 정렬해 신호가 강한 네트워크를 쉽게 식별할 수 있게 한다. 마지막으로 "WAVE" 접두사를 가진 SSID만 골라 신호 강도, 첫 연결 시간과 함께 포맷팅해 리스트에 추가한다.

### Wi-Fi 목록 스캔 구현
실제 Wi-Fi 스캔을 수행하는 핵심 함수이다.

```cpp
std::vector<std::tuple<CString, LONG, CString>> CWifiManagerDlg::ListAvailableWifiNetworks()
{
	std::vector<std::tuple<CString, LONG, CString>> availableNetworks;
	DWORD negotiatedVersion;
	HANDLE clientHandle = NULL;

	DWORD ret = WlanOpenHandle(2, NULL, &negotiatedVersion, &clientHandle);
	if (ret != ERROR_SUCCESS) {
		return availableNetworks;
	}

	PWLAN_INTERFACE_INFO_LIST ifList = NULL;
	ret = WlanEnumInterfaces(clientHandle, NULL, &ifList);
	if (ret != ERROR_SUCCESS) {
		WlanCloseHandle(clientHandle, NULL);
		return availableNetworks;
	}

	for (DWORD i = 0; i < ifList->dwNumberOfItems; i++) {
		PWLAN_INTERFACE_INFO pIfInfo = &ifList->InterfaceInfo[i];
		PWLAN_BSS_LIST pBssList = NULL;
		ret = WlanGetNetworkBssList(clientHandle, &pIfInfo->InterfaceGuid, NULL,
			dot11_BSS_type_any, FALSE, NULL, &pBssList);

		if (ret != ERROR_SUCCESS) {
			continue;
		}

		for (DWORD j = 0; j < pBssList->dwNumberOfItems; j++) {
			PWLAN_BSS_ENTRY pBssEntry = &pBssList->wlanBssEntries[j];
			DOT11_SSID ssid = pBssEntry->dot11Ssid;
			std::wstring networkName = ConvertSSID(ssid.ucSSID, ssid.uSSIDLength);
			LONG rssi = pBssEntry->lRssi;

			ULARGE_INTEGER ftSystemTime1970;
			ftSystemTime1970.QuadPart = 116444736000000000ULL;
			ULARGE_INTEGER ftTimestamp;
			ftTimestamp.QuadPart = ftSystemTime1970.QuadPart + (pBssEntry->ullHostTimestamp * 10);

			FILETIME ftFirstAvailableTime;
			ftFirstAvailableTime.dwHighDateTime = ftTimestamp.HighPart;
			ftFirstAvailableTime.dwLowDateTime = ftTimestamp.LowPart;

			SYSTEMTIME stFirstAvailableTime;
			FileTimeToSystemTime(&ftFirstAvailableTime, &stFirstAvailableTime);

			CString firstAvailableTime;
			firstAvailableTime.Format(_T("%02u:%02u:%02u"),
				stFirstAvailableTime.wHour,
				stFirstAvailableTime.wMinute,
				stFirstAvailableTime.wSecond);

			CStringW networkNameW = CStringW(networkName.c_str());
			CString networkNameT = CString(networkNameW);
			availableNetworks.push_back(std::make_tuple(networkNameT, rssi, firstAvailableTime));
		}
		WlanFreeMemory(pBssList);
	}

	WlanFreeMemory(ifList);
	WlanCloseHandle(clientHandle, NULL);
	return availableNetworks;
}
```

`WlanOpenHandle`에 버전 2를 지정해 클라이언트 핸들을 열고, `WlanEnumInterfaces`로 시스템의 모든 무선 인터페이스(노트북 내장 Wi-Fi, 외장 어댑터 등)를 열거한다. 각 인터페이스마다 `WlanGetNetworkBssList`를 호출해 BSS(Basic Service Set) 단위로 네트워크 세부 정보를 얻는다. 호스트 타임스탬프는 1970년 기준 시간으로 환산한 뒤 시:분:초 형식으로 포맷팅한다.

<br/>

## Wi-Fi 연결 기능

### 연결 버튼 이벤트 처리
사용자가 선택한 Wi-Fi 네트워크에 연결을 시도하는 함수이다.

```cpp
void CWifiManagerDlg::OnBnClickedButtonWifiConnect()
{
	POSITION pos = m_lcWifiList.GetFirstSelectedItemPosition();
	if (pos != NULL) {
		int selectedIndex = m_lcWifiList.GetNextSelectedItem(pos);
		CString selectedNetwork = m_lcWifiList.GetItemText(selectedIndex, 0);

		// SSID 부분만 추출 (SSID - RSSI: XX 형식에서)
		std::wregex ssidPattern(L"^([^ ]+)");
		std::wsmatch match;
		std::wstring selectedNetworkW = selectedNetwork.GetString();
		std::regex_search(selectedNetworkW, match, ssidPattern);
		std::wstring networkName = match.str(1);
		std::wstring password = L"wave1234";  // 기본 비밀번호

		if (ConnectToSelectedWifi(networkName, password)) {
			AfxMessageBox(_T("Wi-Fi에 연결되었습니다!"));

			// 윈도우 타이틀 업데이트
			CString windowTitle;
			windowTitle.Format(_T("FTP Client - Connected to %s"),
				CString(WStringToString(networkName).c_str()));
			this->SetWindowText(windowTitle);
		}
		else {
			AfxMessageBox(_T("Wi-Fi 연결에 실패했습니다."));
		}
	}
	else {
		AfxMessageBox(_T("선택된 Wi-Fi가 없습니다."));
	}
}
```

리스트에서 선택된 항목이 있는지 먼저 확인하고, 없으면 사용자에게 알린다. 리스트 항목은 "SSID - RSSI: XX" 형식이므로 정규식으로 공백 전까지의 문자열만 추출해 네트워크 이름으로 사용한다. 연결에는 기본 비밀번호("wave1234")를 쓰고, 성공하면 윈도우 타이틀을 갱신하며 성공/실패 여부를 메시지 박스로 알린다.

### Wi-Fi 연결 구현
XML 프로파일을 생성하고 실제 연결을 수행하는 함수이다.

```cpp
bool CWifiManagerDlg::ConnectToSelectedWifi(const std::wstring& networkName, const std::wstring& password)
{
	std::string name(networkName.begin(), networkName.end());
	std::string pass(password.begin(), password.end());
	std::string fileName = "myWlan.xml";

	std::ofstream xmlFile;
	xmlFile.open(fileName.c_str());
	if (!xmlFile.is_open()) {
		return false;
	}

	// XML 파일 작성
	xmlFile << "<?xml version=\"1.0\"?>\n";
	xmlFile << "<WLANProfile xmlns=\"http://www.microsoft.com/networking/WLAN/profile/v1\">\n";
	xmlFile << "<name>" << name << "</name>\n";
	xmlFile << "<SSIDConfig>\n<SSID>\n<hex>";
	for (int i = 0; i < name.length(); i++)
		xmlFile << std::hex << (int)name.at(i);
	xmlFile << "</hex>\n<name>" << name << "</name>\n</SSID>\n</SSIDConfig>\n";
	xmlFile << "<connectionType>ESS</connectionType>\n";
	xmlFile << "<connectionMode>auto</connectionMode>\n<MSM>\n<security>\n";
	xmlFile << "<authEncryption>\n<authentication>WPA2PSK</authentication>\n";
	xmlFile << "<encryption>AES</encryption>\n<useOneX>false</useOneX>\n";
	xmlFile << "</authEncryption>\n<sharedKey>\n<keyType>passPhrase</keyType>\n";
	xmlFile << "<protected>false</protected>\n<keyMaterial>" << pass << "</keyMaterial>\n";
	xmlFile << "</sharedKey>\n</security>\n</MSM>\n";
	xmlFile << "<MacRandomization xmlns=\"http://www.microsoft.com/networking/WLAN/profile/v3\">\n";
	xmlFile << "<enableRandomization>false</enableRandomization>\n</MacRandomization>\n";
	xmlFile << "</WLANProfile>";
	xmlFile.close();

	// 시스템 프로파일에 XML 파일 추가
	std::string command = "netsh wlan add profile filename=" + fileName;
	if (system(command.c_str()) != 0) {
		return false;
	}

	// 네트워크 연결
	command = "netsh wlan connect name=" + name;
	if (system(command.c_str()) == 0) {
		return true;
	}

	return false;
}
```

WLANProfile 형식의 XML 문서를 만들면서 SSID 정보를 일반 텍스트와 16진수 형태로 모두 넣고, WPA2-PSK 인증과 AES 암호화를 지정한다. connectionType은 ESS(Extended Service Set), connectionMode는 자동 연결로 설정하고 MAC 무작위화는 비활성화한다. 이렇게 작성한 프로파일을 netsh 명령어로 시스템에 추가한 뒤, 다시 netsh로 해당 네트워크에 연결을 시도한다.

<br/>

## 유틸리티 함수들
문자열 변환과 SSID 처리를 위한 보조 함수들이다.

```cpp
std::wstring CWifiManagerDlg::ConvertSSID(const unsigned char* ssid, size_t ssidLength)
{
	UINT codePage = CP_UTF8;
	int len = MultiByteToWideChar(codePage, MB_ERR_INVALID_CHARS,
		reinterpret_cast<const char*>(ssid), ssidLength, NULL, 0);

	// UTF-8로 변환 실패시 시스템 기본 코드페이지로 시도
	if (len == 0 && GetLastError() == ERROR_NO_UNICODE_TRANSLATION) {
		codePage = CP_ACP;
		len = MultiByteToWideChar(codePage, 0,
			reinterpret_cast<const char*>(ssid), ssidLength, NULL, 0);
	}

	if (len > 0) {
		std::wstring networkName(len, L'\0');
		if (MultiByteToWideChar(codePage, 0,
			reinterpret_cast<const char*>(ssid), ssidLength,
			&networkName[0], len) > 0) {
			return networkName;
		}
	}

	// 변환 실패시 빈 문자열 반환
	return std::wstring();
}

std::string CWifiManagerDlg::WStringToString(const std::wstring& wstr)
{
	string str;
	size_t size;
	str.resize(wstr.length());
	wcstombs_s(&size, &str[0], str.size() + 1, wstr.c_str(), wstr.size());
	return str;
}
```

ConvertSSID는 바이트 배열 형태의 SSID를 와이드 문자열로 변환한다. UTF-8 인코딩을 우선 시도하고, 실패하면 시스템 기본 코드페이지로 다시 변환해 다양한 언어의 SSID를 처리할 수 있다. WStringToString은 유니코드 문자열을 시스템 기본 인코딩의 멀티바이트 문자열로 변환하며, 필요한 버퍼 크기 계산과 할당을 함수 안에서 처리한다.

<br/>

## 결론
지금까지 MFC 기반 UI에서 WlanAPI로 주변 네트워크를 스캔해 "WAVE" 접두사를 가진 SSID만 신호 강도순으로 보여주고, XML 프로파일과 netsh 명령어를 통해 WPA2-PSK/AES 설정으로 연결하는 과정을 구현했다. SSID 필터링 조건이나 보안 설정을 바꾸면 자동 연결 시스템이나 네트워크 모니터링 도구 같은 다른 용도에도 응용할 수 있다.
