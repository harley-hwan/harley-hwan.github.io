---
title: "(C++) DLL Crash가 클라이언트에 미치는 영향과 해결 방법"
description: "DLL 충돌(Crash) 발생 시 클라이언트 측 영향과 명확한 해결법"
date: 2025-05-20 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, dll, crash-dump, exception-handling, windows]
---
## DLL Crash의 개념과 발생 이유

DLL(Dynamic-Link Library)은 실행 중인 프로세스에 동적으로 로드되어 해당 기능을 제공하는 공유 라이브러리다. DLL 내부의 코드가 예외 상황을 적절히 처리하지 못하면 클라이언트 프로세스 전체에 심각한 영향을 줄 수 있다.

주요 Crash 원인은 다음과 같다.

* NULL 포인터 접근, 해제된 메모리 재사용
* 버퍼 오버런, 스택 오버플로우
* 외부 리소스 핸들 누락 또는 손상
* 처리되지 않은 예외, 예기치 않은 `abort()`, `terminate()` 호출

Crash는 단순 논리적 예외가 아니라 운영체제 수준에서의 치명적인 예외로 분류된다.

---

## Crash 발생 시 클라이언트의 반응

DLL은 클라이언트와 동일한 프로세스 공간에서 실행되므로, DLL에서 발생한 Crash는 클라이언트 전체의 중단으로 직결된다. DLL 내 Access Violation이 발생하면 클라이언트도 함께 종료되고, 이로 인해 사용자 데이터 손실, 프로세스 종료 로그 생성, UI 멈춤 등의 문제가 발생한다. Crash가 발생하면 Windows는 메모리 덤프(Dump) 파일을 생성하여 당시의 메모리 상태, 콜스택, 레지스터 정보를 기록한다.

덤프 파일은 디버깅 도구(예: Visual Studio, WinDbg)를 통해 원인을 분석할 수 있는 핵심 자료가 된다.

---

## C++ 예외 처리의 한계

C++의 `try-catch`는 논리적 예외에 대해서만 유효하다. 예를 들어 파일 열기 실패, 잘못된 파라미터 등은 예외 객체로 throw하여 catch할 수 있다.

하지만 다음과 같은 시스템 예외는 C++ `try-catch`로는 잡을 수 없다.

* Access Violation (`0xC0000005`)
* Division by Zero (`0xC0000094`)
* Stack Overflow (`0xC00000FD`)

```cpp
try {
    RiskFunction();
} catch (const std::exception& e) {
    std::cerr << "예외: " << e.what();
}
// 시스템 예외 발생 시 이 catch는 실행되지 않음
```

이유는 C++ 예외는 `throw`에 의해 발생하는 반면, 위 예외들은 운영체제 커널에 의해 강제 종료되기 때문이다.

---

## Windows SEH를 통한 예외 감지

Windows는 `__try / __except` 구문을 통해 시스템 예외를 포착할 수 있는 구조화 예외 처리(SEH)를 제공한다.

```cpp
__try {
    CallDllFunction();
} __except(EXCEPTION_EXECUTE_HANDLER) {
    // 시스템 예외를 포착함 (Access Violation 등)
}
```

SEH를 쓰면 Access Violation, Stack Overflow 같은 시스템 예외를 감지할 수 있고, 프로세스가 완전히 종료되기 전에 정리 작업을 수행할 수 있다. 다만 예외 발생 시 C++ 객체의 소멸자가 호출되지 않아 RAII 기반 설계와 충돌하고, Windows 전용이라 플랫폼 종속성이 생기며 유지보수도 어렵다.

---

## Crash 예방 및 안정성 강화 방법

### 1. DLL 내부 예외 처리 필수

DLL은 자신이 발생시킬 수 있는 예외를 내부에서 반드시 처리해야 한다.

```cpp
extern "C" __declspec(dllexport) void SafeFunction() {
    try {
        // 내부 작업
    } catch (const std::exception& ex) {
        LogError(ex.what());
    }
}
```

### 2. 스마트 포인터로 메모리 안전성 확보

```cpp
std::unique_ptr<int[]> arr(new int[10]);
```

스마트 포인터를 쓰면 메모리가 자동으로 해제되어 메모리 누수와 이중 해제를 예방할 수 있다.

### 3. NULL 포인터 및 인자 유효성 검증

```cpp
void Handle(int* ptr) {
    if (!ptr) return; // 안전 처리
    *ptr = 123;
}
```

### 4. 철저한 테스트와 경계값 검증

다양한 시나리오에서 테스트하고, 비정상 입력, 동시성, 리소스 부족 등 예외 케이스를 검증해야 한다.

---

## Crash에 대비한 아키텍처 설계

Crash 방어를 위해 DLL 로직을 별도 프로세스에서 실행하고 IPC를 통해 통신하는 구조로 분리할 수 있다.

이 구조에서는 DLL이 Crash되어도 클라이언트 프로세스는 유지되므로 안정성이 크게 향상된다. 대신 Named Pipe, Socket, Shared Memory 등의 IPC 구현이 필요하고, 성능 오버헤드와 아키텍처 복잡도가 늘어난다. 웹 브라우저가 플러그인을 별도 프로세스로 실행하는 구조가 대표적인 예다.

---

## 정리

정리하면, try-catch는 논리적 예외만 처리할 수 있고 시스템 예외에는 무력하다. SEH는 시스템 예외를 포착할 수 있지만 C++ 객체 소멸자가 호출되지 않고 Windows 전용이다. 가장 기본적인 방어는 DLL 내부에서 모든 진입점의 예외를 처리하는 것이고, 스마트 포인터와 유효성 검사로 메모리 오류를 줄일 수 있다. Crash로부터 클라이언트를 보호하는 가장 확실한 구조는 프로세스 분리지만 구현 부담이 있다.

결국 DLL Crash는 예외 처리로 막기 어렵고, Crash가 발생하지 않도록 사전에 예방하는 것이 가장 확실하다. 내부 예외 처리와 아키텍처 설계를 병행해 클라이언트 안정성을 확보해야 한다.
