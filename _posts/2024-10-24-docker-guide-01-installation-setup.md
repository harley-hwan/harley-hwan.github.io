---
title: "Docker 실전 가이드: 설치와 환경 구성"
description: ""Docker 환경 구축과 실전 활용을 위한 종합 가이드""
date: 2024-10-24 10:00:00 +0900
categories: [Dev, Docker]
tags: [docker, installation, configuration, devops, containerization, git-bash, winpty]
---

# Docker 실전 가이드: 설치와 환경 구성
- 최초 작성일: 2024년 10월 24일 (금)
- 수정일: 2024년 11월 4일 (월)
- Docker 버전: 24.0.6
- Docker Compose 버전: 2.21.0

<br>

## 목차
1. [Git 및 Git Bash 설정](#git-및-git-bash-설정)
   - Git 설치
   - Git Bash 환경설정
   - winpty 설정과 이해
2. [개발 환경 구성](#개발-환경-구성)
   - Visual Studio Code 설치
   - Docker Desktop 설치
   - 작업 환경 설정
3. [Docker 설치 가이드](#docker-설치-가이드)
   - Windows 환경 설치
   - Linux 환경 설치
   - Mac 환경 설치
4. [초기 설정](#초기-설정)
   - Docker 서비스 설정
   - 네트워크 설정
   - 볼륨 관리
   - 보안 초기 설정
5. [기본 명령어 실습](#기본-명령어-실습)
   - 컨테이너 생명주기 관리
   - 이미지 관리
   - 리소스 모니터링
6. [실전 컨테이너 구성](#실전-컨테이너-구성)
   - 웹 애플리케이션 스택 구성
   - CI/CD 파이프라인 구성
   - 백업 및 복구 시스템
7. [문제 해결 가이드](#문제-해결-가이드)
   - 일반적인 문제와 해결
   - 성능 최적화

<br>

## Git 및 Git Bash 설정

### Git 설치
Windows 환경에서 Docker를 효과적으로 사용하기 위해서는 먼저 Git과 Git Bash를 설치해야 한다.

1. **Git 다운로드 및 설치**
   - [Git 공식 웹사이트](https://git-scm.com)에서 최신 버전 다운로드
   - 설치 시 "Git Bash Here" 옵션 선택 확인
   - PATH 환경변수 설정 옵션에서 "Git from the command line and also from 3rd-party software" 선택

   &nbsp;

2. **Git 설치 확인**
   ```bash
   git --version
   ```

   &nbsp;

### Git Bash 환경설정과 winpty 이해

1. **winpty가 필요한 이유**
   - Git Bash는 MSYS2 기반의 UNIX-like 환경을 Windows에서 제공
   - Windows에서 UNIX/Linux 스타일의 터미널 에뮬레이션을 사용할 때, 특히 대화형(interactive) 프로그램 실행 시 입출력 방식의 차이로 인한 호환성 문제 발생
   - winpty는 Windows native 콘솔과 UNIX-like 환경 간의 브릿지 역할을 수행
   - 이후 설치할 Docker의 대화형 명령어들을 Git Bash에서 원활하게 사용하기 위해 필요

   &nbsp;

2. **winpty 설정**
   ```bash
   # Git Bash에서 실행
   echo "alias docker='winpty docker'" >> ~/.bashrc
   
   # 설정 적용
   source ~/.bashrc
   ```

   &nbsp;

3. **설정 확인**
   ```bash
   # alias 설정 확인
   alias docker
   
   # 출력 예시:
   # alias docker='winpty docker'
   ```

   &nbsp;

4. **주의사항과 팁**
   - winpty 설정은 Git Bash에서만 필요하며, Windows Terminal이나 PowerShell에서는 불필요
   - 이 설정은 이후 Docker 설치 완료 후 Git Bash에서 Docker의 대화형 명령어 사용 시 필요
   - `~/.bashrc` 파일을 직접 수정하여 다른 유용한 alias들도 함께 설정 가능
   - 설정한 alias는 새로운 Git Bash 세션을 열거나 `source ~/.bashrc` 명령어 실행 시 적용

   ```bash
   # 유용한 추가 alias 예시 (Docker 설치 후 사용 가능)
   echo "alias dps='docker ps'" >> ~/.bashrc
   echo "alias dimg='docker images'" >> ~/.bashrc
   ```

   &nbsp;

## 개발 환경 구성

### Visual Studio Code 설치
효율적인 개발을 위해 VS Code를 설치하고 필요한 확장을 구성한다.

1. **VS Code 설치**
   - [VS Code 공식 웹사이트](https://code.visualstudio.com)에서 최신 버전 다운로드
   - 설치 시 아래 옵션들 체크 확인:
     - "Code로 열기" 작업을 Windows 탐색기 파일 상황에 맥락 메뉴에 추가
     - "Code로 열기" 작업을 Windows 탐색기 디렉터리 상황에 맥락 메뉴에 추가
     - PATH에 추가

   &nbsp;

2. **추천 VS Code 확장 프로그램**
   - Docker (Microsoft)
   - Remote Development
   - Git Graph
   - Git History
   - GitLens

   ```bash
   # VS Code 설치 확인
   code --version
   ```

   &nbsp;

### Docker Desktop 설치
Windows에서 Docker를 사용하기 위해 Docker Desktop을 설치한다.

1. **사전 준비사항 확인**
   - Windows 10/11 Pro, Enterprise, Education (Build 16299 이상)
   - WSL 2 기능 활성화 (이전 섹션의 WSL 2 설치 참조)
   - BIOS에서 가상화 기능 활성화

   &nbsp;

2. **Docker Desktop 설치**
   - [Docker Hub](https://hub.docker.com/editions/community/docker-ce-desktop-windows/) 에서 Docker Desktop 다운로드
   - 다운로드한 설치 파일(Docker Desktop Installer.exe) 실행
   - "Use WSL 2 instead of Hyper-V" 옵션 선택
   - 설치 완료 후 시스템 재시작

   &nbsp;

### 프로젝트 workspace 구성

1. **작업 디렉토리 생성**
   ```bash
   # 원하는 드라이브로 이동 (예: D드라이브)
   cd /d/

   # workspace 디렉토리 생성
   mkdir docker-workspace
   ```

   &nbsp;

2. **작업 환경 열기**
   
   방법 1: 파일 탐색기 사용
   - 생성한 docker-workspace 폴더로 이동
   - 폴더 내 빈 공간에서 우클릭
   - 상황에 맞게 선택:
     - "Open Git Bash here" 선택하여 Git Bash 열기
     - "Code로 열기" 선택하여 VS Code 열기

   방법 2: 명령줄 사용
   ```bash
   # workspace로 이동
   cd docker-workspace

   # VS Code 열기
   code .
   ```

   &nbsp;

3. **작업 환경 구성 확인**
   ```bash
   # 현재 위치 확인
   pwd

   # Git Bash에서 기본 설정 확인
   alias docker
   ```

   &nbsp;

4. **프로젝트 구조 예시**
   ```plaintext
   docker-workspace/
   ├── project1/
   │   ├── Dockerfile
   │   ├── docker-compose.yml
   │   └── src/
   ├── project2/
   │   ├── Dockerfile
   │   └── docker-compose.yml
   └── README.md
   ```

   &nbsp;

5. **개발 환경 통합 확인**
   - VS Code에서 Docker 확장 동작 확인
   - Git Bash 터미널 작동 확인
   - 기본 설정된 alias 확인
   - Docker Desktop 실행 상태 확인

   &nbsp;

### 개발 환경 사용 팁
1. **VS Code 통합 터미널 설정**
   - VS Code에서 `Ctrl + `` 로 터미널 열기
   - 기본 터미널을 Git Bash로 설정하기:
     1. `Ctrl + Shift + P` 로 명령 팔레트 열기
     2. "Terminal: Select Default Profile" 검색
     3. "Git Bash" 선택

   &nbsp;

2. **작업 공간 구성**
   - 프로젝트별로 별도의 폴더 생성
   - `.gitignore` 파일 설정
   - Docker 관련 파일들을 프로젝트 루트에 배치
   - VS Code 작업 공간 설정 파일 구성

   &nbsp;

## Docker 설치 가이드

### Windows 환경 설치

1. **시스템 요구사항 확인**
   - Windows 10 Pro, Enterprise, Education (Build 16299 이상)
   - 또는 Windows 11
   - CPU 가상화 지원 (BIOS에서 활성화 필요)
   - 최소 4GB RAM (8GB 이상 권장)
   - 최소 50GB 여유 디스크 공간
   
   &nbsp;
   
2. **WSL2 설치 및 설정**

   ```powershell
   # PowerShell 관리자 모드에서 실행
   wsl --install
   
   # WSL2를 기본 버전으로 설정
   wsl --set-default-version 2
   
   # WSL 상태 확인
   wsl -l -v
   ```

   &nbsp;
   
설치 확인:
   ```powershell
   # Docker 버전 확인
   docker --version
   
   # Docker Compose 버전 확인
   docker-compose --version
   
   # Docker 시스템 정보 확인
   docker info
   ```

   &nbsp;

### Linux(Ubuntu) 환경 설치
Linux 환경에서는 패키지 관리자를 통해 Docker를 설치한다. 여기서는 Ubuntu 22.04 LTS를 기준으로 설명한다.

1. **시스템 업데이트 및 필수 패키지 설치**
   ```bash
   # 시스템 업데이트
   sudo apt update
   sudo apt upgrade -y
   
   # 필수 패키지 설치
   sudo apt install -y \
       apt-transport-https \
       ca-certificates \
       curl \
       gnupg \
       lsb-release
   ```

   &nbsp;
   
2. **Docker 공식 저장소 설정**
   ```bash
   # GPG 키 추가
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   
   # 저장소 추가
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```
   
   &nbsp;

3. **Docker 엔진 설치**
   ```bash
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   ```

   &nbsp;

4. **사용자 권한 설정**
   ```bash
   # 현재 사용자를 docker 그룹에 추가
   sudo usermod -aG docker $USER
   
   # 변경사항 적용을 위한 재로그인
   newgrp docker
   ```

   &nbsp;

### Mac 환경 설치
Mac 환경에서는 Docker Desktop을 통해 Docker를 설치하고 관리한다.

1. **시스템 요구사항**
   - macOS 11 이상
   - Apple Silicon(M1/M2) 또는 Intel 프로세서
   - 최소 4GB RAM (8GB 이상 권장)
   - 최소 50GB 여유 디스크 공간

   &nbsp;
   
2. **설치 과정**
   ```bash
   # Homebrew를 통한 설치
   brew install --cask docker
   ```

   &nbsp;
   
3. **설치 확인 및 초기 설정**
   ```bash
   # Docker 버전 확인
   docker --version
   ```

<br>

## 초기 설정

### Docker 서비스 설정
Docker 데몬의 기본 설정을 최적화하고 보안을 강화한다.

1. **데몬 설정 파일 구성**
   ```json
   # /etc/docker/daemon.json
   {
       "storage-driver": "overlay2",
       "log-driver": "json-file",
       "log-opts": {
           "max-size": "10m",
           "max-file": "3"
       },
       "default-ulimits": {
           "nofile": {
               "Name": "nofile",
               "Hard": 64000,
               "Soft": 64000
           }
       },
       "live-restore": true,
       "max-concurrent-downloads": 10,
       "max-concurrent-uploads": 10
   }
```

   &nbsp;
   
2. **서비스 활성화 및 시작**
   ```bash
   # 서비스 상태 확인
   sudo systemctl status docker
   
   # 부팅 시 자동 시작 설정
   sudo systemctl enable docker
   
   # 서비스 재시작
   sudo systemctl restart docker
   ```

<br>

### 네트워크 설정
Docker의 네트워크는 컨테이너 간 통신과 외부 연결을 관리한다.

1. **네트워크 드라이버 이해**
   - bridge: 단일 호스트 내 컨테이너 간 통신
   - host: 호스트의 네트워크 직접 사용
   - overlay: 다중 호스트 간 컨테이너 통신
   - none: 네트워크 기능 비활성화

   &nbsp;
   
2. **사용자 정의 네트워크 생성**
   ```bash
   # 애플리케이션별 격리된 네트워크 생성
   docker network create \
       --driver bridge \
       --subnet 172.18.0.0/16 \
       --gateway 172.18.0.1 \
       app_network
   
   # 암호화된 오버레이 네트워크 생성
   docker network create \
       --driver overlay \
       --opt encrypted \
       secure_network
   ```
   
<br>

## 기본 명령어 실습

### 컨테이너 생명주기 관리
컨테이너의 전체 라이프사이클을 관리하는 기본 명령어들이다.

1. **컨테이너 실행과 관리**
   ```bash
   # 기본 컨테이너 실행
   docker run nginx
   
   # 백그라운드 실행 (-d)와 포트 매핑 (-p)
   docker run -d --name webserver -p 80:80 nginx
   
   # 환경변수 설정과 볼륨 마운트
   docker run -d \
       --name webapp \
       -e "NODE_ENV=production" \
       -v $(pwd):/app \
       node:16
   ```

   &nbsp;
   
2. **컨테이너 상태 관리**
   ```bash
   # 실행 중인 컨테이너 목록
   docker ps
   
   # 모든 컨테이너 목록 (중지된 것 포함)
   docker ps -a
   
   # 컨테이너 상세 정보
   docker inspect webapp
   
   # 실시간 로그 확인
   docker logs -f webapp
   ```

   &nbsp;

3. **컨테이너 리소스 제어**
   ```bash
   # 메모리 제한
   docker run -d \
       --name limited_app \
       --memory="512m" \
       --memory-swap="512m" \
       nginx
   
   # CPU 제한
   docker run -d \
       --name cpu_limited \
       --cpus=".5" \
       nginx
   ```

   &nbsp;

### 이미지 관리
Docker 이미지의 생성, 저장, 배포를 위한 명령어들이다.

1. **이미지 기본 관리**
   ```bash
   # 이미지 검색
   docker search nginx
   
   # 이미지 다운로드
   docker pull nginx:latest
   
   # 이미지 목록 확인
   docker images
   
   # 이미지 삭제
   docker rmi nginx:latest
   ```

   &nbsp;

2. **커스텀 이미지 생성**
   ```dockerfile
   # Dockerfile 예시
   FROM node:16-alpine
   
   WORKDIR /app
   COPY package*.json ./
   RUN npm install
   COPY . .
   
   EXPOSE 3000
   CMD ["npm", "start"]
   ```

   ```bash
   # 이미지 빌드
   docker build -t myapp:1.0 .
   
   # 이미지 태그 설정
   docker tag myapp:1.0 registry.example.com/myapp:1.0
   ```

   &nbsp;

## 실전 컨테이너 구성

### 웹 애플리케이션 스택 구성
   ```yaml
   # docker-compose.yml
   version: '3.8'
   services:
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
       volumes:
         - ./nginx/conf.d:/etc/nginx/conf.d
       depends_on:
         - webapp
   
     webapp:
       build: ./webapp
       environment:
         - NODE_ENV=production
         - DB_HOST=db
       depends_on:
         - db
         - redis
   
     db:
       image: postgres:13
       volumes:
         - postgres_data:/var/lib/postgresql/data
       environment:
         - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
   
     redis:
       image: redis:alpine
       volumes:
         - redis_data:/data
   
   volumes:
     postgres_data:
     redis_data:
   ```

   &nbsp;

### CI/CD 파이프라인 구성
   ```yaml
   # .gitlab-ci.yml
   stages:
     - build
     - test
     - deploy
   
   build:
     stage: build
     script:
       - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
       - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
   
   test:
     stage: test
     script:
       - docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
       - docker run --rm $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA npm test
   
   deploy:
     stage: deploy
     script:
       - docker stack deploy -c docker-compose.prod.yml myapp
   ```

   &nbsp;

### 백업 및 복구 시스템
   ```bash
   #!/bin/bash
   # backup.sh
   
   # 데이터베이스 백업
   docker exec db pg_dump -U postgres myapp > backup_$(date +%Y%m%d).sql
   
   # 볼륨 데이터 백업
   docker run --rm \
       --volumes-from db \
       -v $(pwd)/backups:/backups \
       alpine \
       tar czf /backups/volumes_$(date +%Y%m%d).tar.gz /var/lib/postgresql/data
   ```

   &nbsp;
   
## 문제 해결 가이드

### 일반적인 문제와 해결
1. **컨테이너 시작 실패**
   ```bash
   # 로그 확인
   docker logs --tail 50 container_name
   
   # 컨테이너 상태 확인
   docker inspect container_name
   ```

   &nbsp;

2. **성능 최적화**
   ```dockerfile
   # 다단계 빌드 예시
   FROM node:16 AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci
   COPY . .
   RUN npm run build
   
   FROM nginx:alpine
   COPY --from=builder /app/build /usr/share/nginx/html
   ```

   &nbsp;

## 결론

Docker 개발 환경을 체계적으로 구축하는 방법을 정리한다.

먼저 Git과 Git Bash가 필요하다. Windows 환경에서는 Docker 명령어를 원활하게 사용하기 위해 winpty 설정이 필수다. 이를 통해 Windows에서도 Linux처럼 터미널 명령어를 사용할 수 있다.

개발의 편의성을 위해서는 VS Code가 필요하다. Docker 관련 확장 프로그램을 설치하면 GUI 환경에서도 Docker를 쉽게 관리할 수 있다. Docker Desktop과 WSL2는 Windows에서 Docker를 사용하기 위한 기본 요소다.

작업 공간은 D 드라이브에 docker-workspace 디렉토리를 만들어 구성했다. VS Code의 기본 터미널을 Git Bash로 설정하면 작업 효율을 높일 수 있다.

Docker 환경 구성 시 알아야 할 핵심 내용:
- 컨테이너는 생성, 시작, 중지, 삭제의 생명주기를 가진다
- 이미지는 컨테이너의 기본이 되는 템플릿이다
- docker-compose로 여러 컨테이너를 한 번에 관리할 수 있다
- 볼륨으로 데이터를 영구적으로 저장하고, 네트워크로 컨테이너 간 통신이 가능하다

이 환경 구성을 기반으로 실제 프로젝트를 진행할 수 있다.
