---
title: "(C#) 20. 상속성 (Inheritance)"
description: inheritance
date: 2022-03-23 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, oop, inheritance]
---

# 상속성 (inheritance) : OOP

- 최초 작성일: 2021년 3월 21일(월)

## 내용

```c#
using System;

namespace Inheritance
{
    class Program
    {
        // OOP 상속성 (은닉성 / 상속성 / 다형성)
        class Player    // 부모 클래스 혹은 기반 클래스
        {
            static public int counter = 1;    // 오로지 1개만 존재!
            public int id;
            public int hp;
            public int attack;

            public void Move()
            {
                Console.WriteLine("Player Move");
            }

            public void Attack()
            {
                Console.WriteLine("Player Attack");
            }
            public Player()
            {
                Console.WriteLine("Player 생성자 호출!");
            }

            public Player(int hp)
            {
                this.hp = hp;
                Console.WriteLine("Player hp 생성자 호출!");
            }
        }

        
        class Mage : Player
        {
     
        }

        class Archer : Player
        {
            
        }

        class Knight : Player   // 자식, 파생
        {
            public Knight() : base(100)
            {
                Console.WriteLine("Knight 생성자 호출!");
            }

            // static 함수 -> 클래스에 종속적 (유일성)
            static public Knight CreateKnight()
            {
                Knight knight = new Knight();
                knight.hp = 100;
                knight.attack = 1;
                return knight;
            }
            public Knight Clone()
            {
                Knight knight = new Knight();
                knight.hp = hp;
                knight.attack = attack;
                return knight;
            }
        }

        static void Main(string[] args)
        {
            Knight knight = new Knight();
            knight.Move();
        }
    }
}

```
