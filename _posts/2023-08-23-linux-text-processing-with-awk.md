---
title: "리눅스 텍스트 처리: AWK를 활용한 명령어 출력 파싱"
description: ""명령어 출력에서 특정 필드를 추출하는 스크립트 작성 가이드""
date: 2023-08-23 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, gawk, awk, bash, shell, text-processing, command-line]
---

# 리눅스 텍스트 처리: AWK를 활용한 명령어 출력 파싱
- 최초 작성일: 2023년 8월 23일(수)

<br/>

## 목차
1. [명령어 구조 분석](#명령어-구조-분석)
2. [각 구성 요소 설명](#각-구성-요소-설명)
3. [실제 사용 예제](#실제-사용-예제)
4. [고급 활용 방법](#고급-활용-방법)

<br/>

## 명령어 구조 분석

### 기본 명령어

```bash
sudo /usr/local/bin/app-version -v | gawk 'NR == 1 {print $2}'
```

이 명령어는 다음과 같은 구성 요소로 이루어진다:
1. 권한 상승 (sudo)
2. 프로그램 실행 (/usr/local/bin/app-version -v)
3. 출력 파싱 (gawk를 통한 텍스트 처리)

<br/>

## 각 구성 요소 설명

### 1. sudo 명령어
- 용도: 관리자 권한으로 명령어 실행
- 특징: 보안 정책에 따른 권한 상승
- 동작 방식: 사용자 인증 후 권한 상승

### 2. 프로그램 경로와 옵션

```bash
/usr/local/bin/app-version -v
```
- 경로: 시스템 전역 실행 파일이 위치한 표준 디렉토리
- 옵션: -v (버전 정보 출력)
- 예상 출력: "Version: 1.2.3"

### 3. 파이프와 AWK 처리

```bash
| gawk 'NR == 1 {print $2}'
```
구성 요소 분석:
- `|`: 파이프 연산자
- `gawk`: GNU AWK 텍스트 처리 도구
- `NR == 1`: 첫 번째 라인 선택
- `print $2`: 두 번째 필드 출력

<br/>

## 실제 사용 예제

### 1. 기본 사용법

```bash
# 버전 정보 추출
sudo /usr/local/bin/app-version -v | gawk 'NR == 1 {print $2}'

# 결과 예시
1.2.3
```

### 2. 변수에 저장

```bash
VERSION=$(sudo /usr/local/bin/app-version -v | gawk 'NR == 1 {print $2}')
echo "현재 버전: $VERSION"
```

<br/>

## 고급 활용 방법

### 1. 조건부 필드 추출

```bash
# 특정 조건에 맞는 필드만 추출
gawk '$1 == "Version:" {print $2}'
```

### 2. 다중 필드 처리

```bash
# 여러 필드 동시 처리
gawk '{print $2, $3}'
```

### 3. 에러 처리 추가

```bash
#!/bin/bash
if ! version=$(sudo /usr/local/bin/app-version -v | gawk 'NR == 1 {print $2}'); then
    echo "버전 정보 추출 실패"
    exit 1
fi
echo "추출된 버전: $version"
```

<br/>

## 결론
AWK를 활용한 텍스트 처리는 리눅스 시스템에서 명령어 출력을 파싱하고 필요한 정보를 추출하는데 매우 효과적인 방법이다. 특히 버전 정보, 로그 파일, 시스템 상태 정보 등을 처리할 때 유용하게 활용할 수 있다.
