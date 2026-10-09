---
title: "(C#) 9. 코드의 흐름 제어 (break, continue)"
description: "소수 판정으로 break를, 배수 찾기로 continue를 확인했다. 1을 넣으면 소수로 나오는 버그, while에서 continue가 무한 루프가 되는 이유, 중첩 루프에서 break가 하나만 빠져나오는 문제를 정리했다."
date: 2022-03-21 10:00:00 +0900
slug: '(9)break_continue'
categories: [Dev, CSharp]
series: csharp
series_order: 9
tags: [csharp, unity, codeflowcontrol, break, continue, prime]
---
## 반복을 도중에 끊기

[8편](/posts/(8)for/)까지는 루프가 끝까지 도는 것만 봤다. 그런데 답을 이미 찾았는데 계속 도는 건 낭비다. 반대로 어떤 회차만 건너뛰고 싶을 때도 있다.

```c#
using System;

namespace break_continue
{
    class Program
    {
        static void Main(string[] args)
        {
            int num = 97;   // 1, 97로만 나뉘는 숫자

            bool isPrime = true;

            //////////////// break
            for (int i = 2; i < num; i++)
            {
                if ((num % i) == 0)
                {
                    //Console.WriteLine("소수가 아닙니다!");
                    isPrime = false;
                    break;
                }
            }
            //Console.WriteLine("소수입니다!");
            if (isPrime)
                Console.WriteLine("소수입니다!");
            else
                Console.WriteLine("소수가 아닙니다!");

            //////////////// continue;
            for (int i = 1; i <= 100; i++)
            {
                if ((i % 3) != 0)
                    continue;

                Console.WriteLine($"3으로 나뉘는 숫자 발견 : {i}");
            }
        }
    }
}
```

## break 는 루프를 끝낸다

나누어떨어지는 수를 하나라도 찾으면 그 순간 소수가 아닌 게 확정된다. 나머지를 더 볼 이유가 없다.

주석 처리해둔 코드가 흥미롭다. 처음엔 `break` 자리에서 바로 "소수가 아닙니다!"를 찍으려 했던 것 같은데, 그러면 루프 밖의 "소수입니다!"와 나란히 둘 수가 없다. 루프가 끝난 뒤에는 왜 끝났는지(다 돌아서인지 `break` 때문인지)를 알 방법이 없기 때문이다.

그래서 `isPrime` 같은 **플래그 변수**가 필요해진다. "`break`로 나왔다"는 사실을 변수에 기록해두고 밖에서 판단한다. 이 패턴은 계속 나온다.

함수로 빼면 플래그가 필요 없어진다. `return`이 루프도 함수도 한 번에 끝내기 때문이다.

```c#
static bool IsPrime(int num)
{
    for (int i = 2; i < num; i++)
    {
        if (num % i == 0) return false;
    }
    return true;
}
```

훨씬 짧고, "찾으면 즉시 아니다"라는 의도가 그대로 드러난다.

## 1을 넣으면 소수라고 나온다

위 코드에 `num = 1`을 넣어봤다.

```text
소수입니다!
```

1은 소수가 아니다. 원인은 단순하다. `for (int i = 2; i < 1; i++)`는 **한 번도 돌지 않는다.** 그러면 `isPrime`이 초기값 `true` 그대로 남는다.

0이나 음수도 같다. 루프가 안 돌아서 전부 소수가 된다.

루프가 한 번도 안 도는 경우를 따로 생각 안 했던 게 원인이다. 경계값을 넣어보기 전에는 안 보인다.

```c#
static bool IsPrime(int num)
{
    if (num < 2) return false;      // 0, 1, 음수
    for (int i = 2; i < num; i++)
        if (num % i == 0) return false;
    return true;
}
```

## 제곱근까지만 보면 된다

97을 판정하는데 2부터 96까지 95번을 돈다. 그럴 필요가 없다.

`num = a * b`로 나눠떨어진다면 둘 중 하나는 반드시 √num 이하다. 둘 다 √num보다 크면 곱이 num보다 커지기 때문이다. 그러니 √num까지만 확인하면 충분하다.

```c#
for (int i = 2; i * i <= num; i++)
    if (num % i == 0) return false;
```

97이면 `i * i <= 97`이라 `i`가 9까지만 돈다. 95번이 8번으로 줄었다.

`i * i <= num`으로 쓴 이유는 `Math.Sqrt`를 부르지 않기 위해서다. 실수 연산이 들어가면 경계에서 오차가 생길 수 있고, 매 회차마다 부르면 느리다. 다만 `num`이 아주 크면 `i * i`가 오버플로할 수 있다. [1편](/posts/(1)DataControl/)에서 본 그 문제다. 그때는 `i <= num / i`로 바꾼다.

## continue 는 이번 회차만 건너뛴다

`continue`를 만나면 아래 코드를 건너뛰고 다음 회차로 간다.

```c#
for (int i = 1; i <= 100; i++)
{
    if ((i % 3) != 0)
        continue;

    Console.WriteLine($"3으로 나뉘는 숫자 발견 : {i}");
}
```

이건 이렇게도 쓸 수 있다.

```c#
for (int i = 1; i <= 100; i++)
{
    if ((i % 3) == 0)
        Console.WriteLine($"3으로 나뉘는 숫자 발견 : {i}");
}
```

둘 다 같은 결과다. 본문이 한 줄이면 아래쪽이 더 읽기 쉽다.

`continue`가 이득인 건 **거를 조건이 여러 개**일 때다. 조건마다 `continue`로 걸러내면 중첩이 안 생긴다.

```c#
foreach (var monster in monsters)
{
    if (monster == null) continue;
    if (!monster.IsAlive) continue;
    if (monster.Distance > range) continue;

    Attack(monster);
}
```

[4편](/posts/(4)If_else/)에서 본 가드 절과 같은 생각이다. `return` 대신 `continue`를 쓰는 것뿐이다.

## while 에서 continue 는 무한 루프가 되기 쉽다

`for`에서는 `continue`를 해도 반복식 `i++`가 실행된다. 그래서 안전하다.

`while`은 다르다. 값을 올리는 코드가 본문 안에 있으니 `continue`가 그걸 건너뛴다.

```c#
int i = 0;
while (i < 10)
{
    if (i % 2 == 0) continue;   // i++ 를 건너뛴다
    Console.WriteLine(i);
    i++;
}
```

`i`가 0일 때 `continue`가 걸리고, 다시 조건을 보면 여전히 0이다. 영원히 멈추지 않는다.

`for`를 쓰거나, 값을 올리는 코드를 `continue`보다 위에 두면 된다.

```c#
while (i < 10)
{
    int cur = i;
    i++;                        // 먼저 올린다
    if (cur % 2 == 0) continue;
    Console.WriteLine(cur);
}
```

`for`로 쓸 수 있으면 `for`가 낫다는 이유가 여기에도 있다.

## 중첩 루프에서 break 는 하나만 빠져나온다

이게 나중에 걸렸던 부분이다.

```c#
for (int y = 0; y < 10; y++)
{
    for (int x = 0; x < 10; x++)
    {
        if (map[y, x] == target)
            break;      // 안쪽 for 만 빠져나온다
    }
    // 여기로 온다. 바깥 루프는 계속 돈다
}
```

찾았는데도 바깥 루프가 계속 돈다. 방법이 몇 가지 있다.

플래그를 하나 두는 방식.

```c#
bool found = false;
for (int y = 0; y < 10 && !found; y++)
    for (int x = 0; x < 10; x++)
        if (map[y, x] == target) { found = true; break; }
```

함수로 빼서 `return`하는 방식. 이게 제일 깔끔했다.

```c#
static (int y, int x) Find(int[,] map, int target)
{
    for (int y = 0; y < 10; y++)
        for (int x = 0; x < 10; x++)
            if (map[y, x] == target) return (y, x);
    return (-1, -1);
}
```

C#에는 `goto`도 있어서 라벨로 한 번에 빠져나올 수 있다. 문법상 되지만 흐름을 쫓기 어려워져서 쓰지 않게 됐다.

## switch 안의 break 는 루프를 안 끝낸다

[5편](/posts/(5)switch/)의 `break`와 여기 `break`가 같은 키워드라 헷갈리는 지점이 있다.

```c#
while (true)
{
    switch (command)
    {
        case "quit":
            break;      // switch 를 빠져나올 뿐, while 은 계속 돈다
    }
}
```

루프 안에 `switch`가 있으면 `break`는 **가장 가까운 것**, 즉 `switch`를 끝낸다. 루프를 끝내려면 플래그를 쓰거나 `return`하거나, 루프 자체를 함수로 빼야 한다.

콘솔 메뉴를 만들 때 실제로 이걸로 한 번 막혔다. `quit`을 쳐도 프로그램이 안 끝났다.

## 정리하면

- `break`는 루프를 끝내고, `continue`는 이번 회차만 건너뛴다
- 루프가 왜 끝났는지는 밖에서 알 수 없다. 플래그를 쓰거나 함수로 빼서 `return`한다
- 루프가 한 번도 안 도는 경우를 확인해야 한다. 소수 판정에서 1이 소수로 나온 원인이다
- 약수는 √n까지만 보면 된다. `i * i <= num`
- `while`에서 `continue`는 증감 코드를 건너뛰어 무한 루프가 되기 쉽다
- 중첩 루프에서 `break`는 안쪽 하나만 끝낸다. 함수로 빼는 게 제일 깔끔하다
- 루프 안 `switch`의 `break`는 `switch`만 끝낸다
