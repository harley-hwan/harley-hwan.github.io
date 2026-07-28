---
title: "리눅스 텍스트 처리: AWK를 활용한 명령어 출력 파싱"
description: "명령어 출력에서 특정 필드를 추출하는 스크립트 작성 가이드"
date: 2023-08-23 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, gawk, awk, bash, shell, text-processing, command-line]
---
<br/>

## 명령어 구조 분석

### 기본 명령어

```bash
sudo /usr/local/bin/app-version -v | gawk 'NR == 1 {print $2}'
```

이 명령어는 sudo로 권한을 올려 프로그램을 실행하고, 그 출력을 gawk로 파싱해 원하는 필드만 뽑아내는 구조다.

<br/>

## 각 구성 요소 설명

### sudo
대상 프로그램이 root 권한을 요구하기 때문에 `sudo`를 붙여 관리자 권한으로 실행한다.

### 프로그램 경로와 옵션

```bash
/usr/local/bin/app-version -v
```
/usr/local/bin은 시스템 전역 실행 파일이 놓이는 표준 디렉토리이고, -v는 버전 정보를 출력하는 옵션이다. 실행하면 "Version: 1.2.3" 같은 한 줄이 출력된다.

### 파이프와 gawk 처리

```bash
| gawk 'NR == 1 {print $2}'
```
파이프(`|`)로 앞 명령의 출력을 gawk(GNU AWK)에 넘긴다. `NR == 1`은 첫 번째 라인만 고르고, `print $2`는 그 라인의 두 번째 필드를 출력한다. 위 출력 예에서 두 번째 필드가 버전 번호인 1.2.3이다.

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
버전 문자열처럼 형식이 정해진 명령어 출력에서 특정 필드만 뽑을 때는 이렇게 gawk 한 줄이면 충분하다.
