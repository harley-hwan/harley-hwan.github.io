---
title: "(C#) 22. 클래스 형식 변환"
description: "자식을 부모 타입에 담는 건 항상 되는데 반대는 조건부다. 캐스팅·is·as 세 가지 방법의 실패 방식이 어떻게 다른지, C# 7의 패턴 매칭으로 어떻게 줄어드는지 정리했다."
date: 2022-03-23 10:00:00 +0900
slug: '(22)ClassTypeConv'
categories: [Dev, CSharp]
series: csharp
series_order: 22
tags: [csharp, unity, oop, class, type, conversion, pattern-matching]
---
## 부모 타입으로 받으면 다 받을 수 있다

[20편](/posts/(20)Inheritance/)에서 `Knight`, `Mage`, `Archer`가 전부 `Player`를 상속했다. 그러면 함수 하나로 셋을 다 받을 수 있다.

```c#
using System;

namespace ClassTypeConv
{
    // 클래스 형식 변환
    // OOP (은닉성 / 상속성 / 다형성)

    class Player
    {
        protected int hp;
        protected int attack;
    }

    class Knight : Player
    {

    }

    class Mage : Player
    {
        public int mp;
    }

    class Program
    {
        static void EnterGame(Player player)
        {
            //bool isMage = (player is Mage);
            //if (isMage)
            //{
            //    Mage mage = (Mage)player;
            //    mage.mp = 10;
            //}

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

            // Mage type -> Player type 가능
            // Player type -> Mage type ?   Case by case 

            EnterGame(knight);
        }
    }
}
```

주석에 적힌 두 줄이 이 편의 요지다.

## 한 방향은 항상 되고 반대는 아니다

```c#
Player p = new Knight();     // 항상 된다
```

`Knight`는 `Player`가 가진 것을 전부 갖고 있다. 그래서 `Player`로 다뤄도 부족한 게 없다. 캐스팅도 필요 없다. 이걸 업캐스팅이라고 한다.

```c#
Player p = new Knight();
Mage m = (Mage)p;            // 실행 중 예외
```

반대는 다르다. `Player` 변수에 실제로 들어 있는 게 `Mage`인지 `Knight`인지 알 수 없다. `Knight`가 들어 있는데 `Mage`로 다루려 하면 `mp` 같은 게 없어서 곤란해진다.

여기서 헷갈렸던 게 하나 있다. **변수 타입이 바뀌어도 객체 자체는 안 바뀐다.** `Player p = new Knight();`에서 힙에 있는 건 여전히 `Knight`다. `p`라는 창으로 볼 때 `Player` 부분만 보이는 것뿐이다.

그래서 다운캐스팅은 "바꾸는" 게 아니라 "원래 그거였는지 확인하는" 작업이다.

## 세 가지 방법과 실패 방식

### 캐스팅

```c#
Mage mage = (Mage)player;
```

아니면 `InvalidCastException`이 난다. 확실히 `Mage`일 때만 쓴다. 틀렸다는 걸 즉시 알 수 있는 게 장점이라, 절대 아닐 리 없는 자리에서는 오히려 이게 낫다.

### is

```c#
bool isMage = (player is Mage);
```

맞는지만 알려준다. 예외도 안 나고 변환도 안 한다. 검사한 뒤에 다시 캐스팅해야 해서, 주석 처리된 코드처럼 **타입 검사를 두 번** 하게 된다.

### as

```c#
Mage mage = (player as Mage);
if (mage != null) { }
```

실패하면 예외 대신 `null`을 준다. 검사가 한 번뿐이라 `is` + 캐스팅보다 낫다.

주의할 점은 `as`가 **참조 타입과 nullable에만** 된다는 것이다. `int` 같은 값 형식에는 못 쓴다. `null`을 돌려줄 방법이 없기 때문이다.

```c#
object o = 5;
int n = o as int;      // 컴파일 에러
int? n2 = o as int?;   // 이건 된다
```

## C# 7 부터는 한 줄이다

`as` 다음에 `null` 검사를 하는 형태가 워낙 흔해서 문법이 생겼다.

```c#
if (player is Mage mage)
{
    mage.mp = 10;
}
```

검사와 변수 선언이 한 번에 끝난다. `mage`는 `if` 블록 안에서 쓸 수 있고, 조건이 참일 때만 유효하니 `null` 검사도 필요 없다.

지금 새로 짠다면 이 형태를 쓴다. `as` + `null` 검사는 그 이전 방식이다.

여러 타입을 나눠 처리해야 하면 `switch`에도 쓸 수 있다.

```c#
switch (player)
{
    case Mage m:   m.mp = 10; break;
    case Knight k: /* ... */  break;
    default:                  break;
}
```

[5편](/posts/(5)switch/)에서 본 `switch`가 값이 아니라 타입으로도 갈라진다.

## 이 코드는 아무 일도 안 한다

```c#
EnterGame(knight);
```

`knight`를 넘기니 `player as Mage`가 `null`이고, `mp = 10`은 실행되지 않는다. 예제가 의도한 대로 "안전하게 걸러진" 상태다.

`EnterGame(mage)`로 바꿔야 `mp`가 설정된다. 두 경우를 다 넣어보면 `as`가 무엇을 하는지 확실해진다.

## 다운캐스팅이 많아지면 설계를 의심한다

이 코드를 보면 `EnterGame`이 "법사면 마나를 채운다"를 하고 있다. 직업이 늘어나면 이런 게 계속 붙는다.

```c#
if (player is Mage m)      { m.mp = 10; }
else if (player is Knight k) { k.shield = 5; }
else if (player is Archer a) { a.arrows = 30; }
```

새 직업을 추가할 때마다 이 함수를 고쳐야 한다. 고칠 곳이 여러 군데면 하나를 빠뜨린다.

각자 자기 방식으로 준비하게 하면 이 분기가 사라진다.

```c#
class Player { public virtual void OnEnterGame() { } }
class Mage : Player { public override void OnEnterGame() { mp = 10; } }

static void EnterGame(Player player)
{
    player.OnEnterGame();     // 누구든 알아서 한다
}
```

이게 [23편](/posts/(23)Polymorphism/)의 다형성이다. 다운캐스팅으로 타입을 확인하는 코드가 반복되면 다형성으로 풀 수 있는지 먼저 보게 됐다.

물론 다운캐스팅이 필요한 자리도 있다. 부모가 몰라도 되는 기능을 특정 자식만 갖는 경우가 그렇다. 부모에 `OnEnterGame` 같은 걸 계속 추가하면 부모가 자식들의 사정을 다 알게 되어 그것대로 나빠진다.

## is 와 GetType 은 다르다

```c#
Player p = new Knight();

Console.WriteLine(p is Player);           // True
Console.WriteLine(p.GetType() == typeof(Player));   // False
```

`is`는 "그 타입으로 취급할 수 있는가"를 묻는다. `Knight`는 `Player`이기도 하니 참이다.

`GetType()`은 실제 타입을 정확히 돌려준다. `Knight`이지 `Player`가 아니다.

상속을 포함해서 판단하려면 `is`, 정확히 그 타입인지 봐야 하면 `GetType()`이다. 대부분은 `is`가 맞았다.

## 정리하면

- 자식을 부모 타입에 담는 건 항상 되고 캐스팅도 필요 없다
- 부모를 자식으로 되돌리는 건 실제 객체가 그것일 때만 된다. 변수 타입이 바뀌어도 객체는 안 바뀐다
- `(Mage)`는 실패 시 예외, `is`는 검사만, `as`는 실패 시 `null`
- `as`는 참조 타입과 nullable에만 쓸 수 있다
- C# 7의 `if (player is Mage mage)`가 검사와 선언을 한 번에 처리한다
- 타입을 확인해 갈라지는 코드가 반복되면 다형성으로 풀 수 있는지 본다
- `is`는 상속을 포함하고 `GetType()`은 정확한 타입만 본다
