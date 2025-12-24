---
title: "(C#) 9. 코드의 흐름 제어 (break, continue)"
description: "break & continue"
date: 2022-03-21 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, codeflowcontrol, break, continue]
---

# break & continue

- 최초 작성일: 2021년 3월 21일(월)

## 목차



## 내용

```c#
using System;

namespace break_continue
{
    class Program
    {
        static void Main(string[] args)
        {
            int num = 97;   // 1, 97로만 나뉘는 숫자

            bool isPrime = true;

            //////////////// break
            for (int i = 2; i < num; i++)
            {
                if ((num % i) == 0)
                {
                    //Console.WriteLine("소수가 아닙니다!");
                    isPrime = false;
                    break;
                }
            }
            //Console.WriteLine("소수입니다!");
            if (isPrime)
                Console.WriteLine("소수입니다!");
            else
                Console.WriteLine("소수가 아닙니다!");


            //////////////// continue;
            for (int i = 1; i <= 100; i++)
            {
                if ((i % 3) != 0)
                    continue;

                Console.WriteLine($"3으로 나뉘는 숫자 발견 : {i}");
            }
        }
    }
}

```
