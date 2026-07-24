---
title: "(C/C++) 동적 파일명 생성 및 파일 열기 구현"
description: "MFC와 C 스타일의 파일명 포맷팅 방법"
date: 2023-02-10 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, file, stream, formatting, mfc]
---
<br/>

## 소개
파일을 열 때 시리얼 번호나 날짜 등의 동적 데이터를 포함한 파일명을 생성하는 방법을 구현한다. MFC의 CString과 C 스타일의 sprintf를 사용하는 두 가지 방식을 소개한다.

<br/>

## MFC 구현
CString 클래스의 Format 함수를 사용한 구현이다.

```cpp
// MFC 방식의 파일명 생성
CString fileName;
fileName.Format(_T("Result_%s.txt"), Serialno.c_str());
fout.open(fileName);
```

CString 클래스는 유니코드를 자동으로 지원하고, Format 함수는 printf 스타일의 포맷 문자열을 그대로 쓸 수 있다. _T 매크로를 쓰면 유니코드/멀티바이트 빌드 양쪽에서 호환된다.

<br/>

## C 스타일 구현
sprintf_s 함수를 사용한 구현이다.

```c
// C 스타일의 파일명 생성
char filename[255];
sprintf_s(filename, "Result_%s.txt", Serialno.c_str());
fout.open(filename);
```

고정 크기 버퍼를 사용하므로 문자열 길이를 고려해 버퍼 크기를 잡아야 하고, 버퍼 오버플로우 방지를 위해 sprintf 대신 sprintf_s를 사용한다. 포맷 지정자는 printf 계열 함수와 동일하다.

<br/>

## 구현 비교

- 안전성: C 스타일은 sprintf_s로 버퍼 오버플로우를 방지하고, MFC는 CString의 자동 메모리 관리에 맡긴다
- 유니코드 지원: C 스타일은 별도 처리가 필요하지만 MFC는 _T 매크로로 자동 처리된다
- 사용 환경: C 스타일은 어디서나 쓸 수 있고, MFC는 Windows/MFC 환경에서만 쓸 수 있다
- 확장성: C 스타일은 버퍼 크기 제한을 고려해야 하고, MFC는 문자열 길이에 따라 자동으로 크기가 조절된다

이러한 파일명 생성 방식은 로그 파일 작성, 결과 파일 저장 등 다양한 상황에서 활용할 수 있다.
