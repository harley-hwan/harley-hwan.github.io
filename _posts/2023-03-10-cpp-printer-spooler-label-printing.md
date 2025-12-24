---
title: "(C++) Windows 프린터 스풀러를 이용한 라벨 프린터 제어"
description: "TSC P200 라벨 프린터 인쇄 명령 구현"
date: 2023-03-10 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, printer, windows, spooler, labelprinter, tsc, zpl]
---

# Windows 프린터 스풀러를 이용한 라벨 프린터 제어
- 최초 작성일: 2023년 3월 10일 (금)
- 참고: [ZPL Programming Guide](https://www.zebra.com/content/dam/zebra_new_ia/en-us/manuals/printers/common/programming/zpl-zbi2-pm-en.pdf)

<br/>

## 소개
Windows 프린터 스풀러를 사용하여 TSC P200 라벨 프린터를 제어하는 방법을 구현한다. 프린터와의 통신은 RAW 모드를 사용하며, TSPL과 ZPL 두 가지 명령어 체계를 모두 지원한다.

<br/>

## 기본 구현 - TSPL
기본적인 TSPL(TSC Printer Language) 명령어를 사용하는 구현이다.

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

#### 구현 세부사항:
1. **프린터 연결**
   - OpenPrinterW 함수로 프린터와 연결한다
   - 프린터 이름은 시스템에 설치된 이름과 일치해야 한다

2. **작업 설정**
   - DOC_INFO_1A 구조체로 인쇄 작업 정보를 설정한다
   - RAW 모드를 사용하여 직접 명령어를 전송한다

3. **명령어 전송**
   - WritePrinter 함수로 TSPL 명령어를 전송한다
   - 각 단계별로 에러 처리를 수행한다

<br/>

## 확장 구현 - ZPL
Zebra 프린터 호환을 위한 ZPL(Zebra Programming Language) 명령어 구현이다.

```cpp
    // ZPL 명령어 설정
    std::string command = "^XA\n"
        "^MMT\n"
        "^PW203\n"
        "^LL203\n"
        "^LS0\n"
        "^FO10,10^A0N,28,28^FDHello,World!^FS\n"
        "^PQ1,0,1,Y^XZ\n";
```

#### ZPL 명령어 설명:
1. **기본 명령어**
   - ^XA: 라벨 형식 시작
   - ^XZ: 라벨 형식 종료
   - ^MMT: 미리미터 단위 사용

2. **레이아웃 설정**
   - ^PW203: 프린트 폭 설정 (203 DPI)
   - ^LL203: 라벨 길이 설정
   - ^LS0: 프린트 시프트 없음

3. **텍스트 출력**
   - ^FO10,10: 필드 원점 설정 (x,y 좌표)
   - ^A0N,28,28: 폰트 설정 (폰트 A, 크기 28pt)
   - ^FD: 필드 데이터 시작
   - ^FS: 필드 데이터 종료

4. **인쇄 설정**
   - ^PQ1,0,1,Y: 인쇄 매수, 일시 중지, 복제 수, 역순 인쇄

<br/>

## 주요 함수 설명

1. **OpenPrinterW**
   - Windows 프린터 연결을 시작한다
   - 프린터 핸들을 반환한다

2. **StartDocPrinterA**
   - 새 인쇄 작업을 시작한다
   - 작업 ID를 반환한다

3. **StartPagePrinter**
   - 새 페이지 인쇄를 시작한다
   - 성공 여부를 반환한다

4. **WritePrinter**
   - 프린터에 RAW 데이터를 전송한다
   - 전송된 바이트 수를 반환한다

5. **EndPagePrinter/EndDocPrinter**
   - 페이지/문서 인쇄를 종료한다
   - 리소스를 정리한다

이 구현은 라벨 프린터와의 직접 통신을 통해 텍스트 출력, 바코드 생성 등 다양한 라벨링 작업을 수행할 수 있다. TSPL과 ZPL 두 가지 명령어 체계를 지원하여 다양한 프린터 모델에 대응할 수 있다.
