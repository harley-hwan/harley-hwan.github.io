---
title: "(C++) DLL Crash가 클라이언트에 미치는 영향과 해결 방법"
description: "DLL이 죽으면 호출한 프로그램도 같이 죽는다. try-catch로 왜 못 막는지, SEH를 쓸 때 걸리는 컴파일 에러, 현장에서 덤프를 받아 원인을 찾는 방법, DLL 경계에서 힙이 갈려 생기는 크래시까지 정리했다."
date: 2025-05-20 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, dll, crash-dump, exception-handling, windows, seh, minidump]
---
## DLL이 죽으면 프로그램도 같이 죽는다

측정 로직을 DLL로 분리해두고 검사 프로그램에서 불러 쓰는 구조였다. 어느 날부터 검사 도중에 프로그램이 통째로 사라지는 일이 생겼다. 에러 대화상자도 없고 로그도 마지막 줄에서 끊긴다.

DLL은 별도 프로세스가 아니라 **호출한 프로세스의 주소 공간에 로드된다**. 같은 메모리, 같은 스택을 쓴다. DLL 안에서 잘못된 주소에 접근하면 그건 그 프로세스가 잘못된 주소에 접근한 것이고, OS는 프로세스를 끝낸다. DLL만 격리해서 죽일 방법이 없다.

주요 원인은 이런 것들이다.

- 널 포인터 접근, 해제된 메모리 재사용
- 버퍼 오버런, 스택 오버플로
- 처리되지 않은 예외, `abort()`나 `terminate()` 호출

이건 논리적 오류가 아니라 운영체제 수준의 치명적 예외로 분류된다.

## try-catch로는 못 잡는다

처음에 한 일은 DLL 호출을 `try`/`catch`로 감싼 것이다. 아무 효과가 없었다.

```cpp
try {
    RiskFunction();
} catch (const std::exception& e) {
    std::cerr << "예외: " << e.what();
}
// 시스템 예외 발생 시 이 catch 는 실행되지 않음
```

C++ 예외는 `throw` 문이 만드는 것이다. 컴파일러가 그에 맞춰 스택 되감기 코드를 준비해둔다. 반면 아래 것들은 CPU가 감지해서 커널이 프로세스에 통보하는 것이라 `throw`를 거치지 않는다.

- Access Violation (`0xC0000005`)
- Division by Zero (`0xC0000094`)
- Stack Overflow (`0xC00000FD`)

`catch (...)`도 마찬가지다. 기본 설정에서는 안 잡힌다.

## SEH와 컴파일 옵션

윈도우에는 구조화 예외 처리(SEH)가 따로 있다.

```cpp
__try {
    CallDllFunction();
} __except(EXCEPTION_EXECUTE_HANDLER) {
    // Access Violation 같은 시스템 예외를 잡는다
}
```

이걸로 잡히긴 한다. 그런데 실제로 붙이려니 컴파일이 안 됐다.

```text
error C2712: Cannot use __try in functions that require object unwinding
```

같은 함수에 소멸자를 가진 객체(`std::string`, `std::vector` 등)가 있으면 `__try`를 못 쓴다. SEH가 스택을 되감을 때 C++ 소멸자를 호출하지 않기 때문에 컴파일러가 아예 막는다.

해결은 함수를 쪼개는 것이다. `__try`만 있는 얇은 함수를 하나 만들고, C++ 객체는 그 바깥에 둔다.

```cpp
// SEH 전용 - C++ 객체를 두지 않는다
static int CallGuarded(int (*fn)(const void*), const void* arg)
{
    __try {
        return fn(arg);
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        return -1;
    }
}
```

`/EHa` 옵션을 켜면 `catch (...)`가 SEH 예외까지 잡게 되는데, 이건 권장하지 않는다. 잡히긴 하지만 잡은 뒤에 뭘 할 수 있는지가 문제다. 메모리가 이미 망가진 상태에서 계속 실행하면 더 이상한 곳에서 죽는다.

SEH의 한계는 그대로 남는다. 예외가 발생한 자리와 `__except` 사이의 C++ 객체 소멸자가 호출되지 않으니, RAII로 관리하던 파일이나 락이 그대로 남는다. 윈도우 전용이라는 것도 있다.

## 잡는 것보다 덤프를 남기는 게 낫다

방향을 바꾼 게 여기서였다. 크래시를 막으려는 대신 **왜 죽었는지 알 수 있게** 하는 쪽으로 갔다.

윈도우는 처리되지 않은 예외가 발생했을 때 부를 함수를 등록할 수 있다.

```cpp
#include <windows.h>
#include <dbghelp.h>
#pragma comment(lib, "dbghelp.lib")

LONG WINAPI OnCrash(EXCEPTION_POINTERS* ep)
{
    HANDLE f = CreateFileW(L"crash.dmp", GENERIC_WRITE, 0, nullptr,
                           CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (f != INVALID_HANDLE_VALUE) {
        MINIDUMP_EXCEPTION_INFORMATION mei{};
        mei.ThreadId          = GetCurrentThreadId();
        mei.ExceptionPointers = ep;
        mei.ClientPointers    = FALSE;

        MiniDumpWriteDump(GetCurrentProcess(), GetCurrentProcessId(), f,
                          MiniDumpWithIndirectlyReferencedMemory,
                          &mei, nullptr, nullptr);
        CloseHandle(f);
    }
    return EXCEPTION_EXECUTE_HANDLER;    // 프로세스 종료
}

// 프로그램 시작 시
SetUnhandledExceptionFilter(OnCrash);
```

덤프 파일에는 크래시 시점의 콜스택, 레지스터, 메모리 상태가 들어 있다. Visual Studio나 WinDbg로 열면 어느 줄에서 죽었는지 바로 보인다.

**pdb 파일을 같이 보관해야 한다.** 덤프만 있고 그 빌드의 pdb가 없으면 함수 이름이 안 나오고 주소만 보인다. 배포한 빌드마다 pdb를 따로 저장해두는 습관이 이때 생겼다.

덤프 핸들러 안에서 조심할 게 있다. 크래시 시점에는 힙이 이미 망가져 있을 수 있어서 **새로 메모리를 할당하면 안 된다**. 문자열을 만들거나 로그 라이브러리를 부르면 그 안에서 또 죽는다. 파일 경로 같은 건 미리 만들어두고 핸들러에서는 정해진 API만 부른다.

`MiniDumpWithIndirectlyReferencedMemory` 대신 `MiniDumpNormal`을 쓰면 파일이 훨씬 작아진다. 콜스택만 보면 되는 경우엔 그걸로 충분하고, 변수 값까지 봐야 하면 큰 쪽을 쓴다.

### 이 필터가 안 잡는 것들

전부 잡히는 건 아니다.

**스택 오버플로**는 잡기 어렵다. 핸들러를 실행할 스택 자체가 없기 때문이다. 가드 페이지가 한 번 소진되면 다음엔 그대로 죽는다. `_resetstkoflw`로 복구를 시도할 수 있지만 제한적이다.

**힙 손상**은 윈도우가 필터를 부르지 않고 즉시 프로세스를 끝낸다. 손상된 상태로 코드를 더 실행하는 게 위험하다고 판단하기 때문이다.

**CRT의 잘못된 매개변수 처리**와 **순수 가상 함수 호출**은 별도 핸들러가 있다.

```cpp
_set_invalid_parameter_handler(MyInvalidParam);
_set_purecall_handler(MyPurecall);
std::set_terminate(MyTerminate);
```

`std::terminate`는 처리되지 않은 C++ 예외나 소멸자에서 던진 예외로 불린다. 여기서도 덤프를 남기게 해두면 원인 파악이 훨씬 쉽다.

### 코드를 안 고치고도 덤프를 받는 방법

레지스트리 설정 하나로 윈도우가 알아서 덤프를 만들게 할 수 있다.

```text
HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps
  DumpFolder  (REG_EXPAND_SZ)  C:\Dumps
  DumpCount   (REG_DWORD)      10
  DumpType    (REG_DWORD)      2      ; 2 = full dump
```

현장 PC에서 재현이 안 되는 문제를 쫓을 때 이게 제일 빨랐다. 프로그램을 다시 빌드해서 보낼 필요가 없다.

## DLL 경계에서 힙이 갈린다

크래시 원인 중에 한동안 못 찾았던 게 이거다.

DLL과 실행 파일이 CRT를 각각 정적 링크(`/MT`)하면, **힙이 두 개가 된다**. DLL 안에서 `new`한 메모리를 실행 파일에서 `delete`하면 다른 힙에 반납하는 것이라 그 자리에서 죽거나 나중에 힙이 망가진다.

```cpp
// DLL
__declspec(dllexport) Buffer* CreateBuffer();

// 실행 파일
Buffer* b = CreateBuffer();
delete b;                     // DLL 의 힙에서 잡은 것을 여기서 해제
```

`std::string`이나 `std::vector`를 DLL 경계로 주고받는 것도 같은 이유로 위험하다. 컨테이너가 내부적으로 할당한 메모리를 반대편에서 해제하게 된다.

해결은 두 가지다. CRT를 동적 링크(`/MD`)로 통일해서 힙을 하나로 만들거나, **할당한 쪽이 해제하도록** 인터페이스를 짜는 것이다.

```cpp
__declspec(dllexport) Buffer* CreateBuffer();
__declspec(dllexport) void    DestroyBuffer(Buffer*);   // 해제도 DLL 이 한다
```

후자가 확실하다. 상대가 어떤 옵션으로 빌드했는지 통제할 수 없는 경우에도 안전하다.

C++ 예외를 DLL 경계 밖으로 던지는 것도 같은 문제가 있다. 컴파일러와 CRT 버전이 정확히 일치할 때만 동작한다. DLL 인터페이스는 에러 코드를 반환하는 C 스타일로 두는 게 안전하다.

## 결국 예방이 대부분이다

크래시를 잡으려는 시도는 대체로 늦다. 크래시 시점에는 이미 상태가 망가져 있어서 복구할 게 없다. 그래서 대부분의 노력은 예방에 들어갔다.

### DLL의 모든 진입점에서 예외를 막는다

```cpp
extern "C" __declspec(dllexport) int SafeFunction() {
    try {
        // 내부 작업
        return 0;
    } catch (const std::exception& ex) {
        LogError(ex.what());
        return -1;
    } catch (...) {
        LogError("unknown");
        return -2;
    }
}
```

C++ 예외가 경계를 넘지 않게 하고, 실패는 반환값으로 알린다.

### 인자를 믿지 않는다

```cpp
extern "C" __declspec(dllexport) int Process(const float* data, int n) {
    if (!data || n <= 0 || n > kMaxSamples) return -1;
    // ...
}
```

DLL은 누가 어떻게 부를지 모른다. 널 포인터와 범위를 매번 확인하는 게 답답해 보여도, 안 하면 그게 그대로 Access Violation이다.

### 스마트 포인터와 컨테이너

```cpp
std::unique_ptr<int[]> arr(new int[10]);
```

수동 `delete`가 없어지면 이중 해제와 누수가 같이 사라진다. 배열 인덱스는 `at()`을 쓰거나 경계를 명시적으로 검사한다.

### 진단 도구를 돌린다

Visual Studio의 Address Sanitizer(`/fsanitize=address`)나 Application Verifier를 개발 중에 켜두면, 실제로 죽기 전에 잘못된 접근을 잡아준다. 해제된 메모리를 읽는 것 같은 문제는 평소엔 조용히 지나가다가 나중에 엉뚱한 곳에서 터지는데, 이 도구들은 그 자리에서 알려준다.

## 프로세스 분리

정말로 격리해야 한다면 DLL을 별도 프로세스에서 돌리고 IPC로 통신하는 구조가 된다. 그쪽이 죽어도 이쪽은 산다.

브라우저가 탭이나 플러그인을 별도 프로세스로 돌리는 것과 같은 구조다. 대신 Named Pipe나 소켓, 공유 메모리를 구현해야 하고 데이터를 주고받는 비용이 생긴다. 프레임마다 큰 배열을 넘겨야 하는 구조에서는 이 비용이 무시할 수 없어서, 공유 메모리를 쓰지 않으면 현실적이지 않았다.

DLL이 외부 업체가 만든 것이라 손댈 수 없는 경우라면 이 방법이 유일한 답이다. 내가 만든 DLL이면 예방 쪽에 투자하는 게 낫다.

## 정리하면

- DLL은 호출한 프로세스와 같은 주소 공간에 있다. DLL의 크래시는 프로세스의 크래시다
- `try`/`catch`는 `throw`로 발생한 예외만 잡는다. Access Violation 같은 시스템 예외는 SEH 영역이다
- `__try`는 소멸자가 필요한 객체와 같은 함수에 쓸 수 없다. 얇은 함수로 분리한다
- 잡는 것보다 `SetUnhandledExceptionFilter` + `MiniDumpWriteDump`로 덤프를 남기는 게 실질적이다. pdb를 같이 보관해야 한다
- 스택 오버플로와 힙 손상은 그 필터로도 안 잡힌다
- DLL과 실행 파일의 CRT가 다르면 힙이 갈린다. 할당한 쪽이 해제하도록 인터페이스를 짠다
- 크래시 시점에는 복구할 게 거의 없다. 진입점 검증과 진단 도구가 결국 답이다
