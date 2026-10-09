---
title: "(C++) 로그를 좀더 보기쉽게 찍기 (g++)"
description: "__FILE__, __LINE__, __func__, __PRETTY_FUNCTION__의 정체가 각각 다르다는 점부터, 이것들을 묶어 쓸 만한 로그 매크로를 만들 때 걸리는 함정까지 정리했다."
date: 2022-09-21 10:00:00 +0900
categories: [Dev, C++]
tags: [file-macro, func-macro, line-macro, pretty-function-macro, logging, macro, cpp, gcc, log, typeid]
---
## 왜 이걸 찾아봤나

보드에 올려놓고 도는 프로그램은 디버거를 붙이기가 번거롭다. 결국 로그를 찍게 되는데, 처음엔 그냥 이런 식이었다.

```c++
printf("read fail\n");
printf("read fail\n");
```

같은 문구를 여러 군데에 복붙해두면 나중에 로그만 보고는 어디서 찍힌 건지 알 수가 없다. 그래서 파일명, 줄 번호, 함수명을 자동으로 붙이는 방법을 찾아봤다.

## 네 가지 정체가 다르다

이름이 비슷하게 생겨서 다 같은 매크로인 줄 알았는데 아니었다. 이 차이 때문에 나중에 매크로를 만들 때 한 번 막힌다.

| 이름 | 정체 | 값 |
| :--- | :--- | :--- |
| `__FILE__` | 전처리기 매크로 | 컴파일러에 넘긴 소스 경로 문자열 |
| `__LINE__` | 전처리기 매크로 | 줄 번호 (정수) |
| `__func__` | 함수 스코프의 지역 배열 | 함수 이름 |
| `__PRETTY_FUNCTION__` | 함수 스코프의 지역 배열 (GCC 확장) | 반환형·네임스페이스·인자까지 포함한 시그니처 |

`__FILE__`과 `__LINE__`은 전처리 단계에서 토큰으로 치환된다. 그래서 다른 문자열 리터럴과 이어 붙일 수 있다.

`__func__`는 다르다. C++ 표준은 이걸 매크로가 아니라 **함수 본문 맨 앞에 선언된 것처럼 동작하는 `static const char[]`** 로 정의한다. `__PRETTY_FUNCTION__`도 GCC 확장이지만 성격은 같다. 그래서 아래 코드는 컴파일이 안 된다.

```c++
// 컴파일 에러 - __func__ 는 문자열 리터럴이 아니라 변수다
#define LOG_TAG "[" __func__ "] "

// 이건 된다 - 둘 다 전처리기 매크로
#define LOC __FILE__ ":" TOSTR(__LINE__)
```

그리고 `__func__`는 함수 밖에서는 아예 쓸 수 없다. 전역 스코프에 뒀다가 `'__func__' was not declared in this scope`를 보고 나서야 이유를 알았다.

## 예제

원래 확인용으로 짰던 코드다.

```c++
#include <iostream>
#include <typeinfo>

class CPrettyLog
{
public:
    void Print(void)
    {
        std::cout
            << "__PRETTY_FUNCTION__ = " << __PRETTY_FUNCTION__ << std::endl
            << "__func__ = " << __func__ << std::endl
            << "__LINE__ = " << __LINE__ << std::endl
            << "__FILE__ = " << __FILE__ << std::endl
            << "typeid(this).name() = " << typeid(this).name() << std::endl
            << std::endl;
    }
};

void Print(void)
{
    std::cout
        << "__PRETTY_FUNCTION__ = " << __PRETTY_FUNCTION__ << std::endl
        << "__func__ = " << __func__ << std::endl
        << "__LINE__ = " << __LINE__ << std::endl
        << "__FILE__ = " << __FILE__ << std::endl
        << std::endl;
}
 
 
int main(int argc, char** argv)
{
    CPrettyLog pl;
    pl.Print();
 
    Print();
 
    std::cout
        << "__PRETTY_FUNCTION__ = " << __PRETTY_FUNCTION__ << std::endl
        << "__func__ = " << __func__ << std::endl
        << "__LINE__ = " << __LINE__ << std::endl
        << "__FILE__ = " << __FILE__ << std::endl
        << std::endl;
 
    return 0;
}
```

결과.

```text
__PRETTY_FUNCTION__ = void CPrettyLog::Print()
__func__ = Print
__LINE__ = 13
__FILE__ = main.cpp
typeid(this).name() = P10CPrettyLog

__PRETTY_FUNCTION__ = void Print()
__func__ = Print
__LINE__ = 26
__FILE__ = main.cpp

__PRETTY_FUNCTION__ = int main(int, char**)
__func__ = main
__LINE__ = 42
__FILE__ = main.cpp
```

여기서 눈여겨볼 지점이 두 개다.

첫째, 클래스 안의 `Print`와 전역 `Print`의 `__func__`가 둘 다 `Print`로 똑같이 나온다. 이름이 겹치는 함수가 있으면 `__func__`만으로는 구분이 안 된다. `__PRETTY_FUNCTION__`은 `void CPrettyLog::Print()`와 `void Print()`로 갈라준다. 오버로딩된 함수를 추적할 때도 인자 타입까지 나오니 이쪽이 확실하다.

둘째, `typeid(this).name()`이 `P10CPrettyLog`로 나온다. 사람이 읽으라고 만든 문자열이 아니라 Itanium ABI 맹글링 결과다. `P`는 포인터, `10`은 뒤따르는 이름의 글자 수, `CPrettyLog`가 실제 이름이다.

## 맹글링 풀기

맹글링된 이름을 그대로 로그에 찍으면 나중에 자기가 봐도 못 읽는다. GCC는 푸는 함수를 제공한다.

```c++
#include <cxxabi.h>
#include <typeinfo>
#include <memory>
#include <string>
#include <cstdlib>

std::string demangle(const char* name)
{
    int status = 0;
    std::unique_ptr<char, void(*)(void*)> p(
        abi::__cxa_demangle(name, nullptr, nullptr, &status), std::free);
    return (status == 0 && p) ? p.get() : name;
}

// demangle(typeid(this).name())  ->  "CPrettyLog*"
```

`__cxa_demangle`이 돌려주는 버퍼는 `malloc`으로 잡힌 것이라 `free`해야 한다. 그래서 `unique_ptr`에 삭제자로 `std::free`를 물려뒀다. 실패했을 때(status가 0이 아닐 때)는 원본을 그대로 돌려주는 편이 안전하다. 로그 유틸이 예외를 던지거나 널을 뱉으면 디버깅하려다 오히려 죽는다.

MSVC는 `typeid(...).name()`이 처음부터 `class CPrettyLog *`처럼 읽을 수 있는 형태로 나와서 이 과정이 필요 없다.

## 컴파일러마다 이름이 다르다

`__PRETTY_FUNCTION__`은 GCC 확장이라 MSVC에는 없는 이름이다. 같은 코드를 윈도우 쪽 툴과 보드 쪽 프로그램에서 같이 쓰려면 한 번 감싸야 한다.

```c++
#if defined(_MSC_VER)
  #define FUNC_SIG __FUNCSIG__
#elif defined(__GNUC__) || defined(__clang__)
  #define FUNC_SIG __PRETTY_FUNCTION__
#else
  #define FUNC_SIG __func__
#endif
```

`__FUNCTION__`은 GCC와 MSVC 양쪽에 다 있지만 표준이 아니다. 표준만 쓰겠다면 `__func__`가 답이고, 대신 시그니처는 못 얻는다.

## 파일 경로가 지저분한 문제

`__FILE__`은 컴파일러에게 넘긴 경로를 그대로 담는다. 빌드 스크립트가 절대 경로로 넘기면 로그가 이렇게 된다.

```text
[/home/pi/work/project/src/module/handler.cpp:214] read fail
```

한 줄이 거의 다 경로다. 파일명만 뽑아내면 된다.

```c++
constexpr const char* base_name(const char* p)
{
    const char* f = p;
    for (const char* c = p; *c; ++c)
        if (*c == '/' || *c == '\\') f = c + 1;
    return f;
}
```

`constexpr`이라 상수식이 요구되는 자리에서는 컴파일 타임에 끝난다. 다만 로그 매크로 안에서 그냥 호출하면 런타임 호출로 남을 수 있으니, 신경 쓰이면 파일마다 `static constexpr const char* kFile = base_name(__FILE__);`처럼 상수에 한 번 받아두면 확실하다.

GCC 12부터는 `__FILE_NAME__`이 생겨서 이 함수 없이 파일명만 얻을 수 있다. 다만 오래된 툴체인이 물려 있는 보드에서는 못 쓰는 경우가 많다.

## 실제로 쓰는 매크로

여기까지 모아서 쓴 형태다.

```c++
#include <cstdio>

#define LOG(fmt, ...)                                            \
    do {                                                         \
        std::fprintf(stderr, "[%s:%d][%s] " fmt "\n",            \
                     base_name(__FILE__), __LINE__, __func__,    \
                     ##__VA_ARGS__);                             \
    } while (0)
```

몇 가지가 들어 있다.

`do { ... } while (0)`으로 감싼 이유는 `if (x) LOG("a"); else ...` 같은 자리에서 매크로가 문장 하나로 취급되게 하려는 것이다. 중괄호만 쓰면 뒤에 붙는 세미콜론 때문에 `else`가 떨어져 나간다.

`fmt`를 `"[%s:%d][%s] "` 뒤에 그냥 붙여 쓴 건 `fmt`가 문자열 리터럴이라 전처리 단계에서 이어 붙기 때문이다. 여기가 `__func__`를 앞쪽 리터럴에 못 붙이는 이유와 정확히 대칭이다. `__func__`는 변수라서 `%s` 인자로 넘겨야 하고, `fmt`는 리터럴이라 붙여도 된다.

`##__VA_ARGS__`는 인자가 없을 때 앞의 쉼표를 지워주는 GCC 확장이다. 이게 없으면 `LOG("start")`가 `fprintf(stderr, "..." "start" "\n", )`로 펼쳐져서 컴파일이 깨진다. C++20부터는 `__VA_OPT__(,)`라는 표준 문법이 생겼다.

```c++
// C++20
#define LOG(fmt, ...) \
    std::fprintf(stderr, "[%s:%d][%s] " fmt "\n", \
                 base_name(__FILE__), __LINE__, __func__ __VA_OPT__(,) __VA_ARGS__)
```

> **끌 때는 인자 계산까지 같이 꺼야 한다.** 로그 레벨을 넣을 때 `if (level >= kDebug) fprintf(...)` 식으로 함수 안에서 거르면, 로그가 꺼져 있어도 인자로 넘긴 표현식은 그대로 평가된다. `LOG_D("state=%s", expensive_dump().c_str())` 같은 줄이 있으면 로그를 껐는데도 `expensive_dump()`가 매번 불린다. 매크로 안에서 `if`로 감싸 인자 평가 자체를 건너뛰게 해야 한다.
{: .prompt-warning }

## C++20이면 매크로가 필요 없다

C++20에 `std::source_location`이 들어왔다. 기본 인자로 두면 호출한 쪽의 위치가 채워진다.

```c++
#include <source_location>
#include <string_view>
#include <iostream>

void log(std::string_view msg,
         const std::source_location loc = std::source_location::current())
{
    std::cerr << loc.file_name() << ':' << loc.line()
              << " [" << loc.function_name() << "] " << msg << '\n';
}

log("read fail");   // 호출한 줄 번호가 찍힌다
```

매크로가 아니라 함수라서 네임스페이스에 넣을 수 있고, 오버로딩도 되고, 디버거에서 밟히기도 한다. GCC 11, MSVC 16.10 이상이면 쓸 수 있는데 보드 쪽 툴체인이 그 버전을 안 넘기는 경우가 흔해서 프로젝트마다 갈린다.

## 정리하면

- `__FILE__`, `__LINE__`은 전처리기 매크로라 리터럴과 이어 붙일 수 있고, `__func__`, `__PRETTY_FUNCTION__`은 변수라서 안 된다
- 이름이 겹치는 함수가 있으면 `__func__`로는 구분이 안 되고 `__PRETTY_FUNCTION__`이 필요하다
- `typeid(...).name()`은 GCC에서 맹글링된 문자열이라 `abi::__cxa_demangle`로 풀어야 읽을 수 있다
- 가변인자 매크로는 인자 0개 케이스에서 깨지므로 `##__VA_ARGS__`나 `__VA_OPT__`가 필요하다
- C++20을 쓸 수 있으면 `std::source_location` 쪽이 매크로보다 낫다

## 참고

- [GCC 매뉴얼: Function Names as Strings](https://gcc.gnu.org/onlinedocs/gcc/Function-Names.html)
- [dev-crazybird: 로그를 좀더 이쁘게 박아보자(g++ 기준)](https://dev-crazybird.blogspot.com/2014/04/g.html)
