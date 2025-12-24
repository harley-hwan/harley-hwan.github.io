---
title: DT1-Remote 버튼 자동화 프로그램
description: "c, c++, shellapi, windowsapi, system, command, exe, execute, HWND, windows.h, Shellapi.h, DT1-Remote"
date: 2024-10-09 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, shellapi, windowsapi, system, command, exe, execute, HWND, windows.h, Shellapi.h, DT1-Remote]
---

# DT1-Remote ( (.exe ) )
- 최초 작성일: 2023년 4월 4일 (화)

## 

이 C++ 코드는 "DT1-Remote.exe" 프로세스를 찾아 실행하고, 해당 프로그램의 창을 찾는 작업을 수행한다.

<br/>

<br/>

## 

- __'IsProcessRunning'__ 함수: 이 함수는 주어진 프로세스 이름을 사용하여 프로세스가 실행 중인지 확인한다. 프로세스 이름을 비교하기 위해 __'\_wcsicmp'__ 함수를 사용하며, 프로세스가 실행 중이면 __'true'__ 를 반환한다.
- __'main'__ 함수: 프로그램의 주 실행 부분
    - __'IsProcessRunning'__ 함수를 사용하여 "DT1-Remote.exe" 프로세스가 실행 중인지 확인한다.
    - 프로세스가 실행 중이 아닐 경우, __'system'__ 함수를 사용하여 "DT1-Remote.exe" 프로그램을 실행한다. 실행에 실패하면 에러 메시지를 출력하고 종료한다.
    - "DT1-Remote.exe" 프로그램이 실행되고 나서 창이 로드되는 시간을 주기 위해 3초 동안 대기한다.
    - __'FindWindow'__ 함수를 사용하여 "DT1-Remote" 창을 찾는다. 창을 찾지 못하면 에러 메시지를 출력하고 종료한다.

이 코드는 "DT1-Remote.exe" 프로세스를 실행하고 해당 프로그램의 창을 찾는 작업을 수행하지만, "Target on" 버튼을 찾고 작동시키는 부분은 포함되어 있지 않습니다. 이전에 제공한 코드에서 이 부분을 추가하면 완전한 기능을 구현할 수 있습니다.

<br/>

<br/>

## 1

```c++
#include <iostream>
#include <Windows.h>
#include <Shellapi.h>

int main() {
    // DT1-Remote.exe를 실행
    int result = system("\"E:\\Program Files (x86)\\RFbeam\\DT1-Remote\\DT1-Remote.exe\"");

    if (result != 0) {
        std::cerr << "Error executing DT1-Remote.exe" << std::endl;
        return 1;
    }

    // 일정 시간을 기다린 후, "Target on" 버튼이 있는 창을 찾음
    Sleep(3000);
    HWND hwnd = FindWindow(NULL, "DT1-Remote");

    if (!hwnd) {
        std::cerr << "Unable to find DT1-Remote window" << std::endl;
        return 1;
    }

    // "Target on" 버튼 찾음
    const int TARGET_ON_BUTTON_ID = 1001; // 버튼의 실제 ID
    HWND hwndButton = GetDlgItem(hwnd, TARGET_ON_BUTTON_ID);

    if (!hwndButton) {
        std::cerr << "Unable to find Target on button" << std::endl;
        return 1;
    }

    // "Target on" 버튼을 ON 상태로 변경
    SendMessage(hwndButton, BM_CLICK, 0, 0);

    return 0;
}

```

<br/>

<br/>

## 2

DT1-Remote.exe 파일이 이미 실행 중인지 체크하는거 추가

```c++
#include <iostream>
#include <Windows.h>
#include <Shellapi.h>
#include <TlHelp32.h>

bool IsProcessRunning(const char* processName) {
    bool isRunning = false;
    PROCESSENTRY32 entry;
    entry.dwSize = sizeof(PROCESSENTRY32);

    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, NULL);

    if (Process32First(snapshot, &entry)) {
        do {
            if (!_stricmp(entry.szExeFile, processName)) {
                isRunning = true;
                break;
            }
        } while (Process32Next(snapshot, &entry));
    }

    CloseHandle(snapshot);
    return isRunning;
}

int main() {
    bool isRunning = IsProcessRunning("DT1-Remote.exe");

    if (!isRunning) {
        int result = system("\"E:\\Program Files (x86)\\RFbeam\\DT1-Remote\\DT1-Remote.exe\"");

        if (result != 0) {
            std::cerr << "Error executing DT1-Remote.exe" << std::endl;
            return 1;
        }
    }

    Sleep(3000);
    HWND hwnd = FindWindow(NULL, "DT1-Remote");

    if (!hwnd) {
        std::cerr << "Unable to find DT1-Remote window" << std::endl;
        return 1;
    }

    // 창의 제목을 가져옵니다.
    char windowTitle[512];
    GetWindowTextA(hwnd, windowTitle, 512);

    // "Target on" 버튼을 찾습니다.
    HWND hwndButton = FindWindowEx(hwnd, NULL, "Button", "Target on");

    if (!hwndButton) {
        std::cerr << "Unable to find Target on button" << std::endl;
        return 1;
    }

    // 버튼의 현재 상태를 가져옵니다.
    LRESULT state = SendMessage(hwndButton, BM_GETSTATE, 0, 0);

    // 버튼이 OFF 상태일 때만 ON으로 변경합니다.
    if (!(state & BST_CHECKED)) {
        SendMessage(hwndButton, BM_CLICK, 0, 0);
    }

    return 0;
}
```

<br/>

그런데, 이미 프로그램이 실행중이면 "Target ON" 버튼이 OFF 상태여도 ON으로 변경하지 못함...
