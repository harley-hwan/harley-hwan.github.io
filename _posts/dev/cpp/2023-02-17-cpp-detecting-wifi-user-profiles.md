---
title: "(C++) 와이파이 사용자 프로필 검출하기"
description: "netsh wlan show profiles와 같은 결과를 WlanGetProfileList로 얻는다. 목록 순서가 곧 연결 우선순위라는 점, 와이드 문자열 변환에서 널 문자가 하나 더 붙는 버그, 저장된 비밀번호를 읽는 방법까지 정리했다."
date: 2023-02-17 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, wifi, ssid, wlanopenhandle, wlan-enum-interfaces, wlan-get-profile-list, windows, wlanapi]
---
## 왜 프로필 목록이 필요했나

검사 PC를 새로 세팅할 때마다 장비 AP 프로필을 등록해줘야 한다. 안 되어 있으면 검사 프로그램이 장비를 못 찾는데, 그 시점에는 원인이 "통신 안 됨" 하나로만 보인다.

그래서 프로그램 시작할 때 "이 PC에 장비 프로필이 등록되어 있는가"를 먼저 확인하고, 없으면 그렇다고 알려주기로 했다. 명령으로는 `netsh wlan show profiles`가 하는 일과 같다.

`netsh`를 `popen`으로 돌려서 파싱해도 되지만, 출력이 OS 언어에 따라 달라진다. 한국어 윈도우에서는 "모든 사용자 프로필"이라고 나오고 영문에서는 "All User Profile"이다. 현장 PC의 언어를 통제할 수 없어서 API로 갔다.

## 코드

```c++
#include <iostream>
#include <Windows.h>
#include <wlanapi.h>
#include <objbase.h>
#include <wtypes.h>
#include <string>
#pragma comment(lib, "Wlanapi.lib")
#pragma comment(lib, "ole32.lib")

std::string ConvertWCharToString(const wchar_t* wstr) {
    std::string str;
    int len = WideCharToMultiByte(CP_ACP, 0, wstr, -1, NULL, 0, NULL, NULL);
    if (len > 0) {
        str.resize(len);
        WideCharToMultiByte(CP_ACP, 0, wstr, -1, &str[0], len, NULL, NULL);
    }
    return str;
}

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

        PWLAN_PROFILE_INFO_LIST pProfileList = NULL;
        ret = WlanGetProfileList(clientHandle, &pIfInfo->InterfaceGuid, NULL, &pProfileList);
        if (ret != ERROR_SUCCESS) {
            std::cerr << "WlanGetProfileList failed with error: " << ret << std::endl;
            continue;
        }

        for (DWORD j = 0; j < pProfileList->dwNumberOfItems; j++) {
            std::string profileName = ConvertWCharToString(pProfileList->ProfileInfo[j].strProfileName);
            std::cout << "SSID: " << profileName << std::endl;
        }

        WlanFreeMemory(pProfileList);
    }

    WlanFreeMemory(ifList);
    WlanCloseHandle(clientHandle, NULL);
    return 0;
}
```

![저장된 Wi-Fi 프로필 목록](/assets/img/posts/cpp-detecting-wifi-user-profiles/001-219567840-c4b6e361-a4e4-4b36-b693-99c8895eb5a2.png)

결과가 `netsh wlan show profiles`와 일치한다.

## 문자열 변환에 널이 하나 더 붙는다

`ConvertWCharToString`에 버그가 있다. 나중에 프로필 이름을 파일에 쓰다가 발견했다.

`WideCharToMultiByte`에 원본 길이로 `-1`을 주면 "널 종료 문자열"이라는 뜻이고, 반환되는 길이에 **널 문자가 포함된다**. 그걸 그대로 `str.resize(len)`에 쓰면 `std::string` 안에 널 문자가 하나 남는다.

```c++
// "VISION_01" -> len == 10 (널 포함)
// str.size() == 10, 마지막 원소가 '\0'
```

`std::cout`으로 찍으면 널이 안 보이니 화면상으로는 멀쩡하다. 그런데 다른 문자열과 비교하면 항상 다르고, 파일에 쓰면 널 바이트가 그대로 들어간다. 나는 프로필 이름을 로그 파일에 남겼다가 텍스트 에디터에서 이상한 문자가 보여서 알았다.

두 가지 방법이 있다. 원본 길이를 명시하거나, 결과에서 널을 빼거나.

```c++
std::string wide_to_utf8(const std::wstring& w)
{
    if (w.empty()) return {};
    const int len = WideCharToMultiByte(CP_UTF8, 0, w.data(), (int)w.size(),
                                        nullptr, 0, nullptr, nullptr);
    std::string out(len, '\0');
    WideCharToMultiByte(CP_UTF8, 0, w.data(), (int)w.size(),
                        out.data(), len, nullptr, nullptr);
    return out;
}
```

`-1` 대신 `w.size()`를 넘기면 널을 포함하지 않은 길이가 나온다. 빈 문자열을 먼저 걸러내는 이유는, 길이 0으로 `WideCharToMultiByte`를 부르면 실패(반환값 0)로 처리되어 에러와 구분이 안 되기 때문이다.

## CP_ACP를 쓰면 글자가 사라진다

코드페이지를 `CP_ACP`로 준 것도 나중에 문제가 됐다. `CP_ACP`는 시스템 기본 코드페이지, 한국어 윈도우면 CP949다. 이 코드페이지에 없는 문자는 `?`로 바뀐다.

한글 SSID는 CP949에 있으니 괜찮다. 그런데 사무실에 일본어나 중국어 이름의 AP가 하나 있으면 그 프로필 이름이 전부 `?????`가 된다. 그 문자열로 다시 `WlanDeleteProfile`을 부르면 당연히 실패한다.

위처럼 `CP_UTF8`로 바꾸면 손실 없이 변환된다. 다만 그 값을 콘솔에 그대로 찍으면 이번엔 콘솔이 UTF-8을 못 읽어서 깨진다. 화면에 보여줄 거면 `std::wcout`으로 와이드 문자열 그대로 출력하는 게 제일 안전하다. 변환은 파일에 쓰거나 통신으로 보낼 때만 한다.

## 목록 순서가 곧 연결 우선순위다

`WlanGetProfileList`가 돌려주는 순서는 임의가 아니라 **연결 우선순위 순서**다. 윈도우는 주변에 여러 개가 보일 때 이 순서대로 시도한다.

검사 PC에서 문제가 됐던 게 이거였다. 사무실 공용 AP가 목록 위에 있어서, 장비 AP가 켜져 있어도 윈도우가 공용 AP에 먼저 붙었다. 사용자가 수동으로 바꿔줘야 하는데 그걸 잊으면 검사가 안 된다.

순서는 코드로 바꿀 수 있다.

```c++
// 장비 프로필을 맨 앞으로
DWORD ret = WlanSetProfilePosition(h, &guid, L"VISION_01", 0, nullptr);
```

이건 조회가 아니라 설정이라 **관리자 권한**이 필요하다. 일반 사용자로 돌리면 `ERROR_ACCESS_DENIED`가 난다.

## 프로필 종류 구분하기

`WLAN_PROFILE_INFO`의 `dwFlags`로 프로필 성격을 알 수 있다.

| 플래그 | 의미 |
| :--- | :--- |
| `WLAN_PROFILE_GROUP_POLICY` | 그룹 정책으로 배포됨. 사용자가 지우거나 못 바꾼다 |
| `WLAN_PROFILE_USER` | 현재 사용자 전용. 없으면 모든 사용자용 |

회사에서 관리하는 PC는 공용 AP 프로필이 그룹 정책으로 내려온다. 이걸 지우려고 `WlanDeleteProfile`을 불러도 실패하니, 순서만 바꾸는 쪽으로 처리해야 한다.

사용자 전용 프로필도 걸린 적이 있다. A 계정으로 장비 프로필을 등록했는데 B 계정으로 로그인하면 목록에 없다. `WlanGetProfileList`는 호출한 프로세스의 사용자 컨텍스트에서 보이는 것만 돌려준다. 서비스로 돌리면 또 다르게 보인다.

## 저장된 비밀번호 읽기

프로필의 실제 내용은 XML로 되어 있고 `WlanGetProfile`로 받을 수 있다.

```c++
LPWSTR xml = nullptr;
DWORD flags = WLAN_PROFILE_GET_PLAINTEXT_KEY;   // 평문 키를 달라
DWORD access = 0;

DWORD ret = WlanGetProfile(h, &guid, L"VISION_01", nullptr, &xml, &flags, &access);
if (ret == ERROR_SUCCESS) {
    // xml 안의 <keyMaterial> 이 비밀번호
    WlanFreeMemory(xml);
}
```

`WLAN_PROFILE_GET_PLAINTEXT_KEY`를 주면 `<keyMaterial>`에 비밀번호가 평문으로 들어온다. **관리자 권한이 필요하다.** 없으면 그 부분이 암호화된 상태로 오거나 `ERROR_ACCESS_DENIED`가 난다.

원래는 프로그램이 프로필을 자동 등록하도록 만들려고 확인해본 것인데, 결국 등록 쪽은 `WlanSetProfile`로 XML을 직접 만들어 넣는 방식으로 갔다. 그 얘기는 [Wi-Fi 검색 및 연결 기능 구현](/posts/cpp-windows-wifi-programming/)에 있다.

## 프로필이 있다 ≠ 지금 붙을 수 있다

당연한 얘기인데 처음엔 이걸 구분 안 했다. 프로필 목록에 있다는 건 "예전에 접속한 적이 있다"는 뜻이지 지금 주변에 그 AP가 있다는 뜻이 아니다.

검사 프로그램에서는 두 가지를 나눠서 알려주는 게 맞았다.

- 프로필이 없다: PC 세팅 문제. 등록해야 한다
- 프로필은 있는데 주변에 안 보인다: 장비가 꺼져 있거나 거리가 멀다

주변에 보이는지는 `WlanGetAvailableNetworkList`나 `WlanGetNetworkBssList`로 확인한다. 두 정보를 합쳐서 판정하니 현장에서 원인 파악이 훨씬 빨라졌다.

현재 연결된 프로필과 저장된 목록을 대조하는 코드는 [Windows WLAN API를 이용한 WiFi 프로필 검출](/posts/cpp-get-connected-wifi-profile-list/)에 따로 정리했다.

## 정리하면

- `WideCharToMultiByte`에 `-1`을 주면 반환 길이에 널이 포함된다. 원본 길이를 명시하는 편이 안전하다
- `CP_ACP`는 코드페이지에 없는 문자를 `?`로 바꾼다. 손실 없이 다루려면 `CP_UTF8`이나 와이드 문자열 그대로
- 프로필 목록의 순서가 연결 우선순위다. 바꾸려면 `WlanSetProfilePosition`, 관리자 권한 필요
- 그룹 정책 프로필은 지울 수 없고, 사용자 전용 프로필은 계정이 다르면 안 보인다
- 프로필 존재 여부와 지금 접속 가능 여부는 다른 문제다. 나눠서 판정해야 원인이 보인다

## 참고

- [WlanGetProfileList](https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/nf-wlanapi-wlangetprofilelist)
- [WlanGetProfile](https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/nf-wlanapi-wlangetprofile)
