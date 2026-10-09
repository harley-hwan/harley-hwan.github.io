---
title: "(C++) Windows 프린터 스풀러를 이용한 라벨 프린터 제어"
description: "검사 끝난 장비에 라벨을 붙이려고 TSC P200을 RAW 모드로 직접 제어했다. 드라이버를 우회하는 이유, 줄바꿈과 라벨 규격 때문에 인쇄가 밀리는 문제, WritePrinter가 성공해도 인쇄가 안 되는 경우를 정리했다."
date: 2023-03-10 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, printer, windows, spooler, labelprinter, tsc, zpl, tspl, raw]
---
## 왜 드라이버를 안 쓰고 직접 보내나

검사를 통과한 장비에 시리얼 번호와 검사 날짜가 찍힌 라벨을 붙여야 했다. 프린터는 TSC P200이다.

처음엔 평범하게 프린터 드라이버로 그려서 보내려고 했다. `CreateDC`로 프린터 DC를 얻고 `TextOut`으로 찍는 방식이다. 그런데 라벨 프린터는 일반 프린터와 성격이 다르다. 203 dpi에 30×10 mm짜리 좁은 영역이고, 바코드를 찍으려면 정확한 도트 위치가 필요하다. GDI로 그리면 프린터 쪽에서 다시 래스터로 바꾸는 과정에서 바코드가 미세하게 뭉개져서 스캐너가 못 읽는 경우가 생긴다.

라벨 프린터는 자기만의 명령어를 가지고 있다. TSC 계열은 TSPL, Zebra 계열은 ZPL이다. 이 명령을 프린터가 그대로 받게 하려면 스풀러에 **RAW** 데이터로 밀어 넣으면 된다. 드라이버가 손대지 않고 통과시킨다.

## TSPL 버전

```cpp
#include <iostream>
#include <string>
#include <Windows.h>

int main() {
    // 프린터 이름 설정
    std::wstring printerName = L"TSC P200";

    // 인쇄 명령어 설정 (TSPL)
    std::string command = "SIZE 30 mm, 10 mm\n"
        "GAP 3 mm, 0\n"
        "DIRECTION 1\n"
        "CLS\n"
        "TEXT 10, 10, \"3\", 0, 1, 1, \"Hello, World!\"\n"
        "PRINT 1\n";

    // 프린터 핸들 초기화
    HANDLE hPrinter;
    if (!OpenPrinterW(const_cast<LPWSTR>(printerName.c_str()), &hPrinter, nullptr)) {
        std::cerr << "Error opening printer: " << GetLastError() << std::endl;
        return 1;
    }

    // 인쇄 작업 정보 설정
    DOC_INFO_1A docInfo;
    docInfo.pDocName = const_cast<char*>("TSC P200 Printing");
    docInfo.pOutputFile = nullptr;
    docInfo.pDatatype = const_cast<char*>("RAW");

    DWORD jobId = StartDocPrinterA(hPrinter, 1, reinterpret_cast<LPBYTE>(&docInfo));
    if (jobId == 0) {
        std::cerr << "Error starting print job: " << GetLastError() << std::endl;
        ClosePrinter(hPrinter);
        return 1;
    }

    if (!StartPagePrinter(hPrinter)) {
        std::cerr << "Error starting page: " << GetLastError() << std::endl;
        EndDocPrinter(hPrinter);
        ClosePrinter(hPrinter);
        return 1;
    }

    DWORD bytesWritten;
    if (!WritePrinter(hPrinter, const_cast<char*>(command.data()), command.size(), &bytesWritten)) {
        std::cerr << "Error writing to printer: " << GetLastError() << std::endl;
        EndPagePrinter(hPrinter);
        EndDocPrinter(hPrinter);
        ClosePrinter(hPrinter);
        return 1;
    }

    if (!EndPagePrinter(hPrinter)) {
        std::cerr << "Error ending page: " << GetLastError() << std::endl;
        EndDocPrinter(hPrinter);
        ClosePrinter(hPrinter);
        return 1;
    }

    if (!EndDocPrinter(hPrinter)) {
        std::cerr << "Error ending print job: " << GetLastError() << std::endl;
        ClosePrinter(hPrinter);
        return 1;
    }

    ClosePrinter(hPrinter);
    return 0;
}
```

순서는 `OpenPrinter` → `StartDocPrinter` → `StartPagePrinter` → `WritePrinter` → `EndPagePrinter` → `EndDocPrinter` → `ClosePrinter`로 고정이다. `pDatatype`에 `"RAW"`를 주는 게 핵심이고, 이걸 빼면 드라이버가 데이터를 해석하려 들어서 이상한 게 인쇄된다.

에러 처리가 계단처럼 쌓여 있는 게 눈에 거슬린다. 단계마다 앞에서 잡은 걸 순서대로 풀어야 해서 이렇게 됐다. RAII로 감싸면 훨씬 짧아진다.

```cpp
struct PrinterHandle {
    HANDLE h = nullptr;
    ~PrinterHandle() { if (h) ClosePrinter(h); }
};
struct DocScope {
    HANDLE h;
    bool ok = false;
    ~DocScope() { if (ok) EndDocPrinter(h); }
};
```

## 줄바꿈 때문에 인쇄가 안 됐다

처음에 아무리 보내도 라벨이 안 나왔다. `WritePrinter`는 성공하고 스풀러 큐에도 작업이 보이는데 프린터는 조용하다.

원인은 줄바꿈이었다. TSPL 명령은 각 줄이 **CR+LF**로 끝나야 한다. C++ 문자열에 `"\n"`만 쓰면 LF 하나만 나간다. 프린터가 명령의 끝을 인식하지 못하고 계속 기다린다.

```cpp
std::string command =
    "SIZE 30 mm, 10 mm\r\n"
    "GAP 3 mm, 0\r\n"
    "DIRECTION 1\r\n"
    "CLS\r\n"
    "TEXT 10,10,\"3\",0,1,1,\"Hello, World!\"\r\n"
    "PRINT 1\r\n";
```

RAW 모드라서 스풀러가 개행을 변환해주지 않는다는 게 포인트다. 일반 텍스트 인쇄였다면 드라이버가 알아서 처리했을 것이다. 원하는 대로 통과시켜 달라고 RAW를 골랐으니 개행도 내가 챙겨야 한다.

LF만 받아들이는 모델도 있어서 이걸로 몇 시간을 썼다. 라벨 프린터를 처음 붙일 때는 이것부터 확인하는 게 빠르다.

## SIZE와 GAP은 실물을 재서 넣는다

`SIZE`는 라벨 한 장의 크기, `GAP`은 라벨 사이의 간격이다. 이 값이 실제 라벨과 다르면 인쇄 내용이 두 장에 걸쳐 나오거나, 프린터가 라벨을 몇 장씩 헛돌린다.

`GAP 3 mm, 0`의 두 번째 값은 오프셋이다. 갭 센서가 감지한 위치에서 얼마나 더 보낼지를 지정한다. 인쇄가 일정하게 위나 아래로 밀리면 이 값으로 맞춘다.

값을 모르겠으면 프린터에 자동 보정 명령이 있다.

```text
GAPDETECT\r\n
```

한 번 돌리면 프린터가 라벨 몇 장을 넘기면서 크기와 갭을 스스로 측정한다. 그 뒤 자가 진단 출력을 뽑으면 측정값이 찍혀 나온다. 처음 라벨 규격이 바뀌었을 때 이걸 몰라서 자로 재고 있었다.

## ZPL 버전

Zebra 프린터로 바꿔야 할 가능성이 있어서 ZPL도 만들어뒀다. 명령 문자열만 바꾸면 나머지 코드는 그대로다.

```cpp
    // ZPL 명령어 설정
    std::string command = "^XA\r\n"
        "^MMT\r\n"
        "^PW203\r\n"
        "^LL203\r\n"
        "^LS0\r\n"
        "^FO10,10^A0N,28,28^FDHello,World!^FS\r\n"
        "^PQ1,0,1,Y^XZ\r\n";
```

| 명령 | 뜻 |
| :--- | :--- |
| `^XA` / `^XZ` | 라벨 형식의 시작과 끝 |
| `^MMT` | 인쇄 모드 Tear-off |
| `^PW203` | 인쇄 폭 203도트 (203 dpi에서 1인치) |
| `^LL203` | 라벨 길이 203도트 |
| `^LS0` | 라벨 좌우 시프트 없음 |
| `^FO10,10` | 필드 원점 (x, y) |
| `^A0N,28,28` | 폰트와 크기 |
| `^FD` ~ `^FS` | 필드 데이터 시작과 끝 |
| `^PQ1,0,1,Y` | 매수, 일시정지, 복제 수, 역순 |

TSC 프린터도 에뮬레이션 모드를 켜면 ZPL을 받는다. 반대로 모드가 안 맞으면 명령이 문자 그대로 인쇄되는 식으로 티가 난다. 라벨에 `^XA`가 글자로 찍혀 나오면 언어 모드부터 확인하면 된다.

좌표 단위가 다르다는 것도 짚어둘 만하다. TSPL은 `SIZE`에서 mm를 쓰지만 `TEXT`의 좌표는 도트다. ZPL은 전부 도트다. 203 dpi면 1 mm가 약 8도트다.

## 한글은 그냥 안 나온다

시리얼과 날짜만 찍을 때는 몰랐는데, 모델명에 한글을 넣으려니 안 나왔다. 라벨 프린터의 내장 폰트는 대개 아스키만 들어 있다.

방법이 두 가지 있었다.

프린터에 폰트를 다운로드하는 방법이 있다. TSPL의 `DOWNLOAD` 명령으로 폰트 파일을 프린터 메모리에 올린다. 한 번 올려두면 계속 쓸 수 있는데, 프린터를 교체하면 다시 해야 하고 모델마다 방식이 다르다.

다른 방법은 PC에서 이미지로 그려서 비트맵으로 보내는 것이다. TSPL은 `BITMAP`, ZPL은 `^GF`가 있다. 폰트를 자유롭게 쓸 수 있는 대신 데이터가 커지고 좌표 계산을 직접 해야 한다.

결국 라벨에는 영문과 숫자만 넣기로 정리했다. 라벨은 작아서 한글을 넣어봐야 읽기도 어렵고, 스캐너로 읽을 바코드가 본체라 텍스트는 보조 정보였다.

바코드는 명령 하나로 끝난다.

```text
BARCODE 10,30,"128",50,1,0,2,2,"SERIAL0001"\r\n
```

`"128"`이 Code 128이고, `50`이 높이(도트), 마지막이 데이터다. 좁은 라벨에는 Code 128이 데이터 밀도가 높아서 잘 맞았다.

## WritePrinter가 성공해도 인쇄가 안 될 수 있다

이게 제일 늦게 알게 된 부분이다.

`WritePrinter`가 참을 돌려주는 건 "스풀러가 데이터를 받았다"는 뜻이다. 프린터가 실제로 찍었다는 뜻이 아니다. 프린터 전원이 꺼져 있어도, 용지가 없어도, USB가 빠져 있어도 이 함수는 성공한다. 데이터는 큐에 쌓인다.

검사 프로그램에서 "라벨 출력 완료"라고 띄웠는데 라벨이 안 나오는 상황이 여기서 나왔다. 작업자는 완료 메시지를 보고 다음 장비로 넘어간다.

작업 상태를 확인하려면 `GetJob`을 쓴다. `StartDocPrinter`가 돌려준 `jobId`가 여기서 쓰인다.

```cpp
BYTE buf[4096];
DWORD needed = 0;
if (GetJob(hPrinter, jobId, 1, buf, sizeof(buf), &needed)) {
    auto* ji = reinterpret_cast<JOB_INFO_1*>(buf);
    if (ji->Status & (JOB_STATUS_ERROR | JOB_STATUS_OFFLINE |
                      JOB_STATUS_PAPEROUT | JOB_STATUS_BLOCKED_DEVQ)) {
        // 문제가 있다
    }
}
```

작업이 큐에서 사라지면 `GetJob`이 `ERROR_INVALID_PARAMETER`로 실패하는데, 이건 정상 완료와 구분이 안 된다. 그래서 완벽하게 확인하기는 어렵고, 대신 프린터 자체 상태를 먼저 보는 편이 실용적이었다.

```cpp
DWORD needed = 0;
GetPrinter(hPrinter, 2, nullptr, 0, &needed);
std::vector<BYTE> buf(needed);
if (GetPrinter(hPrinter, 2, buf.data(), needed, &needed)) {
    auto* pi = reinterpret_cast<PRINTER_INFO_2*>(buf.data());
    if (pi->Status & (PRINTER_STATUS_OFFLINE | PRINTER_STATUS_PAPER_OUT |
                      PRINTER_STATUS_ERROR | PRINTER_STATUS_NOT_AVAILABLE)) {
        // 인쇄를 시도하기 전에 알려준다
    }
}
```

인쇄를 보내기 전에 이걸 확인하고, 문제가 있으면 사용자에게 먼저 알리도록 바꿨다.

## 프린터 이름을 박아두면 안 된다

`L"TSC P200"`은 시스템에 등록된 이름과 **정확히** 일치해야 한다. 같은 프린터를 두 번 설치하면 `TSC P200 (사본 1)`이 되고, 사용자가 이름을 바꾸면 그대로 실패한다.

설치된 목록을 얻어서 고르게 하는 게 맞다.

```cpp
DWORD needed = 0, count = 0;
EnumPrinters(PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS, nullptr, 2,
             nullptr, 0, &needed, &count);
std::vector<BYTE> buf(needed);
if (EnumPrinters(PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS, nullptr, 2,
                 buf.data(), needed, &needed, &count)) {
    auto* p = reinterpret_cast<PRINTER_INFO_2*>(buf.data());
    for (DWORD i = 0; i < count; ++i) {
        // p[i].pPrinterName
    }
}
```

`EnumPrinters`도 크기를 먼저 물어보고 다시 부르는 두 단계 패턴이다. 윈도우 API에 이 패턴이 계속 나온다.

기본 프린터는 `GetDefaultPrinter`로 얻는다. 검사 PC에 라벨 프린터 하나만 물려 있으면 이걸 그대로 써도 되는데, 문서 프린터가 같이 있으면 라벨이 A4로 나온다. 목록에서 골라 설정에 저장하는 방식으로 갔다.

## 정리하면

- 라벨 프린터는 GDI로 그리는 것보다 TSPL/ZPL을 RAW로 보내는 쪽이 정확하다
- RAW 모드는 개행 변환을 안 해준다. TSPL 명령은 `\r\n`으로 끝내야 한다
- `SIZE`/`GAP`이 실물과 다르면 인쇄가 밀리거나 라벨을 헛돌린다. `GAPDETECT`로 자동 보정된다
- 내장 폰트로는 한글이 안 나온다. 폰트를 프린터에 올리거나 비트맵으로 보내야 한다
- `WritePrinter` 성공은 스풀러가 받았다는 뜻이다. 프린터가 꺼져 있어도 성공한다
- 프린터 이름을 소스에 박지 말고 `EnumPrinters`로 고르게 한다

## 참고

- [WritePrinter](https://learn.microsoft.com/en-us/windows/win32/printdocs/writeprinter)
- ZPL Programming Guide — [Zebra 지원 페이지](https://www.zebra.com/us/en/support-downloads.html)에서 받을 수 있다
- TSPL/TSPL2 Programming Manual — TSC 지원 페이지
