---
title: "Docker 실전 가이드: 컨테이너 정리하기"
description: "OS별 Docker 컨테이너 정리 방법 가이드"
date: 2024-11-05 10:00:00 +0900
categories: [Dev, Docker]
tags: [docker, container, cleanup, devops, windows, macos, linux]
---

# Docker 실전 가이드: 컨테이너 정리하기
- 최초 작성일: 2024년 11월 5일 (화)
- Docker 버전: 24.0.6
- Docker Compose 버전: 2.21.0

<br>

## Docker 컨테이너 정리하기

### 개요
Docker로 개발을 진행하다 보면 컨테이너가 제대로 종료되지 않거나, 충돌이 발생하는 경우가 있다. 이런 상황에서 깔끔하게 컨테이너를 정리하는 방법을 OS별로 정리한다.

### 기본 확인 명령어
모든 OS에서 동일하게 사용 가능한 기본 명령어다.

1. **실행 중인 컨테이너 확인**
   ```bash
   docker ps
   ```
   이 명령어로 현재 실행 중인 컨테이너의 목록을 볼 수 있다.

2. **모든 컨테이너 확인**
   ```bash
   docker ps -a
   ```
   중지된 컨테이너를 포함한 모든 컨테이너 목록을 확인할 수 있다.

### OS별 컨테이너 정리 방법

#### macOS 또는 Linux 환경
```bash
# 모든 컨테이너 강제 삭제
docker rm -f $(docker ps -aq)
```

#### Windows 환경
```powershell
# PowerShell에서 실행
docker ps -aq | ForEach-Object {docker rm -f $_}
```

#### Windows Git Bash 환경
```bash
# Git Bash에서 실행
docker ps -aq | xargs docker rm -f
```

### 주의사항
- 컨테이너 삭제 시 컨테이너 내부의 데이터도 함께 삭제된다.
- 볼륨을 사용하지 않은 데이터는 복구가 불가능하다.
- 프로덕션 환경에서는 특히 주의해서 사용해야 한다.

### 유용한 팁
자주 사용하는 명령어는 각 환경에 맞게 alias로 등록해두면 편리하다.

#### macOS나 Linux의 경우
```bash
# ~/.bashrc 또는 ~/.zshrc 파일에 추가
echo "alias docker-clean='docker rm -f \$(docker ps -aq)'" >> ~/.bashrc
source ~/.bashrc
```

#### Windows PowerShell의 경우
```powershell
# PowerShell 프로필에 추가
echo "function docker-clean { docker ps -aq | ForEach-Object {docker rm -f $_} }" >> $PROFILE
```

#### Windows Git Bash의 경우
```bash
# ~/.bashrc 파일에 추가
echo "alias docker-clean='docker ps -aq | xargs docker rm -f'" >> ~/.bashrc
source ~/.bashrc
```

### 다음 단계
이제 OS에 맞는 컨테이너 정리 방법을 익혔으니, 실제 컨테이너를 생성하고 운영하는 실습을 진행할 수 있다.
