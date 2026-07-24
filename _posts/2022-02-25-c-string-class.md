---
title: (MFC) CString 클래스
description: About CString Class
date: 2022-02-25 10:00:00 +0900
slug: 'CStringClass'
categories: [Dev, MFC]
tags: [cpp, mfc, cstring]
---
## 설명

CString 클래스는 문자열을 관리하는 클래스이다.

<br/>

## CString 멤버 함수

|멤버 함수|설명|
|---|---|
|GetLength| CString 객체 안에 있는 수를 반환|
|IsEmpty|객체가 비어있는지 결정|
|Empty|객체를 비우고 메모리를 비움|
|GetAt|문자열의 특정 위치의 문자값을 반환|
|SetAt|문자열의 특정 위치에 새로운 문자 삽입|
|Compare|다른 문자열과 비교|
|Mid|지정한 중간 부분부터 문자열 추출|
|Right|오른쪽을 기준으로 문자열 추출|
|Left|왼쪽을 기준으로 문자열 추출|
|MakeUpper|문자열을 모두 대문자로 변환|
|MakeLower|문자열을 모두 소문자로 변환|
|MakeReverse|앞과 뒤를 역순으로 변환|
|TrimLeft|문자열의 왼쪽에서 공백이나 탭 또는 지정한 문자열을 제거|
|TrimRight|문자열의 오른쪽에서 공백이나 탭 또는 지정한 문자열을 제거|
|Format|지정된 format 형식에 따라 문자열을 지정해 주는 함수|
|Find|부분 문자열의 match되는 문자열을 찾음|

<br/>

## 문자열 변환 함수

아래 함수들은 CString의 멤버가 아니라 C 런타임(CRT)이 제공하는 변환 함수다. CString과 함께 문자열-숫자 변환에 자주 쓰인다.

- atoi() : char형 문자열을 int(4byte 정수)로 변환
- atol() : char형 문자열을 long(4byte 정수)로 변환
- atof() : char형 문자열을 double(8byte 실수)로 변환
- itoa() : int형을 char 문자열로 변환
