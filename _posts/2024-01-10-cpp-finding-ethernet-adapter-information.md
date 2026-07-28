---
title: "(C++) Windows 환경에서의 이더넷 어댑터 정보 추출"
description: "NetworkListManager를 이용한 네트워크 인터페이스 목록 획득"
date: 2024-01-10 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, windows, ethernet, network, interface, com]
---
<br/>

## 소개
Windows 환경에서 COM 인터페이스를 통해 현재 인터넷에 연결된 네트워크의 이름을 가져오는 기능을 구현한다. NetworkListManager는 이더넷 어댑터를 포함한 시스템의 네트워크 연결을 열거하며, 그중 인터넷에 연결된 네트워크의 이름을 추출한다.

<br/>

## 구현 코드
NetworkListManager를 사용하여 인터넷에 연결된 네트워크의 이름을 가져오는 함수이다.

```cpp
std::vector<std::wstring> GetConnectedNetworkNames() {
    std::vector<std::wstring> networkNames;
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
                        networkNames.push_back(bstrNetworkName);
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
    return networkNames;
}
```

<br/>

## 주요 기능 설명

먼저 CoInitializeEx로 COM 라이브러리를 초기화한다. 스레드 모델은 COINIT_APARTMENTTHREADED로 지정하고, 반환값으로 초기화 성공 여부를 확인한다. 작업이 끝나면 CoUninitialize를 호출해 초기화했던 내용을 정리한다.

CoCreateInstance는 COM 객체의 인스턴스를 생성한다. CLSID_NetworkListManager가 생성할 클래스의 ID, IID_INetworkListManager가 사용할 인터페이스 ID다. 이렇게 얻은 NetworkListManager에서 GetNetworkConnections를 호출하면 시스템의 모든 네트워크 연결 목록을 IEnumNetworkConnections로 받아 열거할 수 있다.

IEnumNetworkConnections의 Next는 네트워크 연결 정보를 하나씩 가져온다. 매개변수는 가져올 항목 수, 연결 포인터, 실제로 가져온 수다. 각 연결에 대해 get_IsConnectedToInternet을 호출하면 인터넷 연결 여부가 VARIANT_BOOL로 반환된다.

인터넷에 연결된 연결이라면 GetNetwork로 INetworkConnection에서 INetwork 인터페이스를 얻어 네트워크의 상세 정보에 접근한다. GetName은 네트워크 이름을 BSTR 형식으로 반환하는데, 시스템에 표시되는 네트워크 이름과 동일하다.

BSTR 문자열은 SysFreeString으로 해제하고, 사용이 끝난 COM 인터페이스는 Release로 참조 카운트를 감소시킨다. 카운트가 0이 되면 객체가 해제된다. COM 기반 코드이므로 초기화와 리소스 해제를 빠뜨리지 않아야 한다.
