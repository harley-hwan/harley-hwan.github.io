---
title: (c++) 현재 연결된 USB들의 VID/PID 검출
description: "c++, libusb, usb, libusb_device, libusb_context, device, vid, pid, vendorid, productid"
date: 2023-03-15 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c c++, libusb, usb, libusb_device, libusb_context, device, vid, pid]
---

# 현재 연결된 USB들의 VID/PID 검출하기
- 최초 작성일: 2023년 3월 15일 (수)

## 목차

[TOC]

<br/>

## 내용

libusb 라이브러리를 사용하여 컴퓨터에 연결된 USB 장치의 정보를 출력하는 예제 코드이다.

- 먼저, libusb를 초기화하기 위해 libusb_init() 함수를 호출한다. 이 함수는 libusb 컨텍스트를 초기화하고, 작업을 수행하기 위한 준비를 한다.
- 다음으로, libusb_get_device_list() 함수를 호출하여 연결된 USB 장치의 리스트를 받아온다. 이 함수는 리스트의 개수를 반환하고, 만약 에러가 발생하면 음수 값을 반환한다.
- for 루프를 사용하여 리스트에 있는 장치들을 하나씩 확인한다. 
- libusb_get_device_descriptor() 함수를 호출하여 해당 장치의 디스크립터 정보를 가져오며, 이 정보는 libusb_device_descriptor 구조체에 저장된다.
- 다음으로, 가져온 디스크립터 정보를 출력하여 VID(Vender ID)와 PID(Product ID)를 확인한다.
- 마지막으로, libusb_free_device_list() 함수를 호출하여 디바이스 리스트를 해제하고, libusb_exit() 함수를 호출하여 libusb를 종료합니다.

<br/>

### 소스 1

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

## 결과

![image](https://user-images.githubusercontent.com/68185569/225209108-e4f78b75-72b3-4acf-82f4-89e8dc5bc06a.png)
