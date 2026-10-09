---
title: "(C#) 12. 코드의 흐름 제어 (overloading)"
description: "같은 이름의 함수를 여러 개 두는 오버로딩과 기본값 매개변수. 반환형은 구분에 안 쓰인다는 것, 둘을 섞으면 어느 쪽이 불리는지 애매해지는 것, 기본값이 호출부에 박힌다는 것을 확인했다."
date: 2022-03-22 10:00:00 +0900
slug: '(12)overloading'
categories: [Dev, CSharp]
series: csharp
series_order: 12
tags: [csharp, unity, codeflowcontrol, overloading, default-parameter, named-argument]
---
## 하는 일이 같은데 이름을 다르게 지어야 하나

`int`를 더하는 함수와 `float`을 더하는 함수를 만들어야 한다면, `AddInt`와 `AddFloat`처럼 이름을 나눠야 할 것 같다. 그런데 하는 일이 같은데 이름이 다르면 부르는 쪽에서 매번 어느 걸 써야 하는지 신경 써야 한다.

C#은 **매개변수가 다르면 같은 이름을 여러 번** 쓸 수 있다.

```c#
using System;

namespace overloading
{
    class Program
    {
        // 함수 이름의 재사용
        static int Add(int a, int b)
        {
            Console.WriteLine("Add int 호출");
            return a + b;
        }

        static int Add(int a, int b, int c)
        {
            Console.WriteLine("Add int 호출");
            return a + b + c;
        }

        static float Add(float a, float b)
        {
            Console.WriteLine("Add float 호출");
            return a + b;
        }

        static double Add(int a, int b, int c = 0, float d = 1.0f, double e = 3.0) 
        {
            Console.WriteLine("Add int 호출");
            return a + b + c + d + e;
        }

        static void Main(string[] args)
        {
            int ret = Program.Add(2, 3);
            Console.WriteLine(ret);

            int ret2 = Program.Add(2, 3, 4);
            Console.WriteLine(ret2);

            float ret3 = Program.Add(2.0f, 3.0f);
            Console.WriteLine(ret3);

            double ret4 = Program.Add(1, 2, d: 2.0f);
            Console.WriteLine(ret4);
        }
    }
}
```

## 무엇으로 구분되는가

컴파일러가 오버로드를 구분하는 데 쓰는 건 이 셋이다.

- 매개변수의 **개수**
- 매개변수의 **타입**
- 매개변수의 **순서**

여기 **반환형은 없다.** 이걸 몰라서 한 번 막혔다.

```c#
static int   Add(int a, int b) { return a + b; }
static float Add(int a, int b) { return a + b; }   // 컴파일 에러
```

`Add(2, 3)`이라고 썼을 때 컴파일러가 어느 쪽인지 알 방법이 없다. 반환값을 어디에 담는지는 나중 일이라 판단 근거로 쓸 수 없다.

`ref`와 `out`은 시그니처에 포함된다. 그래서 `Add(int)`와 `Add(ref int)`는 공존한다. 다만 `Add(ref int)`와 `Add(out int)`는 서로 구분되지 않아 에러다.

## 실험 자체에 문제가 있었다

돌려보고 나서 알았는데, 네 함수 중 셋이 똑같이 `"Add int 호출"`을 찍는다. 어느 게 불렸는지 알 수가 없다.

메시지를 다르게 해야 실험이 성립한다.

```c#
static int Add(int a, int b)                       { Console.WriteLine("2개"); ... }
static int Add(int a, int b, int c)                { Console.WriteLine("3개"); ... }
static double Add(int a, int b, int c = 0, ...)    { Console.WriteLine("기본값"); ... }
```

이렇게 고쳐서 돌려보니 결과가 나왔다.

| 호출 | 불리는 함수 |
| :--- | :--- |
| `Add(2, 3)` | `Add(int, int)` |
| `Add(2, 3, 4)` | `Add(int, int, int)` |
| `Add(2.0f, 3.0f)` | `Add(float, float)` |
| `Add(1, 2, d: 2.0f)` | 기본값 있는 버전 |

## 오버로딩과 기본값이 겹치면

위 결과에서 눈여겨볼 게 있다. `Add(2, 3)`은 후보가 **둘**이다.

- `Add(int a, int b)`
- `Add(int a, int b, int c = 0, float d = 1.0f, double e = 3.0)` — 뒤 셋을 생략하면 호출 가능

둘 다 부를 수 있는데 컴파일러는 에러를 내지 않는다. **기본값을 생략하지 않아도 되는 쪽**을 더 좋은 후보로 보고 고른다. 그래서 `Add(int, int)`가 불린다.

`Add(2, 3, 4)`도 마찬가지로 후보가 둘이고, 3개짜리가 이긴다.

규칙이 있으니 동작은 예측 가능하다. 문제는 **읽는 사람이 이걸 모른다**는 것이다. 코드를 보고 어느 함수가 불릴지 바로 알 수 없으면, 나중에 한쪽을 고쳤을 때 왜 반영이 안 되는지 헤매게 된다.

그래서 오버로딩과 기본값 매개변수를 섞지 않는 쪽으로 정리했다. 둘 중 하나만 쓴다.

## 기본값은 호출부에 박힌다

기본값 매개변수에는 덜 알려진 함정이 하나 더 있다.

```c#
static void Attack(int damage = 10) { }

Attack();     // 컴파일 결과는 Attack(10) 이다
```

기본값은 함수 쪽이 아니라 **부르는 쪽 코드에 값이 복사되어** 들어간다. 컴파일 시점에 결정된다는 뜻이다.

같은 프로젝트 안에서는 문제가 없다. 라이브러리를 DLL로 나눠 쓸 때 걸린다. 라이브러리에서 기본값을 10에서 20으로 바꾸고 DLL만 교체하면, 이미 컴파일된 호출부는 여전히 10을 넘긴다. 라이브러리를 고쳤는데 동작이 안 바뀐다.

이 경우에는 오버로딩이 안전하다.

```c#
static void Attack()           { Attack(10); }   // 기본값이 함수 안에 있다
static void Attack(int damage) { }
```

## 명명된 인자

```c#
double ret4 = Program.Add(1, 2, d: 2.0f);
```

`c`는 건너뛰고 `d`만 지정했다. 이름을 쓰면 순서와 무관하게 원하는 것만 넘길 수 있다.

`bool`을 넘길 때 특히 유용했다.

```c#
CreateMonster(true, false, true);                              // 뭐가 뭔지 모른다
CreateMonster(isBoss: true, canFly: false, isElite: true);     // 읽힌다
```

주의할 점은 **매개변수 이름이 공개 계약의 일부가 된다**는 것이다. 이름을 바꾸면 이름으로 부르던 코드가 깨진다. 라이브러리를 만든다면 매개변수 이름도 함부로 바꾸면 안 된다.

## 암시적 변환이 끼어들 때

후보가 여러 개면 컴파일러가 "가장 잘 맞는" 것을 고른다. 정확히 일치하는 게 있으면 그게 이긴다.

```c#
static void Print(int x)    { Console.WriteLine("int"); }
static void Print(double x) { Console.WriteLine("double"); }

Print(3);      // int
Print(3.0);    // double
Print('a');    // int - char 는 int 로 변환되는 게 double 보다 가깝다
```

`Print('a')`가 `int`로 가는 게 처음엔 의외였다. `char`에서 `int`로 가는 변환이 `double`로 가는 것보다 "덜 잃는" 변환이라 우선한다.

후보가 비슷하게 잘 맞으면 모호하다는 에러가 난다.

```c#
static void F(int a, double b) { }
static void F(double a, int b) { }

F(1, 1);       // 에러: 모호한 호출입니다
```

둘 다 한 번씩 변환이 필요해서 우열을 가릴 수 없다. 이럴 땐 캐스팅으로 명시하거나 이름을 나눠야 한다.

## 언제 오버로딩을 쓰나

정리하면서 기준이 이렇게 됐다.

**쓸 만한 경우**는 같은 개념을 다른 타입이나 다른 재료로 표현할 때다. `Console.WriteLine`이 좋은 예다. `int`든 `string`이든 `bool`이든 "출력한다"는 개념 하나다.

**나누는 게 나은 경우**는 하는 일이 실제로 다를 때다. 이름이 같으면 부르는 쪽에서 무슨 일이 일어나는지 예측하기 어려워진다.

```c#
static void Save(string path)  { /* 파일로 저장 */ }
static void Save(int slotId)   { /* 서버로 전송 */ }   // 이건 이름을 나눠야 한다
```

## 정리하면

- 오버로딩은 매개변수의 개수, 타입, 순서로 구분된다. **반환형은 포함되지 않는다**
- 오버로딩과 기본값 매개변수를 섞으면 후보가 겹친다. 규칙은 있지만 읽는 사람이 알기 어렵다
- 기본값은 컴파일 시점에 호출부에 박힌다. DLL로 나눠 쓰면 값을 바꿔도 반영되지 않는다
- 명명된 인자를 쓰면 읽기 쉬워지지만, 매개변수 이름이 계약이 된다
- 정확히 맞는 후보가 있으면 그게 이기고, 우열을 못 가리면 모호하다는 에러가 난다
- 개념이 같을 때만 이름을 공유한다. 하는 일이 다르면 이름을 나눈다
