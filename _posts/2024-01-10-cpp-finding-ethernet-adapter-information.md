---
title: "(C++) Windows 환경에서의 이더넷 어댑터 정보 추출"
description: ""NetworkListManager를 이용한 네트워크 인터페이스 목록 획득""
date: 2024-01-10 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, windows, ethernet, network, interface, com]
---

# Windows 환경에서의 이더넷 어댑터 정보 추출
- 최초 작성일: 2024년 1월 10일 (수)

<br/>

## 목차
1. [소개](#소개)
2. [구현 코드](#구현-코드)
3. [주요 기능 설명](#주요-기능-설명)

<br/>

## 소개
Windows 환경에서 COM 인터페이스를 통해 현재 연결된 네트워크 어댑터의 정보를 가져오는 기능을 구현한다. NetworkListManager를 사용하여 연결된 모든 네트워크 인터페이스를 열거하고, 각 인터페이스의 이름을 추출한다.

<br/>

## 구현 코드
NetworkListManager를 사용하여 Wi-Fi 인터페이스 이름을 가져오는 함수이다.

```cpp
std::vector<std::wstring> GetWifiInterfaceNames() {
    std::vector<std::wstring> wifiNames;
    HRESULT hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);
    if (SUCCEEDED(hr)) {
        INetworkListManager* pNetworkListManager;
        hr = CoCreateInstance(CLSID_NetworkListManager, NULL, CLSCTX_ALL, 
                            IID_INetworkListManager, 
                            (void**)&pNetworkListManager);
        
        if (SUCCEEDED(hr)) {
            IEnumNetworkConnections* pEnumNetworkConnections;
            hr = pNetworkListManager->GetNetworkConnections(
                &pEnumNetworkConnections);
            
            if (SUCCEEDED(hr)) {
                INetworkConnection* pNetworkConnection;
                ULONG fetched;
                while (pEnumNetworkConnections->Next(1, 
                       &pNetworkConnection, &fetched) == S_OK) {
                    VARIANT_BOOL isConnected;
                    pNetworkConnection->get_IsConnectedToInternet(&isConnected);
                    
                    if (isConnected) {
                        INetwork* pNetwork;
                        pNetworkConnection->GetNetwork(&pNetwork);
                        BSTR bstrNetworkName;
                        pNetwork->GetName(&bstrNetworkName);
                        wifiNames.push_back(bstrNetworkName);
                        SysFreeString(bstrNetworkName);
                        pNetwork->Release();
                    }
                    pNetworkConnection->Release();
                }
                pEnumNetworkConnections->Release();
            }
            pNetworkListManager->Release();
        }
        CoUninitialize();
    }
    return wifiNames;
}
```

<br/>

## 주요 기능 설명

1. **COM 초기화 관련 함수**
   - CoInitializeEx
     - COM 라이브러리를 초기화한다
     - 스레드 모델을 설정한다 (COINIT_APARTMENTTHREADED)
     - 반환값으로 초기화 성공 여부를 확인할 수 있다
   
   - CoUninitialize
     - COM 라이브러리 사용을 종료한다
     - 이전에 CoInitializeEx로 초기화한 내용을 정리한다
     - 프로그램 종료 전 반드시 호출해야 한다

2. **NetworkListManager 관련 함수**
   - CoCreateInstance
     - COM 객체의 인스턴스를 생성한다
     - CLSID_NetworkListManager: 생성할 클래스의 ID
     - IID_INetworkListManager: 사용할 인터페이스 ID
   
   - GetNetworkConnections
     - 시스템의 모든 네트워크 연결 목록을 가져온다
     - 반환된 IEnumNetworkConnections로 연결을 열거할 수 있다

3. **네트워크 연결 열거 함수**
   - Next
     - IEnumNetworkConnections의 메서드
     - 다음 네트워크 연결 정보를 가져온다
     - 매개변수: 가져올 항목 수, 연결 포인터, 실제 가져온 수

   - get_IsConnectedToInternet
     - 현재 네트워크가 인터넷에 연결되어 있는지 확인한다
     - VARIANT_BOOL 타입으로 연결 상태를 반환한다
     - TRUE: 인터넷 연결됨, FALSE: 연결되지 않음

4. **네트워크 정보 관련 함수**
   - GetNetwork
     - INetworkConnection에서 INetwork 인터페이스를 가져온다
     - 네트워크의 상세 정보에 접근할 수 있다

   - GetName
     - INetwork 인터페이스의 메서드
     - 네트워크의 이름을 BSTR 형식으로 반환한다
     - 시스템에 표시되는 네트워크 이름과 동일하다

5. **메모리 관리 함수**
   - SysFreeString
     - BSTR 타입의 문자열을 해제한다
     - Windows에서 사용하는 유니코드 문자열 메모리를 정리한다

   - Release
     - COM 객체의 참조 카운트를 감소시킨다
     - 카운트가 0이 되면 객체를 해제한다
     - 모든 COM 인터페이스 사용 후 반드시 호출해야 한다

이 코드는 Windows의 네트워크 관리 API를 사용하여 현재 시스템에 연결된 모든 네트워크 인터페이스의 이름을 가져온다. COM 인터페이스를 사용하므로 적절한 초기화와 정리 과정이 필요하며, 모든 리소스를 올바르게 해제해야 한다.
