---
title: "(C#) 41. 미로 알고리즘 (SideWinder)"
description: SideWinder 미로 생성 알고리즘
date: 2022-03-30 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, maze, algorithm, sidewinder]
---

# SideWinder 미로 생성 알고리즘 (Maza Algorithm)

- 최초 작성일: 2021년 3월 30일(수)

## 목차

[TOC]

## 내용

### SideWinder 원리

![image](https://user-images.githubusercontent.com/68185569/160752280-ff737c12-11df-4f84-85f2-f57e8301e7f9.png)

위의 사진과 같이 우측으로 연속으로 5개의 길이 뚫렸다면, 그 중에서 랜덤으로 인덱스를 골라 그 곳에서 아래로 길을 뚤는 원리이다.

<br/>

---

<br/>

그러면, Board.cs 코드에서 SideWinder를 위한 함수를 구현해주고, Initialize에서 함수를 호출해주자. (앞서 했던 BinaryTree 방식 대신에 넣는다.)

그리고 마찬가지로 외벽은 막혀있어야한다는 것이 조건이므로 추가해준다.

#### Board.cs

```c#
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Maze
{
    class Board
    {
        const char CIRCLE = '\u25cf';
        public TileType[,] Tile;    //배열
        public int Size;

        public enum TileType
        {
            Empty,
            Wall,
        }
        public void Initialize(int size)
        {
            if (size % 2 == 0)
                return;

            Tile = new TileType[size, size];
            Size = size;

            // Mazes for Programmers
            //GenerateByBinaryTree();
            GenerateBySideWinder();
        }

        void GenerateBySideWinder()
        {
            // 일단 길을 다 막아버리는 작업
            for (int y = 0; y < Size; y++)
            {
                for (int x = 0; x < Size; x++)
                {
                    if (x % 2 == 0 || y % 2 == 0)
                        Tile[y, x] = TileType.Wall;
                    else
                        Tile[y, x] = TileType.Empty;
                }
            }

            // 랜덤으로 우측 혹은 아래로 길을 뚫는 작업
            Random rand = new Random();
            for (int y = 0; y < Size; y++)
            {
                int count = 1;  // 몇 개의 점을 연속으로 뚫었는지 확인하기 위함. (그 중에서 랜덤으로 하나를 뽑아야하므로)
                for (int x = 0; x < Size; x++)
                {
                    if (x % 2 == 0 || y % 2 == 0)
                        continue;

                    if (y == Size - 2 && x == Size - 2)     // 가장 오른쪽 아래 지점 도착
                        continue;                           // 더 이상 길을 뚫지 않음.

                    if (y == Size - 2)                      // 아래쪽 벽을 만났을 때
                    {
                        Tile[y, x + 1] = TileType.Empty;    // 무조건 오른쪽으로 길을 뚫는다.
                        continue;
                    }

                    if (x == Size - 2)                      // 오른쪽 벽을 만났을 때
                    {
                        Tile[y + 1, x] = TileType.Empty;    // 무조건 아래로 길을 뚫는다.
                        continue;
                    }

                    if (rand.Next(0, 2) == 0)
                    {
                        Tile[y, x + 1] = TileType.Empty;
                        count++;
                    }
                    else
                    {
                        int randomIndex = rand.Next(0, count);  // 연속된 count 수 중의 하나를 선택
                        Tile[y + 1, x] = TileType.Empty;
                        count = 1;      // 연속이 끝나면 초기화
                    }
                }
            }
        }

        public void Render()        // 렌더링
        {
            ConsoleColor prevColor = Console.ForegroundColor;

            for (int y = 0; y < Size; y++)
            {
                for (int x = 0; x < Size; x++)
                {
                    Console.ForegroundColor = GetTileColor(Tile[y, x]);
                    Console.Write(CIRCLE);
                }
                Console.WriteLine();
            }
            Console.ForegroundColor = prevColor;
        }

        ConsoleColor GetTileColor(TileType type)
        {
            switch (type)
            {
                case TileType.Empty:
                    return ConsoleColor.Green;
                case TileType.Wall:
                    return ConsoleColor.Red;
                default:
                    return ConsoleColor.Green;
            }
        }
    }
}
```

#### Program.cs

```c#
using System;

namespace Maze
{
    class Program
    {
        static void Main(string[] args)
        {
            Board board = new Board();
            board.Initialize(25);

            Console.CursorVisible = false;

            const int WAIT_TICK = 1000 / 30;
            int lastTick = 0;
            while (true)
            {
                #region 프레임 관리
                // FPS 프레임 (60프레임 OK, 30프레임 이하 NO) : 1초에 몇번 동작하는가

                int currentTick = System.Environment.TickCount;
                int elapsedTick = currentTick - lastTick;   // 경과한 시간

                // 만약에 경과한 시간이 1/30초보다 작다면
                if (elapsedTick < WAIT_TICK)
                    continue;
                int deltaTick = currentTick - lastTick; // 경과한 시간.
                lastTick = currentTick;
                
                #endregion

                // 입력

                // 로직
                // 렌더링
                Console.SetCursorPosition(0, 0);
                board.Render();
            }
        }
    }
}

```
### Result

![image](https://user-images.githubusercontent.com/68185569/160753226-8a7ec8d2-d634-4411-bb57-b2178ed9c5da.png)
