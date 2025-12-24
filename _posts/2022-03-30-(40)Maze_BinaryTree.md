---
title: "(C#) 40. 미로 알고리즘 (Binary Tree)"
description: Binary Tree 미로 생성 알고리즘
date: 2022-03-30 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, maze, algorithm, binary tree]
---

# Binary Tree 미로 생성 알고리즘 (Maza Algorithm)

- 최초 작성일: 2021년 3월 30일(수)

## 목차



## 내용

### 맵 만들기

우선, 우리가 미로 생성 알고리즘을 구현할 맵을 먼저 만들어보자.

비어 있는 공간을 Green, 벽이 있는 공간을 Red로 색상을 표현하여 우선, 테두리를 벽으로 설정하고 시작한다.

<br/>

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
            
            for (int y = 0; y < Size; y++) {
                for (int x = 0; x < Size; x++)
                {
                    if (x == 0 || x == Size - 1 || y == 0 || y == Size - 1)
                        Tile[y, x] = TileType.Wall;
                    else
                        Tile[y, x] = TileType.Empty;
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

#### Result1

![image](https://user-images.githubusercontent.com/68185569/160740000-96dd2abf-e708-4435-94b2-6d9b53ff30e9.png)

<br/>

---

### Binary Tree 미로 알고리즘

Board.cs의 Initialize 함수만 살짝 바꿔본다.

그러면, 맵의 모든 공간이 벽인 상태에서 듬성듬성 공간을 비워주는 형태를 확인할 수 있다.

#### Board.cs

```c#
public void Initialize(int size)
{
    if (size % 2 == 0)
        return;

    Tile = new TileType[size, size];
    Size = size;

    for (int y = 0; y < Size; y++) {
        for (int x = 0; x < Size; x++)
        {
            if (x % 2 == 0 || y % 2 == 0) // 수정
                Tile[y, x] = TileType.Wall;
            else
                Tile[y, x] = TileType.Empty;
        }
    }
}      
```

<br/>

#### Result 2-1

![image](https://user-images.githubusercontent.com/68185569/160740572-3c78dec5-bd26-498b-8253-9bacf3c71bee.png)

<br/>

<br/>

그 다음은 띄엄띄엄 비워준 부분을 기준으로 오른쪽 혹은 아래로 갈지를 랜덤으로 결정하여 경로를 만들어보자.

<br/>

#### Board.cs

``` c#
public void Initialize(int size)
{
    if (size % 2 == 0)
        return;

    Tile = new TileType[size, size];
    Size = size;

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
    for (int  y = 0; y < Size; y++)
    {
        for (int x = 0; x < Size; x++)
        {
            if (x % 2 == 0 || y % 2 == 0)
                continue;

            if (rand.Next(0, 2) == 0)
            {
                Tile[y, x + 1] = TileType.Empty;
            }
            else
            {
                Tile[y + 1, x] = TileType.Empty;
            }

        }
    }
}
```

<br/>

#### Result 2-2

![image](https://user-images.githubusercontent.com/68185569/160750218-8d1118d4-4713-45cf-8e24-b7dd6a9516bf.png)

<br/>

<br/>

그런데, 여기서 미로가 외벽이 다 막히도록 만들어야하므로

오른쪽 벽을 만났을 때는 무조건 아래로 이동, 

아래쪽 벽을 만났을 때는 무조건 오른쪽으로 이동이라는 조건을 추가해준다.

<br/>

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
            GenerateByBinaryTree();
        }

        void GenerateByBinaryTree()
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
                for (int x = 0; x < Size; x++)
                {
                    if (x % 2 == 0 || y % 2 == 0)
                        continue;

                    if (y == Size - 2 && x == Size - 2)     // 가장 오른쪽 아래 지점에 도착했을 때
                        continue;                           // 무조건 오른쪽으로 가게하던 것을 없앰.

                    if (y == Size - 2)  // 아래쪽 벽을 만났을 때
                    {
                        Tile[y, x + 1] = TileType.Empty;    // 무조건 오른쪽으로 가게함.
                        continue;
                    }

                    if (x == Size - 2)  // 오른쪽 벽을 만났을 때
                    {
                        Tile[y + 1, x] = TileType.Empty;    // 무조건 아래로 가게함.
                        continue;
                    }

                    if (rand.Next(0, 2) == 0)
                    {
                        Tile[y, x + 1] = TileType.Empty;
                    }
                    else
                    {
                        Tile[y + 1, x] = TileType.Empty;
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

#### Result 2-3

![image](https://user-images.githubusercontent.com/68185569/160750721-48d71e11-2788-4b6d-a98b-019dc3185960.png)
