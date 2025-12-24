---
title: "(C#) 2. 데이터 연산"
description: "Data Operation with C#"
date: 2022-03-21 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, dataoperation]
---

# 데이터 연산

- 최초 작성일: 2021년 3월 21일(월)

## 목차

[TOC]

## 내용

```c#
using System;

namespace DataOperation
{
    class Program
    {
        static void Main(string[] args)
        {
            int hp = 100;
            int level = 50;

            // < <= > >= == !=
            bool isAlive = (hp > 0);
            bool isHighLevel = (level >= 40);

            // %% AND   || OR   ! NOT
            // a = 살아있는 고랩 유저인가?
            bool a = isAlive && isHighLevel;

            // b = 살아있거나, 고렙 유저이거나, 둘 중 하나인가요?
            bool b = isAlive || isHighLevel;

            // c = 죽은 유저인가?
            bool c = !isAlive;
        }
    }
}

```
