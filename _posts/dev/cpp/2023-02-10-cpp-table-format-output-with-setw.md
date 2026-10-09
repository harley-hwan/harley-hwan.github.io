---
title: "(C++) iomanip을 이용한 표 형식 출력 구현"
description: "검사 결과를 콘솔에 표로 찍으려고 setw를 썼는데, setw가 바이트를 센다는 것과 한글이 섞이면 코드페이지에 따라 정렬이 무너진다는 것을 나중에 알았다. 그 과정과 대안을 정리했다."
date: 2023-02-10 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, iomanip, formatting, output, console, setw, encoding]
---
## 표로 찍고 싶었던 이유

장비 검사 프로그램의 결과를 콘솔에 남기는데, 처음엔 그냥 한 줄씩 찍었다.

```text
카메라 Roll Pass(0.3) Threshold 2
진단 ErrCode Pass(0x00)
버전 SW Ver 1.0.0
```

항목 수가 늘어나니 눈으로 훑기가 어려워졌다. 특히 검사가 실패했을 때 어느 항목이 걸렸는지 빨리 찾아야 하는데, 열이 안 맞으니 한 줄씩 읽어야 한다. 열을 맞춰서 표처럼 만들기로 했다.

## 처음 짠 코드

`<iomanip>`의 `setw`와 `cout.setf(ios_base::left)` 조합이다.

```cpp
#include <iostream>
#include <iomanip>
#include <string>

using namespace std;

int main() {
    // 왼쪽 정렬 설정
    cout.setf(ios_base::left);

    // 검사 결과 및 버전 값 (예시)
    string resCameraPass = "Pass";
    string degreebuffer = "0.3";
    string resdiagPass = "Pass";
    string strErrCode = "0x00";
    string SWVer = "1.0.0";
    string FWVer = "2.1.3";
    string E6Ver = "1.0.5";

    // 결과 문자열 구성
    string resCamera = resCameraPass + "(" + degreebuffer + ")";    // 카메라 검증 결과
    string resdiag = resdiagPass + "(" + strErrCode + ")";         // 진단 결과

    // 테이블 헤더 출력
    cout << setw(3)  << " "   << setw(10) << "항목"    
         << setw(12) << "내용"    << setw(15) << "결과"    
         << setw(15) << "비고"    << endl;

    // 카메라 정보
    cout << setw(3)  << "1"   << setw(10) << "카메라"    
         << setw(12) << "Roll"    << setw(15) << resCamera 
         << setw(15) << "Threshold 2" << endl;

    // 진단 정보
    cout << setw(3)  << "2"   << setw(10) << "진단"    
         << setw(12) << "ErrCode" << setw(15) << resdiag  
         << setw(15) << " "       << endl;

    // 버전 정보
    cout << setw(3)  << "3"   << setw(10) << "버전"    
         << setw(12) << "SW Ver"  << setw(15) << SWVer   
         << setw(15) << " "       << endl;
    cout << setw(3)  << " "   << setw(10) << " "       
         << setw(12) << "FW Ver"  << setw(15) << FWVer   
         << setw(15) << " "       << endl;
    cout << setw(3)  << " "   << setw(10) << " "       
         << setw(12) << "E6 Ver"  << setw(15) << E6Ver   
         << setw(15) << " "       << endl;

    // 추가 정보
    cout << setw(3)  << "4"   << setw(10) << "위상캘"   
         << setw(12) << " "       << setw(15) << resdiag 
         << setw(15) << " "       << endl;
    cout << setw(3)  << "5"   << setw(10) << "IMU"     
         << setw(12) << " "       << setw(15) << resdiag 
         << setw(15) << " "       << endl;

    return 0;
}
```

![표 형식 출력 결과](/assets/img/posts/cpp-table-format-output-with-setw/001-218002463-c66dc783-8de1-4220-a3b3-5d4a7f14aa33.png)

값이 없는 자리에 공백 문자 하나(`" "`)를 넣은 이유는, 아무것도 안 넣으면 `setw`가 소비되지 않고 다음 출력으로 넘어가서 열이 밀리기 때문이다.

## setw는 한 번만 먹는다

이게 첫 번째로 막힌 지점이다. `setw`는 **바로 다음 출력 하나에만** 적용되고 곧바로 0으로 돌아간다. 그래서 매 항목마다 다시 써줘야 한다. 열마다 `setw`가 반복해서 붙는 이유가 이거다.

반면 `cout.setf(ios_base::left)`는 한 번 걸면 계속 유지된다. `setprecision`, `setfill`, `fixed`도 같은 부류다. `setw`만 일회성이라 예외라고 기억해두면 편하다.

`cout.setf` 대신 조작자를 쓰는 편이 요즘 문법에 가깝다.

```cpp
cout << std::left;   // cout.setf(ios_base::left) 와 같다
```

한 가지 더, `setf`로 바꾼 플래그는 스트림 전역에 남는다. 이 함수만 왼쪽 정렬을 쓰고 싶으면 원래대로 되돌려야 한다.

```cpp
const std::ios::fmtflags saved = cout.flags();
cout << std::left;
// ... 표 출력 ...
cout.flags(saved);
```

## 한글이 들어가면 어긋난다

여기가 진짜 문제였다. 위 코드는 내 환경에서는 잘 맞았는데, 콘솔 코드페이지를 UTF-8로 바꾸니까 열이 어긋났다.

이유는 `setw`가 **표시 폭이 아니라 문자(바이트) 개수**를 세기 때문이다. `const char*`를 넘기면 `strlen` 기준이다. 한글은 인코딩마다 바이트 수가 다르고, 콘솔에서 차지하는 폭은 또 별개다.

"항목"이라는 두 글자로 `setw(10)`을 걸면 이렇게 갈린다.

| 환경 | "항목"의 크기 | 채워지는 공백 | 화면상 총 폭 |
| :--- | ---: | ---: | ---: |
| CP949 (`char`) | 4바이트 | 6 | 4 + 6 = 10칸 |
| UTF-8 (`char`) | 6바이트 | 4 | 4 + 4 = 8칸 |
| 유니코드 (`wchar_t`) | 2문자 | 8 | 4 + 8 = 12칸 |

CP949에서 우연히 딱 맞는 이유가 있다. 이 코드페이지에서 한글 한 글자는 2바이트이고 콘솔에서 차지하는 폭도 2칸이다. 바이트 수와 표시 폭이 같으니 `setw`의 계산이 그대로 맞아떨어진다. 내가 짤 때 MBCS 빌드에 한국어 콘솔이라 문제가 안 보였던 것이고, 코드가 옳아서가 아니라 조건이 우연히 맞았던 것이다.

UTF-8로 바꾸면 한글 한 글자가 3바이트인데 폭은 여전히 2칸이라 글자마다 1칸씩 모자라게 된다. 한글이 세 글자인 "카메라"는 3칸이 밀린다.

와이드 스트림(`wcout`)은 반대 방향으로 어긋난다. `wchar_t` 하나를 1로 세는데 화면에서는 2칸을 먹으니, 글자마다 1칸씩 남는다.

## 표시 폭으로 채우기

제대로 하려면 표시 폭을 직접 계산해서 패딩해야 한다. 한중일 문자를 2칸으로 세는 함수를 하나 두면 된다.

```cpp
#include <string>

// wchar_t 문자열의 콘솔 표시 폭 (CJK 는 2칸)
size_t display_width(const std::wstring& s)
{
    size_t w = 0;
    for (wchar_t c : s) {
        if ((c >= 0x1100 && c <= 0x115F) ||   // 한글 자모
            (c >= 0x2E80 && c <= 0xA4CF) ||   // CJK 부수 ~ 이(Yi)
            (c >= 0xAC00 && c <= 0xD7A3) ||   // 한글 음절
            (c >= 0xF900 && c <= 0xFAFF) ||   // CJK 호환 한자
            (c >= 0xFF00 && c <= 0xFF60))     // 전각 기호
            w += 2;
        else
            w += 1;
    }
    return w;
}

std::wstring pad_right(const std::wstring& s, size_t width)
{
    const size_t w = display_width(s);
    return (w >= width) ? s : s + std::wstring(width - w, L' ');
}
```

`setw` 대신 이걸 쓴다.

```cpp
std::wcout << pad_right(L"항목", 10)
           << pad_right(L"내용", 12)
           << pad_right(L"결과", 15) << L'\n';
```

범위 판정이 완벽하진 않다(이모지나 결합 문자는 별도 처리가 필요하다). 다만 검사 결과 표에 들어가는 건 한글, 영문, 숫자, 괄호 정도라 이 정도면 충분했다.

> **콘솔 코드페이지를 UTF-8로 바꾼다면** `chcp 65001` 만으로는 부족하고 소스 파일 인코딩과 실행 문자 집합도 맞춰야 한다. Visual Studio 2019 이후는 `/utf-8` 옵션 하나로 소스와 실행 문자 집합을 UTF-8로 고정할 수 있다. 셋 중 하나만 어긋나도 한글이 깨진다.
{: .prompt-warning }

## 값이 열 폭을 넘으면 표가 무너진다

`setw`는 **최소 폭**이지 최대 폭이 아니다. 지정한 폭보다 긴 문자열은 잘리지 않고 그대로 나오고, 그 줄만 이후 열이 전부 밀린다.

검사 항목의 비고란에 실패 사유를 넣기 시작하면서 이걸 겪었다. 대부분 짧은데 한 줄만 길어져서 그 줄만 표가 깨진다. 넘치면 자르는 처리를 넣어야 한다.

```cpp
std::string fit(std::string s, size_t width)
{
    if (s.size() > width) {
        s.resize(width);
        if (width >= 3) s.replace(width - 3, 3, "...");
    }
    return s;
}

cout << setw(15) << fit(remark, 14) << ...;
```

폭보다 1 작게 잘라서 열 사이에 최소 한 칸은 남기는 편이 읽기 좋았다.

## 구분선과 숫자 정렬

표처럼 보이게 하려면 구분선이 하나 있는 게 확실히 낫다.

```cpp
const std::string line(55, '-');
cout << line << '\n';
```

숫자 열은 왼쪽 정렬보다 오른쪽 정렬이 읽기 좋다. 자릿수가 맞아서 크기 비교가 눈에 바로 들어온다. 소수점 자리도 고정한다.

```cpp
cout << std::right << std::fixed << std::setprecision(2)
     << setw(10) << 3.14159      // "      3.14"
     << setw(10) << 12.5;        // "     12.50"
```

`setfill`로 채움 문자를 바꾸면 목차처럼 만들 수 있는데, 이것도 sticky라 되돌려야 한다.

```cpp
cout << std::setfill('.') << setw(20) << "카메라" << "Pass\n";
cout << std::setfill(' ');   // 되돌리지 않으면 이후 모든 출력에 점이 찍힌다
```

## C++20이면 std::format

`std::format`은 `setw`의 두 가지 불편을 한 번에 없앤다. 폭을 포맷 문자열 안에 쓰니 코드가 짧고, 정렬 지정자가 각 필드에 따로 붙어서 상태가 남지 않는다.

```cpp
#include <format>
#include <iostream>

std::cout << std::format("{:<3}{:<10}{:<12}{:<15}{:<15}\n",
                         "1", "카메라", "Roll", "Pass(0.3)", "Threshold 2");
std::cout << std::format("{:>10.2f}\n", 3.14159);   // "      3.14"
```

다만 폭 계산은 여전히 문자 단위라서, `std::format`을 써도 한글 표시 폭 문제는 그대로 남는다. 위의 `display_width` 계산은 어느 쪽을 쓰든 필요하다.

## 정리하면

- `setw`는 다음 출력 하나에만 적용되고, `left`/`fixed`/`setfill`은 계속 유지된다
- `setw`가 세는 건 표시 폭이 아니라 문자 개수다. CP949에서 한글이 맞아떨어지는 건 바이트 수와 표시 폭이 둘 다 2라서 생긴 우연이다
- UTF-8이나 와이드 스트림으로 옮기면 그 우연이 깨진다. 표시 폭을 직접 계산해야 한다
- `setw`는 최소 폭이라 넘치는 값은 잘리지 않고 표를 무너뜨린다. 자르는 처리를 같이 넣어야 한다
