---
title: "(C++) 싱글톤 패턴(Singleton Pattern) 이해하기"
description: "가장 흔한 싱글톤 구현이 왜 스레드 안전하지 않고 소멸자도 안 불리는지, 함수 지역 static 한 줄로 그게 다 해결되는 이유, 그리고 DLL 경계에서 인스턴스가 둘로 갈리는 문제를 정리했다."
date: 2025-03-17 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, singleton, design-pattern, oop, programming, thread-safety, static]
---
## 왜 쓰게 됐나

설정값을 여러 화면과 여러 모듈이 같이 봐야 했다. 인자로 계속 넘기자니 호출 경로가 깊어서 중간 함수들이 쓰지도 않는 인자를 받아 넘기는 모양이 됐다.

로거도 마찬가지다. 어디서든 로그를 찍는데 로그 파일은 하나여야 한다. 객체를 여러 개 만들면 같은 파일을 여러 개가 열게 된다.

이럴 때 쓰는 게 싱글톤이다. 인스턴스가 하나만 존재하도록 강제하고, 어디서든 그것에 접근할 수 있게 한다. 회사 공용 Wi-Fi를 모두가 쓰지만 네트워크 자체는 하나인 것과 비슷하다.

## 흔히 보는 구현

```cpp
#include <iostream>
using namespace std;

class Singleton {
private:
    static Singleton* instance;
    Singleton() {}  // 생성자를 private로 선언하여 외부에서 객체를 직접 생성하지 못하게 함.

public:
    static Singleton* GetInstance() {
        if (instance == nullptr)
            instance = new Singleton();
        return instance;
    }

    void ShowMessage() {
        cout << "싱글톤 인스턴스입니다." << endl;
    }
};

Singleton* Singleton::instance = nullptr;

int main() {
    Singleton* obj1 = Singleton::GetInstance();
    Singleton* obj2 = Singleton::GetInstance();

    obj1->ShowMessage();

    if (obj1 == obj2)
        cout << "두 객체는 동일합니다." << endl;

    return 0;
}
```

생성자를 private으로 막아서 외부에서 직접 만들 수 없게 하고, `GetInstance()`로만 얻게 한다. 처음 부를 때 만들고 이후에는 같은 것을 돌려준다.

의도한 대로 동작한다. 그런데 이 구현에는 문제가 세 개 있다.

## 문제 1: 스레드 안전하지 않다

```cpp
if (instance == nullptr)
    instance = new Singleton();
```

두 스레드가 거의 동시에 들어오면, 둘 다 `instance`가 널인 것을 보고 둘 다 `new`를 한다. 인스턴스가 두 개 생기고 하나는 그대로 샌다. 어느 쪽이 최종적으로 `instance`에 남을지도 정해져 있지 않다.

"하나만 존재한다"를 보장하려고 만든 패턴이 그걸 못 하는 상황이다. 실행할 때마다 되기도 하고 안 되기도 해서, 이 버그를 만나면 원인을 찾기가 상당히 어렵다.

락을 거는 게 첫 번째 생각인데, 매 호출마다 락을 잡으면 비용이 아깝다. 초기화는 딱 한 번뿐인데 그것 때문에 이후의 모든 호출이 락을 지나간다.

그래서 나온 게 이중 검사 잠금인데, 이것도 오래 쓰인 것에 비해 함정이 있다.

```cpp
// C++11 이전에는 이 코드가 옳지 않았다
if (instance == nullptr) {
    lock_guard<mutex> lock(m);
    if (instance == nullptr)
        instance = new Singleton();
}
```

`new Singleton()`은 메모리 할당, 생성자 호출, 포인터 대입 세 단계다. 컴파일러나 CPU가 순서를 바꿔서 **생성자가 끝나기 전에 포인터를 먼저 대입**할 수 있다. 그러면 다른 스레드가 락 밖의 첫 검사에서 널이 아닌 포인터를 보고, 아직 초기화 안 된 객체를 쓰게 된다.

C++11에서 메모리 모델이 표준에 들어오면서 `std::atomic`으로 제대로 쓸 수 있게 됐지만, 코드가 복잡해진다.

## 문제 2: 소멸자가 안 불린다

`new`만 있고 `delete`가 없다. 프로그램이 끝나면 OS가 메모리를 회수하니 누수라고 하기는 애매한데, **소멸자가 실행되지 않는 게 진짜 문제**다.

로거라면 버퍼에 남은 로그가 파일에 안 써진다. 마지막 몇 줄이 사라진다. 하필 프로그램이 이상 종료 직전에 남긴 로그가 제일 중요한데 그게 없다.

파일 핸들이나 장비 연결도 정리가 안 된 채로 프로세스가 끝난다. 다음에 다시 켤 때 장비가 아직 이전 세션을 붙들고 있는 상황이 생긴다.

## 문제 3: 복사를 막지 않았다

```cpp
Singleton a = *Singleton::GetInstance();     // 복사본이 하나 더 생긴다
```

생성자를 private으로 막았는데 **복사 생성자는 컴파일러가 자동으로 만들어준다**. 역참조해서 복사하면 두 번째 객체가 생긴다.

의도적으로 이렇게 쓸 사람은 없지만, 실수로는 나온다. 특히 `auto s = *GetInstance();`처럼 `auto`를 쓰면 포인터를 역참조한 값이 복사되는 걸 눈치채기 어렵다.

```cpp
Singleton(const Singleton&) = delete;
Singleton& operator=(const Singleton&) = delete;
```

`delete`로 지워두면 그런 코드가 컴파일 단계에서 걸린다.

## 함수 지역 static 하나로 다 해결된다

위의 세 문제가 한 번에 없어지는 구현이 있다.

```cpp
class Config {
public:
    static Config& Instance() {
        static Config inst;      // 처음 호출될 때 한 번만 초기화된다
        return inst;
    }

    Config(const Config&) = delete;
    Config& operator=(const Config&) = delete;

private:
    Config()  { /* 설정 로드 */ }
    ~Config() { /* 정리 */ }
};
```

**스레드 안전하다.** C++11 표준이 함수 지역 static의 초기화를 한 번만, 그리고 다른 스레드는 완료될 때까지 기다리도록 보장한다. 컴파일러가 안에서 필요한 동기화를 넣어준다. 이걸 매직 스태틱이라고 부른다.

**소멸자가 불린다.** 정적 저장 기간 객체라 `main`이 끝난 뒤 정리된다. 로그가 flush되고 핸들이 닫힌다.

**포인터가 아니라 참조를 돌려준다.** 널 검사를 할 필요가 없고, 호출하는 쪽에서 `delete`할 여지도 없다.

`GetInstance()`가 처음 불릴 때 만들어지므로, 서로 다른 cpp 파일의 전역 객체 초기화 순서 문제도 없다. [static 멤버](/posts/cpp-static-members-in-classes/) 쪽에 적은 초기화 순서 이야기가 여기서 해결된다.

## 그래도 남는 것들

이 구현이 좋다고 해서 싱글톤 자체의 문제가 없어지는 건 아니다.

### 초기화만 안전하고 사용은 안 안전하다

매직 스태틱이 보장하는 건 **초기화가 한 번만 일어난다**는 것뿐이다. 그 뒤 여러 스레드가 멤버를 동시에 읽고 쓰는 것은 여전히 각자 보호해야 한다.

```cpp
class Config {
public:
    void Set(const std::string& k, const std::string& v) {
        std::lock_guard<std::mutex> lock(m_);     // 이건 내가 해야 한다
        map_[k] = v;
    }
private:
    std::mutex m_;
    std::map<std::string, std::string> map_;
};
```

### 소멸 순서

정적 객체는 초기화의 역순으로 소멸한다. 그런데 다른 정적 객체의 소멸자에서 싱글톤을 쓰면, 이미 소멸된 것을 건드릴 수 있다.

```cpp
class Foo {
    ~Foo() { Logger::Instance().Write("bye"); }   // Logger 가 먼저 죽었다면?
};
static Foo g_foo;
```

로거처럼 끝까지 살아 있어야 하는 것은 일부러 소멸시키지 않기도 한다. `new`로 만들고 지우지 않는 것인데, 소멸자가 안 불리는 대신 죽은 참조 문제가 없다. 어느 쪽이 나은지는 그 객체가 소멸자에서 뭘 하느냐에 달렸다.

### DLL 경계에서 둘로 갈린다

같은 헤더를 실행 파일과 DLL이 각각 빌드하면, 함수 지역 static도 각자 하나씩 생긴다. 싱글톤이라고 만들었는데 실제로는 두 개다.

DLL 쪽에서 설정한 값이 실행 파일 쪽에서 안 보이는 걸로 알게 된다. 인스턴스를 얻는 함수를 DLL이 export하고 실행 파일은 그것만 쓰도록 해야 한다.

### 테스트가 어렵다

이게 제일 실질적인 단점이다. 싱글톤은 전역 상태라 테스트 사이에 상태가 남는다. 앞 테스트가 바꾼 설정이 뒤 테스트에 영향을 준다. 순서를 바꾸면 결과가 달라진다.

상태를 초기화하는 함수를 두는 게 최소한의 대응이다.

```cpp
void ResetForTest();     // 테스트에서만 부른다
```

근본적으로는 싱글톤이 아니라 인자로 넘기는 게 낫다. 인스턴스는 한 곳에서 하나만 만들되, 필요한 곳에 참조로 전달한다.

```cpp
class Engine {
public:
    explicit Engine(Config& cfg) : cfg_(cfg) {}   // 주입받는다
private:
    Config& cfg_;
};
```

이러면 테스트에서 다른 `Config`를 넣을 수 있고, 이 클래스가 무엇에 의존하는지가 생성자에 드러난다. 싱글톤은 어디서 뭘 쓰는지 코드를 다 읽어봐야 안다.

## 어디에 쓰나

전부 주입으로 바꾸는 게 항상 옳지는 않았다. 실제로 싱글톤으로 남긴 것들이다.

- **로거**: 호출 경로가 너무 넓다. 모든 함수에 로거를 넘길 수는 없다
- **설정**: 프로그램 시작에 한 번 읽고 그 뒤로는 읽기만 한다. 상태 변화가 없으니 부작용이 적다
- **장비 연결**: 하드웨어가 하나뿐이라 물리적으로도 하나다

반대로 주입으로 바꾼 것도 있다. 측정 파이프라인의 파라미터는 테스트마다 다르게 넣어봐야 해서 싱글톤이면 곤란했다.

기준은 "여러 개가 있으면 안 되는가"가 아니라 **"여러 개를 만들어보고 싶은 일이 생기는가"**로 잡았다. 후자면 싱글톤이 아니라 그냥 하나만 만들어 쓰는 객체다.

## 정리하면

- `if (nullptr) new` 방식은 스레드 안전하지 않고, 소멸자가 안 불리고, 복사를 막지 않는다
- 함수 지역 static(`static T inst;`)이면 세 가지가 한 번에 해결된다. C++11부터 초기화가 스레드 안전하다
- 초기화만 안전하다. 멤버 접근은 별도로 보호해야 한다
- 정적 객체의 소멸 순서 때문에 다른 소멸자에서 싱글톤을 쓰면 위험하다
- DLL과 실행 파일이 같은 헤더를 쓰면 인스턴스가 둘로 갈릴 수 있다
- 테스트를 생각하면 주입이 낫다. 로거처럼 호출 경로가 너무 넓은 것만 싱글톤으로 남긴다
