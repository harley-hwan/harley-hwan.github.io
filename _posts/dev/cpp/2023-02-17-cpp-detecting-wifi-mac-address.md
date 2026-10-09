---
title: "(C++) WlanAPI를 이용한 Wi-Fi MAC 주소 검출"
description: "접속한 AP의 MAC(BSSID)을 뽑는 코드. 이게 내 어댑터 MAC이 아니라는 점, 같은 장비인데 대역마다 BSSID가 다른 점, 로컬 관리 비트로 임의 주소를 구분하는 법까지 정리했다."
date: 2023-02-17 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, windows, wlan, mac, network, wlanapi, bssid]
---
## SSID만으로는 장비를 구분 못 한다

장비들이 자체 AP를 띄우는데, 펌웨어가 같으면 SSID도 같은 이름 뒤에 번호만 다르게 붙는다. 여러 대를 나란히 켜두고 검사하다 보니 "지금 붙은 게 몇 번 장비지?"가 애매해지는 순간이 생겼다. SSID를 잘못 읽거나 자동 연결이 다른 장비로 붙어버리면 엉뚱한 장비의 결과를 기록한다.

그래서 검사 로그에 AP의 MAC 주소를 같이 남기기로 했다. SSID는 사람이 바꿀 수 있어도 MAC은 고유하니까.

## 코드

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

![MAC 주소 출력 결과](/assets/img/posts/cpp-detecting-wifi-mac-address/001-219561425-804218a4-137d-47aa-a0be-6c993f9e0ba7.png)

기본 흐름은 [SSID 검출](/posts/cpp-detecting-current-wifi-ssid/)과 같다. `WlanOpenHandle`로 열고, 인터페이스를 열거하고, `wlan_intf_opcode_current_connection`으로 연결 정보를 받는다. 거기서 `wlanAssociationAttributes.dot11Bssid`를 읽는다.

`DOT11_MAC_ADDRESS`는 `UCHAR[6]`이라 `sizeof`가 6으로 나온다. 배열이라 그렇지, 포인터로 넘어온 자리에서 `sizeof`를 쓰면 8이 나오니 조심해야 한다.

## 이건 내 PC의 MAC이 아니다

한동안 헷갈렸던 부분이다. `dot11Bssid`는 **접속한 AP 쪽 MAC**이다. 인프라 모드 무선랜에서 BSSID는 AP의 무선 인터페이스 MAC과 같다.

내 PC 어댑터의 MAC이 필요하면 다른 API를 써야 한다.

```cpp
#include <winsock2.h>
#include <iphlpapi.h>
#pragma comment(lib, "iphlpapi.lib")

ULONG size = 15000;
auto buf = std::make_unique<char[]>(size);
auto* addrs = reinterpret_cast<IP_ADAPTER_ADDRESSES*>(buf.get());

if (GetAdaptersAddresses(AF_UNSPEC, GAA_FLAG_SKIP_ANYCAST,
                         nullptr, addrs, &size) == NO_ERROR) {
    for (auto* p = addrs; p; p = p->Next) {
        if (p->IfType != IF_TYPE_IEEE80211) continue;
        // p->PhysicalAddress / p->PhysicalAddressLength 가 내 어댑터 MAC
    }
}
```

내 것이 필요했던 게 아니라 장비 식별용이었으니 `dot11Bssid`가 맞았다. 다만 이름만 보고 "MAC 주소"라고 로그에 찍어놓으면 나중에 자기가 봐도 어느 쪽인지 모른다. 지금은 로그에 `AP BSSID`로 명시해서 남긴다.

## 같은 장비인데 BSSID가 다르게 나온다

2.4 GHz와 5 GHz를 같이 쓰는 AP는 대역마다 **다른 BSSID**를 쓴다. 보통 마지막 바이트만 1 차이 나는 식이다. SSID가 같아도 어느 대역에 붙었는지에 따라 MAC이 달라진다.

MAC을 장비 식별자로 쓰려다 같은 장비가 두 개로 잡히는 걸 보고 알았다. 대응은 둘 중 하나다. 마지막 바이트를 무시하고 앞 5바이트만 비교하거나(같은 칩에서 파생된 주소라는 가정), 애초에 장비가 자기 시리얼을 통신으로 알려주게 하는 것이다. 결국 후자로 갔다. MAC 규칙에 기대는 건 벤더가 바뀌면 깨진다.

## 임의 주소인지 구분하기

Windows 10부터 "임의 하드웨어 주소" 기능이 있어서 클라이언트 MAC이 접속할 때마다 바뀔 수 있다. AP 쪽 BSSID는 이 영향을 안 받지만, 소프트웨어 AP나 일부 장비는 임의 주소를 쓰기도 한다.

MAC 첫 바이트의 두 번째 비트(0x02)가 로컬 관리 비트다. 이게 1이면 제조사가 할당한 주소가 아니라 소프트웨어가 만든 주소다.

```cpp
bool is_locally_administered(const UCHAR mac[6]) { return (mac[0] & 0x02) != 0; }
bool is_multicast(const UCHAR mac[6])            { return (mac[0] & 0x01) != 0; }
```

이 비트가 서 있으면 그 MAC은 재부팅하면 바뀔 수 있다고 보고 식별자로 안 쓰는 게 맞다. 반대로 0이면 앞 3바이트가 OUI라서 제조사를 알 수 있다. 처음 보는 AP가 어느 칩셋인지 확인할 때 유용했다.

## 출력 포맷 정리

원 코드는 `std::cout`과 `printf`를 섞어 쓴다. 기본 설정에서는 두 스트림이 동기화되어 있어서 순서가 꼬이지는 않는데, 성능 때문에 `std::ios::sync_with_stdio(false)`를 켜는 순간 출력 순서가 어긋난다. 한쪽으로 통일하는 게 낫다.

```cpp
#include <string>
#include <cstdio>

std::string mac_to_string(const UCHAR mac[6])
{
    char buf[18];
    std::snprintf(buf, sizeof(buf), "%02X:%02X:%02X:%02X:%02X:%02X",
                  mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    return buf;
}
```

`iomanip`으로 하려면 이렇게 되는데, `setfill`과 `hex`가 스트림에 남는다는 점을 잊으면 뒤이어 출력하는 숫자가 전부 16진수로 나온다.

```cpp
std::ostringstream ss;
ss << std::hex << std::uppercase << std::setfill('0');
for (int i = 0; i < 6; ++i) {
    if (i) ss << ':';
    ss << std::setw(2) << static_cast<int>(mac[i]);
}
```

`static_cast<int>`가 필요한 이유는, `UCHAR`를 그대로 넣으면 스트림이 문자로 취급해서 제어 문자가 그대로 찍히기 때문이다. `printf("%02X", ...)`는 가변 인자 승격 덕에 알아서 `int`가 되니 이 문제가 없다. 스트림으로 옮길 때 자주 놓치는 부분이다.

## 접속 전에 미리 알고 싶다면

지금 붙어 있는 AP가 아니라 **주변 AP들의 BSSID**를 보려면 `WlanGetNetworkBssList`를 쓴다.

```cpp
PWLAN_BSS_LIST bssList = nullptr;
WlanGetNetworkBssList(h, &guid, nullptr, dot11_BSS_type_any, FALSE, nullptr, &bssList);

for (DWORD i = 0; i < bssList->dwNumberOfItems; ++i) {
    const auto& e = bssList->wlanBssEntries[i];
    // e.dot11Bssid, e.lRssi (dBm), e.ulChCenterFrequency (kHz)
}
```

`WLAN_BSS_ENTRY`에는 RSSI가 백분율이 아니라 dBm(`lRssi`)으로 그대로 들어 있어서 편하다. 채널 주파수도 있어서 2.4 GHz인지 5 GHz인지 바로 구분된다. 이걸 실제로 쓴 얘기는 [Wi-Fi 검색 및 연결 기능 구현](/posts/cpp-windows-wifi-programming/)에 있다.

## 정리하면

- `dot11Bssid`는 접속한 AP의 MAC이다. 내 어댑터 MAC은 `GetAdaptersAddresses`로 따로 얻는다
- 듀얼 밴드 AP는 대역마다 BSSID가 다르다. MAC을 장비 식별자로 쓰면 한 대가 두 대로 보인다
- 첫 바이트의 0x02 비트가 서 있으면 소프트웨어가 만든 주소라 바뀔 수 있다
- `UCHAR`를 스트림에 그대로 넣으면 문자로 찍힌다. `static_cast<int>`가 필요하다
- 주변 AP까지 보려면 `WlanGetNetworkBssList`. 이쪽은 RSSI가 dBm으로 나온다

## 참고

- [WLAN_ASSOCIATION_ATTRIBUTES](https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/ns-wlanapi-wlan_association_attributes)
- [WLAN_BSS_ENTRY](https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/ns-wlanapi-wlan_bss_entry)
