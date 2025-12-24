---
title: 모든 타겟 프로세스 kill하기 (bash 쉘 스크립트)
description: "linux, embedded, bash, shell, sh, kill, bash, script"
date: 2023-08-23 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, embedded, bash, shell, sh, kill, bash, script]
---

# 모든 타켓 프로세스 kill하기 (kill_proc.sh 스크립트)

- 최초 작성일: 2023년 8월 23일(수)

## 목차



<br/>

## 코드

```bash
"kill_proc.sh" 31L, 704C
#!/bin/bash

# kjh [2023.08.23]
# run check proc


FILES=0
CTIME2=10
#COUNT=`ps -ef | grep "proc" | grep -v grep | wc -l`

KILL="proc"
COUNT=`ps -ef | grep -i $KILL | grep -v grep | wc -l`
GETpid=`ps -ef | grep -i $KILL | grep -v grep | gawk NR==$COUNT | gawk -F" " '{printf $2}'`

echo "start[$0 $KILL $COUNT $GETpid]"

if [ "$COUNT" == "$FILES" ]; then
 echo "not running !!![$0]"
else
 while [ $COUNT -ne $FILES ]
  do
  echo "kill !!! $GETpid"
  kill -15 $GETpid
  sleep 1
  COUNT=`ps -ef | grep -i $KILL | grep -v grep | wc -l`
  GETpid=`ps -ef | grep -i $KILL | grep -v grep | gawk NR==$COUNT | gawk -F" " '{printf $2}'`
  echo "[$0 $KILL $COUNT $GETpid]"
  done
fi
echo "end[$0]"

sleep 2
```

<br/>

<br/>

## 설명

### **1. Shebang**
```bash
#!/bin/bash
```
- **Shebang(`#!`)**: 스크립트 파일의 첫 줄에 위치하며 해당 스크립트를 어떤 인터프리터로 실행할지를 지정해줍니다. 여기서는 bash 쉘로 실행하라고 지정되어 있다.

### **2. 변수 초기화**
```bash
FILES=0
CTIME2=10
```
- `FILES`: "proc" 프로세스가 하나도 실행 중이지 않을 때의 기대되는 개수를 나타내는 변수이다. 여기서는 0으로 초기화.
- `CTIME2`: 초기 값 10이다.

### **3. 타겟 프로세스 정보 추출**
```bash
KILL="proc"
COUNT=`ps -ef | grep -i $KILL | grep -v grep | wc -l`
GETpid=`ps -ef | grep -i $KILL | grep -v grep | gawk NR==$COUNT | gawk -F" " '{printf $2}'`
```
- `KILL`: 종료하고자 하는 프로세스의 이름을 저장하는 변수이다.
- `COUNT`: 현재 시스템에서 실행 중인 "E6Client" 프로세스의 개수를 저장한다.
- `GETpid`: "proc" 프로세스 중 마지막 프로세스의 PID(Process ID)를 저장한다.

### **4. 스크립트 시작 상태 출력**
```bash
echo "start[$0 $KILL $COUNT $GETpid]"
```
- 스크립트가 시작될 때의 상태를 출력합니다. 출력되는 정보에는 스크립트의 경로와 이름(`$0`), 타겟 프로세스 이름(`$KILL`), 실행 중인 프로세스의 개수(`$COUNT`), 마지막 프로세스의 PID(`$GETpid`)가 포함된다.

### **5. 조건문을 통한 프로세스 종료**
```bash
if [ "$COUNT" == "$FILES" ]; then
 echo "not running !!![$0]"
```
- "E6Client" 프로세스의 개수(`COUNT`)가 0(`FILES`)이면, 해당 프로세스가 실행 중이지 않다는 메시지와 함께 스크립트 이름(`$0`)을 출력한다.

```bash
else
 while [ $COUNT -ne $FILES ]
  do
  echo "kill !!! $GETpid"
  kill -15 $GETpid
  sleep 1
  COUNT=`ps -ef | grep -i $KILL | grep -v grep | wc -l`
  GETpid=`ps -ef | grep -i $KILL | grep -v grep | gawk NR==$COUNT | gawk -F" " '{printf $2}'`
  echo "[$0 $KILL $COUNT $GETpid]"
  done
```
- `else`문 내부에 있는 `while`문은 "proc" 프로세스의 개수(`COUNT`)가 0이 아닐 동안 반복된다.
  - 해당 프로세스의 PID(`GETpid`)를 출력하며, 해당 프로세스를 `kill -15` 명령을 통해 종료시킨다.
  - 1초 동안 대기 후, 다시 "E6Client" 프로세스의 개수(`COUNT`)와 마지막 프로세스의 PID(`GETpid`)를 갱신한다.
  - 현재 상태를 출력한다.

```bash
fi
```
- 조건문 `if`를 종료.

### **6. 스크립트 종료 전 대기**
```bash
echo "end[$0]"
```
- 스크립트 종료를 알리는 메시지 출력. $0은 현재 스크립트의 이름을 나타낸다.
---

이 스크립트는 시스템에서 "proc" 프로세스가 실행 중인지 확인하고, 만약 실행 중이라면 해당 프로세스를 순차적으로 종료하는 역할을 한다.
