---
title: "(C++) getifaddrs를 이용한 네트워크 인터페이스 정보 구현"
description: "보드가 자기 IP를 알아야 해서 getifaddrs를 썼다. 인터페이스 이름으로 거르면 안 되는 이유, 링크 로컬 주소를 걸러야 하는 이유, 윈도우 GetAdaptersAddresses의 버퍼 재시도 규칙을 정리했다."
date: 2023-03-10 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, linux, windows, network, ifaddrs, ip, interface, getadaptersaddresses]
---
## 자기 IP를 알아야 했다

보드가 부팅하면 자기 IP를 로그에 남기고 상대 쪽에도 알려줘야 했다. DHCP로 받으니 재부팅할 때마다 바뀐다.

터미널에서는 `ifconfig`나 `ip addr`로 보면 되는데, 프로그램에서 그 출력을 파싱하는 건 앞에서 [arp로 한 번 데인](/posts/cpp-get-connected-ip-list-with-arp/) 뒤라 피하고 싶었다. 같은 정보를 주는 함수가 있다.

## 기본 구현

```cpp
#include <iostream>
#include <ifaddrs.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <vector>
#include <cstring>

std::vector<std::string> get_wifi_ips() {
    std::vector<std::string> ips;

    struct ifaddrs *ifaddr, *ifa;
    if (getifaddrs(&ifaddr) == -1) {
        std::cerr << "Failed to get network interface information.\n";
        return ips;
    }

    for (ifa = ifaddr; ifa != nullptr; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == nullptr) {
            continue;
        }

        if (ifa->ifa_addr->sa_family == AF_INET && 
            strstr(ifa->ifa_name, "wlan") != nullptr) {
            struct sockaddr_in *addr = (struct sockaddr_in *) ifa->ifa_addr;
            char ip_str[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &addr->sin_addr, ip_str, INET_ADDRSTRLEN);
            ips.push_back(ip_str);
        }
    }

    freeifaddrs(ifaddr);
    return ips;
}
```

![리눅스 Wi-Fi IP 목록](/assets/img/posts/cpp-network-interface-info-with-ifaddrs/001-224203955-c5e35379-41da-422c-8081-da33da12b77b.png)

`getifaddrs`가 연결 리스트를 만들어주고, 그걸 끝까지 돌면서 필요한 것만 고른다. `ifa_addr`이 널일 수 있어서 먼저 검사하는 게 중요하다. 주소가 할당되지 않은 인터페이스가 그렇다.

마지막에 `freeifaddrs`를 한 번 부르면 리스트 전체가 해제된다. 항목마다 해제하는 게 아니다.

## 이름으로 거르면 언젠가 깨진다

`strstr(ifa->ifa_name, "wlan")` 이 부분이 나중에 문제가 됐다.

라즈베리파이는 무선 인터페이스가 `wlan0`이라 잘 맞는다. 그런데 다른 보드로 옮기니 이름이 달랐다. systemd를 쓰는 배포판은 기본적으로 "예측 가능한 인터페이스 이름"을 쓰는데, PCI 위치나 MAC 기반으로 `wlp2s0`, `wlx001122334455` 같은 이름이 붙는다. `wlan`이라는 문자열이 없으니 목록이 비어 나온다.

USB Wi-Fi 동글을 꽂으면 또 달라지고, 이름을 바꿔주는 udev 규칙이 있으면 완전히 다른 이름이 된다.

이름 대신 **플래그로** 거르는 게 맞다.

```cpp
if (!(ifa->ifa_flags & IFF_UP))       continue;   // 활성 상태
if (!(ifa->ifa_flags & IFF_RUNNING))  continue;   // 실제로 링크가 붙어 있음
if (ifa->ifa_flags & IFF_LOOPBACK)    continue;   // 127.0.0.1 제외
```

`IFF_UP`과 `IFF_RUNNING`은 다르다. `IFF_UP`은 관리자가 켜둔 상태이고, `IFF_RUNNING`은 실제로 케이블이 꽂혀 있거나 AP에 붙어 있는 상태다. 랜선을 뽑아도 `IFF_UP`은 그대로라, 이것만 보면 죽은 인터페이스를 고른다.

유선과 무선을 구분해야 하면 `/sys/class/net/<이름>/wireless` 디렉토리가 있는지 보는 방법이 있다. 무선이면 존재한다. 이름 규칙보다 훨씬 안정적이다.

## 링크 로컬 주소를 걸러야 한다

DHCP를 못 받으면 리눅스가 `169.254.x.x` 대역의 주소를 스스로 붙인다. 이게 `getifaddrs`에도 그대로 나오니, 필터가 없으면 "IP를 받았다"고 판단해버린다.

실제로 이걸로 한참 헤맸다. 보드가 IP를 보고하는데 그 IP로는 아무도 접속을 못 한다. 로그만 보면 정상으로 보인다.

```cpp
const uint32_t a = ntohl(addr->sin_addr.s_addr);
if ((a & 0xFFFF0000u) == 0xA9FE0000u) continue;    // 169.254.0.0/16
```

DHCP 실패를 정상 동작과 구분해서 알려주는 게 목적이라면, 거르는 대신 "링크 로컬 주소만 있음"을 별도 상태로 보고하는 편이 낫다. 그래야 원인이 바로 보인다.

## 전체 인터페이스 훑어보기

어떤 인터페이스가 있는지 눈으로 확인할 때 쓴 코드다.

```cpp
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <netdb.h>
#include <linux/if_link.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    struct ifaddrs *ifaddr, *ifa;
    char host[NI_MAXHOST];

    if (getifaddrs(&ifaddr) == -1) {
        perror("getifaddrs");
        exit(EXIT_FAILURE);
    }

    // Wi-Fi IP 주소 검색
    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == NULL || ifa->ifa_addr->sa_family != AF_INET) {
            continue;
        }
        if (strcmp(ifa->ifa_name, "wlan0") == 0) {
            struct sockaddr_in* addr = (struct sockaddr_in*)ifa->ifa_addr;
            char ip[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &(addr->sin_addr), ip, INET_ADDRSTRLEN);
            printf("Wi-Fi IPv4 Address: %s\n", ip);
            break;
        }
    }

    // 모든 인터페이스 정보 출력
    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == NULL) {
            continue;
        }

        int family = ifa->ifa_addr->sa_family;
        printf("%-8s %s (%d)\n", 
            ifa->ifa_name,
            (family == AF_PACKET) ? "AF_PACKET" :
            (family == AF_INET) ? "AF_INET" :
            (family == AF_INET6) ? "AF_INET6" : "???",
            family);

        if (family == AF_INET || family == AF_INET6) {
            int s = getnameinfo(ifa->ifa_addr,
                        (family == AF_INET) ? sizeof(struct sockaddr_in) :
                        sizeof(struct sockaddr_in6),
                        host, NI_MAXHOST, NULL, 0, NI_NUMERICHOST);
            printf("\t\taddress: <%s>\n", host);
        }
    }

    freeifaddrs(ifaddr);
    return 0;
}
```

![모든 네트워크 인터페이스 정보](/assets/img/posts/cpp-network-interface-info-with-ifaddrs/002-224610333-a240b558-e48c-475b-b006-f9438ef9a43f.png)

출력을 보면 알 수 있는 게 하나 있다. **같은 인터페이스가 여러 번 나온다.** `wlan0`이 `AF_PACKET`, `AF_INET`, `AF_INET6`로 각각 한 번씩이다. `getifaddrs`가 주는 건 인터페이스 목록이 아니라 "인터페이스 × 주소 패밀리" 목록이다. 인터페이스 개수를 세려면 이름으로 중복을 제거해야 한다.

`AF_PACKET` 항목에는 MAC 주소가 들어 있다.

```cpp
#include <linux/if_packet.h>

if (ifa->ifa_addr->sa_family == AF_PACKET) {
    auto* s = reinterpret_cast<struct sockaddr_ll*>(ifa->ifa_addr);
    // s->sll_addr, s->sll_halen (보통 6)
}
```

위 코드에서 `getnameinfo`의 반환값 `s`를 받아놓고 확인하지 않는 것도 고쳐야 할 부분이다. 실패하면 `host`에 이전 값이 남아 있어서 앞 인터페이스의 주소가 다시 찍힌다.

## 윈도우 쪽

같은 코드를 검사 프로그램에서도 써야 해서 양쪽을 맞췄다.

```cpp
#include <iostream>
#include <string>
#include <vector>
#ifdef _WIN32
    #include <winsock2.h>
    #include <iphlpapi.h>
    #pragma comment(lib, "iphlpapi.lib")
    #pragma comment(lib, "ws2_32.lib")
#else
    #include <arpa/inet.h>
    #include <ifaddrs.h>
    #include <netinet/in.h>
#endif

std::vector<std::string> getWiFiIPAddresses() {
    std::vector<std::string> ipAddresses;
#ifdef _WIN32
    ULONG family = AF_INET;
    ULONG flags = GAA_FLAG_INCLUDE_PREFIX;
    ULONG bufferSize = 15000;
    PIP_ADAPTER_ADDRESSES pAddresses = (IP_ADAPTER_ADDRESSES *)malloc(bufferSize);
    
    if (pAddresses == NULL) {
        return ipAddresses;
    }
    
    ULONG ret = GetAdaptersAddresses(family, flags, NULL, pAddresses, &bufferSize);
    if (ret != NO_ERROR) {
        free(pAddresses);
        return ipAddresses;
    }
    
    for (PIP_ADAPTER_ADDRESSES pCurr = pAddresses; pCurr; pCurr = pCurr->Next) {
        for (PIP_ADAPTER_UNICAST_ADDRESS pUni = pCurr->FirstUnicastAddress; 
             pUni; pUni = pUni->Next) {
            if (pUni->Address.lpSockaddr->sa_family == AF_INET) {
                sockaddr_in *sa_in = (sockaddr_in *)pUni->Address.lpSockaddr;
                char strBuffer[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &(sa_in->sin_addr), strBuffer, INET_ADDRSTRLEN);
                ipAddresses.push_back(strBuffer);
            }
        }
    }
    
    free(pAddresses);
#else
    struct ifaddrs *ifAddrStruct = NULL;
    getifaddrs(&ifAddrStruct);
    
    for (struct ifaddrs *ifa = ifAddrStruct; ifa != NULL; ifa = ifa->ifa_next) {
        if (!ifa->ifa_addr) {
            continue;
        }
        
        if (ifa->ifa_addr->sa_family == AF_INET) {
            void *addr = &((struct sockaddr_in *)ifa->ifa_addr)->sin_addr;
            char addressBuffer[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, addr, addressBuffer, INET_ADDRSTRLEN);
            ipAddresses.push_back(addressBuffer);
        }
    }
    
    if (ifAddrStruct != NULL) {
        freeifaddrs(ifAddrStruct);
    }
#endif
    return ipAddresses;
}
```

윈도우 쪽에 두 가지 문제가 있었다.

### 버퍼 크기를 한 번만 시도한다

`GetAdaptersAddresses`는 버퍼가 모자라면 `ERROR_BUFFER_OVERFLOW`를 돌려주면서 `bufferSize`에 필요한 크기를 채워준다. 그걸 보고 다시 잡아 호출하는 게 정해진 사용법이다. 위 코드는 실패하면 그냥 빈 목록을 돌려준다.

15000바이트면 대부분 충분해서 개발 PC에서는 안 걸린다. 그런데 VPN 클라이언트나 가상 머신 프로그램이 깔린 PC는 가상 어댑터가 열 개 넘게 잡혀서 넘칠 수 있다. 현장 PC 한 대에서 IP가 안 나오는 걸로 확인했다.

```cpp
ULONG size = 15000;
std::vector<char> buf;
ULONG ret = 0;
for (int attempt = 0; attempt < 3; ++attempt) {
    buf.resize(size);
    ret = GetAdaptersAddresses(AF_INET, flags, nullptr,
                               reinterpret_cast<IP_ADAPTER_ADDRESSES*>(buf.data()),
                               &size);
    if (ret != ERROR_BUFFER_OVERFLOW) break;      // size 에 필요한 값이 들어왔다
}
if (ret != NO_ERROR) return {};
```

재시도 횟수를 제한한 이유는, 그사이에 어댑터가 추가되면 다시 넘칠 수 있어서 이론상 무한 루프가 가능하기 때문이다.

### WSAStartup을 안 불렀다

`inet_ntop`은 Winsock 함수다. `WSAStartup` 없이 부르면 실패한다. 리눅스 코드를 그대로 옮기다 보니 이걸 빠뜨렸다.

```cpp
WSADATA wsa;
WSAStartup(MAKEWORD(2, 2), &wsa);
// ...
WSACleanup();
```

프로그램 전체에서 한 번만 부르면 되니, 보통은 시작할 때 초기화하고 끝날 때 정리한다. 이 함수 안에서 매번 부르면 참조 카운트가 오르내리면서 다른 소켓 코드에 영향을 줄 수 있다.

### 이왕이면 필터도 같이

윈도우 쪽도 필터가 필요하다. 리눅스에서 `IFF_RUNNING`을 본 것과 같은 이유다.

```cpp
for (auto* p = addrs; p; p = p->Next) {
    if (p->OperStatus != IfOperStatusUp)        continue;
    if (p->IfType == IF_TYPE_SOFTWARE_LOOPBACK) continue;
    if (p->IfType != IF_TYPE_IEEE80211)         continue;   // 무선만
    // ...
}
```

`IfType`으로 유선(`IF_TYPE_ETHERNET_CSMACD`)과 무선(`IF_TYPE_IEEE80211`)이 깔끔하게 갈린다. 리눅스에서 이름으로 씨름했던 것과 대조적이다.

## 목록이 아니라 "쓰이는 IP"가 필요할 때

한동안 놓쳤던 접근이다. 위 코드들은 모든 IP를 나열해준다. 그런데 실제로 알고 싶은 건 대개 하나다. **저 상대에게 연결할 때 내 주소로 쓰이는 IP.**

인터페이스가 여러 개면 목록만 보고는 어느 게 쓰일지 모른다. 라우팅 테이블이 정한다. 그걸 커널에 물어보면 된다.

```cpp
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <string>

std::string local_ip_for(const char* peer_ip, uint16_t port = 53)
{
    int s = ::socket(AF_INET, SOCK_DGRAM, 0);
    if (s < 0) return {};

    sockaddr_in to{};
    to.sin_family = AF_INET;
    to.sin_port   = htons(port);
    inet_pton(AF_INET, peer_ip, &to.sin_addr);

    std::string result;
    if (::connect(s, reinterpret_cast<sockaddr*>(&to), sizeof(to)) == 0) {
        sockaddr_in me{};
        socklen_t len = sizeof(me);
        if (::getsockname(s, reinterpret_cast<sockaddr*>(&me), &len) == 0) {
            char buf[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &me.sin_addr, buf, sizeof(buf));
            result = buf;
        }
    }
    ::close(s);
    return result;
}
```

UDP 소켓의 `connect`는 패킷을 하나도 안 보낸다. 커널에 목적지를 알려주는 것뿐이고, 그 시점에 커널이 라우팅 테이블을 보고 소스 주소를 정한다. `getsockname`으로 그걸 읽으면 된다. 상대가 꺼져 있어도 상관없다.

윈도우에서도 소켓 API가 같아서 그대로 동작한다. 인터페이스를 나열하고 고르는 로직 전체가 이 함수 하나로 대체됐다.

## 정리하면

- `getifaddrs`는 "인터페이스 × 주소 패밀리" 목록이라 같은 이름이 여러 번 나온다
- 인터페이스 이름으로 거르면 보드나 배포판이 바뀔 때 깨진다. `IFF_UP`/`IFF_RUNNING`/`IFF_LOOPBACK` 플래그로 거른다
- `169.254.x.x`는 DHCP 실패 시 스스로 붙인 주소다. 정상 IP로 취급하면 원인이 안 보인다
- `GetAdaptersAddresses`는 `ERROR_BUFFER_OVERFLOW` 재시도가 정해진 사용법이다
- `inet_ntop`은 윈도우에서 `WSAStartup`이 필요하다
- 특정 상대에게 쓰일 내 IP만 필요하면 UDP `connect` + `getsockname`이 제일 정확하다
