---
title: "(C#) 3. 비트 연산"
description: "Bit Operation with C#"
date: 2022-03-21 10:00:00 +0900
slug: '(3)BitOperation'
categories: [Dev, CSharp]
series: csharp
series_order: 3
tags: [csharp, unity, bitoperation]
---
## 내용

```c#
using System;

namespace BitOperation
{
    class Program
    {
        static void Main(string[] args)
        {
            int num = 1;
            int id = 123;
            int key = 401;

            int a = id ^ key;
            int b = a ^ key;
            // <<   >>  &(and)   !(not)   ^(xor)   ~(not)
            num = num << 3;

            Console.WriteLine(a);
            Console.WriteLine(b);
        }
    }
}
```
