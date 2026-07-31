---
title: "(C#) 23. 다형성 (Polymorphism)"
description: "부모 타입으로 불러도 자식 구현이 실행되게 하는 virtual/override. virtual을 빼면 변수 타입에 따라 다른 함수가 불리는 것, base와 sealed, abstract까지 확인했다."
date: 2022-03-23 10:00:00 +0900
slug: '(23)Polymorphism'
categories: [Dev, CSharp]
series: csharp
series_order: 23
tags: [csharp, unity, oop, polymorphism, virtual, override, abstract]
---
## 부모 타입으로 불러도 자식 것이 실행되게

[22편](/posts/(22)ClassTypeConv/) 마지막에 적었듯이, 타입을 확인해서 갈라지는 코드는 직업이 늘어날 때마다 고쳐야 한다. 각자 자기 방식으로 동작하게 만들면 그 분기가 사라진다.

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

![실행 결과](/assets/img/posts/23-polymorphism/001-159215772-c082d966-db91-4515-b620-f076fe01eaf9.png)

## virtual 과 override

부모에 `virtual`, 자식에 `override`를 붙인다. 둘 다 있어야 한다.

```c#
public virtual void Move()    // 부모: 자식이 바꿔도 된다
public override void Move()   // 자식: 바꾸겠다
```

`virtual` 없이 자식에서 `override`를 쓰면 컴파일 에러가 난다. 부모가 허락한 것만 재정의할 수 있다는 뜻이다.

C#이 `override` 키워드를 **필수로** 요구하는 것도 좋은 설계다. C++는 안 붙여도 되는데, 그러다 보니 부모 함수 이름이 바뀌었을 때 자식이 조용히 별개 함수가 되는 사고가 난다. C#은 `override`를 붙였는데 부모에 그런 함수가 없으면 컴파일 에러다.

## 오버로딩과 오버라이딩

주석에 나란히 적혀 있는데 완전히 다른 것이다.

| | 오버로딩 | 오버라이딩 |
| :--- | :--- | :--- |
| 무엇 | 같은 이름, 다른 매개변수 | 같은 시그니처를 자식이 재정의 |
| 결정 시점 | 컴파일 타임 | 실행 타임 |
| 관계 | 같은 클래스 안 | 부모-자식 |

[12편](/posts/(12)overloading/)의 오버로딩은 인자를 보고 컴파일러가 고른다. 오버라이딩은 실행할 때 **객체의 실제 타입**을 보고 정해진다.

이 차이가 다형성의 핵심이다.

```c#
Player p = new Mage();
p.Move();          // "Mage 이동!"
```

변수 타입은 `Player`인데 `Mage`의 것이 불린다. 컴파일 시점에는 `p`에 뭐가 들어올지 모르니 결정할 수가 없고, 실행 시점에 객체를 보고 정한다.

`EnterGame(Player player)`가 이 덕분에 성립한다. 어떤 직업이 들어오든 `player.Move()` 한 줄이면 각자의 이동이 실행된다.

## 이 예제에서 다형성이 안 보인다

돌려보니 출력이 이랬다.

```text
Player 이동!
Knight 이동!
```

`knight.Move()`만 부르고 있어서다. `knight`는 `Knight` 타입이라 어차피 `Knight.Move`가 불린다. **다형성이 없어도 같은 결과**다.

정작 다형성을 보여주는 줄은 주석 처리되어 있다.

```c#
//EnterGame(mage);
```

이걸 풀면 `Player` 타입 매개변수로 받았는데 `Mage 이동!`이 나온다. 그게 이 편의 요점이다.

둘을 나란히 넣어보면 확실해진다.

```c#
EnterGame(knight);   // Player 이동! / Knight 이동!
EnterGame(mage);     // Mage 이동!
```

같은 함수에 같은 한 줄인데 결과가 다르다.

## base.Move()

```c#
public sealed override void Move()
{
    base.Move();
    Console.WriteLine("Knight 이동!");
}
```

`base.Move()`는 부모 구현을 부른다. 그래서 "Player 이동!"이 먼저 찍힌다.

부모 동작을 **대체**할지 **확장**할지에 따라 넣거나 뺀다. `Knight`는 부모 것을 하고 자기 것을 더한다. `Mage`는 `base.Move()`가 없어서 부모 동작을 완전히 대체한다.

[20편](/posts/(20)Inheritance/)의 `base(100)`은 생성자를 부르는 것이었고, 여기 `base.Move()`는 일반 함수를 부르는 것이다. 같은 키워드지만 쓰임이 다르다.

## sealed

```c#
public sealed override void Move()
```

`Knight`가 재정의한 `Move`를 **더 이상 못 바꾸게** 잠근다. 그래서 `SuperKnight`의 주석 처리된 코드는 풀면 컴파일 에러다.

```text
'SuperKnight.Move()': 상속된 멤버 'Knight.Move()'는 sealed이므로 재정의할 수 없습니다.
```

주석에 "사용하는 경우 거의 없음"이라고 적혀 있는데 동의한다. 다만 쓸 자리가 있긴 하다. 재정의하면 클래스의 규칙이 깨지는 함수를 잠글 때다.

`sealed`는 클래스 자체에도 붙는다. 그러면 상속 자체가 안 된다. `string`이 `sealed`다.

```c#
sealed class Knight : Player { }    // 더 이상 상속 불가
```

## virtual 을 빼면 어떻게 되나

이게 제일 헷갈렸던 부분이다. `virtual`/`override` 없이 자식에 같은 이름 함수를 만들면 컴파일은 된다. 경고만 나온다.

```c#
class Player { public void Move() { Console.WriteLine("Player"); } }
class Mage : Player { public new void Move() { Console.WriteLine("Mage"); } }
```

이건 재정의가 아니라 **가리기**다. 부모 함수는 그대로 있고 자식이 같은 이름으로 새 함수를 만든 것이다. `new` 키워드로 "일부러 가린다"고 표시한다.

결과가 이렇게 갈린다.

```c#
Mage m = new Mage();
Player p = m;          // 같은 객체다

m.Move();              // "Mage"
p.Move();              // "Player"
```

같은 객체인데 **변수 타입에 따라 다른 함수**가 불린다. `virtual`이었다면 둘 다 "Mage"였다.

이 차이를 모르면 "분명 재정의했는데 부모 것이 불린다"에서 한참 헤맨다. 자식에 같은 이름 함수를 만들었는데 컴파일러가 `new`를 쓰라고 경고하면, 대부분은 `virtual`을 빠뜨린 것이다.

## abstract

부모에 기본 구현이 딱히 없는 경우가 있다. `Player.Move()`가 "Player 이동!"을 찍는 게 의미가 있나 싶으면, 구현 없이 선언만 둘 수 있다.

```c#
abstract class Player
{
    public abstract void Move();     // 본문이 없다
}

class Knight : Player
{
    public override void Move() { Console.WriteLine("Knight 이동!"); }
}
```

`abstract` 함수가 있으면 클래스도 `abstract`여야 하고, 그 클래스는 `new`로 만들 수 없다. 자식은 반드시 구현해야 한다. 안 하면 컴파일 에러다.

`virtual`은 "바꿔도 된다", `abstract`는 "반드시 바꿔라"다. 직업을 추가하면서 `Move` 구현을 잊는 실수를 막고 싶으면 `abstract`가 맞다.

## 비용

`virtual` 함수는 호출할 때 실제 타입을 확인하는 과정이 들어간다. 함수 주소를 표에서 찾아 가는 방식이라 일반 호출보다 아주 약간 느리고, 인라인 최적화가 어려워진다.

매 프레임 수만 번 부르는 자리가 아니면 신경 쓸 수준이 아니었다. 다만 C#이 기본을 비-virtual로 둔 이유가 이것이다. 필요할 때만 붙이라는 것이다.

## 정리하면

- 부모에 `virtual`, 자식에 `override`. 둘 다 있어야 재정의가 된다
- 오버로딩은 컴파일 타임에 인자로, 오버라이딩은 실행 타임에 실제 객체 타입으로 정해진다
- 부모 타입 변수에 담아도 자식 구현이 불린다. 그래서 타입 검사 분기가 사라진다
- `base.Move()`는 부모 구현을 부른다. 대체할지 확장할지에 따라 넣고 뺀다
- `sealed override`는 더 이상 재정의를 막고, `sealed class`는 상속 자체를 막는다
- `virtual` 없이 같은 이름 함수를 만들면 가리기가 되어 **변수 타입**에 따라 다른 함수가 불린다
- 반드시 구현하게 하려면 `abstract`
