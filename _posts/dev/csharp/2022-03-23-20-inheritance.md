---
title: "(C#) 20. 상속성 (Inheritance)"
description: "직업마다 클래스를 만들다 중복이 생겨서 공통 부분을 부모로 뺐다. base()로 부모 생성자를 고르는 법, 생성자 실행 순서, 부모에 기본 생성자가 없으면 자식이 컴파일되지 않는 이유를 정리했다."
date: 2022-03-23 10:00:00 +0900
slug: '(20)Inheritance'
categories: [Dev, CSharp]
series: csharp
series_order: 20
tags: [csharp, unity, oop, inheritance, base, constructor]
---
## 같은 코드를 세 번 쓰게 되면

[16편](/posts/(16)TextRPG/)의 Text RPG에는 기사, 궁수, 법사가 있었다. 셋을 각각 클래스로 만들면 `hp`, `attack`, `Move`, `Attack`이 세 번씩 똑같이 나온다. 하나를 고치면 셋을 다 고쳐야 한다.

공통 부분을 위로 빼고 나머지만 따로 두는 게 상속이다.

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

`class Knight : Player`의 콜론이 상속이다. `Mage`와 `Archer`는 본문이 비어 있는데도 `hp`, `attack`, `Move`, `Attack`을 전부 갖는다. 물려받았기 때문이다.

`knight.Move()`가 되는 것도 그래서다. `Knight`에는 `Move`가 없지만 `Player`에 있다.

## 실행 순서

`new Knight()`를 돌리면 이렇게 나온다.

```text
Player hp 생성자 호출!
Knight 생성자 호출!
```

**부모가 먼저다.** 자식 생성자 본문이 돌기 전에 부모 생성자가 완료된다.

당연한 순서다. 자식은 부모의 필드를 쓸 수 있는데, 부모가 아직 초기화되지 않았다면 쓰레기 값을 만지게 된다. 토대를 먼저 만들고 그 위에 얹는 순서여야 한다.

[18편](/posts/(18)Constructor/)의 `: this()`가 같은 클래스 안의 다른 생성자를 부르는 것이었다면, `: base()`는 부모 생성자를 부른다. 둘 다 본문보다 먼저 실행된다.

## base(100) 으로 어느 생성자를 부를지 고른다

```c#
public Knight() : base(100)
```

`Player`에는 생성자가 둘 있다. `base(100)`이라고 썼으니 `Player(int hp)` 쪽이 불리고, 그래서 `hp`가 100이 된다. 출력에도 "Player hp 생성자 호출!"이 찍힌다.

`base()`를 아예 안 쓰면 컴파일러가 `base()`를 자동으로 넣는다. 즉 **부모의 인자 없는 생성자가 항상 불린다.**

```c#
public Knight()                 // : base() 가 숨어 있다
{
    Console.WriteLine("Knight 생성자 호출!");
}
```

`Mage`와 `Archer`처럼 생성자를 아예 안 쓴 경우도 마찬가지다. 컴파일러가 만들어준 기본 생성자가 `base()`를 부른다.

## 부모에 기본 생성자가 없으면 자식이 컴파일되지 않는다

이게 실제로 걸렸던 부분이다. `Player`에서 인자 없는 생성자를 지워봤다.

```c#
class Player
{
    public Player(int hp) { this.hp = hp; }    // 이것만 남김
}

class Mage : Player { }     // 컴파일 에러
```

```text
'Player'에 0개의 인수를 사용하는 생성자가 없습니다.
```

`Mage`의 자동 생성자가 `base()`를 부르려는데 그런 생성자가 없다. [18편](/posts/(18)Constructor/)에서 "생성자를 하나라도 만들면 기본 생성자가 사라진다"고 적은 게 여기서 연쇄적으로 터진다.

`Mage`에 생성자를 직접 만들어 `base(100)`처럼 넘겨주면 해결된다.

```c#
class Mage : Player
{
    public Mage() : base(50) { }
}
```

부모 클래스를 고쳤을 뿐인데 자식들이 전부 깨지는 걸 보고, 상속이 생각보다 강한 결합이라는 걸 알았다.

## 상속받아도 못 쓰는 게 있다

`Player`의 필드가 전부 `public`이라 자식에서 자유롭게 쓸 수 있다. `private`이면 물려받기는 하지만 **접근은 못 한다.**

```c#
class Player { private int secret; }
class Knight : Player
{
    void Test() { secret = 1; }   // 컴파일 에러
}
```

메모리에는 존재하는데 자식이 손을 못 댄다. 자식에게만 열어주려면 `protected`를 쓴다. 이건 [21편](/posts/(21)Encapsulation/)에서 다룬다.

생성자도 상속되지 않는다. `Player(int hp)`가 있어도 `new Knight(100)`은 안 된다. 자식에서 같은 형태를 다시 만들어야 한다.

## C#은 클래스를 하나만 상속한다

```c#
class Knight : Player, Weapon    // 컴파일 에러
```

C++와 달리 부모 클래스는 하나뿐이다. 여러 개를 물려받으면 같은 이름의 멤버가 겹칠 때 어느 쪽인지 정할 수 없는 문제가 생기는데, C#은 아예 막아버렸다.

기능을 여러 갈래로 붙이고 싶으면 인터페이스를 쓴다. 인터페이스는 여러 개를 구현할 수 있다. [31편](/posts/(31)Interface/)에서 나온다.

```c#
class Knight : Player, IAttackable, IMovable    // 이건 된다
```

## 상속을 언제 쓰나

처음엔 코드 중복을 없애는 도구로만 봤는데, 그것만으로 상속을 결정하면 나중에 꼬인다.

기준은 **"자식이 부모의 한 종류인가"** 였다. 기사는 플레이어의 한 종류다. 그래서 `Knight : Player`가 자연스럽다.

반대로 "기사는 무기를 가진다"를 상속으로 만들면 어색해진다.

```c#
class Knight : Weapon { }     // 기사가 무기의 한 종류인가? 아니다
class Knight { Weapon weapon; }   // 이게 맞다
```

가진 것은 필드로 두고, 종류인 것만 상속한다. 상속이 아니라 포함으로 푸는 경우가 실제로는 더 많았다.

상속 깊이가 깊어지는 것도 조심하게 됐다. `Knight : Player : Character : Entity`처럼 되면 어떤 필드가 어디서 왔는지 찾으려고 계속 위로 올라가야 한다.

## 남아 있는 문제

`Move`가 `Player`에 있어서 기사든 법사든 똑같이 "Player Move"를 찍는다. 직업마다 다르게 움직여야 하는데 지금은 방법이 없다.

`Knight`에 `Move`를 다시 만들면 어떻게 되는지, 그리고 `Player` 변수에 `Knight`를 담았을 때 어느 쪽이 불리는지가 [22편](/posts/(22)ClassTypeConv/)과 [23편](/posts/(23)Polymorphism/)의 주제다.

## 정리하면

- `class 자식 : 부모`로 공통 부분을 물려받는다. 본문이 비어 있어도 부모의 멤버를 다 갖는다
- 생성자는 부모가 먼저, 자식이 나중에 실행된다
- `base(...)`로 부모의 어느 생성자를 부를지 고른다. 안 쓰면 `base()`가 자동으로 들어간다
- 부모에 인자 없는 생성자가 없으면 자식이 컴파일되지 않는다
- `private` 멤버는 물려받아도 자식이 접근할 수 없고, 생성자는 상속되지 않는다
- 클래스 상속은 하나만 된다. 여러 갈래는 인터페이스로 붙인다
- "가진다"가 아니라 "한 종류다"일 때만 상속한다
