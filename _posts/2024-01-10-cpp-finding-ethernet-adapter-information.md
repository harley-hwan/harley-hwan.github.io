---
title: "(C++) Windows 환경에서의 이더넷 어댑터 정보 추출"
description: "NetworkListManager로 인터넷에 연결된 네트워크 이름을 얻는 코드. COM 초기화가 이미 되어 있을 때의 처리, VARIANT_BOOL이 bool이 아니라는 것, 그리고 '인터넷 연결됨' 판정을 어디까지 믿을 수 있는지 정리했다."
date: 2024-01-10 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, windows, ethernet, network, interface, com, netlistmgr]
---
## 어느 망에 붙어 있는지 알아야 했다

검사 PC가 장비 AP에 붙어 있으면 사내망과는 끊긴다. 반대로 사내망에 붙어 있으면 장비와 통신이 안 된다. 검사 결과를 서버로 올리는 단계에서 이 구분이 필요했다.

IP 대역으로 판단할 수도 있는데 그건 대역이 바뀌면 깨진다. 윈도우가 이미 "이 네트워크가 인터넷에 연결되어 있는가"를 판정하고 있으니 그걸 물어보기로 했다.

## 코드

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

흐름은 이렇다. COM을 초기화하고, `NetworkListManager` 객체를 만들고, 네트워크 연결 목록을 열거자로 받고, 하나씩 꺼내면서 인터넷 연결 여부를 확인하고, 연결된 것만 이름을 가져온다.

`CoCreateInstance`의 인자는 각각 만들 클래스의 ID(`CLSID_NetworkListManager`), 컨텍스트, 받을 인터페이스의 ID(`IID_INetworkListManager`)다. `netlistmgr.h`를 포함하고 `ole32.lib`를 링크해야 한다.

COM은 참조 카운트로 수명을 관리하니 다 쓴 인터페이스마다 `Release`를 부른다. `BSTR`은 COM의 문자열 타입이라 `SysFreeString`으로 해제한다. `free`나 `delete`가 아니다.

동작은 했는데 실제로 붙이면서 몇 군데 고쳤다.

## COM이 이미 초기화되어 있을 때

이 함수를 MFC 대화상자에서 부르면 `CoInitializeEx`가 성공하지 않을 수 있다.

MFC 앱은 시작할 때 이미 COM을 STA로 초기화한 경우가 많다. 그 상태에서 같은 아파트로 다시 부르면 `S_FALSE`가 나온다. **이건 성공이다.** "이미 초기화되어 있다"는 뜻이고, 그래도 참조 카운트가 올라갔으니 `CoUninitialize`를 짝으로 불러야 한다.

문제는 다른 아파트로 부를 때다. 이미 STA인데 `COINIT_MULTITHREADED`로 부르면 `RPC_E_CHANGED_MODE`가 나온다. 이건 실패이고, **이때는 `CoUninitialize`를 부르면 안 된다.** 초기화하지 않았는데 해제하면 남의 참조 카운트를 깎는 것이다. 그러면 아직 COM을 쓰고 있는 다른 코드가 이상해진다.

`SUCCEEDED(hr)` 하나로 뭉뚱그리면 이 구분이 안 된다. 상황을 나눠야 한다.

```cpp
class ComScope {
public:
    explicit ComScope(DWORD model = COINIT_APARTMENTTHREADED) {
        const HRESULT hr = CoInitializeEx(nullptr, model);
        // S_OK: 내가 초기화했다 / S_FALSE: 이미 되어 있었다 -> 둘 다 해제 필요
        // RPC_E_CHANGED_MODE: 다른 모델로 이미 초기화됨 -> 해제하면 안 된다
        need_uninit_ = SUCCEEDED(hr);
        ok_ = SUCCEEDED(hr) || hr == RPC_E_CHANGED_MODE;
    }
    ~ComScope() { if (need_uninit_) CoUninitialize(); }
    explicit operator bool() const { return ok_; }
private:
    bool need_uninit_ = false;
    bool ok_ = false;
};
```

`RPC_E_CHANGED_MODE`여도 COM 자체는 이미 초기화되어 있으니 인터페이스를 쓸 수는 있다. 그래서 `ok_`는 참으로 둔다.

## VARIANT_BOOL은 bool이 아니다

```cpp
VARIANT_BOOL isConnected;
pNetworkConnection->get_IsConnectedToInternet(&isConnected);
if (isConnected) { ... }
```

`VARIANT_BOOL`은 `short`이고, 참이 `1`이 아니라 **`-1`(`VARIANT_TRUE`)** 이다. 거짓은 `0`(`VARIANT_FALSE`)이다.

`if (isConnected)`는 0이 아니면 참이니 우연히 맞게 동작한다. 그런데 이렇게 쓰면 틀린다.

```cpp
if (isConnected == true)  { }    // true 는 1 이라 항상 거짓
bool b = isConnected;            // -1 -> true 로 변환되긴 하지만 의도가 흐려진다
```

상수와 비교하는 게 명확하다.

```cpp
if (isConnected == VARIANT_TRUE) { }
```

그리고 이 변수가 초기화되어 있지 않다. `get_IsConnectedToInternet`이 실패하면 스택 쓰레기 값을 그대로 읽는다. 반환값을 확인하고, 변수는 초기화해두는 게 맞다.

```cpp
VARIANT_BOOL isConnected = VARIANT_FALSE;
if (FAILED(conn->get_IsConnectedToInternet(&isConnected))) continue;
```

## HRESULT를 안 보는 호출들

`GetNetwork`와 `GetName`도 반환값을 안 본다.

```cpp
INetwork* pNetwork;
pNetworkConnection->GetNetwork(&pNetwork);   // 실패하면 pNetwork 는 미초기화
BSTR bstrNetworkName;
pNetwork->GetName(&bstrNetworkName);         // 여기서 죽는다
```

`GetNetwork`가 실패하면 `pNetwork`는 초기화되지 않은 포인터다. 그걸 역참조하는 순간 Access Violation이다. 그리고 실패 경로에서 `Release`도 안 된다.

COM API는 거의 모든 함수가 `HRESULT`를 돌려준다. 검사를 매번 쓰는 게 지루해서 자꾸 빠뜨리게 되는데, 포인터를 받는 함수만큼은 반드시 봐야 한다.

## 포인터는 스마트 포인터로

`Release` 호출을 손으로 관리하면 실패 경로에서 반드시 빠뜨린다. ATL의 `CComPtr`을 쓰면 소멸자가 알아서 부른다.

```cpp
#include <atlbase.h>
#include <netlistmgr.h>
#include <vector>
#include <string>

std::vector<std::wstring> GetConnectedNetworkNames()
{
    std::vector<std::wstring> names;

    ComScope com;
    if (!com) return names;

    CComPtr<INetworkListManager> mgr;
    if (FAILED(mgr.CoCreateInstance(CLSID_NetworkListManager))) return names;

    CComPtr<IEnumNetworkConnections> e;
    if (FAILED(mgr->GetNetworkConnections(&e))) return names;

    for (;;) {
        CComPtr<INetworkConnection> conn;
        ULONG fetched = 0;
        if (e->Next(1, &conn, &fetched) != S_OK || fetched == 0) break;

        VARIANT_BOOL online = VARIANT_FALSE;
        if (FAILED(conn->get_IsConnectedToInternet(&online))) continue;
        if (online != VARIANT_TRUE) continue;

        CComPtr<INetwork> net;
        if (FAILED(conn->GetNetwork(&net))) continue;

        CComBSTR name;
        if (FAILED(net->GetName(&name))) continue;

        names.emplace_back(name.m_str, name.Length());
    }
    return names;
}
```

`CComBSTR`도 `SysFreeString`을 알아서 부른다. 그리고 `name.Length()`를 같이 넘긴 게 중요하다. `BSTR`은 길이 접두사를 들고 있고 **내부에 널 문자가 있을 수 있는** 타입이라, `std::wstring(bstr)`처럼 널 종료를 가정하면 잘릴 수 있다. 네트워크 이름에 그런 게 들어갈 일은 거의 없지만, `BSTR`을 다룰 때는 습관을 들여두는 게 낫다.

`CComPtr`을 반복문 안에 선언한 것도 의도한 것이다. 회차마다 소멸하면서 `Release`가 불린다. 밖에 두면 `Next`가 새 포인터를 덮어쓰면서 앞의 것이 샌다.

## 인터넷 연결 판정을 어디까지 믿나

이 함수의 결과가 항상 맞는 건 아니었다.

윈도우의 "인터넷 연결됨" 판정은 NLA(Network Location Awareness) 서비스가 마이크로소프트 서버에 작은 요청을 보내 응답을 확인하는 방식이다. 이 프로브가 막혀 있으면 인터넷이 되는데도 "연결 안 됨"으로 나온다.

실제로 겪은 경우들이다.

- 방화벽이 프로브 대상 도메인을 막아둔 사내망: 인터넷이 되는데 "연결 안 됨"
- 로그인이 필요한 공용 Wi-Fi(캡티브 포털): 붙자마자는 "연결됨"으로 나왔다가 나중에 바뀐다
- 프록시를 거쳐야 나가는 망: 프로브가 프록시를 안 거쳐서 실패한다

그래서 이 값을 "인터넷이 된다"의 증거로 쓰지 않고, **어느 네트워크에 붙어 있는지 구분하는 용도**로만 썼다. 네트워크 이름과 조합하면 그건 충분히 신뢰할 수 있었다.

더 확실한 건 실제로 서버에 한 번 붙어보는 것이다. 결과를 올려야 하는 서버가 정해져 있으니, 짧은 타임아웃으로 연결을 시도해보면 판정이 정확하다.

## 제목과 실제 내용의 차이

이 코드는 사실 "이더넷 어댑터 정보"를 얻지 않는다. 네트워크 이름만 얻는다. 어댑터의 IP, MAC, 속도 같은 건 안 나온다.

어댑터 정보가 필요하면 `GetAdaptersAddresses`가 맞다. [getifaddrs 글](/posts/cpp-network-interface-info-with-ifaddrs/)에 정리해뒀다.

둘을 이어 붙일 수도 있다. `INetworkConnection::GetAdapterId`가 어댑터의 GUID를 주고, `IP_ADAPTER_ADDRESSES::AdapterName`이 같은 GUID를 문자열로 들고 있다.

```cpp
GUID adapterId{};
conn->GetAdapterId(&adapterId);

wchar_t buf[64];
StringFromGUID2(adapterId, buf, 64);   // "{XXXXXXXX-....}"
// GetAdaptersAddresses 의 AdapterName 과 비교
```

이러면 "인터넷에 연결된 네트워크의 어댑터가 어느 것이고 IP가 뭔지"까지 한 번에 나온다. 제목대로 하려면 여기까지 가야 했다.

## 정리하면

- `CoInitializeEx`의 `S_FALSE`는 성공이고 해제가 필요하다. `RPC_E_CHANGED_MODE`는 실패이고 해제하면 안 된다
- `VARIANT_BOOL`의 참은 `-1`이다. `== true`로 비교하면 항상 거짓이다
- 포인터를 받는 COM 함수는 `HRESULT`를 반드시 확인한다. 실패 시 포인터는 초기화되지 않는다
- `CComPtr`, `CComBSTR`을 쓰면 실패 경로의 `Release` 누락이 없어진다
- `BSTR`은 길이 접두사가 있는 타입이다. 널 종료를 가정하지 말고 `Length()`를 쓴다
- 윈도우의 인터넷 연결 판정은 프로브 기반이라 사내망이나 프록시 환경에서 틀릴 수 있다
