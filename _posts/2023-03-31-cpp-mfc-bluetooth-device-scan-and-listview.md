---
title: (c++) 주변의 블루투스 기기 스캔 및 리스트뷰 출력 (MFC)
description: "c++, mfc, bluetooth, devices, ble, listview, blescan, bluetoothscan, acrylicbleanalyzer, arcrylic, analyzer"
date: 2023-03-31 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, mfc, bluetooth, devices, ble, listview, blescan, bluetoothscan, arcrylic, analyzer]
---

# 주변의 모든 블루투스 기기 스캔하여 MFC 리스트 뷰에 출력
- 최초 작성일: 2023년 3월 31일 (금)

## 목차

[TOC]

<br/>

## 내용

주변의 모든 블루투스 기기를 스캔하고, 해당 기기의 장치명(LocalName)과 SSID(신호 세기) 를 출력하는 프로그램이며,

Acrylic Suite 의 "Acrylic BLE Analyzer" 앱을 사용했을 때의 결과와 비슷한 결과를 출력한다.

<br/>

이 프로그램을 사용하면, 주변의 블루투스 기기들을 스캔하고 조건에 맞는 기기들을 리스트 박스에 출력할 수 있다. 

필요에 따라 기기 이름 필터와 스캔 시간을 조정하여 검색 결과를 개선할 수 있다.

<br/>

<br/>

### 코드 구성

1. __using namespace winrt::Windows::Devices::Bluetooth::Advertisement;__ 를 사용하여 블루투스 Advertisement API를 사용할 수 있도록 한다.
2. __BluetoothLEAdvertisementWatcher watcher;__ 객체를 생성한다. 이 객체는 블루투스 Low Energy 장치를 검색하는 데 사용된다.
3. __watcher.Received__ 이벤트 핸들러를 설정한다. 이 이벤트는 블루투스 LE Advertisement 패킷이 수신될 때마다 호출된다. 여기에서 각 기기의 이름을 가져와 필터링 조건을 확인한다. 조건에 맞는 기기들은 __m_bleDevices__ 맵에 저장되고, 해당 기기의 RSSI 값이 업데이트된다.
4. __watcher.Stopped__ 이벤트 핸들러를 설정한다. 이 이벤트는 블루투스 LE Advertisement Watcher가 중지될 때 호출된다.
5. __watcher.Start();__ 를 호출하여 블루투스 LE Advertisement Watcher를 시작한다. 이 시점부터 __watcher.Received__ 이벤트 핸들러가 호출되기 시작한다.
6. __std::this_thread::sleep_for(std::chrono::seconds(5));__ 를 사용하여 스캔 시간을 정의한다. 이 예에서는 5초 동안 스캔한다.
7. 스캔 시간이 지나면 __watcher.Stop();__ 를 호출하여 블루투스 LE Advertisement Watcher를 중지한다.
8. __m_completed__ 변수를 사용하여 Watcher가 완전히 중지될 때까지 기다린다.
9. 스캔이 완료되면 __PostMessage(WM_UPDATE_BLE_LIST, 0, 0);__ 를 호출하여 메인 스레드에서 리스트 박스를 업데이트하도록 메시지를 보낸다.

<br/>

<br/>

## 참고

만약, 빌드 시 아래와 같은 에러가 발생한다면, Windows SDK Version을 업데이트해주어야 한다.

필자는 10.0.22621.0 버전으로 업데이트해주니 문제없이 빌드되었다.

```c++
Severity	Code	Description	Project	File	Line	Suppression State
Error	C2039	'wait_for': is not a member of 'winrt::impl'	ConsoleApplication2	C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\cppwinrt\winrt\impl\Windows.Foundation.0.h	983	
Message		see declaration of 'winrt::impl'	ConsoleApplication2	C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\cppwinrt\winrt\impl\Windows.Foundation.0.h	103	
Message		see reference to class template instantiation 'winrt::impl::consume_Windows_Foundation_IAsyncAction<D>' being compiled	ConsoleApplication2	C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\cppwinrt\winrt\impl\Windows.Foundation.0.h	985	
```
<br/>

또한, 다음 헤더 파일들을 include 해야한다.

<br/>

```c++
#include <iostream>
#include <string>
#include <map>
#include <chrono>
#include <thread>
#include <winrt/Windows.Devices.Bluetooth.Advertisement.h>
#include <winrt/Windows.Foundation.h>
```

<br/>

또한, 이 코드는 Windows 10 (또는 그 이상)에서만 실행되며, Windows Runtime C++ Template Library (WinRT C++ /20)와 함께 사용되어야 한다.

WinRT를 사용하려면 프로젝트에 필요한 NuGet 패키지를 설치해야 한다. 

Visual Studio에서 프로젝트를 클릭한 후 "Manage NuGet Packages"를 선택하고 "Microsoft.Windows.CppWinRT"를 찾아 설치한다.

그런 다음 프로젝트 속성에서 C++ 언어 표준을 "/std:c++17" 또는 그 이상으로 설정해야한다.

이 코드가 클래스의 멤버 함수로 작성되어 있다고 가정하면, 해당 클래스 선언을 헤더 파일에 추가해야 한다. 

예를 들면 다음과 같다.

<br/>

```c++
#pragma once
#include <winrt/Windows.Devices.Bluetooth.Advertisement.h>
#include <map>
#include <string>
#include <chrono>

class CMainDlg
{
public:
    void ScanForBluetoothLEDevices();

private:
    winrt::Windows::Devices::Bluetooth::Advertisement::BluetoothLEAdvertisementWatcher m_watcher;
    std::map<std::wstring, int16_t> m_bleDevices;
    std::map<std::wstring, std::chrono::steady_clock::time_point> m_bleDevicesLastSeen;
    bool m_completed;
    static constexpr UINT WM_UPDATE_BLE_LIST = WM_USER + 1; // 사용자 정의 메시지
};

```

<br/>

## 소스 (MFC)

#### MainDlg.h

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

<br/>

#### MainDlg.cpp

```c++
BEGIN_MESSAGE_MAP(CMainDlg, CDialogEx)
  ON_MESSAGE(WM_UPDATE_BLE_LIST, &CMainDlg::OnUpdateBLEList)
END_MESSAGE_MAP()
```

<br/>

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

<br/>

```c++
void CMainDlg::ScanForBluetoothLEDevices()
{
  using namespace winrt::Windows::Devices::Bluetooth::Advertisement;
  try
  {
    BluetoothLEAdvertisementWatcher watcher;
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

void CMainDlg::OnBnClickedBtnBlescan()
{
  // 기존 스레드가 실행 중이면 종료하고 새로 시작
  if (bleScanThread.joinable())
  {
    bleScanThread.join();
  }
  bleScanThread = std::thread(&CMainDlg::ScanForBluetoothLEDevices, this);
}


void CMainDlg::OnBnClickedBtnBlescanstop()
{
  // 기존 스레드가 실행 중이면 종료
  if (bleScanThread.joinable())
  {
    m_completed = true;
    m_watcher.Stop();
    bleScanThread.join();
  }
}
```

<br/>

<br/>

<br/>

### 추가 소스

위의 소스는 쓰레드를 이용하여, 최신 정보를 계속적으로 갱신하는 구조이다.

필요에 의해, 버튼 클릭 이벤트가 있을 때만 해당 시점의 최신 정보를 한 번 갱신하도록 수정해보았다.

또한, 원하는 문자열이 들어간 블루투스 기기만 출력하도록 하였다.

<br/>

```c++
// 블루투스 기기 목록을 리스트 박스에 출력하는 메시지 핸들러
LRESULT CMainDlg::OnUpdateBLEList(WPARAM wParam, LPARAM lParam)
{
	// 리스트 박스 (IDC_LIST_BLE_DEVICES: 리스트 박스의 리소스 ID).
	//CListBox* pListBox = (CListBox*)GetDlgItem(IDC_LIST_BLE);
	//if (pListBox == nullptr)
	//{
	//	return 0;
	//}

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

<br/>

```c++
void CMainDlg::ScanForBluetoothLEDevices()
{
	using namespace winrt::Windows::Devices::Bluetooth::Advertisement;
	try
	{
		BluetoothLEAdvertisementWatcher watcher;
		m_completed = false;

		// Device found event
		watcher.Received([&](BluetoothLEAdvertisementWatcher sender, BluetoothLEAdvertisementReceivedEventArgs args)
			{
				std::wstring localName = args.Advertisement().LocalName().c_str();
				if (localName.find(L"BLE") == 0)
				{
					// 블루투스 기기를 맵에 저장하고 RSSI 값을 업데이트
					m_bleDevices[localName] = args.RawSignalStrengthInDBm();
					m_bleDevicesLastSeen[localName] = std::chrono::steady_clock::now();
				}
			});

		// Stopped event
		watcher.Stopped([&](BluetoothLEAdvertisementWatcher sender, BluetoothLEAdvertisementWatcherStoppedEventArgs args)
			{
				m_completed = true;
			});

		// Start the watcher
		watcher.Start();

		// Wait for a short period of time (e.g., 2 seconds) to allow the watcher to scan devices
		std::this_thread::sleep_for(std::chrono::seconds(2));

		// Stop the watcher
		watcher.Stop();

		// Wait until the watcher stops
		while (!m_completed)
		{
			std::this_thread::sleep_for(std::chrono::milliseconds(100));
		}

		// 메인 스레드에서 리스트 박스를 업데이트하도록 메시지를 보냄
		PostMessage(WM_UPDATE_BLE_LIST, 0, 0);
	}
	catch (const winrt::hresult_error& ex)
	{
		std::wcerr << L"Exception thrown: " << ex.message().c_str() << std::endl;
	}
}


// "BLE SCAN" Button
void CMainDlg::OnBnClickedBtnBlescan()
{
	ScanForBluetoothLEDevices();
}

```

<br/>

---

<br/>

## 소스 (C++)

```c++
#include <winrt/Windows.Devices.Bluetooth.Advertisement.h>
#include <winrt/Windows.Foundation.h>
#include <iostream>
#include <string>
#include <map>
#include <thread>
#include <chrono>

class BluetoothLEScanner
{
public:
    void ScanForBluetoothLEDevices()
    {
        using namespace winrt::Windows::Devices::Bluetooth::Advertisement;
        try
        {
            BluetoothLEAdvertisementWatcher watcher;
            m_completed = false;

            // Device found event
            watcher.Received([&](BluetoothLEAdvertisementWatcher sender, BluetoothLEAdvertisementReceivedEventArgs args)
                {
                    std::wstring localName = args.Advertisement().LocalName().c_str();
                    if (localName.find(L"BLE") == 0)
                    {
                        // Save the Bluetooth device in the map and update the RSSI value
                        m_bleDevices[localName] = args.RawSignalStrengthInDBm();
                        m_bleDevicesLastSeen[localName] = std::chrono::steady_clock::now();
                    }
                });

            // Stopped event
            watcher.Stopped([&](BluetoothLEAdvertisementWatcher sender, BluetoothLEAdvertisementWatcherStoppedEventArgs args)
                {
                    m_completed = true;
                });

            // Start the watcher
            watcher.Start();

            // Wait for a short period of time (e.g., 2 seconds) to allow the watcher to scan devices
            std::this_thread::sleep_for(std::chrono::seconds(2));

            // Stop the watcher
            watcher.Stop();

            // Wait until the watcher stops
            while (!m_completed)
            {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }

            // Update the list of devices
            UpdateDeviceList();
        }
        catch (const winrt::hresult_error& ex)
        {
            std::wcerr << L"Exception thrown: " << ex.message().c_str() << std::endl;
        }
    }

private:
    void UpdateDeviceList()
    {
        for (const auto& device : m_bleDevices)
        {
            std::wcout << L"Device: " << device.first << L" RSSI: " << device.second << std::endl;
        }
    }

    bool m_completed;
    std::map<std::wstring, int16_t> m_bleDevices;
    std::map<std::wstring, std::chrono::steady_clock::time_point> m_bleDevicesLastSeen;
};

int main()
{
    winrt::init_apartment();
    BluetoothLEScanner scanner;
    scanner.ScanForBluetoothLEDevices();
    return 0;
}

```
