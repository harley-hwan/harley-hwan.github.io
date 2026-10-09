---
title: "(C++) 클래스의 Static 멤버 변수와 Static 멤버 함수 이해하기"
description: "static 멤버를 쓰면서 부딪힌 것들 — 정의를 빼먹으면 나는 링크 에러, const 멤버인데도 정의가 필요한 경우, 초기화 순서 문제, 그리고 C 콜백에 멤버 함수를 넘기는 방법."
date: 2024-06-05 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, programming, static-keyword, static-member-variable, static-member-function, linker, thread-safety]
---
## 인스턴스마다 있으면 안 되는 것들

로그를 파일에 쓰는 클래스를 만들면서 처음 진지하게 쓰게 됐다. 객체를 여러 개 만들어도 로그 파일은 하나여야 하고, 지금까지 만든 객체가 몇 개인지도 한 군데서 세야 한다.

이런 건 객체마다 하나씩 있으면 안 된다. 클래스에 하나만 있어야 한다. 그게 static 멤버다.

## 선언과 정의를 나눠야 한다

```cpp
// MyClass.h
class MyClass {
public:
    static int myStaticVariable;
};
```

```cpp
// MyClass.cpp
int MyClass::myStaticVariable = 0;
```

헤더의 `static int myStaticVariable;`은 **선언**이다. "이런 게 있다"고 알리는 것뿐이고 메모리는 안 잡힌다. 실제 메모리는 cpp 파일의 정의에서 잡힌다.

이유는 헤더가 여러 cpp에 포함되기 때문이다. 헤더에 정의를 두면 포함하는 cpp마다 변수가 하나씩 생겨서 링커가 중복이라고 거부한다. 그래서 선언은 헤더에, 정의는 한 곳에만 둔다.

사용은 클래스 이름과 범위 연산자로 한다. 객체를 만들 필요가 없다.

```cpp
MyClass::myStaticVariable = 10;
```

## 정의를 빼먹으면 링크 에러

처음에 반드시 한 번은 겪는다.

```text
LNK2001: unresolved external symbol "public: static int MyClass::myStaticVariable"
```

컴파일은 통과한다. 헤더에 선언이 있으니 컴파일러는 만족한다. 그런데 링커가 실제 심볼을 찾을 때 없다.

에러가 컴파일 단계가 아니라 링크 단계에서 나기 때문에 "코드는 맞는 것 같은데 왜"라는 상태가 된다. `unresolved external symbol`에 `static` 멤버 이름이 보이면 cpp에 정의를 안 썼는지부터 확인하면 된다.

반대 실수도 있다. 헤더에 정의를 쓰면 이렇게 된다.

```text
LNK2005: "public: static int MyClass::myStaticVariable" already defined in Other.obj
```

한 번만 정의해야 하는데 여러 번 정의된 것이다. `#pragma once`나 include guard로도 못 막는다. 그건 같은 파일 안에서의 중복만 막고, 서로 다른 cpp가 각각 포함하는 건 막지 못한다.

## const 멤버인데도 정의가 필요한 경우

이게 한참 헷갈렸던 부분이다.

`static const int`는 클래스 안에서 초기화할 수 있다.

```cpp
class Config {
public:
    static const int kMaxChannels = 3;   // 여기서 초기화 가능
};
```

이렇게 써두고 대부분 잘 쓴다. 그런데 어떤 자리에서만 링크 에러가 났다.

```cpp
int n = Config::kMaxChannels;                    // 된다
int m = std::max(Config::kMaxChannels, count);   // 링크 에러
```

차이는 **주소를 필요로 하는가**다. 첫 줄은 값만 읽으니 컴파일러가 상수를 그 자리에 박아 넣고 끝난다. 둘째 줄의 `std::max`는 `const int&`를 받으니 참조를 만들어야 하고, 참조를 만들려면 실제 메모리가 있어야 한다. 그때 정의를 찾다가 없어서 에러가 난다.

C++17 이전에는 이걸 위해 cpp에 정의를 하나 더 써야 했다.

```cpp
// Config.cpp — 값 없이 정의만
const int Config::kMaxChannels;
```

같은 값을 쓰는 코드인데 어떤 함수에 넘기느냐에 따라 링크가 되고 안 되고가 갈리는 게 납득이 안 갔는데, 이유를 알고 나니 규칙 자체는 일관적이었다.

## C++17부터는 inline으로 끝난다

C++17에 inline 변수가 들어오면서 이 번거로움이 사라졌다.

```cpp
class Config {
public:
    inline static int counter = 0;              // 헤더에서 정의까지
    static constexpr int kMaxChannels = 3;      // constexpr 은 자동으로 inline
};
```

`inline`을 붙이면 여러 번역 단위에 같은 정의가 있어도 링커가 하나로 합친다. cpp 파일에 따로 쓸 게 없어진다.

`static constexpr` 멤버는 C++17부터 암묵적으로 inline이라 `std::max`에 넘겨도 링크 에러가 안 난다. 위에서 겪은 문제가 통째로 없어진 것이다.

지금 새로 짤 때는 상수는 `static constexpr`, 변수는 `inline static`으로 두고 헤더에서 끝낸다.

## static 멤버 함수

```cpp
class MyClass {
public:
    static int counter;
    static void reset();
    void tick();
};

void MyClass::reset() {
    counter = 0;              // static 멤버에 직접 접근
}

void MyClass::tick() {
    counter++;                // 일반 멤버 함수에서도 접근된다
    MyClass::counter++;       // 이렇게 써도 같다
}
```

static 멤버 함수에는 `this`가 없다. 그래서 일반 멤버 변수에는 접근할 수 없고 static 멤버에만 접근한다.

`this`가 없다는 게 제약처럼 보이는데, 오히려 그 덕분에 쓸 수 있는 자리가 있다.

## C 콜백에 멤버 함수를 넘기기

실무에서 static 멤버 함수를 제일 자주 쓰는 이유가 이것이다.

C API의 콜백은 대부분 순수 함수 포인터를 받는다. 멤버 함수는 숨은 `this` 인자가 있어서 시그니처가 안 맞는다. 그런데 static 멤버 함수는 `this`가 없으니 일반 함수 포인터로 넘어간다.

문제는 콜백 안에서 객체의 상태에 접근해야 한다는 것이다. 대부분의 C API가 사용자 데이터 포인터를 같이 받도록 되어 있어서, 거기에 `this`를 실어 보낸다.

```cpp
class Watcher {
public:
    void Start() {
        // 콜백에 this 를 사용자 데이터로 넘긴다
        RegisterCallback(&Watcher::OnEventThunk, this);
    }

private:
    // C 가 부르는 함수 — this 가 없다
    static void OnEventThunk(int code, void* user) {
        static_cast<Watcher*>(user)->OnEvent(code);
    }

    // 실제 처리 — 여기서는 멤버에 자유롭게 접근
    void OnEvent(int code) {
        count_++;
    }

    int count_ = 0;
};
```

이 패턴을 썽크(thunk)라고 부른다. static 함수는 캐스팅해서 넘겨주는 역할만 하고, 실제 로직은 일반 멤버 함수에 둔다.

Win32의 `WNDPROC`, pthread의 `pthread_create`, libusb의 핫플러그 콜백, WinRT의 이벤트 핸들러까지 같은 구조다. 사용자 데이터를 안 받는 API를 만나면 전역 맵으로 핸들과 객체를 연결하는 수밖에 없는데, 그런 API는 설계가 잘못된 것이다.

콜백을 다루는 다른 방법은 [콜백 함수 이해하기](/posts/cpp-callback-function/)에 따로 정리했다.

## 초기화 순서 문제

static 멤버는 `main`이 시작하기 전에 초기화된다. 여기서 조심할 게 있다.

**서로 다른 cpp 파일에 있는 정적 객체들의 초기화 순서는 정해져 있지 않다.**

```cpp
// A.cpp
Logger Logger::instance;

// B.cpp
Config Config::instance;   // 생성자에서 Logger::instance 를 쓴다면?
```

`Config`의 생성자가 `Logger::instance`를 쓰는데 `Logger` 쪽이 아직 초기화되지 않았다면, 아직 만들어지지 않은 객체를 건드리는 것이다. 링크 순서나 컴파일러에 따라 되기도 하고 안 되기도 한다. 개발 PC에서는 되는데 빌드 서버에서 죽는 종류의 문제다.

함수 안의 지역 static으로 바꾸면 해결된다.

```cpp
class Logger {
public:
    static Logger& Instance() {
        static Logger inst;      // 처음 호출될 때 초기화된다
        return inst;
    }
};
```

지역 static은 그 함수가 처음 불릴 때 초기화된다. 순서가 사용 시점으로 정해지니 위 문제가 없어진다. C++11부터는 이 초기화가 스레드 안전하다고 표준이 보장한다. 여러 스레드가 동시에 들어와도 한 번만 초기화된다.

이 형태는 [싱글톤 패턴](/posts/cpp-singleton-pattern/)에서 더 다뤘다.

소멸 쪽에도 비슷한 문제가 있다. 정적 객체는 `main`이 끝난 뒤 초기화 역순으로 소멸하는데, 번역 단위 간 순서는 역시 미정이다. 소멸자에서 다른 정적 객체를 쓰면 이미 소멸된 것을 건드릴 수 있다. 그래서 로거 같은 건 아예 소멸시키지 않고 두는 방법을 쓰기도 한다.

## 공유 자원이라는 뜻은 경쟁이 생긴다는 뜻

static 멤버 변수는 모든 인스턴스가 공유한다. 여러 스레드에서 객체를 만들면 그 카운터를 여러 스레드가 동시에 건드린다.

```cpp
class Session {
public:
    Session()  { ++count_; }     // 여러 스레드에서 동시에 실행될 수 있다
    ~Session() { --count_; }
private:
    inline static int count_ = 0;
};
```

`++count_`는 한 줄이지만 읽기, 더하기, 쓰기 세 단계다. 두 스레드가 겹치면 증가가 하나 사라진다. 자주 일어나진 않아서 더 찾기 어렵다.

```cpp
inline static std::atomic<int> count_{0};
```

카운터 정도면 `std::atomic`으로 충분하다. 더 복잡한 상태면 뮤텍스를 같이 static으로 두고 잠근다.

## DLL 경계에서 인스턴스가 갈린다

이건 나중에 겪은 것인데 적어둘 만하다.

같은 헤더를 실행 파일과 DLL이 각각 포함해서 빌드하면, static 멤버가 **각자 하나씩** 생긴다. 싱글톤이라고 만들어놨는데 실제로는 두 개가 돌아가는 상황이 된다.

DLL 쪽에서 등록한 설정이 실행 파일 쪽에서 안 보이는 걸로 알게 됐다. 해결하려면 `__declspec(dllexport)`/`dllimport`로 심볼을 하나만 두거나, 인스턴스를 넘겨주는 함수를 DLL이 export해야 한다.

## 정리하면

- 선언은 헤더, 정의는 cpp 한 곳. 빼먹으면 `unresolved external`, 헤더에 두면 `already defined`
- `static const int`를 클래스 안에서 초기화해도, 주소가 필요한 자리에 쓰면 정의가 따로 필요하다 (C++17 이전)
- C++17부터 `inline static`과 `static constexpr`로 헤더에서 끝난다
- static 멤버 함수는 `this`가 없어서 C 콜백에 넘길 수 있다. 사용자 데이터로 `this`를 실어 보내는 썽크 패턴
- 번역 단위 간 정적 객체의 초기화 순서는 미정이다. 함수 지역 static으로 피한다
- 공유 자원이므로 멀티스레드에서는 `atomic`이나 뮤텍스가 필요하다
- DLL과 실행 파일이 같은 헤더를 쓰면 인스턴스가 둘로 갈릴 수 있다
