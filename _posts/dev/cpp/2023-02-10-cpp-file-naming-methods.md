---
title: "(C++) 동적 파일명 생성 및 파일 열기 구현"
description: "시리얼 번호로 결과 파일명을 만드는 데 CString::Format과 sprintf_s를 써봤다. 유니코드 빌드에서 std::string을 %s로 넘기면 깨지는 문제, sprintf_s가 넘칠 때 자르는 게 아니라 죽는 문제까지 정리했다."
date: 2023-02-10 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, file, stream, formatting, mfc, cstring, unicode]
---
## 시리얼 번호를 파일명에 넣어야 했다

검사 지그 프로그램이라 장비 한 대를 검사할 때마다 결과 파일이 하나씩 나온다. 어느 장비 결과인지 알아야 하니 시리얼 번호를 파일명에 넣기로 했다. MFC 프로젝트라 두 가지 방법이 있었다.

## MFC의 CString::Format

```cpp
CString fileName;
fileName.Format(_T("Result_%s.txt"), Serialno.c_str());
fout.open(fileName);
```

`CString::Format`은 `printf` 계열의 포맷 문자열을 그대로 쓴다. 버퍼 크기를 신경 쓸 필요가 없고, 필요한 만큼 내부에서 늘려준다.

## C 스타일

```c
char filename[255];
sprintf_s(filename, "Result_%s.txt", Serialno.c_str());
fout.open(filename);
```

`sprintf_s`는 고정 버퍼에 쓴다. 배열을 넘기면 크기를 템플릿 오버로드가 자동으로 추론해주기 때문에 크기 인자를 생략할 수 있다. 다만 이건 배열일 때만이다. 함수 인자로 받은 `char*`처럼 포인터로 넘어오면 크기를 직접 써야 한다.

```c
void make_name(char* buf, size_t n, const char* serial) {
    sprintf_s(buf, n, "Result_%s.txt", serial);   // 크기를 명시해야 한다
}
```

## 유니코드 빌드에서 위 코드는 깨진다

한참 뒤에 알게 된 건데, MFC 쪽 코드에 문제가 있다.

`_T("Result_%s.txt")`는 유니코드 빌드에서 `L"Result_%s.txt"`가 되고, 와이드 포맷 문자열의 `%s`는 **`wchar_t*`를 기대한다**. 그런데 `Serialno`가 `std::string`이면 `c_str()`은 `const char*`다. 타입이 안 맞는데 가변 인자라서 컴파일러가 경고를 안 준다.

결과는 그때그때 다르다. 운이 좋으면 첫 글자만 나오고, 운이 나쁘면 엉뚱한 메모리를 문자열로 읽다가 죽는다. MBCS 빌드에서 테스트하고 유니코드 빌드로 넘기는 순간 터지는 종류의 버그다.

MSVC에는 이럴 때 쓰라고 `%hs`가 있다. `h`가 narrow 문자열이라는 뜻이다.

```cpp
fileName.Format(_T("Result_%hs.txt"), Serialno.c_str());   // std::string 을 그대로
```

반대로 MBCS 빌드에서 `wchar_t*`를 넘겨야 하면 `%ls`다. 다만 이런 식으로 빌드 설정에 따라 갈리는 코드는 나중에 또 걸린다. 애초에 문자열 타입을 통일해두는 편이 낫다.

```cpp
CString serial(Serialno.c_str());          // 변환은 한 번만
fileName.Format(_T("Result_%s.txt"), (LPCTSTR)serial);
```

`CString`을 `%s`에 넘길 때 캐스팅 없이 그냥 넘겨도 대개 동작하는데, 이건 `CString`이 내부적으로 문자 포인터 하나만 들고 있어서 생기는 우연이다. 가변 인자에는 클래스를 넘기는 것 자체가 정의되지 않은 동작이라 `(LPCTSTR)`을 명시하는 게 맞다.

## sprintf_s는 넘치면 자르지 않는다

`sprintf_s`의 `_s`를 보고 "넘치면 알아서 잘라주겠지"라고 생각했는데 아니었다. 버퍼가 모자라면 잘못된 매개변수 처리기가 호출되고, 기본 설정에서는 프로그램이 그 자리에서 종료된다. Release 빌드에서도 마찬가지다.

시리얼 번호는 짧으니 255바이트를 넘길 일이 없다고 생각했는데, 장비에서 읽어온 값이 이상하게 들어오는 경우가 있었다. 통신이 꼬여서 쓰레기 문자열이 들어오면 그 길이를 보장할 수 없다.

자르고 싶으면 `_TRUNCATE`를 쓴다.

```c
char filename[255];
_snprintf_s(filename, _countof(filename), _TRUNCATE,
            "Result_%s.txt", serial);
```

`_TRUNCATE`를 주면 잘린 경우 `-1`을 반환하고 널 종료는 보장한다. 반환값을 확인해서 시리얼 번호가 이상하다는 로그를 남기게 해뒀다.

## 외부에서 받은 값을 파일명에 그대로 쓰면 안 된다

이것도 실제로 걸렸다. 윈도우 파일명에는 못 쓰는 문자가 있다.

```text
\ / : * ? " < > |
```

장비에서 읽은 시리얼에 이 중 하나라도 섞이면 `ofstream::open`이 조용히 실패한다. 예외도 안 던지고, `is_open()`이 false일 뿐이다. 결과를 안 남기고 지나가서 나중에 파일이 없는 걸 보고서야 알게 된다.

거르는 함수를 하나 두고 통과시킨다.

```cpp
std::string sanitize(std::string s)
{
    for (char& c : s) {
        if (c == '\\' || c == '/' || c == ':' || c == '*' ||
            c == '?'  || c == '"' || c == '<' || c == '>' ||
            c == '|'  || static_cast<unsigned char>(c) < 0x20)
            c = '_';
    }
    if (s.empty()) s = "unknown";
    return s;
}
```

제어 문자(0x20 미만)도 같이 막았다. 시리얼 앞뒤에 `\r`이 붙어 오는 경우가 실제로 있었고, 이건 눈에 안 보여서 원인 찾기가 훨씬 어렵다.

경로 끝에 점이나 공백이 오는 것도 윈도우에서는 문제가 된다. `CON`, `PRN`, `AUX`, `NUL`, `COM1`~`COM9`, `LPT1`~`LPT9` 같은 예약된 이름도 못 쓴다. 여기까지 다 막을 필요는 없었지만, 사용자 입력을 파일명으로 쓰는 프로그램이라면 확인해둘 만하다.

## 열고 나서 확인하기

`ofstream`은 열기에 실패해도 예외를 안 던진다. 그냥 실패 상태로 남는다.

```cpp
std::ofstream fout(filename);
if (!fout) {
    Log(_T("결과 파일 생성 실패: %s"), filename);
    return;
}
```

디렉토리가 없을 때도 똑같이 조용히 실패한다. `.\result\` 아래에 쓰는데 그 폴더가 없으면 아무 일도 안 일어난다. 쓰기 전에 디렉토리를 만들어두는 게 맞다.

```cpp
#include <filesystem>
namespace fs = std::filesystem;

fs::create_directories("./result");                 // 이미 있으면 아무 일 없음
std::ofstream fout(fs::path("./result") / filename);
```

`create_directories`는 중간 경로까지 다 만들고, 이미 있으면 그냥 false를 돌려준다. 리눅스에서 같은 걸 직접 짤 때의 얘기는 [리눅스 환경에서 디렉토리 생성을 보장하는 함수](/posts/cpp-directory-creation-function-linux/)에 정리해뒀다.

`fs::path`의 `/` 연산자를 쓰면 구분자를 손으로 붙이지 않아도 된다. `"./result" + "\\" + name` 같은 문자열 조합에서 슬래시를 하나 빠뜨리거나 두 개 넣는 실수가 의외로 자주 나온다.

## 두 방식 비교

| | CString::Format | sprintf_s |
| :--- | :--- | :--- |
| 버퍼 관리 | 자동 | 직접. 넘치면 종료 |
| 유니코드 | `_T`/`TCHAR` 매핑을 따라감 | 별도 처리 필요 |
| 이식성 | Windows + MFC/ATL 전용 | 어디서나 (`snprintf`) |
| 문자열 타입 | 섞어 쓰면 `%hs`/`%ls` 필요 | 같은 문제 있음 |

MFC 프로젝트 안에서 끝나는 코드면 `CString::Format`이 편하다. 나중에 리눅스로 옮길 가능성이 있는 로직이면 처음부터 `std::string`과 `snprintf`(또는 C++20의 `std::format`)로 가는 게 낫다.

C++20을 쓸 수 있으면 이 고민이 대부분 없어진다.

```cpp
#include <format>
std::string filename = std::format("Result_{}.txt", serial);
```

타입 검사가 컴파일 타임에 되기 때문에, 위에서 겪은 `%s`에 narrow 문자열을 넘기는 종류의 실수가 애초에 컴파일되지 않는다.

## 정리하면

- 유니코드 빌드에서 `_T("%s")`에 `std::string::c_str()`을 넘기면 안 된다. `%hs`를 쓰거나 문자열 타입을 통일한다
- `sprintf_s`는 넘치면 자르는 게 아니라 프로그램을 끝낸다. 자르려면 `_snprintf_s` + `_TRUNCATE`
- 외부에서 받은 값을 파일명에 쓸 때는 금지 문자와 제어 문자를 걸러야 한다
- `ofstream`은 열기 실패를 조용히 넘기므로 반드시 확인하고, 디렉토리는 미리 만들어둔다
