---
title: "(C#) 6. 가위바위보 게임"
description: Rock-Scissors-Paper Game
date: 2022-03-21 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, codeflowcontrol, rockscissorspaper]
---

# 

- 최초 작성일: 2021년 3월 21일(월)

## 

```c#
using System;

namespace Rock_Paper_Scissors
{
    class Program
    {
        static void Main(string[] args)
        {
            enum Choice
            {
                // 0:가위     1:바위    2:보
                const int ROCK = 0;
                const int SCISSOR = 2;
               const int PAPER = 1;
            }
            
            
  
            Random rand = new Random();
            int aiChoice = rand.Next(0, 3);     // 0~2사이의 랜덤 값
            int choice = Convert.ToInt32(Console.ReadLine());

            switch (choice)
            {
                case 0:
                    Console.WriteLine("당신의 선택은 가위입니다.");
                    break;
                case 1:
                    Console.WriteLine("당신의 선택은 바위입니다.");
                    break;
                case 2:
                    Console.WriteLine("당신의 선택은 보입니다.");
                    break;
            }

            switch (aiChoice)
            {
                case 0:
                    Console.WriteLine("상대방의 선택은 가위입니다.");
                    break;
                case 1:
                    Console.WriteLine("상대방의 선택은 바위입니다.");
                    break;
                case 2:
                    Console.WriteLine("상대방의 선택은 보입니다.");
                    break;
            }

            // 승리 무승부 패배
            if (choice == 0)
            {
                if (aiChoice == 0)
                {
                    Console.WriteLine("무승부");
                }
                else if (aiChoice == 1)
                {
                    Console.WriteLine("패배.");
                }
                else   // choice == 2
                {
                    Console.WriteLine("승리.");
                }
            }
            else if (choice == 1)
            {
                if (aiChoice == 0)
                {
                    Console.WriteLine("승리.");
                }
                else if (aiChoice == 1)
                {
                    Console.WriteLine("무승부");
                }
                else   // choice == 2
                {
                    Console.WriteLine("패배.");
                }
            }
            else   // choice == 2
            {
                if (aiChoice == 0)
                {
                    Console.WriteLine("패배.");
                }
                else if (aiChoice == 1)
                {
                    Console.WriteLine("승리.");
                }
                else   // choice == 2
                {
                    Console.WriteLine("무승부");
                }
            }
        }
    }
}

```
