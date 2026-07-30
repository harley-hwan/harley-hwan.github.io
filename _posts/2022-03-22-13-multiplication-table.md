---
title: "(C#) 13. 구구단"
description: "이중 루프를 처음 써본 예제. 바깥과 안쪽 루프가 각각 무엇을 세는지, 루프 순서를 바꾸면 출력이 어떻게 달라지는지, 표처럼 가로로 찍으려면 무엇이 필요한지 정리했다."
date: 2022-03-22 10:00:00 +0900
slug: '(13)MultiplicationTable'
categories: [Dev, CSharp]
series: csharp
series_order: 13
tags: [csharp, unity, codeflowcontrol, multiplicationtable, nested-loop, string-interpolation]
---
## 루프 안에 루프

[8편](/posts/(8)for/)까지는 루프가 하나였다. 구구단은 "단"과 "곱하는 수" 두 축이 있어서 루프가 두 겹이 된다.

```c#
using System;

namespace ex1
{
    class Program
    {
        static void Main(string[] args)
        {
            // 구구단
            for (int i = 2; i <= 9; i++)
            {
                for (int j = 1; j <= 9; j++)
                {
                    Console.WriteLine($"{i} * {j} = {i * j}");
                }
                Console.WriteLine();
            }
        }
    }
}
```

바깥 루프가 한 번 돌 때 안쪽 루프가 9번 다 돈다. 그래서 총 8 × 9 = 72줄이 나온다.

이중 루프에서 처음에 헷갈렸던 건 **안쪽 루프의 변수가 매번 초기화된다**는 점이다. `j`는 바깥 루프가 한 바퀴 돌 때마다 다시 1부터 시작한다. `for (int j = 1; ...)`의 초기화식이 안쪽 루프에 진입할 때마다 실행되기 때문이다.

인자 없는 `Console.WriteLine()`은 줄바꿈만 한다. 안쪽 루프가 끝난 자리에 있으니 단과 단 사이에 빈 줄이 들어간다. 이 위치가 바깥 루프 안이라는 게 중요하다. 밖으로 빼면 맨 마지막에 한 번만 찍힌다.

## 루프 순서를 바꾸면

`i`와 `j`를 바꿔 써보면 결과가 완전히 달라진다.

```c#
for (int j = 1; j <= 9; j++)
{
    for (int i = 2; i <= 9; i++)
    {
        Console.WriteLine($"{i} * {j} = {i * j}");
    }
    Console.WriteLine();
}
```

`2*1, 3*1, 4*1 ... 9*1` 다음에 `2*2, 3*2 ...` 순서로 나온다. 곱셈 결과의 집합은 같은데 나열 순서가 다르다.

**바깥 루프가 "무엇을 기준으로 묶을지"를 정한다.** 이게 이중 루프를 읽는 요령이 됐다. 2차원 배열을 다룰 때도 똑같이 적용된다.

## 표처럼 가로로 찍기

실제 구구단 표는 한 줄에 여러 단이 나란히 있다. 그렇게 하려면 줄바꿈 위치를 바꿔야 한다.

```c#
for (int j = 1; j <= 9; j++)          // 줄 = 곱하는 수
{
    for (int i = 2; i <= 9; i++)      // 열 = 단
    {
        Console.Write($"{i} * {j} = {i * j}\t");
    }
    Console.WriteLine();
}
```

`WriteLine`을 `Write`로 바꿔 줄바꿈을 없애고, 한 줄이 끝나는 자리에서만 `WriteLine()`을 부른다.

탭 대신 폭을 지정하면 열이 반듯하게 맞는다. 문자열 보간에서 쉼표 뒤에 숫자를 쓰면 자리 폭이 된다.

```c#
Console.Write($"{i} * {j} = {i * j,-3}");
```

`-3`은 왼쪽 정렬 3칸이고, 음수를 빼면 오른쪽 정렬이다. 결과가 한 자리든 두 자리든 열이 어긋나지 않는다.

## 문자열 보간

```c#
$"{i} * {j} = {i * j}"
```

문자열 앞에 `$`를 붙이면 중괄호 안에 식을 그대로 쓸 수 있다. C# 6부터 생겼다.

이전 방식들과 비교하면 차이가 뚜렷하다.

```c#
Console.WriteLine(i + " * " + j + " = " + (i * j));      // 이어붙이기
Console.WriteLine("{0} * {1} = {2}", i, j, i * j);       // 자리표시자
Console.WriteLine($"{i} * {j} = {i * j}");               // 보간
```

두 번째 방식은 자리표시자 번호와 인자 순서를 맞춰야 해서, 인자가 늘어나면 어긋나기 쉽다. 번호를 빠뜨리면 실행 시점에 예외가 난다. 보간은 값이 그 자리에 있으니 그럴 일이 없다.

중괄호를 글자로 쓰고 싶으면 두 번 겹쳐 쓴다.

```c#
Console.WriteLine($"{{{i}}}");    // {2}
```

## 출력이 느린 이유

72줄이라 체감이 안 되는데, 이 방식은 줄마다 `Console.WriteLine`을 부른다. 콘솔 출력은 한 번마다 시스템 호출이 일어나서 생각보다 비싸다.

수천 줄을 찍을 일이 생기면 문자열을 모았다가 한 번에 내보내는 게 훨씬 빠르다.

```c#
using System.Text;

var sb = new StringBuilder();
for (int i = 2; i <= 9; i++)
{
    for (int j = 1; j <= 9; j++)
        sb.AppendLine($"{i} * {j} = {i * j}");
    sb.AppendLine();
}
Console.Write(sb.ToString());
```

`StringBuilder`가 왜 `string` 이어붙이기보다 나은지는 [24편](/posts/(24)string/)에서 다룬다.

## 정리하면

- 이중 루프에서 안쪽 루프 변수는 바깥이 한 바퀴 돌 때마다 다시 초기화된다
- 줄바꿈을 어디에 두느냐로 출력 모양이 정해진다. 바깥 루프 안이면 묶음마다, 밖이면 맨 끝에 한 번
- 바깥 루프가 "무엇으로 묶을지"를 정한다. 순서를 바꾸면 나열 순서가 달라진다
- `Write`와 `WriteLine`을 섞으면 표 형태로 찍을 수 있고, `{값,폭}`으로 열을 맞춘다
- 문자열 보간은 자리표시자 번호를 맞출 필요가 없어 실수가 준다
- 출력이 많으면 `StringBuilder`에 모아 한 번에 내보낸다
