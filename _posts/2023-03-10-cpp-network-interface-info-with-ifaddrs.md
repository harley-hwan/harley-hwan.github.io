---
title: "(C++) getifaddrs를 이용한 네트워크 인터페이스 정보 구현"
description: "리눅스와 윈도우 환경에서의 IP 주소 목록 추출"
date: 2023-03-10 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, linux, windows, network, ifaddrs, ip, interface]
---

# getifaddrs를 이용한 네트워크 인터페이스 정보 구현
- 최초 작성일: 2023년 3월 10일 (금)

<br/>

## 목차
1. [소개](#소개)
2. [기본 구현 - 리눅스](#기본-구현---리눅스)
3. [확장 구현 - 모든 인터페이스](#확장-구현---모든-인터페이스)
4. [크로스 플랫폼 구현](#크로스-플랫폼-구현)

<br/>

## 소개
리눅스 환경에서는 네트워크 인터페이스 정보를 가져오기 위해 ifconfig나 ip 명령어를 사용할 수 있다. 그러나 프로그래밍 방식으로는 getifaddrs 함수를 사용하여 더 효율적으로 정보를 얻을 수 있다.

<br/>

## 기본 구현 - 리눅스
Wi-Fi 인터페이스의 IP 주소를 가져오는 기본적인 구현이다.

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

#### 실행 결과:
![리눅스 Wi-Fi IP 목록](https://user-images.githubusercontent.com/68185569/224203955-c5e35379-41da-422c-8081-da33da12b77b.png)

#### 동작 원리:
1. **초기화**
   - getifaddrs 함수로 네트워크 인터페이스 정보를 가져온다
   - 실패 시 빈 벡터를 반환한다

2. **인터페이스 검색**
   - 모든 인터페이스를 순회하며 Wi-Fi 인터페이스를 찾는다
   - AF_INET(IPv4) 주소 체계만 처리한다
   - "wlan" 문자열이 포함된 인터페이스만 선택한다

3. **IP 주소 변환**
   - inet_ntop 함수로 IP 주소를 문자열로 변환한다
   - 변환된 주소를 벡터에 저장한다

<br/>

## 확장 구현 - 모든 인터페이스
모든 네트워크 인터페이스의 상세 정보를 출력하는 확장 구현이다.

```cpp
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <netdb.h>
#include <linux/if_link.h>
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

#### 실행 결과:
![모든 네트워크 인터페이스 정보](https://user-images.githubusercontent.com/68185569/224610333-a240b558-e48c-475b-b006-f9438ef9a43f.png)

#### 주요 기능:
1. **Wi-Fi 주소 검색**
   - wlan0 인터페이스의 IPv4 주소를 찾아 출력한다
   - 다른 Wi-Fi 인터페이스 이름을 사용할 경우 수정이 필요하다

2. **전체 정보 출력**
   - 모든 네트워크 인터페이스의 정보를 출력한다
   - 인터페이스 이름, 주소 체계, IP 주소를 표시한다

<br/>

## 크로스 플랫폼 구현
윈도우와 리눅스 환경에서 모두 동작하는 구현이다.

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

#### 구현 세부사항:
1. **Windows 환경**
   - GetAdaptersAddresses API를 사용한다
   - IP_ADAPTER_ADDRESSES 구조체로 정보를 가져온다
   - 모든 유니캐스트 주소를 처리한다

2. **Linux 환경**
   - getifaddrs 함수를 사용한다
   - ifaddrs 구조체로 정보를 가져온다
   - IPv4 주소만 처리한다

3. **공통 사항**
   - inet_ntop 함수로 IP 주소를 문자열로 변환한다
   - 결과를 vector<string>으로 반환한다

<br/>

## 결론
네트워크 인터페이스 정보를 가져오는 방법은 운영체제별로 다른 API를 사용해야 한다. 윈도우에서는 GetAdaptersAddresses를, 리눅스에서는 getifaddrs를 사용하여 구현할 수 있다. 이 코드는 두 환경에서 모두 동작하는 크로스 플랫폼 솔루션을 제공하며, 필요에 따라 특정 인터페이스나 주소 체계만 필터링하여 사용할 수 있다.
