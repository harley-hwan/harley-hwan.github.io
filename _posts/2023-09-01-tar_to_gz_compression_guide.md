---
title: 리눅스에서의 파일 아카이빙 및 압축
description: .tar 파일을 .gzip로 변환하는 Bash 사용하기
date: 2023-09-01 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, tar, gzip, bash, 압축]
---

# Bash를 사용하여 파일 아카이빙 및 압축하기 가이드

- 최초 작성일: 2023년 9월 1일(금)

## 목차

[TOC]

<br/>

## 개요

리눅스에서 파일을 아카이빙 및 압축하는 bash 스크립트. 

스크립트의 주 목적은 `.tar` 파일을 `.gzip` 형식으로 변환하는 것이다.

<br/>

## 코드

```bash
#!/bin/bash

## make zip 

count=0
Dir=/home/dbgftp/Result2
File=/home/dbgftp/Result2/Result.tar

count=$(ls -ltr $Dir | grep "^-.*\.tar" | wc -l)
echo "file total" $count

#tar
FILE_4=`ls -ltr $Dir | grep .tar | gawk NR==1 | gawk -F" " '{printf $9}'`
echo $FILE_4

if [ $count -gt 0 ] ; then
        #zip $Dir/$FILE_4.zip $Dir/$FILE_4
        gzip $Dir/$FILE_4
        rm -r $Dir/$FILE_4
else
        echo "file nothing2"
fi
```

<br/>

## 설명

1. **변수 초기화**:
    ```bash
    count=0
    Dir=/home/dbgftp/Result2
    File=/home/dbgftp/Result2/Result.tar
    ```
    - `count`: `.tar` 파일의 수를 저장하기 위한 변수. 초기 값은 0.
    - `Dir`: 파일들이 위치한 디렉토리의 경로를 저장하는 변수.
    - `File`: 대상 `.tar` 파일의 전체 경로를 저장하는 변수. 이 스크립트에서는 실제로 이 변수를 사용하지 않는다.

2. **.tar 파일 수 카운팅**:
    ```bash
    count=$(ls -ltr $Dir | grep "^-.*\.tar" | wc -l)
    echo "file total" $count
    ```
    - 이 부분에서는 `Dir` 디렉토리 내의 `.tar` 파일의 수를 `count` 변수에 저장.
    - `ls -ltr $Dir`: `$Dir` 디렉토리의 파일들을 최신 수정 시간 순으로 역순으로 나열.
    - `grep "^-.*\.tar"`: 나열된 파일 중에서 `.tar` 확장자를 가진 파일만을 필터링.
    - `wc -l`: 필터링된 파일의 수를 센다.

3. **대상 .tar 파일 식별**:
    ```bash
    FILE_4=`ls -ltr $Dir | grep .tar | gawk NR==1 | gawk -F" " '{printf $9}'`
    echo $FILE_4
    ```
    - `ls -ltr $Dir | grep .tar`: `$Dir` 디렉토리에 있는 `.tar` 파일들을 나열.
    - `gawk NR==1`: 나열된 파일 중에서 첫 번째 파일만 선택. (`ls -ltr`에 의해 가장 오래된 파일이 첫 번째로 표시)
    - `gawk -F" " '{printf $9}'`: 선택된 파일의 이름만 추출.

4. **압축 및 파일 제거**:
    ```bash
    if [ $count -gt 0 ] ; then
            gzip $Dir/$FILE_4
            rm -r $Dir/$FILE_4
    else
            echo "file nothing2"
    fi
    ```
    - `.tar` 파일이 하나라도 있으면:
        - `gzip $Dir/$FILE_4`: 지정된 `.tar` 파일을 `.gzip` 형식으로 압축.
        - `rm -r $Dir/$FILE_4`: 원본 `.tar` 파일 삭제.
    - `.tar` 파일이 없으면: "file nothing2" 메시지 출력.

<br/>

스크립트는 주로 `$Dir` 디렉토리에 위치한 `.tar` 파일들 중 가장 오래된 파일을 `.gzip` 형식으로 압축한 후 원본 `.tar` 파일을 삭제하는 작업을 수행한다.
