---
layout: post
title: "(C++) DLL Crash가 클라이언트에 미치는 영향과 해결 방법"
subtitle: "DLL 충돌(Crash) 발생 시 클라이언트 측 영향과 명확한 해결법"
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: \[star, fork, follow]
tags: \[c++, dll, debugging, crash, programming]
comments: true
filename: "2025-05-20-cpp-dll-crash-handling.md"
---

# (C++) DLL Crash가 클라이언트에 미치는 영향과 해결 방법

* 최초 작성일: 2025년 5월 20일 (화)

## 목차

1. [DLL Crash의 개념과 발생 이유](#dll-crash의-개념과-발생-이유)
2. [Crash 발생 시 클라이언트의 반응](#crash-발생-시-클라이언트의-반응)
3. [C++ 예외 처리의 한계](#c-예외-처리의-한계)
4. [Windows SEH를 통한 예외 감지](#windows-seh를-통한-예외-감지)
5. [Crash 예방 및 안정성 강화 방법](#crash-예방-및-안정성-강화-방법)
6. [Crash에 대비한 아키텍처 설계](#crash에-대비한-아키텍처-설계)
7. [요약 및 비교](#요약-및-비교)

---

## DLL Crash의 개념과 발생 이유

DLL(Dynamic-Link Library)은 실행 중인 프로세스에 동적으로 로드되어 해당 기능을 제공하는 공유 라이브러리다. DLL 내부의 코드가 예외 상황을 적절히 처리하지 못하면 클라이언트 프로세스 전체에 심각한 영향을 줄 수 있다.

주요 Crash 원인은 다음과 같다:

* **NULL 포인터 접근** 또는 **해제된 메모리 재사용**
* **버퍼 오버런**, **스택 오버플로우**
* **외부 리소스 핸들 누락 또는 손상**
* **처리되지 않은 예외** 및 예기치 않은 `abort()`, `terminate()` 호출

Crash는 단순 논리적 예외가 아니라 **운영체제 수준에서의 치명적인 예외**로 분류된다.

---

## Crash 발생 시 클라이언트의 반응

DLL은 클라이언트와 동일한 프로세스 공간에서 실행되므로, DLL에서 발생한 Crash는 클라이언트 전체의 중단으로 직결된다.

* DLL 내 Access Violation이 발생하면 **클라이언트도 함께 종료**된다.
* 이로 인해 사용자 데이터 손실, 프로세스 종료 로그 생성, UI 멈춤 등의 문제가 발생한다.
* Crash가 발생하면 Windows는 **메모리 덤프(Dump) 파일**을 생성하여 당시의 메모리 상태, 콜스택, 레지스터 정보를 기록한다.

덤프 파일은 디버깅 도구(예: Visual Studio, WinDbg)를 통해 원인을 분석할 수 있는 핵심 자료가 된다.

---

## C++ 예외 처리의 한계

C++의 `try-catch`는 **논리적 예외**에 대해서만 유효하다. 예를 들어 파일 열기 실패, 잘못된 파라미터 등은 예외 객체로 throw하여 catch할 수 있다.

하지만 다음과 같은 **시스템 예외**는 C++ `try-catch`로는 잡을 수 없다:

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

이유는 C++ 예외는 `throw`에 의해 발생하는 반면, 위 예외들은 **운영체제 커널에 의해 강제 종료**되기 때문이다.

---

## Windows SEH를 통한 예외 감지

Windows는 `__try / __except` 구문을 통해 시스템 예외를 포착할 수 있는 \*\*구조화 예외 처리(SEH)\*\*를 제공한다.

```cpp
__try {
    CallDllFunction();
} __except(EXCEPTION_EXECUTE_HANDLER) {
    // 시스템 예외를 포착함 (Access Violation 등)
}
```

장점:

* Access Violation, Stack Overflow 등을 감지 가능
* 프로세스를 완전히 종료시키기 전에 정리 작업 수행 가능

단점:

* **C++ 객체의 소멸자가 호출되지 않음** → RAII 기반 설계와 충돌
* 유지보수 어려움, 플랫폼 종속성 존재 (Windows 전용)

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

* 자동 메모리 해제
* 메모리 누수 및 이중 해제 예방

### 3. NULL 포인터 및 인자 유효성 검증

```cpp
void Handle(int* ptr) {
    if (!ptr) return; // 안전 처리
    *ptr = 123;
}
```

### 4. 철저한 테스트와 경계값 검증

* 다양한 시나리오에서의 테스트 필요
* 비정상 입력, 동시성, 리소스 부족 등 예외 케이스 검증

---

## Crash에 대비한 아키텍처 설계

Crash 방어를 위해 DLL 로직을 **별도 프로세스에서 실행**하고 IPC를 통해 통신하는 구조로 분리할 수 있다.

장점:

* DLL이 Crash되어도 클라이언트 프로세스는 유지됨
* 안정성과 유연성이 향상됨

단점:

* IPC 구현 필요 (Named Pipe, Socket, Shared Memory 등)
* 성능 오버헤드 및 아키텍처 복잡도 증가

예:

* 웹 브라우저의 플러그인 별도 프로세스 실행 구조

---

## 요약 및 비교

| 방법                       | 설명                            | 제한 사항                        |
| ------------------------ | ----------------------------- | ---------------------------- |
| try-catch                | 논리적 예외 처리                     | 시스템 예외는 무력화                  |
| SEH (`__try / __except`) | 시스템 예외 포착 가능                  | C++ 객체 소멸자 호출 불가, Windows 전용 |
| DLL 내부 예외 처리             | 가장 기본적이며 중요한 방어 방법            | 모든 함수 진입점에서 구현 필요            |
| 스마트 포인터 및 유효성 검사         | 메모리 오류 예방, 안정성 향상             | 논리적 버그에는 여전히 취약              |
| 프로세스 분리                  | Crash 방지에 가장 효과적, 클라이언트 보호 가능 | 구현 복잡, IPC 구조 필요             |

---

DLL Crash는 예외 처리로 막기 어렵다. 가장 확실한 방법은 **Crash가 발생하지 않도록 사전에 예방**하는 것이다. 내부 예외 처리와 아키텍처 설계를 병행해, 클라이언트 안정성을 확보하는 것이 중요하다.
