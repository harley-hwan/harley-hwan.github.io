---
title: "(C#) 23. 다형성 (Polymorphism)"
description: polymorphism
date: 2022-03-23 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, oop, polymorphism]
---

# 다형성 (Polymorphism) : OOP

- 최초 작성일: 2021년 3월 21일(월)

## 목차

[TOC]

## 내용

```c#
using System;

namespace Polymorphism
{
    // OOP Polymorphism (은닉성 / 상속성 / 다형성)
    class Player
    {
        protected int hp;
        protected int attack;

        public virtual void Move()
        {
            Console.WriteLine("Player 이동!");
        }
    }

    // 오버로딩(함수 이름의 재사용), 오버라이딩

    class Knight : Player
    {
        // sealed: 봉인. 더 이상 해당 함수를 재정의할 수 없다.  사용하는 경우 거의 없음.
        public sealed override void Move()
        {
            base.Move();

            Console.WriteLine("Knight 이동!");
        }
    }

    class SuperKnight : Knight
    {
        //public override void Move()       // 재정의할 수 없음. 
        //{
        //    base.Move();
        //    {
        //        Console.WriteLine("SuperKnight 이동!");
        //    }
        //}
    }

    class Mage : Player
    {
        public override void Move()
        {
            Console.WriteLine("Mage 이동!");
        }

        public int mp;
    }

    class Program
    {
        static void EnterGame(Player player)
        {
            player.Move();
            // '없음'
            Mage mage = (player as Mage);
            if (mage != null)
            {
                mage.mp = 10;
            }
        }

        static void Main(string[] args)
        {
            Knight knight = new Knight();
            Mage mage = new Mage();

            knight.Move();

            //EnterGame(mage);
        }
    }
}


```

<br/>

## Result

![image](https://user-images.githubusercontent.com/68185569/159215772-c082d966-db91-4515-b620-f076fe01eaf9.png)

