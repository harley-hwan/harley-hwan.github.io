---
title: "(C++) DT1-Remote 버튼 자동화 프로그램"
description: "남이 만든 프로그램을 띄우고 버튼을 대신 눌러주는 코드. ShellExecute를 쓴 이유, Sleep(3000)을 없앤 방법, 그리고 '이미 실행 중이면 버튼이 안 눌리는' 문제가 왜 남았는지까지 적었다."
date: 2024-10-09 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, shellapi, windowsapi, system, command, exe, execute, hwnd, windows-h, shellapi-h, dt1-remote, ui-automation]
---
## 매번 손으로 하던 걸 없애려고

센서 측정을 시작하려면 DT1-Remote를 켜고 "Target on" 버튼을 눌러야 했다. 측정 자체는 자동화되어 있는데 이 앞단만 손으로 하고 있었다. 하루에 수십 번 반복하면 잊어버리기도 하고, 안 눌린 채로 측정이 돌아서 데이터를 다시 받는 일도 생겼다.

남이 만든 프로그램이라 소스가 없다. 창 핸들을 찾아서 버튼에 메시지를 보내는 방식으로 갔다.

## system()이 아니라 ShellExecute

처음에 `system("...DT1-Remote.exe")`로 띄웠는데 그 뒤 코드가 실행되지 않았다.

`system()`은 **실행한 프로그램이 끝날 때까지 반환하지 않는다**. DT1-Remote는 사용자가 닫을 때까지 계속 떠 있으니, 창을 찾는 코드에 영원히 도달하지 않는다.

`ShellExecute`는 프로그램을 띄우고 바로 반환한다.

```c++
#include <iostream>
#include <Windows.h>
#include <Shellapi.h>

int main() {
    // DT1-Remote.exe를 실행
    HINSTANCE result = ShellExecute(NULL, "open", "E:\\Program Files (x86)\\RFbeam\\DT1-Remote\\DT1-Remote.exe", NULL, NULL, SW_SHOWNORMAL);

    if ((INT_PTR)result <= 32) {
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

`ShellExecute`의 반환값이 32 이하면 실패다. `HINSTANCE`를 돌려주는데 실제로는 핸들이 아니라 에러 코드다. 16비트 시절 API의 흔적이라 이렇게 이상하게 생겼다. `ShellExecuteEx`가 더 정상적인 형태이고, 무엇보다 프로세스 핸들을 돌려줘서 그다음에 쓸 게 많다.

## Sleep(3000)을 없애기

3초를 기다리는 이유는 프로그램이 뜨고 창이 만들어질 시간을 주려는 것이다. 근거는 없다. 몇 번 해보니 그 정도면 되겠다 싶었던 값이다.

느린 PC에서는 부족해서 창을 못 찾고, 빠른 PC에서는 3초를 그냥 버린다. 둘 다 겪었다.

프로세스가 입력을 받을 준비가 됐는지 물어보는 함수가 있다.

```c++
SHELLEXECUTEINFOA si{};
si.cbSize = sizeof(si);
si.fMask  = SEE_MASK_NOCLOSEPROCESS;      // hProcess 를 받겠다
si.lpVerb = "open";
si.lpFile = exePath;
si.nShow  = SW_SHOWNORMAL;

if (!ShellExecuteExA(&si)) return 1;

WaitForInputIdle(si.hProcess, 10000);      // 메시지 루프가 돌기 시작할 때까지
```

`WaitForInputIdle`은 대상 프로세스가 입력 대기 상태에 들어갈 때까지 기다린다. 그 시점에 창이 있다는 보장까지는 없어서, 찾는 쪽도 재시도 루프로 바꿨다.

```c++
HWND WaitForWindow(const char* title, DWORD timeout_ms)
{
    const DWORD start = GetTickCount();
    for (;;) {
        HWND h = FindWindowA(nullptr, title);
        if (h) return h;
        if (GetTickCount() - start > timeout_ms) return nullptr;
        Sleep(100);
    }
}
```

"충분히 기다리기"가 아니라 "될 때까지, 단 상한을 두고 기다리기"다. 빠른 PC에서는 100 ms 만에 끝나고, 느린 PC에서도 실패하지 않는다.

## 창 제목이 정확히 일치해야 한다

`FindWindow(NULL, "DT1-Remote")`는 제목이 **완전히 같은** 창만 찾는다. 프로그램이 버전 업 되면서 제목에 버전이 붙거나, 파일을 연 상태에서 파일명이 제목에 들어가면 못 찾는다.

부분 일치로 찾으려면 창을 열거해야 한다.

```c++
struct FindCtx { const char* needle; HWND found; };

BOOL CALLBACK EnumProc(HWND h, LPARAM lp)
{
    auto* ctx = reinterpret_cast<FindCtx*>(lp);
    char title[512] = {};
    GetWindowTextA(h, title, sizeof(title));
    if (strstr(title, ctx->needle) && IsWindowVisible(h)) {
        ctx->found = h;
        return FALSE;                       // 찾았으니 중단
    }
    return TRUE;
}

HWND FindWindowContaining(const char* needle)
{
    FindCtx ctx{ needle, nullptr };
    EnumWindows(EnumProc, reinterpret_cast<LPARAM>(&ctx));
    return ctx.found;
}
```

제목 대신 창 클래스명으로 찾는 방법도 있다. 클래스명은 잘 안 바뀌어서 더 안정적인데, 값을 알아내려면 Spy++ 같은 도구로 실제 창을 들여다봐야 한다. 프로세스 ID로 좁히는 것도 방법이다. `GetWindowThreadProcessId`로 창의 소유 프로세스를 확인하면, 같은 프로그램이 여러 개 떠 있을 때도 내가 띄운 것을 고를 수 있다.

## 이미 실행 중인지 확인하기

두 번 띄우면 안 되니 프로세스 목록을 확인하는 코드를 추가했다.

```c++
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
        HINSTANCE result = ShellExecute(NULL, "open", "E:\\Program Files (x86)\\RFbeam\\DT1-Remote\\DT1-Remote.exe", NULL, NULL, SW_SHOWNORMAL);

        if ((INT_PTR)result <= 32) {
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

    // 창의 제목을 가져온다.
    char windowTitle[512];
    GetWindowTextA(hwnd, windowTitle, 512);

    // "Target on" 버튼을 찾는다.
    HWND hwndButton = FindWindowEx(hwnd, NULL, "Button", "Target on");

    if (!hwndButton) {
        std::cerr << "Unable to find Target on button" << std::endl;
        return 1;
    }

    // 버튼의 현재 상태를 가져온다.
    LRESULT state = SendMessage(hwndButton, BM_GETSTATE, 0, 0);

    // 버튼이 OFF 상태일 때만 ON으로 변경한다.
    if (!(state & BST_CHECKED)) {
        SendMessage(hwndButton, BM_CLICK, 0, 0);
    }

    return 0;
}
```

버튼 찾는 방식도 바꿨다. `GetDlgItem(hwnd, 1001)`은 컨트롤 ID를 추측한 것이라 근거가 없었다. `FindWindowEx(hwnd, NULL, "Button", "Target on")`은 클래스가 `Button`이고 텍스트가 `Target on`인 자식 창을 찾으니 훨씬 확실하다.

`CreateToolhelp32Snapshot`이 실패하면 `INVALID_HANDLE_VALUE`를 돌려주는데, 그 검사가 없어서 실패 시 `Process32First`에 잘못된 핸들이 들어가고 `CloseHandle`도 그걸 닫으려 한다. 검사를 넣어야 한다.

```c++
HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
if (snapshot == INVALID_HANDLE_VALUE) return false;
```

## 남은 문제: 이미 실행 중이면 안 눌린다

프로그램이 이미 떠 있는 상태에서 실행하면, "Target on"이 꺼져 있어도 켜지지 않는다. 새로 띄운 경우에는 잘 된다.

당시엔 원인을 못 찾고 그대로 뒀다. 지금 정리하면서 다시 보니 `BM_GETSTATE` 쪽이 의심된다.

`BST_CHECKED`는 체크박스나 라디오 버튼, 또는 `BS_AUTOCHECKBOX`/`BS_PUSHLIKE` 스타일로 만든 토글 버튼에서만 의미가 있다. 평범한 푸시 버튼은 이 비트가 안 선다. 그리고 프로그램이 자체 변수로 ON/OFF를 관리하고 화면만 직접 그리는 경우(오너 드로우), Win32가 아는 버튼 상태와 실제 상태가 아예 다르다.

즉 `state & BST_CHECKED`가 프로그램의 실제 ON/OFF와 무관한 값일 가능성이 크다. 그러면 조건이 우연히 맞았다 틀렸다 한다.

확인하는 방법은 단순하다. 상태 값을 그냥 찍어보면 된다.

```c++
LRESULT state = SendMessage(hwndButton, BM_GETSTATE, 0, 0);
printf("BM_GETSTATE = 0x%08llX\n", (unsigned long long)state);
```

ON일 때와 OFF일 때 값이 같으면 이 방법으로는 상태를 알 수 없다는 뜻이다. 그때는 상태를 읽으려 하지 말고 다른 신호를 봐야 한다. 버튼 텍스트가 "Target on"과 "Target off"로 바뀐다면 `GetWindowText`로 판별할 수 있다.

또 하나 가능성이 있다. 대상 프로그램이 관리자 권한으로 떠 있고 내 프로그램은 일반 권한이면, **UIPI 때문에 메시지가 차단된다**. `SendMessage`가 실패해도 반환값만으로는 구분이 안 된다. 두 프로그램의 권한 수준을 맞춰야 한다. 새로 띄운 경우에는 내 프로그램의 자식이라 같은 권한이고, 이미 떠 있던 경우에는 다른 권한일 수 있다는 점이 "새로 띄우면 되고 아니면 안 되는" 증상과도 맞아떨어진다.

## UI Automation이 정공법

`SendMessage`로 컨트롤을 조작하는 건 오래된 방식이고, Win32 컨트롤이 아니면 아예 안 통한다. WPF나 Qt로 만든 프로그램은 창이 하나뿐이고 버튼이 별도 HWND가 아니라서 `FindWindowEx`로는 찾을 수조차 없다.

UI Automation은 그런 프레임워크까지 공통으로 다룬다.

```c++
#include <UIAutomation.h>

CComPtr<IUIAutomation> ua;
ua.CoCreateInstance(CLSID_CUIAutomation);

CComPtr<IUIAutomationElement> root;
ua->ElementFromHandle(hwnd, &root);

CComPtr<IUIAutomationCondition> cond;
ua->CreatePropertyCondition(UIA_NamePropertyId, CComVariant(L"Target on"), &cond);

CComPtr<IUIAutomationElement> button;
root->FindFirst(TreeScope_Descendants, cond, &button);

if (button) {
    CComPtr<IUIAutomationTogglePattern> toggle;
    if (SUCCEEDED(button->GetCurrentPatternAs(UIA_TogglePatternId,
            IID_PPV_ARGS(&toggle))) && toggle) {
        ToggleState st;
        toggle->get_CurrentToggleState(&st);      // 실제 상태
        if (st != ToggleState_On) toggle->Toggle();
    }
}
```

`TogglePattern`을 지원하는 컨트롤이면 상태를 정확히 읽을 수 있다. `BM_GETSTATE`로 추측할 필요가 없다. 지원하지 않으면 `InvokePattern`으로 그냥 누르기만 한다.

## 그런데 UI 자동화 자체가 마지막 수단이다

이 코드를 다 정리하고 나서 든 생각은, 애초에 GUI를 자동화하는 게 최선이었나 하는 것이다.

UI 자동화는 상대 프로그램이 업데이트되면 언제든 깨진다. 버튼 위치, 이름, 창 제목 중 하나만 바뀌어도 동작을 멈추는데, 그 사실을 알아채는 게 "측정 데이터가 이상하다"는 시점이라는 게 제일 나쁘다.

센서 자체는 USB나 시리얼로 명령을 받는다. 제조사 문서에 프로토콜이 공개되어 있다면, 그 프로그램을 거치지 않고 직접 통신하는 쪽이 훨씬 안정적이다. 명령줄 인자나 설정 파일로 자동 시작을 지원하는지도 확인해볼 만하다.

지금이라면 순서를 이렇게 잡는다.

1. 장비와 직접 통신할 수 있는가 (프로토콜 문서 확인)
2. 프로그램이 명령줄 인자나 설정으로 자동화를 지원하는가
3. 안 되면 UI Automation
4. 그것도 안 되면 `SendMessage`

## 정리하면

- `system()`은 프로그램이 끝날 때까지 반환하지 않는다. GUI를 띄울 때는 `ShellExecuteEx` + `WaitForInputIdle`
- `Sleep(3000)`처럼 고정 대기는 느린 PC에서 실패하고 빠른 PC에서 시간을 버린다. 상한을 둔 재시도 루프로 바꾼다
- `FindWindow`는 제목 완전 일치다. 부분 일치가 필요하면 `EnumWindows`, 더 안정적으로는 클래스명이나 프로세스 ID로 좁힌다
- `BM_GETSTATE`의 `BST_CHECKED`는 버튼 스타일에 따라 의미가 없다. 값을 찍어보고 판단해야 한다
- 대상이 관리자 권한이면 UIPI가 메시지를 막는다
- Win32 컨트롤이 아닌 프로그램은 UI Automation으로만 다룰 수 있다
- 그리고 UI 자동화는 마지막 수단이다. 장비와 직접 통신할 방법이 있으면 그쪽이 맞다
