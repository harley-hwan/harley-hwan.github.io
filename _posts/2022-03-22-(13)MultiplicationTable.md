---
title: "(C#) 13. 구구단"
description: "multiplication table with C#"
date: 2022-03-22 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, codeflowcontrol, multiplicationtable]
---

# 

- 최초 작성일: 2021년 3월 21일(월)

## 

```c#
using System;

namespace ex1
{
    class Program
    {
        static void Main(string[] args)
        {
            // 구구단
            for (int i = 2; i <= 9; i++)
            {
                for (int j = 1; j <= 9; j++)
                {
                    Console.WriteLine($"{i} * {j} = {i * j}");
                }
                Console.WriteLine();
            }
        }
    }
}

```
