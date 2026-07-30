---
title: "(C++) 주변의 블루투스 기기 스캔 및 리스트뷰 출력 (MFC)"
description: "WinRT의 BluetoothLEAdvertisementWatcher를 MFC에 붙여 BLE 기기를 스캔했다. 이름이 없는 장치가 하나로 뭉치던 문제, 콜백이 다른 스레드라서 생긴 경합, 버튼을 두 번 누르면 UI가 멎던 이유를 정리했다."
date: 2023-03-31 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, mfc, bluetooth, devices, ble, listview, blescan, bluetoothscan, winrt, thread-safety]
---
## 보드를 거치지 않고 직접 스캔하기

[앞에서는](/posts/cpp-http-client-bluetooth-device-list-boost-asio/) 스캔을 보드에 맡기고 PC는 HTTP로 결과만 받아왔다. 구조는 깔끔했는데 보드가 켜져 있어야만 목록을 볼 수 있다는 게 불편했다. 장비를 처음 세팅할 때는 보드에 아직 접속이 안 된 상태라 정작 필요한 순간에 못 쓴다.

윈도우에서 직접 스캔하기로 했다. 결과는 Acrylic BLE Analyzer로 본 것과 비슷하게 나온다.

## 환경 설정에서 먼저 막혔다

C++/WinRT를 MFC 프로젝트에 넣는 것부터 손이 갔다.

빌드하니 이런 에러가 났다.

```c++
Severity	Code	Description	Project	File	Line	Suppression State
Error	C2039	'wait_for': is not a member of 'winrt::impl'	ConsoleApplication2	C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\cppwinrt\winrt\impl\Windows.Foundation.0.h	983	
Message		see declaration of 'winrt::impl'	ConsoleApplication2	C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\cppwinrt\winrt\impl\Windows.Foundation.0.h	103	
Message		see reference to class template instantiation 'winrt::impl::consume_Windows_Foundation_IAsyncAction<D>' being compiled	ConsoleApplication2	C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\cppwinrt\winrt\impl\Windows.Foundation.0.h	985	
```

Windows SDK가 오래돼서 나는 에러다. 10.0.22621.0으로 올리니 그대로 빌드됐다. 에러 메시지가 SDK 헤더 안쪽을 가리키고 있어서 내 코드 문제로 보이는데, 경로에 SDK 버전이 찍혀 있는 게 단서였다.

필요한 것들을 정리하면 이렇다.

- NuGet에서 `Microsoft.Windows.CppWinRT` 설치
- C++ 언어 표준을 `/std:c++17` 이상으로
- Windows 10 이상, 그리고 최신 SDK

헤더는 이 정도가 필요하다.

```c++
#include <iostream>
#include <string>
#include <map>
#include <chrono>
#include <thread>
#include <winrt/Windows.Devices.Bluetooth.Advertisement.h>
#include <winrt/Windows.Foundation.h>
```

### init_apartment에서 한 번 더

콘솔 예제에는 `winrt::init_apartment()`가 들어 있다. MFC 프로젝트에 그대로 넣었더니 `RPC_E_CHANGED_MODE` 예외가 났다.

`init_apartment()`의 기본값이 멀티스레드 아파트(MTA)인데, MFC 대화상자 앱은 이미 단일 스레드 아파트(STA)로 COM이 초기화되어 있다. 한 스레드에서 아파트 모델을 바꿀 수 없어서 나는 에러다.

```c++
winrt::init_apartment(winrt::apartment_type::single_threaded);
```

이렇게 STA를 명시하면 이미 초기화된 상태와 맞아떨어진다. 아니면 아예 호출하지 않아도 된다. MFC가 이미 해준 상태라서다. 스캔을 별도 스레드에서 돌리면 그 스레드에서는 다시 초기화가 필요하다.

## 헤더와 메시지 맵

```c++
public:
  CListBox m_list_ble;
  std::map<std::wstring, int> m_bleDevices;
  std::map<std::wstring, std::chrono::steady_clock::time_point> m_bleDevicesLastSeen;

  std::thread bleScanThread;
  bool m_completed = false;
  winrt::Windows::Devices::Bluetooth::Advertisement::BluetoothLEAdvertisementWatcher m_watcher;

  void ScanForBluetoothLEDevices();
  afx_msg void OnBnClickedBtnBlescanstop();
```

```c++
BEGIN_MESSAGE_MAP(CMainDlg, CDialogEx)
  ON_MESSAGE(WM_UPDATE_BLE_LIST, &CMainDlg::OnUpdateBLEList)
END_MESSAGE_MAP()
```

`WM_UPDATE_BLE_LIST`는 `WM_USER + 1`로 정의한 사용자 메시지다. 스캔 콜백이 다른 스레드에서 오기 때문에, 리스트 박스를 직접 건드리지 않고 메시지를 던져 UI 스레드에서 처리하게 하려는 것이다. 이 방향 자체는 맞았다.

## 스캔 본체

```c++
void CMainDlg::ScanForBluetoothLEDevices()
{
  using namespace winrt::Windows::Devices::Bluetooth::Advertisement;
  try
  {
    m_completed = false;

    // Device found event
    m_watcher.Received([&](BluetoothLEAdvertisementWatcher sender, BluetoothLEAdvertisementReceivedEventArgs args)
      {
        std::wstring localName = args.Advertisement().LocalName().c_str();
        // 블루투스 기기를 맵에 저장하고 RSSI 값을 업데이트
        m_bleDevices[localName] = args.RawSignalStrengthInDBm();
        m_bleDevicesLastSeen[localName] = std::chrono::steady_clock::now();

        // 메인 스레드에서 리스트 박스를 업데이트하도록 메시지를 보냄
        PostMessage(WM_UPDATE_BLE_LIST, 0, 0);
      });

    // Stopped event
    m_watcher.Stopped([&](BluetoothLEAdvertisementWatcher sender, BluetoothLEAdvertisementWatcherStoppedEventArgs args)
      {
        m_completed = true;
      });

    // Start the watcher
    m_watcher.Start();

    // Wait until the watcher stops
    while (!m_completed)
    {
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
  }
  catch (const winrt::hresult_error& ex)
  {
    std::wcerr << L"Exception thrown: " << ex.message().c_str() << std::endl;
  }
}
```

```c++
LRESULT CMainDlg::OnUpdateBLEList(WPARAM wParam, LPARAM lParam)
{
  // 타임아웃 (예: 3초).
  const auto timeout = std::chrono::seconds(3);

  // 만료된 기기 제거
  for (auto it = m_bleDevicesLastSeen.begin(); it != m_bleDevicesLastSeen.end();)
  {
    if (std::chrono::steady_clock::now() - it->second > timeout)
    {
      m_bleDevices.erase(it->first);
      it = m_bleDevicesLastSeen.erase(it);
    }
    else
    {
      ++it;
    }
  }

  // 리스트 박스 리셋.
  m_list_ble.ResetContent();

  // 맵에 저장된 블루투스 기기를 리스트 박스에 추가
  for (const auto& device : m_bleDevices)
  {
    CString deviceInfo;
    std::string localName(device.first.begin(), device.first.end()); // Convert to std::string
    deviceInfo.Format(_T("%s - RSSI: %d"), localName.c_str(), device.second);
    m_list_ble.AddString(deviceInfo);
  }

  return 0;
}
```

`Received`가 광고 패킷을 받을 때마다 호출되고, 3초 넘게 안 보인 기기는 목록에서 지운다. 화면에는 이름과 RSSI가 나온다.

이 코드로 목록이 뜨긴 했는데, 실제로 써보니 이상한 게 여러 개 있었다.

## 이름 없는 장치들이 하나로 뭉친다

가장 먼저 눈에 띈 문제다. 주변에 BLE 기기가 여럿인데 목록에 몇 개밖에 안 나온다.

BLE 광고 패킷에 **이름이 없는 경우가 대부분**이다. 광고 패킷은 31바이트뿐이라 제조사 데이터나 서비스 UUID로 채우고 이름은 생략하는 기기가 많다. 그러면 `LocalName()`이 빈 문자열이 된다.

맵의 키가 이름이니, 이름 없는 기기 열 개가 전부 같은 키로 들어가서 **하나로 합쳐진다**. RSSI는 마지막에 온 것으로 계속 덮어써지니 값이 계속 튄다.

키는 주소여야 한다. `BluetoothAddress()`가 64비트 정수로 주소를 준다.

```c++
struct BleDevice {
    uint64_t     address;
    std::wstring name;
    int16_t      rssi;
    std::chrono::steady_clock::time_point last_seen;
};
std::map<uint64_t, BleDevice> m_devices;    // 주소가 키

// 콜백에서
const uint64_t addr = args.BluetoothAddress();
auto& d = m_devices[addr];
d.address = addr;
d.rssi = args.RawSignalStrengthInDBm();
d.last_seen = std::chrono::steady_clock::now();
if (!args.Advertisement().LocalName().empty())
    d.name = args.Advertisement().LocalName().c_str();   // 있을 때만 갱신
```

이름은 "있을 때만" 갱신하는 게 중요하다. 같은 기기가 이름이 든 패킷과 안 든 패킷을 번갈아 보내는 경우가 있어서, 매번 덮어쓰면 이름이 깜빡인다.

이름을 더 잘 받으려면 스캔을 능동 모드로 바꾼다.

```c++
m_watcher.ScanningMode(BluetoothLEScanningMode::Active);
```

능동 모드는 광고를 받으면 스캔 요청을 보내서 추가 응답(Scan Response)까지 받는다. 이름은 대개 여기 들어 있다. 대신 전파를 더 쓰고 배터리 소모가 늘어난다는 게 상대 기기 입장의 단점이다.

주소를 화면에 보여줄 때는 MAC 형식으로 바꾸면 익숙하다.

```c++
CString AddrToString(uint64_t a) {
    CString s;
    s.Format(_T("%02X:%02X:%02X:%02X:%02X:%02X"),
             (BYTE)(a >> 40), (BYTE)(a >> 32), (BYTE)(a >> 24),
             (BYTE)(a >> 16), (BYTE)(a >> 8),  (BYTE)a);
    return s;
}
```

## 콜백이 다른 스레드에서 온다

`Received` 콜백은 WinRT의 스레드 풀에서 호출된다. 그런데 `m_bleDevices`와 `m_bleDevicesLastSeen`을 콜백에서 쓰고, `OnUpdateBLEList`(UI 스레드)에서도 순회하며 지운다. **같은 맵을 두 스레드가 동시에 만진다.**

`std::map`은 스레드 안전하지 않다. 한쪽이 노드를 삽입하는 중에 다른 쪽이 순회하면 반복자가 깨지거나 그대로 죽는다. 이게 눈에 잘 안 띄는 이유는, 광고 패킷이 뜸하면 두 스레드가 겹칠 확률이 낮아서다. 기기가 많은 곳에 가면 그때 죽는다.

뮤텍스로 감싸야 한다.

```c++
std::mutex m_mutex;

// 콜백
{
    std::lock_guard<std::mutex> lock(m_mutex);
    // 맵 갱신
}

// UI 스레드
std::vector<BleDevice> snapshot;
{
    std::lock_guard<std::mutex> lock(m_mutex);
    for (const auto& [addr, d] : m_devices) snapshot.push_back(d);
}
// 락을 놓고 나서 화면에 그린다
```

락을 잡은 채로 리스트 박스를 그리면 그동안 콜백이 막힌다. 복사본만 뜬 다음 락을 풀고 그리는 편이 낫다.

`m_completed`도 그냥 `bool`이라 스레드 간 가시성이 보장되지 않는다. 최적화에 따라 다른 스레드의 변경이 안 보일 수 있다. `std::atomic<bool>`로 바꿔야 한다.

## PostMessage를 광고마다 보내면 UI가 멎는다

`Received` 콜백에서 매번 `PostMessage`를 보낸다. BLE 광고는 기기 하나가 초당 여러 번 보내고, 주변에 기기가 스무 개면 초당 수백 건이다.

메시지가 올 때마다 `OnUpdateBLEList`가 돌면서 리스트 박스를 통째로 지우고 다시 채운다. UI 스레드가 그것만 하다가 클릭에 반응을 못 한다. 실제로 사무실에서 켜니 창이 버벅였다.

주기적으로만 갱신하면 된다.

```c++
// 대화상자에서 타이머 하나
SetTimer(ID_BLE_REFRESH, 500, nullptr);      // 0.5초마다

void CMainDlg::OnTimer(UINT_PTR id) {
    if (id == ID_BLE_REFRESH) RefreshBleList();
    CDialogEx::OnTimer(id);
}
```

콜백은 맵만 갱신하고 UI는 건드리지 않는다. 화면은 0.5초마다 새로 그린다. 사람이 보기에는 차이가 없고 UI는 멀쩡해졌다.

만료된 기기를 지우는 로직도 이쪽으로 오는 게 맞다. 원래 코드는 `OnUpdateBLEList` 안에 있어서, 광고가 하나도 안 오면 메시지도 안 오고 청소도 안 된다. 즉 **모든 기기가 사라져도 목록이 그대로 남는다**. 타이머로 옮기면 이 문제도 같이 해결된다.

## 문자열 변환이 깨진다

```c++
std::string localName(device.first.begin(), device.first.end());
deviceInfo.Format(_T("%s - RSSI: %d"), localName.c_str(), device.second);
```

두 줄 다 문제다.

첫 줄은 `wchar_t`를 하나씩 `char`로 잘라 넣는다. 아스키 범위 밖 문자는 다 깨진다. BLE 기기 이름에 한글이나 이모지가 들어가는 경우가 있어서 실제로 깨졌다.

둘째 줄은 유니코드 빌드에서 `_T("%s")`가 `L"%s"`이고 와이드 포맷의 `%s`는 `wchar_t*`를 기대하는데, `localName.c_str()`은 `const char*`다. [파일명 만들 때 겪은 것](/posts/cpp-file-naming-methods/)과 같은 실수다.

애초에 변환할 이유가 없다. `CString`은 유니코드 빌드에서 와이드 문자열이니 `std::wstring`을 그대로 넣으면 된다.

```c++
deviceInfo.Format(_T("%s - RSSI: %d"), d.name.c_str(), d.rssi);
```

## 버튼을 두 번 누르면 UI가 멈춘다

```c++
void CMainDlg::OnBnClickedBtnBlescan()
{
  // 기존 스레드가 실행 중이면 종료하고 새로 시작
  if (bleScanThread.joinable())
  {
    bleScanThread.join();
  }
  bleScanThread = std::thread(&CMainDlg::ScanForBluetoothLEDevices, this);
}
```

주석에는 "기존 스레드가 실행 중이면 종료"라고 되어 있는데 `join()`은 종료시키는 함수가 아니다. **스레드가 스스로 끝날 때까지 기다리는** 함수다.

`ScanForBluetoothLEDevices`는 `while (!m_completed)`로 무한 대기 중이고, 아무도 `Stop()`을 안 부르면 안 끝난다. 그러니 스캔 버튼을 두 번 누르면 UI 스레드가 `join()`에서 영원히 멈춘다. 창이 통째로 얼어붙는다.

먼저 멈추게 하고 나서 기다려야 한다.

```c++
void CMainDlg::StopScan()
{
    if (!bleScanThread.joinable()) return;
    m_watcher.Stop();          // Stopped 콜백이 m_completed 를 세운다
    bleScanThread.join();
}

void CMainDlg::OnBnClickedBtnBlescan()
{
    StopScan();
    m_completed = false;
    bleScanThread = std::thread(&CMainDlg::ScanForBluetoothLEDevices, this);
}
```

정지 버튼 쪽도 순서가 뒤집혀 있었다.

```c++
void CMainDlg::OnBnClickedBtnBlescanstop()
{
  if (bleScanThread.joinable())
  {
    m_completed = true;        // 먼저 세워버린다
    m_watcher.Stop();
    bleScanThread.join();
  }
}
```

`m_completed = true`를 먼저 하면 대기 루프가 바로 빠져나온다. `Stopped` 콜백이 오기 전에 함수가 끝나는 것이라, watcher가 아직 정리되지 않은 상태에서 다음 스캔을 시작할 수 있다. `Stop()`만 부르고 콜백이 플래그를 세우게 두는 게 맞다.

**대화상자를 닫을 때 스레드를 정리하는 코드가 없다**는 것도 문제였다. `OnDestroy`나 소멸자에서 `StopScan()`을 안 부르면, 아직 도는 `std::thread`가 소멸되면서 `std::terminate`가 불린다. 프로그램을 끌 때 가끔 오류 대화상자가 뜨던 게 이거였다.

## 한 번만 갱신하는 버전

계속 갱신하는 대신 버튼을 누른 시점의 결과만 한 번 보여주도록 바꾼 버전이다. 이름 필터도 넣었다.

```c++
void CMainDlg::ScanForBluetoothLEDevices()
{
	using namespace winrt::Windows::Devices::Bluetooth::Advertisement;
	try
	{
		BluetoothLEAdvertisementWatcher watcher;
		m_completed = false;

		watcher.Received([&](BluetoothLEAdvertisementWatcher sender, BluetoothLEAdvertisementReceivedEventArgs args)
			{
				std::wstring localName = args.Advertisement().LocalName().c_str();
				if (localName.find(L"BLE") == 0)
				{
					m_bleDevices[localName] = args.RawSignalStrengthInDBm();
					m_bleDevicesLastSeen[localName] = std::chrono::steady_clock::now();
				}
			});

		watcher.Stopped([&](BluetoothLEAdvertisementWatcher sender, BluetoothLEAdvertisementWatcherStoppedEventArgs args)
			{
				m_completed = true;
			});

		watcher.Start();

		// 2초간 스캔
		std::this_thread::sleep_for(std::chrono::seconds(2));

		watcher.Stop();

		while (!m_completed)
		{
			std::this_thread::sleep_for(std::chrono::milliseconds(100));
		}

		PostMessage(WM_UPDATE_BLE_LIST, 0, 0);
	}
	catch (const winrt::hresult_error& ex)
	{
		std::wcerr << L"Exception thrown: " << ex.message().c_str() << std::endl;
	}
}
```

`PostMessage`가 스캔이 끝난 뒤 한 번만 호출되니 UI 부담이 없다. 여기서 `watcher`를 멤버가 아니라 지역 변수로 만든 것도 낫다. 스캔이 끝나면 같이 없어져서 상태가 남지 않는다.

다만 `OnBnClickedBtnBlescan`이 이 함수를 UI 스레드에서 직접 부르면 2초 동안 창이 멈춘다. 스레드로 돌리고 완료를 메시지로 받는 게 맞다.

콘솔에서 확인할 때 쓴 버전도 남겨둔다. MFC 없이 동작을 먼저 확인할 때 유용했다.

```c++
#include <winrt/Windows.Devices.Bluetooth.Advertisement.h>
#include <winrt/Windows.Foundation.h>
#include <iostream>
#include <map>
#include <thread>
#include <chrono>

int main()
{
    using namespace winrt::Windows::Devices::Bluetooth::Advertisement;
    winrt::init_apartment();

    std::map<uint64_t, std::pair<std::wstring, int16_t>> devices;
    std::mutex mtx;

    BluetoothLEAdvertisementWatcher watcher;
    watcher.ScanningMode(BluetoothLEScanningMode::Active);

    watcher.Received([&](auto&&, BluetoothLEAdvertisementReceivedEventArgs args)
        {
            std::lock_guard<std::mutex> lock(mtx);
            auto& d = devices[args.BluetoothAddress()];
            d.second = args.RawSignalStrengthInDBm();
            if (!args.Advertisement().LocalName().empty())
                d.first = args.Advertisement().LocalName().c_str();
        });

    watcher.Start();
    std::this_thread::sleep_for(std::chrono::seconds(5));
    watcher.Stop();

    std::lock_guard<std::mutex> lock(mtx);
    for (const auto& [addr, d] : devices)
        std::wcout << std::hex << addr << L"  " << d.second << L" dBm  " << d.first << L"\n";

    return 0;
}
```

## 정리하면

- BLE 광고에는 이름이 없는 경우가 많다. 맵의 키는 `BluetoothAddress()`여야 한다. 이름은 있을 때만 갱신
- `Received` 콜백은 다른 스레드에서 온다. 공유 컨테이너는 뮤텍스로 보호하고, 플래그는 `std::atomic`
- 광고마다 `PostMessage`를 보내면 UI가 멎는다. 콜백은 데이터만 갱신하고 화면은 타이머로 주기 갱신
- `join()`은 스레드를 끝내지 않는다. `Stop()`을 먼저 부르고 기다려야 한다
- 대화상자를 닫을 때 스레드를 정리하지 않으면 `std::terminate`가 불린다
- MFC에 WinRT를 붙일 때는 `init_apartment`의 아파트 모델을 STA로 맞추거나 아예 부르지 않는다
- 빌드 에러가 SDK 헤더 안쪽을 가리키면 SDK 버전부터 확인한다

## 참고

- [BluetoothLEAdvertisementWatcher](https://learn.microsoft.com/en-us/uwp/api/windows.devices.bluetooth.advertisement.bluetoothleadvertisementwatcher)
- [C++/WinRT 시작하기](https://learn.microsoft.com/en-us/windows/uwp/cpp-and-winrt-apis/get-started)
