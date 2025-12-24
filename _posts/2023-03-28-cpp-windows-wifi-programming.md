---
title: "(C++) WlanAPI를 이용한 Wi-Fi 검색 및 연결 기능 구현"
description: "Windows 환경에서 Wi-Fi 네트워크 검색과 연결하기"
date: 2023-03-28 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, programming, wifi, wlanapi, windows]
---

# WlanAPI를 이용한 Wi-Fi 검색 및 연결 기능 구현
- 최초 작성일: 2023년 3월 28일 (화)

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

#### 동작 원리:
1. **초기화 및 데이터 구조**
   - `std::tuple<CString, LONG, CString>`을 사용하여 각 네트워크의 SSID, 신호 강도, 연결 시간을 저장
   - 기존 리스트 항목들을 모두 삭제하여 새로운 스캔 결과를 표시할 준비

2. **네트워크 스캔**
   - `ListAvailableWifiNetworks()`를 호출하여 실제 Wi-Fi 스캔 수행
   - WlanAPI를 통해 모든 가용한 네트워크 정보 수집

3. **결과 정렬**
   - 람다 표현식을 사용하여 RSSI(신호 강도) 기준 내림차순 정렬
   - 사용자가 신호가 강한 네트워크를 쉽게 식별할 수 있도록 함

4. **필터링 및 표시**
   - "WAVE" 접두사를 가진 SSID만 선택
   - 각 네트워크 정보를 포맷팅하여 리스트에 추가
   - 신호 강도와 첫 연결 시간 정보를 함께 표시

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

#### 구현 세부사항:
1. **WlanAPI 초기화**
   - `WlanOpenHandle`을 사용하여 Wlan 클라이언트 핸들 생성
   - 버전 2를 지정하여 최신 기능 사용

2. **인터페이스 열거**
   - `WlanEnumInterfaces`로 시스템의 모든 무선 인터페이스 열거
   - 노트북의 내장 Wi-Fi, 외장 Wi-Fi 어댑터 등 모든 인터페이스 처리

3. **BSS 목록 획득**
   - 각 인터페이스에 대해 `WlanGetNetworkBssList` 호출
   - BSS(Basic Service Set) 정보를 통해 각 네트워크의 세부 정보 획득

4. **시간 정보 처리**
   - 호스트 타임스탬프를 시스템 시간으로 변환
   - 1970년 기준 시간을 기준으로 계산
   - 시:분:초 형식으로 포맷팅

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

#### 주요 기능:
1. **선택 항목 확인**
   - 리스트에서 선택된 항목의 위치 확인
   - 선택된 항목이 없는 경우 사용자에게 알림

2. **SSID 추출**
   - 정규식을 사용하여 전체 텍스트에서 SSID 부분만 추출
   - 공백 전까지의 문자열을 네트워크 이름으로 사용

3. **연결 시도**
   - 기본 비밀번호("wave1234") 사용
   - 연결 성공/실패 여부를 사용자에게 알림
   - 성공 시 윈도우 타이틀 업데이트

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

#### 구현 세부사항:
1. **XML 프로파일 구조**
   - WLANProfile 형식의 XML 문서 생성
   - SSID 정보를 일반 텍스트와 16진수 형태로 모두 포함
   - WPA2-PSK/AES 보안 설정 지정

2. **프로파일 설정**
   - connectionType: ESS(Extended Service Set) 사용
   - connectionMode: 자동 연결 설정
   - 인증 방식: WPA2-PSK
   - 암호화: AES
   - MAC 무작위화: 비활성화

3. **네트워크 연결**
   - netsh 명령어를 사용하여 프로파일 추가
   - 추가된 프로파일을 사용하여 네트워크 연결 시도

<br/>

## 유틸리티 함수들
문자열 변환과 SSID 처리를 위한 보조 함수들이다.

```cpp
std::wstring CWifiManagerDlg::ConvertSSID(const unsigned char* ssid, size_t ssidLength)
{
	int len = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS,
		reinterpret_cast<const char*>(ssid), ssidLength, NULL, 0);

	// UTF-8로 변환 실패시 시스템 기본 코드페이지로 시도
	if (len == 0 && GetLastError() == ERROR_NO_UNICODE_TRANSLATION) {
		len = MultiByteToWideChar(CP_ACP, 0,
			reinterpret_cast<const char*>(ssid), ssidLength, NULL, 0);
	}

	if (len > 0) {
		std::wstring networkName(len, L'\0');
		if (MultiByteToWideChar(CP_UTF8, 0,
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

#### 기능 설명:
1. **ConvertSSID**
   - 바이트 배열 형태의 SSID를 문자열로 변환
   - UTF-8 인코딩 우선 시도
   - UTF-8 실패 시 시스템 기본 코드페이지 사용
   - 다양한 언어의 SSID 처리 가능

2. **WStringToString**
   - 유니코드 문자열을 멀티바이트 문자열로 변환
   - 시스템 기본 인코딩 사용
   - 메모리 크기 계산 및 할당 자동 처리

<br/>

## 결론
이 구현은 Windows 환경에서 WlanAPI를 사용하여 Wi-Fi 네트워크를 효과적으로 제어하는 방법을 보여준다. 특히 다음과 같은 특징을 가지고 있다:

1. **기능적 특징**
   - "WAVE" 접두사를 가진 네트워크만 필터링하여 처리
   - 신호 강도 기반 정렬로 사용자 편의성 제공
   - WPA2-PSK/AES 보안 설정으로 안전한 연결 지원

2. **구현 특징**
   - MFC 기반의 사용자 인터페이스 제공
   - XML 프로파일을 통한 네트워크 설정 관리
   - 다국어 SSID 지원을 위한 문자열 처리

3. **활용 방안**
   - 특정 SSID 패턴을 가진 네트워크 관리에 활용
   - 자동 Wi-Fi 연결 시스템 구축에 응용
   - 네트워크 모니터링 도구 개발에 참조

이 코드는 Wi-Fi 네트워크 관리 기능이 필요한 Windows 애플리케이션 개발에 유용한 참조가 될 수 있으며, 필요에 따라 SSID 필터링 조건이나 보안 설정을 수정하여 다양한 요구사항에 맞게 확장할 수 있다.
