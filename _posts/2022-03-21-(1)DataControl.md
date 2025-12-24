---
title: "(C#) 1. 데이터 다루기"
description: "Data Control with C#"
date: 2022-03-21 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, datacontrol]
---

# ( , )

- 최초 작성일: 2021년 3월 21일(월)

## 

```c#
using System;

namespace DataControl
{
    class Program
    {
        static void Main(string[] args)
        {
            // 데이터 + 로직
            // 체력 0

            // 1. 바구니 크기가 다른 경우!
            int a = 0x0FFFFFFF; 
            short b = (short)a; // 0xFFFF 만 저장됨 (상위 짤림)

            // 2. 바구니 크기는 같긴 한데, 부호가 다를 경우
            byte c = 255;
            sbyte sb = (sbyte)c;
            // Underflow(언더플로우), Overflow(오버플로우)
            // 0xFF = 0b11111111 = -1

            // 3. 소수
            float f = 3.1415f;
            double d = f;

            /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
            // byte(1바이트, 0~255), short(2바이트, -3만~3만), int(4바이트, -21억~21억), long(8바이트)
            // sbyte(1바이트, -128~127), ushort(2바이트, 0~6만), uint(4바이트, 0~43억), ulong(8바이트)  
            //int hp;
            //short level = 100;
            //long id;
            //hp = 100;

            /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
            // 10진수
            // 0 1 2 3 4 5 6 7 8 9

            //byte attack = 0;
            //attack--;     // -1 이 255(최댓값)가 됨.

            //Console.WriteLine("Hello Number ! {0}", hp);
            /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        }
    }
}
```

<br/>
