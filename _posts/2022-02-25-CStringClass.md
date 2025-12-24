---
title: (MFC) CString 클래스
description: About CString Class
date: 2022-02-25 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, CString]
---

# [MFC] CSting 클래스

- 최초 작성일: 2022년 2월 25일 (금)

## 목차



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

## CString 변환 함수

(1) atoi() : char형을 int(부호있는 2byte 정수) 로 변환
(2) atol() : char형을 long(4byte 정수) 로 변환
(3) atof() : char형을 double(4byte 실수) 로 변환
(4) itoa() : int형을 char 등으로 변환
