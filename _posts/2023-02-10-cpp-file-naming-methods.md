---
title: "(C/C++) 동적 파일명 생성 및 파일 열기 구현"
description: "MFC와 C 스타일의 파일명 포맷팅 방법"
date: 2023-02-10 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, file, stream, formatting, mfc]
---

# 
- 최초 작성일: 2023년 2월 10일 (금)

<br/>

## 
파일을 열 때 시리얼 번호나 날짜 등의 동적 데이터를 포함한 파일명을 생성하는 방법을 구현한다. MFC의 CString과 C 스타일의 sprintf를 사용하는 두 가지 방식을 소개한다.

<br/>

## MFC 
CString 클래스의 Format 함수를 사용한 구현이다.

```cpp
// MFC 방식의 파일명 생성
CString fileName;
fileName.Format(_T("Result_%s.txt"), Serialno.c_str());
fout.open(fileName_res);
```

#### :
1. **CString 사용**
   - MFC의 CString 클래스를 활용한다
   - 유니코드를 자동으로 지원한다

2. **Format 함수**
   - printf 스타일의 포맷 문자열을 사용한다
   - _T 매크로로 유니코드/멀티바이트 호환성을 확보한다

<br/>

## C 
sprintf_s 함수를 사용한 구현이다.

```c
// C 스타일의 파일명 생성
char filename[255];
sprintf_s(filename, "Result_%s.txt", Serialno);
fout.open(filename);
```

#### :
1. **버퍼 관리**
   - 고정 크기 버퍼를 사용한다
   - 버퍼 오버플로우 방지를 위해 sprintf_s를 사용한다

2. **문자열 포맷팅**
   - printf 계열 함수의 포맷 지정자를 사용한다
   - 문자열 길이를 고려한 버퍼 크기 설정이 필요하다

<br/>

## 

1. **안전성**
   - C 스타일: sprintf_s로 버퍼 오버플로우 방지
   - MFC: 자동 메모리 관리로 안전성 확보

2. **유니코드 지원**
   - C 스타일: 별도의 유니코드 처리 필요
   - MFC: _T 매크로로 자동 처리

3. **사용 환경**
   - C 스타일: 모든 환경에서 사용 가능
   - MFC: Windows/MFC 환경에서만 사용 가능

4. **확장성**
   - C 스타일: 버퍼 크기 제한 고려 필요
   - MFC: 동적 크기 조절 자동 지원

이러한 파일명 생성 방식은 로그 파일 작성, 결과 파일 저장 등 다양한 상황에서 활용할 수 있다. 각 방식의 장단점을 고려하여 적절한 구현을 선택하면 된다.
