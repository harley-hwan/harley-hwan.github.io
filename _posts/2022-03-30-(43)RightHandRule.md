---
title: "(C#) 43. 오른손 법칙 (PlayerMoving)"
description: 우수법
date: 2022-03-30 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, unity, maze, algorithm, right hand rule]
---

# 우수법 (오른손 법칙)을 이용한 미로 생성 알고리즘

- 최초 작성일: 2021년 3월 30일(수)

## 목차

[TOC]

## 내용

### 오른손 법칙을 이용한 플레이어의 이동 구현

앞서 플레이어 클래스를 추가하여, 플레이어가 랜덤으로 미로를 찾아가는 과정을 구현해보았다.

그럼 이번엔, 오른손 법칙을 이용하여 오른쪽 경로를 우선시 하는 알고리즘을 추가해보자.

다시 말해, 오른쪽으로 이동이 가능하다면 그 것을 우선으로 하고,

오른쪽이 막혀있다면 직진, 직진도 안된다면 왼쪽으로 회전하는 과정을 반복한다.

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
    class Pos
    {
        public Pos(int y, int x) { Y = y; X = x; }
        public int Y;
        public int X;
    }
    class Player
    {
        public int PosX { get; private set; }   // Player 좌표는 Player만 고칠 수 있다.
        public int PosY { get; private set; }

        Random _random = new Random();
        Board _board;

        enum Dir
        {
            Up = 0,
            Left = 1,
            Down = 2,
            Right = 3
        }

        int _dir = (int)Dir.Up;
        List<Pos> _points = new List<Pos>();

        public void Initialize(int posY, int posX, Board board)
        {
            PosX = posX;
            PosY = posY;
            _board = board;

            // 현재 바라보고 있는 방향을 기준으로, 좌표 변화를 나타낸다.
            int[] frontY = new int[] { -1, 0, 1, 0 };   // Up, Left, Down, Right
            int[] frontX = new int[] { 0, -1, 0, 1 };

            int[] rightY = new int[] { 0, -1, 0, 1 };   // Up, Left, Down, Right
            int[] rightX = new int[] { 1, 0, -1, 0 };

            _points.Add(new Pos(PosY, PosX));

            // 목적지 도착하기 전에는 계속 진행
            while (PosY != board.DestY || PosX != board.DestX)
            {
                // 1. 현재 바라보는 방향을 기준으로 오른쪽으로 갈 수 있는지 확인.
                if (_board.Tile[PosY + rightY[_dir], PosX + rightX[_dir]] == Board.TileType.Empty)
                {
                    // 오른쪽 방향으로 90도 회전 후
                    _dir = (_dir - 1 + 4) % 4;
                    // 앞으로 한 보 전진
                    PosY += frontY[_dir];
                    PosX += frontX[_dir];
                    _points.Add(new Pos(PosY, PosX));
                }
                // 2. 현재 바라보는 방향을 기준으로 전진할 수 있는지 확인
                else if (_board.Tile[PosY + frontY[_dir], PosX + frontX[_dir]] == Board.TileType.Empty)
                {
                    // 앞으로 한 보 전진
                    PosY += frontY[_dir];
                    PosX += frontX[_dir];
                    _points.Add(new Pos(PosY, PosX));
                }
                else
                {
                    // 왼쪽 방향으로 90도 회전   (왼쪽 두번 회전하면 후진이 됨)
                    _dir = (_dir + 1 + 4) % 4;
                }
            }
        }

        const int MOVE_TICK = 10;
        int _sumTick = 0;
        int _lastIndex = 0;

        public void Update(int deltaTick)
        {
            if (_lastIndex >= _points.Count)
                return;

            _sumTick += deltaTick;
            if (_sumTick >= MOVE_TICK)
            {
                _sumTick = 0;

                PosY = _points[_lastIndex].Y;
                PosX = _points[_lastIndex].X;
                _lastIndex++;
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

        public int DestY { get; private set; }
        public int DestX { get; private set; }

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

            DestY = Size - 2;
            DestX = Size - 2;

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
                    else if (y == DestY && x == DestX)
                        Console.ForegroundColor = ConsoleColor.Yellow;
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
            player.Initialize(1, 1, board);

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

<iframe id="video" width="750" height="500" src="/assets/video/2022-03-30-RightHandRule.mp4" frameborder="0"> </iframe>
