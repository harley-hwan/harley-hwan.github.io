---
title: "(C#) 42. 미로 알고리즘 (PlayerMoving)"
description: 플레이어 이동
date: 2022-03-30 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, maze, algorithm, player]
---

# 미로에서 플레이어의 이동 구현

- 최초 작성일: 2021년 3월 30일(수)

## 목차

[TOC]

## 내용

### Player 이동 구현

앞서 미로를 생성했으면, 이제 그 미로를 탈출할 플레이어를 생성해준다.

그리고 x, y 좌표를 설정할 PosX, PosY를 생성해주고, 

상/하/좌/우 좌표 이동에 대한 로직을 구현해준다.

이때 상하좌우 이동은 random Value에 의해 결정되며, 즉 랜덤으로 미로를 찾아가는 과정이 진행된다. 

<br/>

### C# 코드

#### Player.cs

```c#
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Maze
{
    class Player
    {
        public int PosX { get; private set; }   // Player 좌표는 Player만 고칠 수 있다.
        public int PosY { get; private set; }

        Random _random = new Random();
        Board _board;

        public void Initialize(int posY, int posX, int destY, int destX, Board board)
        {
            PosX = posX;
            PosY = posY;
            _board = board;
        }

        const int MOVE_TICK = 10;
        int _sumTick = 0;

        public void Update(int deltaTick)
        {
            _sumTick += deltaTick;
            if (_sumTick >= MOVE_TICK)
            {
                _sumTick = 0;

                //여기에다가 0.1초마다 실횡될 로직을 넣어준다.
                int randValue = _random.Next(0, 4);
                switch (randValue)
                {
                    case 0:     // 상
                        if (PosY - 1 >= 0 && _board.Tile[PosY - 1, PosX] == Board.TileType.Empty)
                            PosY--;
                        break;
                              
                    case 1:     // 하
                        if (PosY + 1 < _board.Size && _board.Tile[PosY + 1, PosX] == Board.TileType.Empty)
                            PosY++;
                        break;

                    case 2:     // 좌
                        if (PosX - 1 >= 0 && _board.Tile[PosY, PosX - 1] == Board.TileType.Empty)
                            PosX--;
                        break; 

                    case 3:     // 우
                        if (PosX + 1 < _board.Size && _board.Tile[PosY, PosX + 1] == Board.TileType.Empty)
                            PosX++;
                        break;
                }
            }
        }
    }
}

```

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
        public TileType[,] Tile { get; private set; }    //배열
        public int Size { get; private set; }

        Player _player;

        public enum TileType
        {
            Empty,
            Wall,
        }
        public void Initialize(int size, Player player)
        {
            if (size % 2 == 0)
                return;

            _player = player;

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
                    // 플레이어 좌표를 갖고 와서, 그 좌표랑 현재 y, x가 일치하면 플레이어 전용 색상으로 표시
                    if (y == _player.PosY && x == _player.PosX)
                        Console.ForegroundColor = ConsoleColor.Blue;
                    else
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
<br/>

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
            Player player = new Player();
            board.Initialize(25, player);
            player.Initialize(1, 1, board.Size - 2, board.Size - 2, board);

            Console.CursorVisible = false;

            const int WAIT_TICK = 1000 / 30;
            //const char CIRCLE = '\u25cf';
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
                player.Update(deltaTick);

                // 렌더링
                Console.SetCursorPosition(0, 0);
                board.Render();
            }
        }
    }
}

```

<br/>

---

### Result Video

<iframe id="video" width="750" height="500" src="/assets/video/PlayerMoving.mp4" frameborder="0"> </iframe>
