---
title: "(C++) WlanAPI를 이용한 Wi-Fi 검색 및 연결 기능 구현"
description: "MFC 툴에서 주변 AP를 스캔해 목록에 띄우고 선택한 AP에 접속시키는 기능. netsh + 임시 XML로 시작했다가 WlanSetProfile/WlanConnect로 옮긴 이유, 스캔 결과가 갱신되지 않던 문제, SSID를 16진수로 만들 때의 버그를 정리했다."
date: 2023-03-28 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, programming, wifi, wlanapi, windows, mfc, wlanscan, wlanconnect]
---
## 사용자가 Wi-Fi를 손으로 바꾸는 게 문제였다

장비마다 자체 AP를 띄우니, 장비를 바꿀 때마다 사용자가 윈도우 트레이에서 Wi-Fi를 눌러 다른 AP로 옮겨야 했다. 검사 한 대에 한 번씩 이 과정이 들어가는데, 여기서 다른 AP를 잘못 고르는 일이 계속 생겼다.

검사 프로그램 안에서 장비 AP만 목록에 띄우고, 클릭 한 번으로 붙게 만들기로 했다. 장비 AP는 SSID가 정해진 접두사(여기서는 `WAVE`)로 시작하니 그걸로 거른다.

## 스캔 결과를 리스트에 채우기

버튼 핸들러부터.

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

신호가 센 순으로 정렬해서 가까운 장비가 위에 오게 했다. `ssid.Find(_T("WAVE")) == 0`으로 접두사를 검사한다. `Find`는 어디에서든 찾으면 위치를 돌려주니 `== 0`을 붙여야 "시작 부분"이 된다. 이걸 빼면 `MY_WAVE_AP` 같은 것도 걸린다.

실제 스캔은 이쪽이다.

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

`WlanGetNetworkBssList`는 BSS 단위로 정보를 준다. RSSI가 백분율이 아니라 dBm(`lRssi`)으로 바로 나와서 정렬 기준으로 쓰기 좋다.

## 스캔 버튼을 눌러도 목록이 안 바뀐다

이걸 만들고 나서 제일 먼저 걸린 문제다. 장비 전원을 켜고 스캔 버튼을 눌러도 새 AP가 안 나온다. 한참 뒤에 다시 누르면 그제야 나온다.

`WlanGetNetworkBssList`는 **캐시된 결과를 돌려주는 함수**다. 실제 스캔을 트리거하지 않는다. 윈도우가 알아서 주기적으로 스캔한 결과를 그냥 읽어오는 것이라, 버튼을 눌러도 마지막 스캔 시점의 목록이 나온다.

새로 스캔하려면 `WlanScan`을 먼저 불러야 한다.

```cpp
WlanScan(clientHandle, &pIfInfo->InterfaceGuid, nullptr, nullptr, nullptr);
```

그런데 이 함수는 **비동기**다. 바로 반환하고 스캔은 뒤에서 돈다. 곧바로 `WlanGetNetworkBssList`를 부르면 여전히 옛날 결과가 나온다. 완료를 기다려야 한다.

```cpp
// 스캔 완료 알림 받기
static void WINAPI OnWlanNotify(PWLAN_NOTIFICATION_DATA data, PVOID ctx)
{
    if (data->NotificationSource == WLAN_NOTIFICATION_SOURCE_ACM &&
        (data->NotificationCode == wlan_notification_acm_scan_complete ||
         data->NotificationCode == wlan_notification_acm_scan_fail))
    {
        SetEvent(reinterpret_cast<HANDLE>(ctx));
    }
}

// ...
HANDLE done = CreateEvent(nullptr, TRUE, FALSE, nullptr);
DWORD prev = 0;
WlanRegisterNotification(clientHandle, WLAN_NOTIFICATION_SOURCE_ACM, TRUE,
                         OnWlanNotify, done, nullptr, &prev);

WlanScan(clientHandle, &guid, nullptr, nullptr, nullptr);
WaitForSingleObject(done, 6000);          // 문서상 4초 안에 끝난다

WlanRegisterNotification(clientHandle, WLAN_NOTIFICATION_SOURCE_NONE, TRUE,
                         nullptr, nullptr, nullptr, &prev);
CloseHandle(done);
```

문서에 스캔은 4초 안에 끝난다고 되어 있어서 6초로 여유를 뒀다. 콜백은 **다른 스레드에서** 호출되므로 UI를 직접 건드리면 안 된다. 이벤트만 세우고 원래 스레드에서 결과를 읽는다.

UI 스레드에서 `WaitForSingleObject`로 몇 초를 막으면 창이 멎어 보인다. 실제로는 스캔을 별도 스레드에서 돌리고 완료되면 `PostMessage`로 알리도록 바꿨다. 같은 구조를 [BLE 스캔](/posts/cpp-mfc-bluetooth-device-scan-and-listview/) 쪽에서도 썼다.

## 타임스탬프는 결국 안 믿기로 했다

`ullHostTimestamp`를 시각으로 바꾸는 부분은 지금 봐도 근거가 약하다. 위 코드는 이 값을 1970년 기준 마이크로초로 가정하고 `* 10`을 해서 100나노초 단위로 맞춘 뒤, 1601년 기준으로 옮기는 상수를 더한다.

그런데 문서에는 이 값의 기준점이나 단위가 명확히 적혀 있지 않다. 실제로 찍어보니 PC마다 나오는 값이 제각각이었고, 어떤 드라이버에서는 부팅 이후 경과 시간처럼 보였다. "First Connect"라는 라벨도 사실 맞지 않는다. 이건 비콘을 받은 시각이지 접속한 시각이 아니다.

결국 이 열은 뺐다. 시각이 필요하면 스캔을 실행한 시점을 프로그램이 직접 기록하는 게 정확하고, 무엇보다 값의 의미가 헷갈리지 않는다.

## 목록에서 SSID를 다시 뽑는 게 문제였다

연결 버튼 핸들러다.

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
			// ...
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

여기가 나중에 실제로 사고가 났다. 리스트에 `"SSID - RSSI: -45 - First Connect: 10:23:11"` 형태로 한 줄에 다 넣어놓고, 연결할 때 정규식 `^([^ ]+)`로 공백 앞까지를 SSID로 되뽑는다.

**SSID에 공백이 들어가면 여기서 잘린다.** 장비 SSID가 `WAVE 01`처럼 바뀐 순간 `WAVE`만 뽑혀서 접속이 안 됐다. 화면에는 이름이 제대로 보이니까 왜 안 되는지 한참 몰랐다.

원본 데이터를 두고 인덱스만 들고 있으면 이런 일이 없다.

```cpp
// 스캔 결과를 멤버로 보관하고
m_scanResults = ListAvailableWifiNetworks();

// 리스트 항목에 원본 인덱스를 붙인다
m_lcWifiList.InsertItem(nIndex, listItem);
m_lcWifiList.SetItemData(nIndex, static_cast<DWORD_PTR>(originalIndex));

// 연결할 때는 인덱스로 원본을 꺼낸다
const size_t k = m_lcWifiList.GetItemData(selectedIndex);
const CString ssid = std::get<0>(m_scanResults[k]);
```

화면에 보여주려고 만든 문자열을 다시 파싱해서 데이터를 복원하는 건 어디서든 문제가 된다. 표시용과 데이터용을 분리해야 한다.

비밀번호를 소스에 박아둔 것도 그대로 두면 안 되는 부분이다. 실행 파일에서 문자열만 뽑아도 나온다. 지금은 설정 파일에서 읽고, 그 파일은 배포 대상에서 뺐다.

## 접속: netsh로 시작했다가 API로 옮겼다

처음 구현은 XML 프로필 파일을 만들고 `netsh` 명령을 호출하는 방식이었다.

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

동작은 했는데 문제가 여러 개였다.

**`system()`이 콘솔 창을 띄운다.** GUI 프로그램인데 접속할 때마다 검은 창이 깜빡인다. 사용자가 "뭔가 잘못된 것 같다"고 물어봤다.

**비밀번호가 평문으로 디스크에 남는다.** `myWlan.xml`을 만들고 지우지도 않는다. 실행 폴더에 그대로 남아 있다.

**에러를 알 수 없다.** `system()`의 반환값은 명령 처리기의 종료 코드라서 `netsh`가 실제로 성공했는지와 항상 일치하지 않는다. 출력도 못 받으니 왜 실패했는지 모른다.

**16진수 SSID가 틀렸다.** 이게 제일 결정적이었다.

```cpp
for (int i = 0; i < name.length(); i++)
    xmlFile << std::hex << (int)name.at(i);
```

`<hex>` 요소는 SSID의 바이트를 두 자리 16진수로 나열해야 한다. 그런데 이 코드는 자리 채움이 없다. `\n`(0x0A) 같은 값이 `a` 한 글자로 나가고, `W`(0x57)는 두 글자로 나가서 전체가 밀린다. 게다가 `char`가 부호 있는 타입이라 0x80 이상이면 음수가 되고, `(int)`로 승격되면 `ffffffab` 같은 게 찍힌다.

```cpp
// 고친 형태
for (unsigned char c : name)
    xmlFile << std::hex << std::setw(2) << std::setfill('0') << (int)c;
```

`std::string name(networkName.begin(), networkName.end())` 이것도 문제다. `wchar_t`를 하나씩 `char`로 잘라 넣는 거라 아스키 밖의 문자는 다 깨진다. 한글 SSID면 이 줄에서 끝난다. `WideCharToMultiByte(CP_UTF8, ...)`로 제대로 변환해야 한다.

## WlanSetProfile + WlanConnect

결국 `netsh`를 버리고 API로 갔다. XML을 파일로 쓸 필요도 없고 콘솔 창도 안 뜬다.

```cpp
bool ConnectWifi(HANDLE h, const GUID& guid,
                 const std::wstring& ssid, const std::wstring& key)
{
    // 1) 프로필 XML 을 메모리에서 구성
    std::wostringstream xml;
    xml << L"<?xml version=\"1.0\"?>"
        << L"<WLANProfile xmlns=\"http://www.microsoft.com/networking/WLAN/profile/v1\">"
        << L"<name>" << ssid << L"</name>"
        << L"<SSIDConfig><SSID><name>" << ssid << L"</name></SSID></SSIDConfig>"
        << L"<connectionType>ESS</connectionType>"
        << L"<connectionMode>manual</connectionMode>"
        << L"<MSM><security>"
        << L"<authEncryption><authentication>WPA2PSK</authentication>"
        << L"<encryption>AES</encryption><useOneX>false</useOneX></authEncryption>"
        << L"<sharedKey><keyType>passPhrase</keyType><protected>false</protected>"
        << L"<keyMaterial>" << key << L"</keyMaterial></sharedKey>"
        << L"</security></MSM></WLANProfile>";

    const std::wstring s = xml.str();

    // 2) 프로필 등록 (덮어쓰기 허용)
    DWORD reason = 0;
    DWORD ret = WlanSetProfile(h, &guid, 0, s.c_str(), nullptr, TRUE, nullptr, &reason);
    if (ret != ERROR_SUCCESS) {
        WCHAR buf[256] = {};
        WlanReasonCodeToString(reason, 256, buf, nullptr);   // 원인이 여기 나온다
        return false;
    }

    // 3) 접속 (비동기)
    WLAN_CONNECTION_PARAMETERS p = {};
    p.wlanConnectionMode = wlan_connection_mode_profile;
    p.strProfile         = ssid.c_str();
    p.pDot11Ssid         = nullptr;
    p.pDesiredBssidList  = nullptr;
    p.dot11BssType       = dot11_BSS_type_infrastructure;
    p.dwFlags            = 0;

    return WlanConnect(h, &guid, &p, nullptr) == ERROR_SUCCESS;
}
```

`WlanSetProfile`이 실패했을 때 `pdwReasonCode`를 `WlanReasonCodeToString`에 넣으면 사람이 읽는 문장이 나온다. XML의 어느 부분이 잘못됐는지까지 알려줘서, `netsh`를 쓰던 시절보다 원인 파악이 훨씬 빨랐다.

SSID에 특수문자가 들어가면 XML 이스케이프도 필요하다. `&`, `<`, `>`를 각각 `&amp;`, `&lt;`, `&gt;`로 바꿔야 하는데, 앰퍼샌드가 들어간 SSID로 한 번 걸렸다.

`WlanSetProfile`의 세 번째 인자 `dwFlags`에 `0`을 주면 모든 사용자용 프로필이라 **관리자 권한이 필요하다**. `WLAN_PROFILE_USER`를 주면 현재 사용자 전용이 되어 권한 없이 등록된다. 검사 PC를 일반 계정으로 쓰는 곳이 있어서 후자로 갔다.

`WlanConnect`도 비동기다. 반환은 "요청을 받았다"는 뜻이고, 실제 접속 완료는 `wlan_notification_acm_connection_complete` 알림으로 온다. 스캔 때와 같은 방식으로 기다린다. 알림 데이터의 `WLAN_CONNECTION_NOTIFICATION_DATA::wlanReasonCode`에 실패 이유가 들어 있어서, 비밀번호가 틀렸는지 AP가 사라졌는지를 구분할 수 있다.

## SSID 변환

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

	return std::wstring();
}
```

이 함수는 지금 봐도 잘 짰다고 생각한다. 802.11 규격이 SSID의 인코딩을 정해두지 않아서, 요즘 공유기는 대부분 UTF-8을 쓰지만 오래된 것은 CP949를 쓰기도 한다. `MB_ERR_INVALID_CHARS`를 주면 UTF-8로 해석이 안 될 때 실패하니, 그걸 신호로 삼아 시스템 코드페이지로 재시도한다.

길이를 `-1`이 아니라 `ssidLength`로 넘긴 것도 맞다. SSID는 널로 끝나지 않는 바이트 배열이라 `-1`을 쓰면 뒤쪽 쓰레기까지 읽는다.

## 목록에 같은 SSID가 여러 번 나온다

빠뜨렸던 게 하나 있다. `WlanGetNetworkBssList`는 **BSS 단위**라, 같은 SSID를 여러 AP가 쓰거나 듀얼 밴드면 항목이 여러 개 나온다. 리스트에 같은 이름이 두세 개 뜨는 걸 사용자가 이상하게 봤다.

SSID로 묶고 RSSI가 제일 센 것만 남기면 된다.

```cpp
std::map<std::wstring, LONG> best;
for (const auto& e : entries) {
    auto it = best.find(e.ssid);
    if (it == best.end() || e.rssi > it->second) best[e.ssid] = e.rssi;
}
```

SSID별로 보고 싶은 게 아니라 특정 AP를 골라야 하는 상황이면 `WLAN_CONNECTION_PARAMETERS::pDesiredBssidList`에 BSSID를 지정해서 접속할 수 있다. 장비가 여러 대 켜져 있는 환경에서는 이쪽이 확실하다.

## 정리하면

- `WlanGetNetworkBssList`는 캐시를 읽는다. 새로 스캔하려면 `WlanScan` + 완료 알림 대기
- `WlanScan`, `WlanConnect` 둘 다 비동기다. 알림을 등록하고 이벤트로 기다린다
- 화면 표시용 문자열을 다시 파싱해서 데이터를 복원하면 안 된다. SSID에 공백 하나 들어가면 깨진다
- `<hex>` SSID는 두 자리 고정이어야 하고, `char`의 부호 때문에 `unsigned char`로 받아야 한다
- `system("netsh ...")`는 콘솔 창이 뜨고 에러를 못 받고 비밀번호가 파일로 남는다. `WlanSetProfile` + `WlanConnect`로 가는 게 낫다
- `WlanSetProfile` 실패 시 `WlanReasonCodeToString`으로 원인을 문장으로 받을 수 있다
- 같은 SSID의 BSS가 여럿이면 목록에 중복이 생긴다. RSSI 최대값으로 묶는다

## 참고

- [WlanScan](https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/nf-wlanapi-wlanscan)
- [WlanSetProfile](https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/nf-wlanapi-wlansetprofile)
- [WlanConnect](https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/nf-wlanapi-wlanconnect)
- [WLAN_profile schema](https://learn.microsoft.com/en-us/windows/win32/nativewifi/wlan-profileschema-elements)
