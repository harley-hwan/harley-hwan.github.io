---
title: "가상머신과 SFTP: VMware Ubuntu 환경에서의 네트워크 설정 가이드"
description: "ens33 네트워크 인터페이스를 통한 SFTP 연결 최적화"
date: 2024-03-26 10:00:00 +0900
categories: [Dev, Linux]
tags: [linux, ubuntu, vmware, networking, sftp, filezilla, ens33]
---
<br/>

## 네트워크 인터페이스 개요

### 리눅스 네트워크 인터페이스의 이해
리눅스 시스템에서 네트워크 인터페이스는 다음과 같은 계층으로 구성된다.

- 물리적 계층: 실제 네트워크 카드, 가상 네트워크 어댑터
- 데이터 링크 계층: 인터페이스 명명 규칙, MAC 주소 관리
- 네트워크 계층: IP 주소 할당, 라우팅 테이블

<br/>

## ens33의 구조와 역할

### 1. 명명 규칙 분석
'ens33'의 각 부분이 나타내는 의미:
- 'en': Ethernet 네트워크
- 's': PCI 핫플러그 슬롯 번호
- '33': 특정 포트/슬롯 식별자

### 2. 시스템에서의 기능
- 네트워크 추상화: 물리적/가상 네트워크 하드웨어를 추상화하고, 드라이버와 운영체제 간 인터페이스를 제공한다.
- 통신 제어: 패킷 송수신 관리, 네트워크 버퍼링 처리, QoS(Quality of Service) 제어를 담당한다.

<br/>

## 네트워크 설정 프로세스

### 1. 인터페이스 상태 확인

```bash
# 네트워크 인터페이스 상태 확인
ip addr show ens33

# 자세한 정보 확인
ethtool ens33
```

### 2. 인터페이스 활성화 및 설정

```bash
# 인터페이스 활성화
sudo ip link set ens33 up

# DHCP를 통한 IP 할당
sudo dhclient ens33

# 고정 IP 설정 (필요시)
sudo ip addr add 192.168.1.100/24 dev ens33
```

### 3. 네트워크 상태 검증

```bash
# 연결성 테스트
ping -c 4 8.8.8.8

# 라우팅 테이블 확인
ip route show
```

<br/>

## SFTP 연결 구성

### 1. SSH 서버 설정

```bash
# SSH 서버 설치
sudo apt install openssh-server

# 서비스 상태 확인
sudo systemctl status ssh

# 방화벽 설정
sudo ufw allow ssh
```

### 2. FileZilla 클라이언트 설정

기본 연결 정보는 다음과 같이 입력한다.

- 프로토콜: SFTP
- 포트: 22
- 로그온 방식: 일반/키 파일

전송 성능을 위해 고급 설정에서 전송 버퍼 크기 4MB, 동시 연결 수 2, 전송 타입 Binary로 지정한다.

<br/>

## 문제 해결과 최적화

### 1. 일반적인 문제 해결

```bash
# 네트워크 인터페이스 재시작
sudo ip link set ens33 down
sudo ip link set ens33 up

# DNS 설정 확인
cat /etc/resolv.conf

# 시스템 로그 확인
sudo journalctl -u networking.service
```

### 2. 성능 최적화

MTU 최적화:

```bash
# MTU 값 확인
ip link show ens33

# MTU 설정
sudo ip link set ens33 mtu 9000
```

TCP 튜닝:

```bash
# TCP 윈도우 크기 조정
sudo sysctl -w net.ipv4.tcp_wmem="4096 87380 16777216"
sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
```

<br/>

## 보안 고려사항

### 1. SSH 보안 강화

```bash
# SSH 설정 파일 수정
sudo nano /etc/ssh/sshd_config

# 주요 보안 설정
PermitRootLogin no
PasswordAuthentication no
MaxAuthTries 3
```

### 2. 방화벽 구성

```bash
# UFW 기본 정책 설정
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH 포트만 허용
sudo ufw allow 22/tcp

# 방화벽 활성화
sudo ufw enable
```

<br/>

## 결론
여기까지 VMware Ubuntu 환경에서 ens33 인터페이스 확인부터 SFTP 연결, 보안 설정까지의 과정을 정리했다.

