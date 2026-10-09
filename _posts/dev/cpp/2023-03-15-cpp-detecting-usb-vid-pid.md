---
title: "(C++) 현재 연결된 USB들의 VID/PID 검출"
description: "COM 포트 번호가 매번 바뀌어서 VID/PID로 장치를 찾기로 했다. libusb로 열거하는 방법과, 윈도우에서는 libusb 대신 SetupAPI를 써야 했던 이유를 정리했다."
date: 2023-03-15 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, libusb, usb, device, vid, pid, setupapi, windows]
---
## COM 포트 번호를 못 믿겠다

장비를 USB로 연결하면 가상 COM 포트가 잡힌다. 문제는 이 번호가 고정이 아니라는 것이다. 다른 USB 장치를 먼저 꽂았거나, 허브를 바꿔 꽂거나, 재부팅 순서가 달라지면 COM3이던 게 COM7이 된다.

설정 파일에 포트 번호를 적어두는 방식은 현장에서 계속 어긋났다. 장치 자체를 식별해서 그 장치의 포트 번호를 찾는 쪽으로 가야 했다. USB 장치는 VID(제조사 ID)와 PID(제품 ID)를 가지고 있으니 그걸 기준으로 잡으면 된다.

## libusb로 열거하기

```c++
#include <iostream>
#include <libusb/libusb.h>

int main() {
    libusb_context* ctx;
    libusb_device** devs;
    int r;
    ssize_t cnt;

    r = libusb_init(&ctx);
    if (r < 0) {
        std::cerr << "libusb_init error: " << libusb_error_name(r) << std::endl;
        return r;
    }

    cnt = libusb_get_device_list(ctx, &devs);
    if (cnt < 0) {
        std::cerr << "libusb_get_device_list error: " << libusb_error_name(cnt) << std::endl;
        libusb_exit(ctx);
        return static_cast<int>(cnt);
    }

    for (ssize_t i = 0; i < cnt; i++) {
        libusb_device* device = devs[i];
        libusb_device_descriptor desc;

        int result = libusb_get_device_descriptor(device, &desc);
        if (result >= 0) {
            std::cout << "VID: " << std::hex << static_cast<int>(desc.idVendor) << ", PID: " << static_cast<int>(desc.idProduct) << std::endl;
        }
    }

    libusb_free_device_list(devs, 1);
    libusb_exit(ctx);
    return 0;
}
```

![연결된 USB 장치의 VID/PID](/assets/img/posts/cpp-detecting-usb-vid-pid/001-225209108-e4f78b75-72b3-4acf-82f4-89e8dc5bc06a.png)

`libusb_init`으로 컨텍스트를 만들고, `libusb_get_device_list`로 장치 배열과 개수를 받고, 각각에서 디스크립터를 읽는다. 마지막에 `libusb_free_device_list(devs, 1)`로 목록을 해제하는데, 두 번째 인자 1은 각 장치의 참조 카운트도 같이 내리라는 뜻이다. 0을 주면 장치 객체가 안 없어진다.

`libusb_get_device_descriptor`는 장치를 열지 않아도 된다. libusb가 열거 과정에서 이미 받아둔 값을 돌려주기 때문이다. 그래서 권한 없이도 VID/PID까지는 볼 수 있다.

## 출력 포맷이 틀렸다

찍힌 값을 실제 장치 관리자의 값과 대조하다가 알았다.

```c++
std::cout << "VID: " << std::hex << (int)desc.idVendor
```

`std::hex`는 한 번 걸면 스트림에 계속 남는다. 이 줄 이후의 모든 정수 출력이 16진수가 된다. 루프 안에 있으니 문제가 안 보이지만, 뒤에 다른 값을 찍는 코드를 넣으면 그때 이상해진다.

자리 채움이 없는 것도 문제다. VID `0x0403`이 `403`으로 찍힌다. `0x0483`과 `0x483`을 눈으로 비교하다 보면 헷갈린다.

```c++
#include <cstdio>
std::printf("VID: %04X  PID: %04X\n", desc.idVendor, desc.idProduct);
```

스트림으로 하려면 이렇게 된다.

```c++
std::cout << std::hex << std::uppercase << std::setfill('0')
          << "VID: " << std::setw(4) << desc.idVendor
          << "  PID: " << std::setw(4) << desc.idProduct << '\n'
          << std::dec << std::setfill(' ');      // 되돌리기
```

되돌리는 줄이 꼭 필요하다. 이걸 안 해서 나중에 찍은 개수가 16진수로 나오는 걸 한참 못 알아봤다.

`libusb_error_name(cnt)`도 정확하지 않다. `cnt`는 `ssize_t`이고 이 함수는 `int`를 받는다. 64비트에서 축소 변환이라 컴파일러가 경고를 준다. `static_cast<int>(cnt)`로 넘기면 된다.

## 윈도우에서 libusb는 답이 아니었다

여기까지 하고 실제 프로그램에 넣으려니 벽에 부딪혔다.

윈도우에서 libusb가 장치를 **열려면** WinUSB나 libusbK 같은 드라이버가 그 장치에 바인딩되어 있어야 한다. 그런데 우리 장치는 가상 COM 포트로 쓰고 있으니 이미 CDC 드라이버가 잡고 있다. Zadig 같은 도구로 드라이버를 WinUSB로 바꾸면 libusb로 열리는 대신 **COM 포트가 사라진다**. 포트 번호를 찾으려고 시작한 일인데 포트가 없어지는 셈이다.

열거만 하는 건 되지만, 열거해서 VID/PID를 안다고 해도 그게 몇 번 COM 포트인지는 libusb가 모른다. libusb는 USB 레벨만 보고 윈도우가 그 위에 얹은 COM 포트 매핑은 관심 밖이다.

윈도우에서 필요한 건 SetupAPI다.

## SetupAPI로 VID/PID와 COM 포트를 같이

윈도우는 장치마다 인스턴스 ID를 가지고 있고, 거기에 VID와 PID가 문자열로 들어 있다.

```text
USB\VID_0403&PID_6001\A50285BI
```

COM 포트 클래스만 열거하면서 이 문자열을 확인하면, VID/PID가 맞는 장치의 포트 이름을 바로 얻을 수 있다.

```cpp
#include <windows.h>
#include <setupapi.h>
#include <string>
#include <vector>
#pragma comment(lib, "setupapi.lib")

// 지정한 VID/PID 를 가진 장치의 COM 포트 이름들을 돌려준다
std::vector<std::wstring> FindComPorts(unsigned short vid, unsigned short pid)
{
    std::vector<std::wstring> ports;

    HDEVINFO set = SetupDiGetClassDevsW(&GUID_DEVCLASS_PORTS, nullptr, nullptr,
                                        DIGCF_PRESENT);
    if (set == INVALID_HANDLE_VALUE) return ports;

    wchar_t want[32];
    swprintf_s(want, L"VID_%04X&PID_%04X", vid, pid);

    SP_DEVINFO_DATA info{};
    info.cbSize = sizeof(info);

    for (DWORD i = 0; SetupDiEnumDeviceInfo(set, i, &info); ++i) {
        wchar_t id[512] = {};
        if (!SetupDiGetDeviceInstanceIdW(set, &info, id, _countof(id), nullptr))
            continue;

        // 대소문자가 섞여 나올 수 있어 대문자로 맞춰 비교한다
        std::wstring sid(id);
        for (auto& c : sid) c = towupper(c);
        if (sid.find(want) == std::wstring::npos) continue;

        // 이 장치의 레지스트리 키에서 PortName 을 읽는다
        HKEY key = SetupDiOpenDevRegKey(set, &info, DICS_FLAG_GLOBAL, 0,
                                        DIREG_DEV, KEY_READ);
        if (key == INVALID_HANDLE_VALUE) continue;

        wchar_t name[32] = {};
        DWORD size = sizeof(name), type = 0;
        if (RegQueryValueExW(key, L"PortName", nullptr, &type,
                             reinterpret_cast<LPBYTE>(name), &size) == ERROR_SUCCESS)
            ports.push_back(name);

        RegCloseKey(key);
    }

    SetupDiDestroyDeviceInfoList(set);
    return ports;
}
```

`GUID_DEVCLASS_PORTS`로 COM 포트 클래스만 열거하니 관계없는 장치를 안 본다. `DIGCF_PRESENT`는 지금 꽂혀 있는 것만 달라는 뜻이고, 이걸 빼면 예전에 꽂았던 장치까지 나온다.

인스턴스 ID의 대소문자가 환경에 따라 다르게 나오는 경우가 있어서 대문자로 맞춰 비교한다. 이걸 빠뜨려서 어떤 PC에서만 못 찾는 상황이 있었다.

같은 장치를 두 대 꽂으면 포트가 두 개 나온다. 이때는 인스턴스 ID 마지막의 시리얼로 구분하면 된다. 위 코드에서 `id`의 마지막 `\` 뒤가 그 부분이다. 다만 시리얼을 안 쓰는 칩도 있어서(그런 경우 포트 번호 기반의 값이 들어간다) 장치마다 확인이 필요하다.

USB 전체 정보가 필요하면 `GUID_DEVINTERFACE_USB_DEVICE`로 열거한다. 이쪽은 COM 포트가 아닌 장치도 다 나온다.

## 리눅스에서 libusb 쓸 때

보드 쪽에서는 libusb가 잘 맞았다. 다만 권한을 챙겨야 한다.

기본적으로 `/dev/bus/usb/*` 노드는 root만 쓸 수 있다. 일반 사용자로 도는 프로그램에서 장치를 **열면** `LIBUSB_ERROR_ACCESS`가 난다. 열거와 디스크립터 읽기까지는 되고 여는 순간 막히니, 처음엔 왜 목록은 나오는데 통신이 안 되는지 헷갈렸다.

udev 규칙을 하나 추가하면 된다.

```text
# /etc/udev/rules.d/99-mydevice.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6001", MODE="0666"
```

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

제품명이나 시리얼 같은 문자열 디스크립터도 장치를 열어야 읽을 수 있다.

```c++
libusb_device_handle* h = nullptr;
if (libusb_open(dev, &h) == 0) {
    unsigned char s[256];
    if (desc.iSerialNumber &&
        libusb_get_string_descriptor_ascii(h, desc.iSerialNumber, s, sizeof(s)) > 0) {
        // s 에 시리얼
    }
    libusb_close(h);
}
```

같은 VID/PID 장치를 여러 대 붙이면 결국 시리얼로 구분해야 하니, 이 부분은 대부분 필요해진다.

## 꽂고 뺄 때 알림 받기

주기적으로 목록을 다시 훑는 대신 libusb가 알려주게 할 수 있다.

```c++
if (libusb_has_capability(LIBUSB_CAP_HAS_HOTPLUG)) {
    libusb_hotplug_register_callback(
        ctx,
        LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED | LIBUSB_HOTPLUG_EVENT_DEVICE_LEFT,
        0, vid, pid, LIBUSB_HOTPLUG_MATCH_ANY,
        on_hotplug, nullptr, &handle);
}
```

VID/PID로 필터를 걸 수 있어서 관심 있는 장치만 콜백이 온다. 이벤트를 받으려면 `libusb_handle_events`를 주기적으로 부르거나 전용 스레드를 돌려야 한다.

윈도우 쪽 대응은 `WM_DEVICECHANGE` 메시지다. MFC 대화상자에서 `RegisterDeviceNotification`으로 등록해두면 장치가 꽂히고 빠질 때 메시지가 온다. 검사 프로그램에서는 이걸로 "장비 연결됨/해제됨"을 화면에 표시했다.

## 정리하면

- VID/PID 열거는 libusb로 간단하다. 디스크립터는 장치를 안 열어도 읽힌다
- `std::hex`는 스트림에 계속 남고 자리 채움이 없으면 값을 잘못 읽게 된다
- 윈도우에서 COM 포트로 쓰는 장치는 libusb로 열 수 없다. SetupAPI로 인스턴스 ID를 보고 `PortName`을 읽는 게 맞다
- 리눅스는 udev 규칙 없이는 장치를 못 연다. 열거만 되는 상태와 구분해야 한다
- 같은 모델 여러 대를 구분하려면 결국 시리얼이 필요하고, 그건 장치를 열어야 읽힌다

레지스트리를 직접 읽어 COM 포트를 찾는 방법은 [자동으로 시리얼 번호 스캔](/posts/FindSerialPort/)에 따로 정리해뒀다.

## 참고

- [libusb API 문서](https://libusb.sourceforge.io/api-1.0/)
- [SetupDiGetClassDevs](https://learn.microsoft.com/en-us/windows/win32/api/setupapi/nf-setupapi-setupdigetclassdevsw)
