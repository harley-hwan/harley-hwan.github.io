---
title: "(C++) 콜백 함수(Callback Function) 이해하기"
description: "콜백의 세 가지 구현 방식과, 실제로 붙이면서 걸린 것들 — C API에 멤버 함수를 못 넘기는 문제, 다른 스레드에서 오는 콜백, 콜백 안에서 등록을 해제할 때의 재진입, 예외가 경계를 넘을 때."
date: 2025-03-17 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, callback, std-function, lambda, programming, thread-safety]
---
## 왜 필요한가

측정 모듈을 DLL로 분리하면서 필요해졌다. 데이터가 한 프레임 준비되면 상위 프로그램에 알려줘야 하는데, DLL은 상위 프로그램이 뭘 하는지 모른다.

상위가 주기적으로 "데이터 있냐"고 물어보게 할 수도 있다. 그러면 지연이 생기고, 없을 때도 계속 물어보게 된다. 반대로 하는 게 콜백이다. 상위가 "준비되면 이 함수를 불러줘"라고 함수를 하나 등록해두고, 모듈이 그때가 되면 그걸 부른다.

택배로 치면 "도착하면 이 번호로 문자 주세요"에 해당한다. 등록한 쪽은 기다리지 않고 다른 일을 하고, 부르는 쪽은 등록된 것이 무엇인지 몰라도 된다.

- 알림 함수: 콜백 (내가 작성, 남이 호출)
- 택배 회사: 콜백을 호출하는 쪽 (라이브러리, 모듈)
- 택배 도착: 이벤트

## 세 가지 방식

### 1. 함수 포인터

가장 기본이다. C와 호환되는 유일한 방식이라 라이브러리 인터페이스에서는 이것만 쓸 수 있는 경우가 많다.

```cpp
#include <iostream>
using namespace std;

void callbackFunc(int value) {
    cout << "콜백 호출! 받은 값은: " << value << endl;
}

void executeCallback(void (*cb)(int), int val) {
    cout << "executeCallback 실행중..." << endl;
    cb(val);
}

int main() {
    executeCallback(callbackFunc, 42);
    return 0;
}
```

가볍고 빠르다. 대신 시그니처가 정확히 일치해야 하고, 상태를 들고 갈 수 없다.

### 2. 멤버 함수 포인터

```cpp
#include <iostream>
using namespace std;

class MyClass {
public:
    void memberCallback(int x) {
        cout << "멤버 콜백 호출됨: " << x << endl;
    }
};

void executeMemberCallback(MyClass* obj, void (MyClass::*cb)(int), int val) {
    cout << "executeMemberCallback 실행중..." << endl;
    (obj->*cb)(val);
}

int main() {
    MyClass myObj;
    executeMemberCallback(&myObj, &MyClass::memberCallback, 123);
    return 0;
}
```

문법이 낯설다. `void (MyClass::*cb)(int)`가 타입이고, 호출은 `(obj->*cb)(val)`이다. 괄호를 빠뜨리면 연산자 우선순위 때문에 컴파일이 안 된다.

객체와 함수 포인터를 항상 짝으로 들고 다녀야 한다는 게 불편하다. 그리고 멤버 함수 포인터는 일반 함수 포인터보다 클 수 있다. 다중 상속이나 가상 상속이 있으면 오프셋 정보가 붙어서 크기가 커진다. `void*`에 담으려 하면 안 되는 이유가 이것이다.

### 3. std::function

```cpp
#include <iostream>
#include <functional>
using namespace std;

void executeStdCallback(function<void(int)> cb, int val) {
    cout << "executeStdCallback 실행중..." << endl;
    cb(val);
}

int main() {
    executeStdCallback([](int v) {
        cout << "람다 콜백 호출됨: " << v << endl;
    }, 2025);

    return 0;
}
```

함수, 람다, 멤버 함수를 바인딩한 것, 함수 객체를 전부 같은 타입에 담을 수 있다. 상태도 캡처로 들고 간다. 지금은 특별한 이유가 없으면 이걸 쓴다.

## C API에는 멤버 함수를 못 넘긴다

실제로 제일 먼저 막히는 부분이다.

라이브러리가 `void (*)(int, void*)` 같은 순수 함수 포인터를 요구하면 `std::function`도 멤버 함수 포인터도 넘길 수 없다. 멤버 함수에는 숨은 `this` 인자가 있어서 시그니처 자체가 다르다.

대부분의 C API가 사용자 데이터 포인터를 같이 받도록 되어 있어서, 거기에 `this`를 실어 보낸다.

```cpp
class Receiver {
public:
    void Start() {
        lib_register(&Receiver::Thunk, this);
    }
private:
    static void Thunk(int code, void* user) {         // C 가 부르는 함수
        static_cast<Receiver*>(user)->OnEvent(code);
    }
    void OnEvent(int code) { count_++; }              // 실제 처리
    int count_ = 0;
};
```

static 멤버 함수는 `this`가 없어서 일반 함수 포인터로 넘어간다. 이 패턴은 [static 멤버](/posts/cpp-static-members-in-classes/) 쪽에도 적어뒀다.

사용자 데이터를 안 받는 C API를 만나면 방법이 없다. 전역 변수나 핸들-객체 맵을 두는 수밖에 없는데, 그런 API는 애초에 한 번에 하나만 쓸 수 있는 설계다.

## 콜백은 대개 다른 스레드에서 온다

이걸 모르고 UI를 직접 건드렸다가 몇 번 데었다.

라이브러리가 자기 작업 스레드에서 콜백을 부르는 경우가 대부분이다. 윈도우 GUI에서 UI 컨트롤은 그것을 만든 스레드에서만 다뤄야 하므로, 콜백 안에서 리스트 박스에 항목을 넣으면 안 된다.

콜백에서는 데이터만 갱신하고 화면 갱신은 메시지나 타이머로 넘긴다.

```cpp
void OnEvent(int code) {
    {
        std::lock_guard<std::mutex> lock(mutex_);
        queue_.push_back(code);          // 데이터만
    }
    PostMessage(hwnd_, WM_MY_UPDATE, 0, 0);   // UI 스레드에 알림만
}
```

공유하는 자료구조는 뮤텍스로 보호해야 한다. 이 부분을 빠뜨려서 [BLE 스캔](/posts/cpp-mfc-bluetooth-device-scan-and-listview/)에서 실제로 문제가 났다.

그리고 콜백 안에서 `PostMessage`를 이벤트마다 보내면 메시지 큐가 넘친다. 이벤트가 초당 수백 건 오는 상황에서는 주기적으로 모아서 처리해야 한다.

## 콜백 안에서 오래 걸리면 안 된다

콜백을 부르는 쪽은 대개 내부 락을 잡은 상태다. 그 안에서 오래 걸리는 작업을 하면 라이브러리 전체가 멈춘다. 더 나쁜 건, 콜백 안에서 그 라이브러리의 다른 함수를 부르면 같은 락을 다시 잡으려다 데드락이 되는 경우다.

```cpp
void OnDataReady(const Frame& f) {
    lib_stop();          // 위험 — 라이브러리가 이미 락을 잡고 있을 수 있다
}
```

콜백에서는 최소한만 하고 빠져나오는 게 원칙이다. 정지 요청 같은 건 플래그만 세우고 다른 곳에서 처리한다.

## 콜백 안에서 등록을 해제할 때

리스너 여러 개를 리스트로 관리하면 이 문제가 나온다.

```cpp
for (auto& cb : listeners_) cb(event);      // 이 안에서 리스너가 제거되면?
```

콜백 안에서 `RemoveListener`를 부르면 순회 중인 컨테이너가 바뀌어서 반복자가 무효가 된다. 리스너를 스스로 해제하는 건 흔한 요구라 반드시 부딪힌다.

복사본을 순회하면 간단히 해결된다.

```cpp
auto snapshot = listeners_;                 // 복사
for (auto& cb : snapshot) cb(event);
```

리스너가 많으면 복사 비용이 있으니, 순회 중에는 삭제를 표시만 하고 끝난 뒤 정리하는 방식도 쓴다.

## 수명 관리

콜백이 캡처한 객체가 콜백보다 먼저 죽으면 그대로 문제가 된다. 등록해두고 객체를 지우는 실수가 생각보다 자주 나온다.

`weak_ptr`로 확인하는 방식이 안전하다.

```cpp
std::weak_ptr<Receiver> weak = shared_receiver;
lib.SetCallback([weak](int code) {
    if (auto r = weak.lock())      // 살아 있을 때만
        r->OnEvent(code);
});
```

등록을 해제하는 수단도 반드시 있어야 한다. 등록만 되고 해제가 안 되는 API는 객체를 지울 방법이 없다. 등록 시 토큰을 돌려주고 그걸로 해제하는 형태가 무난했다.

## std::function은 비어 있을 수 있다

```cpp
std::function<void(int)> cb;    // 아직 아무것도 안 담겼다
cb(42);                         // std::bad_function_call 예외
```

콜백을 등록 안 한 상태에서 이벤트가 나면 이렇게 된다. 부르기 전에 확인해야 한다.

```cpp
if (cb) cb(42);
```

C API의 함수 포인터도 같다. `nullptr`인지 보고 불러야 한다.

## 예외가 경계를 넘으면 안 된다

C 라이브러리가 부른 콜백에서 예외를 던지면, C 코드 프레임을 지나 스택이 풀린다. 이건 정의되지 않은 동작이다. 대부분 그 자리에서 프로그램이 끝난다.

```cpp
static void Thunk(int code, void* user) noexcept {
    try {
        static_cast<Receiver*>(user)->OnEvent(code);
    } catch (const std::exception& e) {
        LogError(e.what());          // 여기서 다 잡는다
    } catch (...) {
        LogError("unknown");
    }
}
```

`noexcept`를 붙여두면 실수로 새어 나갈 때 `std::terminate`가 불려서 최소한 어디서 났는지는 알 수 있다.

## 세 방식 비교

| | 함수 포인터 | 멤버 함수 포인터 | std::function |
| :--- | :--- | :--- | :--- |
| 상태 보유 | 불가 | 객체를 따로 들고 다녀야 함 | 캡처로 가능 |
| C 호환 | 가능 | 불가 | 불가 |
| 호출 비용 | 간접 호출 1회 | 간접 호출 1회 | 간접 호출 + 캡처 크면 힙 |
| 문법 | 단순 | 복잡 | 단순 |

성능이 정말 중요한 경로면 `std::function` 대신 템플릿 인자로 받아 인라인되게 하는 방법이 있다. 다만 타입이 통일되지 않아 컨테이너에 담을 수 없다.

```cpp
template <class F>
void ForEachFrame(F&& cb) { /* ... */ }    // 인라인 가능
```

실제로는 콜백 하나 부르는 비용보다 그 안에서 하는 일이 훨씬 크다. 측정해보기 전에 `std::function`을 피할 이유는 없었다.

## 정리하면

- C API에 멤버 함수를 넘기려면 static 썽크 + 사용자 데이터로 `this`를 실어 보낸다
- 콜백은 대개 다른 스레드에서 온다. 공유 자료는 보호하고 UI는 직접 건드리지 않는다
- 콜백 안에서 오래 걸리거나 라이브러리 함수를 다시 부르면 데드락이 될 수 있다
- 순회 중에 리스너가 해제될 수 있다. 복사본을 순회하거나 지연 삭제한다
- 캡처한 객체의 수명을 `weak_ptr`로 확인하고, 등록 해제 수단을 반드시 둔다
- `std::function`은 비어 있을 수 있다. 부르기 전에 검사한다
- 예외가 C 경계를 넘으면 안 된다. 썽크에서 전부 잡는다
