---
title: "(C#) 6. 가위바위보 게임"
description: "지금까지 배운 것을 합쳐 만든 첫 프로그램. 숫자가 아닌 입력에서 그대로 죽는 문제, 범위 밖 값이 조용히 통과하는 문제, 그리고 9갈래 중첩 if를 나머지 연산 한 줄로 줄인 과정을 남긴다."
date: 2022-03-21 10:00:00 +0900
slug: '(6)RockScisorsPaperGame'
categories: [Dev, CSharp]
series: csharp
series_order: 6
tags: [csharp, unity, codeflowcontrol, rockscissorspaper, tryparse, random]
---
## 배운 것을 합쳐보기

[4편](/posts/(4)If_else/)의 `if`와 [5편](/posts/(5)switch/)의 `switch`를 실제로 쓸 곳이 필요했다. 입력을 받고, 판정하고, 결과를 내는 프로그램 하나를 만들어봤다.

```c#
using System;

namespace Rock_Paper_Scissors
{
    class Program
    {
        static void Main(string[] args)
        {
            // 0:가위     1:바위    2:보
            Random rand = new Random();
            int aiChoice = rand.Next(0, 3);     // 0~2사이의 랜덤 값
            int choice = Convert.ToInt32(Console.ReadLine());

            switch (choice)
            {
                case 0:
                    Console.WriteLine("당신의 선택은 가위입니다.");
                    break;
                case 1:
                    Console.WriteLine("당신의 선택은 바위입니다.");
                    break;
                case 2:
                    Console.WriteLine("당신의 선택은 보입니다.");
                    break;
            }

            switch (aiChoice)
            {
                case 0:
                    Console.WriteLine("상대방의 선택은 가위입니다.");
                    break;
                case 1:
                    Console.WriteLine("상대방의 선택은 바위입니다.");
                    break;
                case 2:
                    Console.WriteLine("상대방의 선택은 보입니다.");
                    break;
            }

            // 승리 무승부 패배
            if (choice == 0)
            {
                if (aiChoice == 0)
                {
                    Console.WriteLine("무승부");
                }
                else if (aiChoice == 1)
                {
                    Console.WriteLine("패배.");
                }
                else   // choice == 2
                {
                    Console.WriteLine("승리.");
                }
            }
            else if (choice == 1)
            {
                if (aiChoice == 0)
                {
                    Console.WriteLine("승리.");
                }
                else if (aiChoice == 1)
                {
                    Console.WriteLine("무승부");
                }
                else   // choice == 2
                {
                    Console.WriteLine("패배.");
                }
            }
            else   // choice == 2
            {
                if (aiChoice == 0)
                {
                    Console.WriteLine("패배.");
                }
                else if (aiChoice == 1)
                {
                    Console.WriteLine("승리.");
                }
                else   // choice == 2
                {
                    Console.WriteLine("무승부");
                }
            }
        }
    }
}
```

돌려보면 동작한다. 그런데 몇 가지를 해보니 바로 깨졌다.

## 숫자가 아닌 걸 넣으면 죽는다

`0` 대신 `a`를 치니 프로그램이 예외를 뱉고 끝났다.

```text
Unhandled exception. System.FormatException: The input string 'a' was not in a correct format.
```

`Convert.ToInt32`는 변환에 실패하면 예외를 던진다. 그냥 엔터만 쳐도 빈 문자열이라 같은 예외가 난다.

`int.TryParse`를 쓰면 예외 대신 성공 여부를 `bool`로 돌려준다.

```c#
string input = Console.ReadLine();
int choice;
if (!int.TryParse(input, out choice))
{
    Console.WriteLine("숫자를 입력하세요.");
    return;
}
```

C# 7부터는 변수를 그 자리에서 선언할 수 있어 더 짧다.

```c#
if (!int.TryParse(Console.ReadLine(), out int choice))
{
    Console.WriteLine("숫자를 입력하세요.");
    return;
}
```

`TryParse` 계열은 `double`, `bool`, `DateTime` 등에도 다 있다. 사용자 입력이나 파일에서 읽은 값처럼 **내가 통제하지 못하는 문자열**에는 `Convert`나 `Parse` 대신 `TryParse`를 쓰는 게 기본이 됐다.

`Console.ReadLine()`이 `null`을 돌려줄 수 있다는 것도 나중에 알았다. 입력이 끝나면(콘솔에서 Ctrl+Z, 파이프로 넘긴 파일의 끝) `null`이 온다. `TryParse`는 `null`을 넣어도 예외 없이 `false`를 주니 이 경우도 같이 처리된다.

## 범위를 벗어난 값이 조용히 통과한다

`5`를 입력하면 첫 `switch`는 아무것도 안 찍는다. `case`가 0, 1, 2뿐이고 `default`가 없기 때문이다.

문제는 그다음이다. 판정 부분의 마지막 `else`가 "`choice == 2`"라는 주석과 달리 **2가 아닌 모든 값**을 받는다. 그래서 5를 넣으면 내 선택은 출력되지 않은 채로 "패배" 같은 결과만 나온다.

[4편](/posts/(4)If_else/)에서 적은 "마지막 `else`는 나머지 전부를 받는다"가 실제로 문제가 된 경우다. 입력을 받은 직후에 걸러야 한다.

```c#
if (choice < 0 || choice > 2)
{
    Console.WriteLine("0, 1, 2 중에서 입력하세요.");
    return;
}
```

## rand.Next(0, 3) 의 3은 포함되지 않는다

`Random.Next(min, max)`는 `min` 이상 `max` **미만**을 돌려준다. 0, 1, 2가 나오고 3은 안 나온다.

처음엔 `Next(0, 2)`라고 썼다가 보가 한 번도 안 나와서 알았다. 상한이 배타적이라는 건 배열 인덱스를 만들 때 `Next(0, arr.Length)`가 딱 맞아떨어져서 편하긴 한데, 익숙해지기 전에는 한 번씩 걸린다.

`Random` 객체를 루프 안에서 매번 새로 만들면 같은 값이 반복해서 나올 수 있다는 것도 같이 알아두면 좋다. 옛날 .NET Framework에서는 시드가 시스템 시간 기반이라, 빠르게 여러 개를 만들면 전부 같은 시드를 받았다. 이 코드처럼 하나만 만들어 재사용하면 문제가 없다.

## 9갈래 중첩을 한 줄로

판정 부분이 `if` 세 개 안에 `if` 세 개씩, 총 9갈래다. 규칙 자체는 간단한데 코드가 40줄이다. 손으로 다 적다 보니 어느 조합을 빠뜨렸는지도 확신이 안 섰다.

가위(0) → 바위(1) → 보(2) → 가위(0)로 순환한다는 점을 쓰면 짧아진다. **내 선택 바로 다음 번호가 나를 이기는 것**이고, 그 전 번호는 내가 이기는 것이다.

```c#
int result = (choice - aiChoice + 3) % 3;
// 0: 무승부, 1: 승리, 2: 패배
```

`+3`을 하는 이유는 `choice - aiChoice`가 음수가 될 수 있어서다. C#의 `%`는 음수에서 음수를 돌려주기 때문에 미리 더해서 0 이상으로 만든다. 이건 [3편](/posts/(3)BitOperation/)에서 본 음수 연산 차이와 같은 부류의 주의점이다.

확인해보면 이렇게 맞아떨어진다.

| 내 선택 | 상대 | `(c - a + 3) % 3` | 결과 |
| :--- | :--- | ---: | :--- |
| 가위(0) | 가위(0) | 0 | 무승부 |
| 가위(0) | 보(2) | 1 | 승리 |
| 가위(0) | 바위(1) | 2 | 패배 |
| 바위(1) | 가위(0) | 1 | 승리 |
| 보(2) | 바위(1) | 1 | 승리 |

출력도 배열로 묶으면 `switch` 두 개가 사라진다.

```c#
string[] names = { "가위", "바위", "보" };
string[] results = { "무승부", "승리", "패배" };

Console.WriteLine($"당신의 선택은 {names[choice]}입니다.");
Console.WriteLine($"상대방의 선택은 {names[aiChoice]}입니다.");
Console.WriteLine(results[(choice - aiChoice + 3) % 3]);
```

100줄이 넘던 게 이렇게 줄었다. 물론 `(choice - aiChoice + 3) % 3`이 왜 승패인지는 코드만 봐서는 안 보이니, 주석이 없으면 오히려 읽기 어려워진다. 이 정도 규칙에서는 축약이 이득이지만 항상 그런 건 아니다. 규칙이 불규칙하면 오히려 `switch`로 다 나열하는 게 낫다.

배열 대신 `enum`을 쓰는 방향은 [4편](/posts/(4)If_else/)에 적어뒀다.

## 정리하면

- 사용자 입력을 정수로 바꿀 때는 `Convert`/`Parse` 대신 `int.TryParse`를 쓴다. 예외 대신 `bool`을 준다
- `Console.ReadLine()`은 `null`을 돌려줄 수 있다
- 입력 범위는 받은 직후에 검사한다. 안 그러면 마지막 `else`가 이상한 값까지 정상 경로로 흘려보낸다
- `Random.Next(min, max)`의 상한은 포함되지 않는다
- 순환 구조가 있는 판정은 나머지 연산으로 줄일 수 있다. C#의 `%`는 음수를 돌려주므로 미리 더해준다
- 값에 대응하는 문자열은 배열이나 `enum`으로 묶으면 `switch`가 사라진다
