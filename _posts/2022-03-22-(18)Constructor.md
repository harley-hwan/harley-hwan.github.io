---
title: "(C#) 18. 생성자"
description: constructor
date: 2022-03-22 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, oop, constructor]
---

# 생성자 

- 최초 작성일: 2021년 3월 21일(월)

## 내용

```c#
using System;

namespace Constructor
{
    class Program
    {
        class Knight
        {
            public int hp;
            public int attack;

            public Knight()
            {
                hp = 100;
                attack = 10;
                Console.WriteLine("생성자 호출!");
            }

            public Knight(int hp) : this()
            {
                this.hp = hp;
                Console.WriteLine("int 생성자 호출!");
            }

            public Knight(int hp, int attack)
            {
                this.hp = hp;
                this.attack = attack;
                Console.WriteLine("int, int 생성자 호출!");
            }
        }
        static void Main(string[] args)
        {
            Knight knight = new Knight(50, 5);
        }
    }
}

```
