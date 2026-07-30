---
title: "(C++) 파이썬 스크립트 불러오기"
description: "C++ 프로그램 안에서 파이썬 스크립트를 돌리려고 인터프리터를 임베딩했다. Debug 빌드에서 링크가 깨지는 문제, Py_Finalize 후 재초기화가 안 되는 문제, 에러 내용을 프로그램으로 받는 방법을 정리했다."
date: 2023-06-08 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, python, python-h, embedding, gil, msvc]
---
## 왜 임베딩인가

측정 데이터를 후처리하는 코드가 파이썬으로 이미 있었다. numpy로 몇 줄이면 되는 계산인데, 같은 걸 C++로 다시 짜는 건 시간 낭비였다.

파이썬을 별도 프로세스로 띄우고 파일이나 파이프로 데이터를 주고받는 방법도 있다. 실제로 그게 더 단순한 경우가 많다. 그런데 여기서는 데이터가 크고 호출이 잦아서, 매번 프로세스를 띄우고 데이터를 직렬화하는 비용이 부담됐다. 그래서 인터프리터를 프로그램 안에 넣기로 했다.

## 최소 예제

```c++
#include <Python.h>

int main(int argc, char* argv[])
{
    // 1. 프로그램 이름 디코딩
    wchar_t* program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    // 2. 파이썬 인터프리터 초기화
    Py_SetProgramName(program);  // 선택적이지만 권장됨
    Py_Initialize();

    // 3. 파이썬 코드 실행
    PyRun_SimpleString("from time import time,ctime\n"
        "print('Today is',ctime(time()))\n");

    // 4. 파이썬 인터프리터 종료
    Py_Finalize();

    // 5. 메모리 정리
    PyMem_RawFree(program);
    return 0;
}
```

`Py_SetProgramName`은 인터프리터가 표준 라이브러리 위치를 찾는 기준을 잡아준다. 이걸 안 주면 실행 파일 위치에 따라 모듈을 못 찾는 경우가 생긴다.

`Py_DecodeLocale`이 돌려주는 버퍼는 `PyMem_RawFree`로 해제한다. `free`가 아니다. 파이썬의 raw 메모리 할당자로 잡힌 것이라 짝을 맞춰야 한다.

## 빌드부터 막혔다

코드보다 빌드 설정에서 시간을 더 썼다.

**포함 경로와 라이브러리 경로**를 넣어야 한다. Visual Studio 기준으로 파이썬 설치 폴더의 `include`와 `libs`다.

```text
추가 포함 디렉터리:   C:\Python311\include
추가 라이브러리 디렉터리: C:\Python311\libs
추가 종속성:          python311.lib
```

**Debug 빌드에서 링크가 깨진다.** 이게 제일 짜증났다. `Python.h`가 `_DEBUG`가 정의되어 있으면 `python311_d.lib`를 링크하도록 `#pragma comment`를 넣는다. 그런데 일반 파이썬 설치본에는 디버그 라이브러리가 없다.

```text
LNK1104: 'python311_d.lib' 파일을 열 수 없습니다.
```

방법이 두 가지다. 파이썬 설치 관리자에서 "Download debug binaries" 옵션을 켜서 다시 설치하거나, `_DEBUG`를 잠깐 끄고 헤더를 포함하는 것이다.

```c++
#ifdef _DEBUG
  #undef _DEBUG
  #include <Python.h>
  #define _DEBUG
#else
  #include <Python.h>
#endif
```

두 번째 방법이 흔히 쓰이는데, 파이썬 쪽만 릴리스 런타임을 쓰게 되는 것이라 완전히 깔끔하진 않다. 디버깅할 때 파이썬 내부로는 못 들어간다. 나는 이쪽으로 갔다. C++ 코드만 디버깅하면 충분했다.

**비트 수를 맞춰야 한다.** 64비트 프로젝트에 32비트 파이썬 라이브러리를 링크하면 `LNK1112`가 난다. 파이썬이 여러 버전 깔려 있으면 어느 경로를 넣었는지 확인해야 한다.

## Py_SetProgramName은 이제 쓰면 안 된다

위 코드는 Python 3.10까지는 그대로 동작한다. 3.11에서 deprecated 되었고 3.12에서 제거됐다. 최신 파이썬으로 올리면 컴파일이 안 된다.

지금 방식은 `PyConfig`로 설정을 채워 초기화하는 것이다.

```c++
#include <Python.h>

PyStatus init_python(const wchar_t* exe_path)
{
    PyConfig config;
    PyConfig_InitPythonConfig(&config);

    PyStatus st = PyConfig_SetString(&config, &config.program_name, exe_path);
    if (PyStatus_Exception(st)) { PyConfig_Clear(&config); return st; }

    st = Py_InitializeFromConfig(&config);
    PyConfig_Clear(&config);
    return st;
}
```

인자가 늘어난 대신 얻는 것도 있다. `config.module_search_paths`로 `sys.path`를 초기화 시점에 직접 지정할 수 있고, `config.isolated`를 켜면 사용자 환경 변수(`PYTHONPATH`, `PYTHONHOME`)의 영향을 안 받는다. 배포할 프로그램에서는 이게 중요하다. 사용자 PC에 다른 파이썬이 깔려 있어도 내가 같이 배포한 것만 쓰게 된다.

## PyRun_SimpleString은 에러를 안 돌려준다

간단한 코드를 돌릴 때는 편한데, 문제가 생기면 답답하다. 스크립트에서 예외가 나면 파이썬이 트레이스백을 **표준 에러로 찍고** 함수는 `-1`만 돌려준다. GUI 프로그램에는 콘솔이 없으니 그 메시지가 어디에도 안 남는다.

"실패했다"는 것만 알고 왜 실패했는지 모르는 상태가 된다.

에러 내용을 받으려면 예외를 직접 꺼내야 한다.

```c++
#include <string>

std::string take_python_error()
{
    if (!PyErr_Occurred()) return {};

    PyObject *type = nullptr, *value = nullptr, *tb = nullptr;
    PyErr_Fetch(&type, &value, &tb);
    PyErr_NormalizeException(&type, &value, &tb);

    std::string msg;
    if (value) {
        PyObject* s = PyObject_Str(value);
        if (s) {
            const char* p = PyUnicode_AsUTF8(s);
            if (p) msg = p;
            Py_DECREF(s);
        }
    }

    Py_XDECREF(type);
    Py_XDECREF(value);
    Py_XDECREF(tb);
    return msg;
}
```

`PyErr_Fetch`는 에러 상태를 가져오면서 **지운다**. 가져오고 나면 `PyErr_Occurred()`가 거짓이 된다. 지우지 않으면 다음 파이썬 호출이 "이전 에러가 남아 있다"는 상태에서 시작해서 엉뚱하게 동작한다.

트레이스백까지 문자열로 만들려면 `traceback` 모듈을 불러서 `format_exception`을 호출해야 한다. 줄 번호가 나와야 원인을 찾을 수 있어서 결국 그것까지 넣었다.

## Py_Finalize 후에 다시 초기화하면 죽는다

처음엔 스크립트를 실행할 때마다 `Py_Initialize`와 `Py_Finalize`를 짝으로 불렀다. 깔끔해 보였다.

두 번째 호출에서 죽었다.

파이썬 문서에도 적혀 있는 알려진 제약이다. 확장 모듈 중 상당수가 재초기화를 지원하지 않는다. numpy가 대표적이다. `Py_Finalize`가 정적 상태를 완전히 되돌리지 못해서, 다시 초기화하면 이전 상태가 남은 채로 시작한다.

**프로그램 시작할 때 한 번 초기화하고 끝날 때까지 유지**하는 게 맞다. 종료할 때도 `Py_Finalize`를 아예 안 부르는 경우가 많다. 프로세스가 끝나면 어차피 다 해제되고, 종료 중에 확장 모듈이 죽는 걸 피할 수 있다.

## 값을 주고받으려면 객체 API가 필요하다

문자열로 코드를 실행하는 것만으로는 계산 결과를 못 받는다. 모듈을 불러서 함수를 부르고 반환값을 가져와야 한다.

```c++
// sys.path 에 스크립트 폴더를 추가
PyRun_SimpleString("import sys; sys.path.insert(0, './scripts')");

PyObject* mod = PyImport_ImportModule("analyze");        // analyze.py
if (!mod) { /* take_python_error() */ }

PyObject* fn = PyObject_GetAttrString(mod, "process");   // def process(a, b)
if (fn && PyCallable_Check(fn)) {
    PyObject* args = Py_BuildValue("(di)", 3.14, 512);
    PyObject* ret  = PyObject_CallObject(fn, args);
    Py_DECREF(args);

    if (ret) {
        double v = PyFloat_AsDouble(ret);
        Py_DECREF(ret);
    } else {
        // 예외 발생
    }
}
Py_XDECREF(fn);
Py_XDECREF(mod);
```

참조 카운트 관리가 이 API의 전부라고 해도 될 정도다. 규칙이 함수마다 다르다.

- `PyImport_ImportModule`, `PyObject_CallObject`, `Py_BuildValue`: 새 참조를 준다. `Py_DECREF` 해야 한다
- `PyList_GetItem`, `PyDict_GetItem`: 빌린 참조다. 해제하면 안 된다
- `PyList_SetItem`, `PyTuple_SetItem`: 참조를 **가져간다**. 넘긴 뒤 해제하면 안 된다

`Py_DECREF`를 빠뜨리면 누수고, 한 번 더 하면 그 자리에서 죽는다. 호출이 몇 개만 늘어도 관리가 어려워져서, 결국 RAII 래퍼를 하나 만들어 썼다.

```c++
class PyRef {
public:
    explicit PyRef(PyObject* p = nullptr) : p_(p) {}
    ~PyRef() { Py_XDECREF(p_); }
    PyRef(const PyRef&) = delete;
    PyRef& operator=(const PyRef&) = delete;
    PyRef(PyRef&& o) noexcept : p_(o.p_) { o.p_ = nullptr; }
    PyObject* get() const { return p_; }
    explicit operator bool() const { return p_ != nullptr; }
private:
    PyObject* p_;
};
```

## GIL

파이썬은 전역 인터프리터 락(GIL)을 잡은 스레드에서만 API를 부를 수 있다. 메인 스레드에서만 쓰면 신경 쓸 게 없는데, 작업 스레드에서 부르려면 명시적으로 잡아야 한다.

```c++
PyGILState_STATE gil = PyGILState_Ensure();
// 여기서 파이썬 API 호출
PyGILState_Release(gil);
```

`Ensure`와 `Release`는 반드시 짝을 맞춰야 하고, 같은 스레드에서 해야 한다. 중간에 예외로 빠져나가면 락이 잡힌 채로 남아서 프로그램 전체가 멈춘다. 이것도 RAII로 감싸는 게 안전하다.

반대로 오래 걸리는 C++ 작업 중에는 GIL을 놓아줘야 다른 파이썬 스레드가 돈다. `Py_BEGIN_ALLOW_THREADS` / `Py_END_ALLOW_THREADS` 매크로 쌍이 그 역할을 한다.

## 배포

개발 PC에서는 잘 되는데 다른 PC에서 안 되는 게 마지막 관문이었다. 파이썬이 안 깔려 있으면 당연히 안 돌아간다.

파이썬 공식 사이트에 embeddable package라는 게 있다. 인터프리터와 표준 라이브러리를 zip 하나로 묶은 것이라 프로그램 폴더에 같이 넣으면 된다. 레지스트리를 안 건드리고 시스템 파이썬과 섞이지 않는다.

이걸 쓸 때는 `PyConfig`로 경로를 명시해야 한다. `config.isolated = 1`을 켜고 `module_search_paths`에 같이 배포한 폴더를 넣으면, 사용자 PC의 다른 파이썬 설치와 완전히 분리된다.

numpy 같은 외부 패키지는 embeddable package에 없어서 따로 넣어야 한다. 여기까지 오니 배포 크기가 꽤 커졌고, 결국 "이럴 거면 프로세스를 따로 띄우는 게 낫지 않나"를 다시 생각하게 됐다. 호출 빈도가 낮으면 그쪽이 맞다.

## 정리하면

- Debug 빌드에서 `python3x_d.lib`가 없으면 링크가 깨진다. 디버그 바이너리를 받거나 `_DEBUG`를 잠깐 끈다
- `Py_SetProgramName`은 3.12에서 제거됐다. `PyConfig` + `Py_InitializeFromConfig`로 간다
- `PyRun_SimpleString`은 에러를 표준 에러로만 찍는다. `PyErr_Fetch`로 직접 가져와야 프로그램에서 다룰 수 있다
- `Py_Finalize` 후 재초기화는 확장 모듈 때문에 깨진다. 한 번만 초기화하고 유지한다
- 참조 카운트 규칙이 함수마다 다르다. RAII로 감싸두면 실수가 줄어든다
- 다른 스레드에서 부르려면 `PyGILState_Ensure`/`Release`

## 참고

- [Embedding Python in Another Application](https://docs.python.org/3/extending/embedding.html)
- [Python Initialization Configuration (PyConfig)](https://docs.python.org/3/c-api/init_config.html)
