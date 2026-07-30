---
title: "(C#) 18. 생성자"
description: "객체를 만들 때 초기값을 채우는 생성자. this()로 생성자끼리 연결하는 방법과 실행 순서, 생성자를 하나라도 만들면 기본 생성자가 사라지는 것, this로 이름 가림을 푸는 것을 정리했다."
date: 2022-03-22 10:00:00 +0900
slug: '(18)Constructor'
categories: [Dev, CSharp]
series: csharp
series_order: 18
tags: [csharp, unity, oop, constructor, this]
---
## 만들자마자 쓸 수 있는 상태로

[17편](/posts/(17)StartofOOP/)에서는 객체를 만든 뒤 필드를 하나씩 채웠다.

```c#
Knight knight = new Knight();
knight.hp = 100;
knight.attack = 10;
```

빠뜨리기 쉽다. `attack`을 안 채우면 0인 채로 돌아다닌다. 객체를 만드는 시점에 반드시 실행되는 코드가 있으면 그 자리에서 채울 수 있다. 그게 생성자다.

```c#
using System;

namespace Constructor
{
    class Program
    {
        class Knight
        {
            public int hp;
            public int attack;

            public Knight()
            {
                hp = 100;
                attack = 10;
                Console.WriteLine("생성자 호출!");
            }

            public Knight(int hp) : this()
            {
                this.hp = hp;
                Console.WriteLine("int 생성자 호출!");
            }

            public Knight(int hp, int attack)
            {
                this.hp = hp;
                this.attack = attack;
                Console.WriteLine("int, int 생성자 호출!");
            }
        }
        static void Main(string[] args)
        {
            Knight knight = new Knight(50, 5);
        }
    }
}
```

생성자는 **이름이 클래스와 같고 반환형이 없다.** `void`도 안 쓴다. 이 두 가지로 컴파일러가 생성자임을 안다.

## 생성자도 오버로딩된다

세 개가 있고 인자에 따라 골라진다. [12편](/posts/(12)overloading/)에서 본 규칙이 그대로 적용된다.

```c#
new Knight()          // 첫 번째
new Knight(50)        // 두 번째
new Knight(50, 5)     // 세 번째
```

`new Knight(50, 5)`를 부르면 "int, int 생성자 호출!"만 찍힌다. 세 번째만 실행된다.

## this() 로 생성자를 이어 붙이기

두 번째 생성자에 붙은 `: this()`가 이 편에서 새로 나온 문법이다.

```c#
public Knight(int hp) : this()
{
    this.hp = hp;
    Console.WriteLine("int 생성자 호출!");
}
```

"본문을 실행하기 **전에** 기본 생성자를 먼저 부른다"는 뜻이다. `new Knight(50)`을 부르면 순서가 이렇다.

```text
생성자 호출!         <- this() 로 불린 기본 생성자
int 생성자 호출!     <- 본인 본문
```

결과적으로 `hp`는 100이 됐다가 50으로 덮어써지고, `attack`은 기본 생성자가 넣은 10이 남는다.

이게 없으면 `attack`이 0이 된다. 중복을 없애면서 초기화를 빠뜨리지 않는 방법이다.

주의할 점은 **본문보다 먼저 실행된다**는 것이다. 기본 생성자가 나중에 도는 게 아니라 먼저 돈다. 순서를 반대로 생각하면 값이 왜 덮어써지는지 헷갈린다.

세 번째 생성자에는 `: this()`가 없어서 기본 생성자가 안 불린다. 대신 두 필드를 다 채우니 문제가 없다. 이런 식으로 어떤 생성자는 연결하고 어떤 건 안 하면 나중에 헷갈리므로, 초기화를 한 곳에 모으는 편이 낫다.

```c#
public Knight() : this(100, 10) { }
public Knight(int hp) : this(hp, 10) { }
public Knight(int hp, int attack)      // 여기 하나만 실제 초기화
{
    this.hp = hp;
    this.attack = attack;
}
```

인자가 가장 많은 생성자로 모으는 방향이다. 초기화 코드가 한 곳에만 있으니 필드를 추가할 때 한 군데만 고치면 된다.

## this 로 이름 가림 풀기

```c#
public Knight(int hp)
{
    this.hp = hp;
}
```

매개변수 이름과 필드 이름이 둘 다 `hp`다. 그냥 `hp`라고 쓰면 **가까운 쪽인 매개변수**를 가리킨다. 필드를 가리키려면 `this.`를 붙여야 한다.

`this.` 없이 `hp = hp;`라고 쓰면 매개변수에 자기 자신을 대입하는 것이라 아무 일도 안 일어난다. 컴파일은 되고 경고만 나온다.

이름을 다르게 지으면 `this`가 필요 없다.

```c#
public Knight(int initialHp) { hp = initialHp; }
```

다만 C#에서는 생성자 매개변수를 필드와 같은 이름으로 짓고 `this.`를 붙이는 게 관례로 굳어져 있다. 매개변수가 어느 필드에 대응되는지 바로 보이기 때문이다.

## 생성자를 하나라도 만들면 기본 생성자가 사라진다

[17편](/posts/(17)StartofOOP/)에서 `Mage`는 생성자를 안 만들었는데도 `new Mage()`가 됐다. 생성자를 하나도 안 쓰면 컴파일러가 인자 없는 것을 자동으로 만들어준다.

그런데 생성자를 하나라도 직접 만들면 자동 생성이 멈춘다.

```c#
class Knight
{
    public int hp;
    public Knight(int hp) { this.hp = hp; }
}

Knight k = new Knight();   // 컴파일 에러
```

인자 있는 생성자만 만들었더니 `new Knight()`가 안 되는 상황을 처음엔 이해 못 했다. 규칙을 알고 나면 오히려 자연스럽다. "이 클래스는 반드시 `hp`를 받아야 한다"는 의도를 강제할 수 있다는 뜻이다.

인자 없는 것도 허용하려면 직접 써주면 된다.

`struct`는 다르다. 인자 없는 생성자가 항상 존재하고 모든 필드를 0으로 만든다. C# 10 이전에는 직접 정의할 수도 없었다.

## 필드 초기화와 순서

필드는 선언하는 자리에서 바로 값을 줄 수 있다.

```c#
class Knight
{
    public int hp = 100;
    public int attack = 10;

    public Knight() { }
}
```

실행 순서는 **필드 초기화가 먼저, 생성자 본문이 나중**이다. 그래서 생성자에서 값을 넣으면 그게 최종값이 된다.

간단한 기본값은 필드 쪽에 두는 게 읽기 좋았다. 생성자가 여러 개일 때 각각에 같은 값을 반복해 쓰지 않아도 된다.

## 정리하면

- 생성자는 이름이 클래스와 같고 반환형이 없다
- 생성자도 오버로딩되고, 인자에 맞는 하나만 실행된다
- `: this()`로 다른 생성자를 먼저 부를 수 있다. 본문보다 **먼저** 실행된다
- 초기화 코드는 인자가 가장 많은 생성자 하나에 모으고 나머지는 거기로 연결한다
- 매개변수와 필드 이름이 같으면 `this.`로 필드를 가리킨다
- 생성자를 하나라도 만들면 컴파일러가 만들어주던 기본 생성자가 사라진다
- 필드 초기화가 생성자 본문보다 먼저 실행된다
