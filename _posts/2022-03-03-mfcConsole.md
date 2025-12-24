---
title: (MFC) 콘솔창 띄우기
description: Console Screen for mfc
date: 2022-03-03 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, debug]
---

# MFC 프로그래밍 시 콘솔창 띄우기

- 최초 작성일: 2021년 3월 3일(목)

## 목차

[TOC]

## 내용

```c++
#pragma comment(linker, "/entry:WinMainCRTStartup /subsystem:console")
```

<br/>
