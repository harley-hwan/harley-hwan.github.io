---
title: "(C#) 21. 은닉성 (Encapsulation)"
description: "필드를 public으로 열어두면 규칙을 지킬 수 없다. private·protected·internal의 범위와 기본값, Setter를 두는 이유와 그것만으로는 부족한 경우를 정리했다."
date: 2022-03-23 10:00:00 +0900
slug: '(21)Encapsulation'
categories: [Dev, CSharp]
series: csharp
series_order: 21
tags: [csharp, unity, oop, encapsulation, access-modifier, protected]
---
## 열어두면 규칙을 못 지킨다

[17편](/posts/(17)StartofOOP/)부터 필드에 계속 `public`을 붙여왔다. 그래서 밖에서 이런 게 된다.

```c#
knight.hp = -9999;
knight.hp = 999999;
```

체력이 음수가 되거나 최대치를 넘어도 막을 방법이 없다. `Knight` 안에 아무리 규칙을 넣어도 밖에서 직접 대입해버리면 소용없다.

자동차로 치면 핸들과 페달만 밖에 두고 엔진은 덮어두는 것과 같다. 쓰는 사람이 엔진을 직접 만지면 차가 어떻게 될지 만든 사람도 보장할 수 없다.

```c#
using System;

namespace Encapsulation
{
    // OOP 은닉성 (Encapsulation)

    // 자동차
    // 핸들 패달 차문

    class Knight
    {
        // 접근 한정자
        //public protected private
        // 
        //int hp;             // dafault: private
        //private int hp;     // 공유 안함. 현재 클래스에서만 사용.
        protected int hp;     // 상속받은 클래스들만 사용가능

        private int id;
        public void SetId(int id)
        {
            this.id = id;
        }
    }

    class SuperKnight : Knight
    {
        void Test()
        {
            hp = 10;
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Knight knight = new Knight();
            knight.SetId(100);
        }
    }
}
```

## 세 가지 범위

주석에 나란히 적어둔 세 가지가 이 편의 전부다.

| 한정자 | 접근 가능한 곳 |
| :--- | :--- |
| `private` | 이 클래스 안에서만 |
| `protected` | 이 클래스 + 상속받은 클래스 |
| `public` | 어디서든 |

`hp`가 `protected`라서 `SuperKnight`의 `Test()`에서 `hp = 10;`이 통과한다. `private`으로 바꾸면 그 줄에서 컴파일 에러가 난다.

[20편](/posts/(20)Inheritance/)에서 "`private` 멤버는 물려받아도 접근할 수 없다"고 적은 게 이것이다. `protected`가 그 사이를 메운다. 밖에는 감추면서 자식에게는 열어준다.

## 아무것도 안 쓰면 private

```c#
//int hp;             // dafault: private
```

이 주석이 중요하다. C#은 **클래스 멤버의 기본 접근 수준이 `private`** 이다.

C++의 `struct`는 기본이 `public`이고 `class`는 `private`이라 헷갈렸는데, C#은 `class`든 `struct`든 멤버 기본값이 `private`이다.

기본이 닫혀 있다는 게 좋은 설계다. 열어야 하는 것만 의식적으로 열게 된다. 다만 명시적으로 `private`을 적어두는 편이 읽는 사람에게 친절해서, 나는 붙여 쓰는 쪽으로 했다.

클래스 자체의 기본값은 다르다. 네임스페이스 바로 아래 클래스는 안 적으면 `internal`이다. `public`으로 적어야 다른 어셈블리에서 보인다.

## internal 도 있다

주석에 안 적힌 게 두 개 더 있다.

- `internal`: 같은 어셈블리(프로젝트) 안에서만
- `protected internal`: 같은 어셈블리 **또는** 자식 클래스
- `private protected`: 같은 어셈블리 **이면서** 자식 클래스 (C# 7.2)

라이브러리를 DLL로 나눠 만들 때 `internal`이 유용했다. 내부 구현용 클래스를 `public`으로 열면 쓰는 쪽에서 그걸 붙잡고 코드를 짜버려서 나중에 못 바꾼다. `internal`로 두면 밖에서는 아예 안 보인다.

## Setter 를 두는 이유

```c#
private int id;
public void SetId(int id)
{
    this.id = id;
}
```

`id`를 감추고 함수로만 바꾸게 했다. 이렇게 하면 **대입 시점에 개입할 수 있다.**

```c#
public void SetId(int id)
{
    if (id < 0) throw new ArgumentOutOfRangeException(nameof(id));
    this.id = id;
    Console.WriteLine($"id 변경: {id}");
}
```

검사를 넣거나, 로그를 남기거나, 다른 값을 같이 갱신할 수 있다. 필드를 그냥 열어뒀다면 이런 걸 나중에 추가할 방법이 없다.

`this.id = id;`에서 `this.`가 필요한 이유는 [18편](/posts/(18)Constructor/)에서 본 이름 가림 때문이다.

## Setter 만으로는 부족한 경우

여기서 한 가지 짚고 넘어갈 게 있다. 값 하나마다 `SetXxx`, `GetXxx`를 만들면 코드가 금방 지저분해진다.

```c#
knight.SetHp(knight.GetHp() - 10);   // 읽기가 나쁘다
```

그리고 검사를 넣어도 이런 건 못 막는다.

```c#
knight.SetHp(50);
knight.SetMaxHp(30);   // 최대치보다 현재 체력이 큰 상태가 된다
```

값 하나씩 검사해서는 **여러 필드 사이의 관계**를 지킬 수 없다. 그래서 "체력을 설정한다"가 아니라 "피해를 입는다" 같은 행동 단위로 함수를 만드는 쪽이 낫다.

```c#
public void TakeDamage(int amount)
{
    hp = Math.Max(0, hp - amount);
    if (hp == 0) Die();
}
```

밖에서는 `hp`를 모르고 "때렸다"만 알면 된다. 규칙이 전부 클래스 안에 있으니 밖에서 깨뜨릴 수가 없다. 은닉성의 진짜 목적이 이거였다.

C#에는 `SetXxx`/`GetXxx`를 문법으로 지원하는 프로퍼티가 있어서, 단순한 값은 그쪽이 훨씬 짧다. [32편](/posts/(32)Property/)에서 다룬다.

```c#
public int Hp { get; private set; }   // 밖에서는 읽기만, 안에서는 쓰기도
```

## 무엇을 감출지 정하기

기준은 "**이 값이 바뀌면 다른 값도 같이 바뀌어야 하는가**"였다.

- 서로 무관한 단순한 데이터 → 열어도 된다. [17편](/posts/(17)StartofOOP/)에서 본 `struct`가 그런 경우다
- 다른 필드와 관계가 있거나 범위 제한이 있다 → 감추고 행동으로만 바꾸게 한다

`protected`도 생각보다 조심해야 했다. 자식에게 열어준다는 건 그 필드를 나중에 못 바꾼다는 뜻이다. 자식이 어떻게 쓰고 있는지 모르니까. 상속 계층이 커지면 `protected`가 사실상 `public`처럼 굳어진다.

## 정리하면

- `private`은 자기 클래스, `protected`는 자식까지, `public`은 어디서든
- C# 멤버의 기본 접근 수준은 `private`이다. 클래스 자체는 `internal`이다
- 같은 어셈블리 안에서만 열려면 `internal`
- `private` + Setter로 대입 시점에 검사와 로그를 넣을 수 있다
- 값 하나씩 검사해서는 필드 사이의 관계를 못 지킨다. 행동 단위 함수로 감싸는 게 낫다
- `protected`로 열어준 필드는 나중에 바꾸기 어려워진다
