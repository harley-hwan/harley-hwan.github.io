---
layout: post
title: "(CNN) 캐글(Kaggle) 커널 사용하기 - 계정 등록 및 GPU 인증"
subtitle: "캐글 계정 생성부터 GPU 사용을 위한 전화번호 인증까지 상세 가이드"
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: \[star, fork, follow]
tags: \[cnn, kaggle, gpu, python, machine learning, data science]
comments: true
filename: "2025-05-26-cnn-00-kaggle-kernel-gpu-setup.md"
---

---------------------------------------------------

# 캐글(Kaggle) 커널 사용하기 - 계정 등록 및 GPU 사용 인증

* 최초 작성일: 2025년 5월 26일 (월)

## 목차

1. [캐글 커널 시작하기](#캐글-커널-시작하기)
2. [GPU 및 인터넷 사용 인증하기](#gpu-및-인터넷-사용-인증하기)
3. [GPU 활성화하기](#gpu-활성화하기)

---


## 캐글 커널 시작하기

[캐글 홈페이지](https://www.kaggle.com)에 접속한다.

계정 생성 후 다음과 같은 방법으로 커널(Notebook)을 만든다.

1. 화면 왼쪽 메뉴의 **Create(+)** 버튼을 클릭하거나, 상단의 **Code** 메뉴로 이동한다.
2. **New Notebook**을 클릭하면 새 캐글 커널이 생성된다.

## GPU 및 인터넷 사용 인증하기

GPU를 사용하기 위해선 전화번호 인증이 필요하다. 방법은 다음과 같다.

1. 커널 화면에서 우측 하단의 **Extended Sidebar**를 클릭한다.
2. 나타난 메뉴에서 **Session Options**를 선택한다.
3. GPU 옵션과 인터넷 연결을 사용하려면 **Get Phone Verified** 버튼을 눌러 전화번호 인증을 진행해야 한다.

그러면 GPU와 인터넷 연결을 사용할 준비가 완료된다.

## GPU 활성화하기

GPU를 활성화하는 방법은 다음과 같다:

1. 다시 캐글 홈페이지에서 **Create > New Notebook**을 선택한다.
2. 커널 우측 하단의 **Accelerator** 옵션을 클릭한다.
3. 메뉴에서 **GPU P100**을 선택한다.
4. 선택하면 GPU 활성화가 완료되며, 일주일에 최대 30시간 동안 사용할 수 있게 된다.
5. 인터넷 연결은 기본적으로 **ON** 상태이며, 이를 끄지 말고 유지해야 한다.

이제 캐글에서 GPU를 활용한 머신 러닝 작업을 할 수 있게 됐다.
