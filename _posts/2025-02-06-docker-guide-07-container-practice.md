---
title: "Docker 실전 가이드: Nginx 컨테이너 실습"
description: "Docker를 사용하여 웹 서버 컨테이너 실행 및 관리하기"
date: 2025-02-06 10:00:00 +0900
categories: [Dev, Docker]
tags: [docker, container, nginx, webserver, cli]
---

# Docker : Nginx 
- 최초 작성일: 2025년 2월 6일 (목)

<br>

## 

이 실습에서는 **Docker를 이용하여 Nginx 웹 서버 컨테이너를 실행하고 접속하는 방법**을 설명한다.

### 
1. Docker 명령어를 사용하여 컨테이너 실행
2. Nginx 컨테이너가 제공하는 웹페이지 접속
3. 컨테이너 종료 및 삭제 방법 학습

Nginx는 전 세계적으로 많이 사용되는 웹 서버이며, 컨테이너 환경에서 빠르고 간편하게 배포할 수 있다.

## 

### 1. Docker 
먼저 도커가 정상적으로 실행되고 있는지 확인한다.

```bash
docker version
```

이 명령어를 실행하면 **클라이언트와 서버의 버전 정보**를 확인할 수 있다.

<img width="700" alt="image" src="https://github.com/user-attachments/assets/b4ec4691-0aa1-457e-ab4b-4512ede5f562" />

### 2. Docker 
현재 실행 중인 Docker 환경에 대한 자세한 정보를 확인하려면 다음 명령어를 실행한다.

```bash
docker info
```

이 명령어를 실행하면 다음과 같은 정보를 확인할 수 있다:
- 실행 중인 컨테이너 개수
- 사용 중인 이미지 개수
- 시스템의 OS 및 CPU 정보

<img width="700" alt="image" src="https://github.com/user-attachments/assets/5648f40d-dc79-4b9e-8649-4723ac98a78e" />

<br>

## Nginx 

### 1. Docker 
컨테이너를 실행하려면 **docker run** 명령어를 사용한다.

```bash
docker run -p 80:80 --name hellonginx nginx
```

### 2. 
- `-p 80:80` → 호스트의 80 포트를 컨테이너의 80 포트로 연결
- `--name hellonginx` → 컨테이너 이름을 `hellonginx`로 지정
- `nginx` → 사용할 이미지(웹서버 소프트웨어) 지정

이 명령어를 실행하면 **Nginx 웹 서버가 컨테이너 내부에서 실행**된다.

<img width="700" alt="image" src="https://github.com/user-attachments/assets/baf29599-440c-4417-972f-ef39971c10a0" />

<br>

## 

Nginx가 실행되었으면 웹 브라우저를 열고 **localhost** 또는 **127.0.0.1**에 접속한다.

```bash
http://localhost
```

정상적으로 실행되었다면 **"Welcome to Nginx!"**라는 기본 웹페이지가 표시된다.

<img width="700" alt="image" src="https://github.com/user-attachments/assets/4ecf7c2a-0a67-4803-80e6-31eaf972bb85" />

또한, 터미널에서 다음 명령어를 사용하여 컨테이너 내부 로그를 확인할 수도 있다:

```bash
docker logs hellonginx
```

<br>

## 

### 1. 
컨테이너 실행을 중지하려면 다음 명령을 실행한다:

```bash
ctrl + c  # 실행 중인 컨테이너 종료 (터미널 점유 상태에서)
```
또는 아래 명령어를 사용하여 특정 컨테이너를 종료할 수도 있다:

```bash
docker stop hellonginx
```

<br>

### 2. 
실행이 종료된 컨테이너를 삭제하려면 다음 명령을 실행한다:

```bash
docker rm hellonginx
```

이제 컨테이너가 완전히 제거되었다.

<br>

## 

이 실습에서는 **Docker를 사용하여 Nginx 웹 서버 컨테이너를 실행하고 관리하는 방법**을 설명했다.

### 
1. **Docker 버전 및 환경 확인**
2. **Nginx 컨테이너 실행 및 웹페이지 접속**
3. **컨테이너 로그 확인 및 종료, 삭제**

컨테이너를 사용하면 단순한 명령어 한 줄로 빠르게 웹 서버를 실행할 수 있으며, 별도의 환경 설정 없이 다양한 서비스를 배포할 수 있다.

다음 파트에서는 **Docker 이미지의 개념과 관리 방법**에 대해 자세히 다룬다.

---

