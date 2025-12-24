---
title: "(C#) 48. 다익스트라(Dijkstra) 최단 경로 알고리즘"
description: Maze with Dijkstra Algorithm
date: 2023-01-13 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, datastructure, graph, dijkstra, shortestpath, algorithm, maze]
---

# 다익스트라 (Dijkstra) 최단 경로 알고리즘 (Graph)

- 최초 작성일: 2023년 1월 13일(금)

## 내용

## 개념

- 가중치 값을 갖는 경로의 경우 사용할 수 있다.
- 그 정보가 정말로 최단 거리라는 보장이 없기 때문에 미리 예약된 지점도 언제든지 뒤바뀔 수 있다. 
- 예약된 순서는 아무런 상관이 없고, 각 턴마다 그 상황에 맞는 best solution을 구한다.

<br/>

## 실습

### Dijistra 함수

```c#
  public void Dijikstra(int start)
  {
      bool[] visited = new bool[6];
      int[] distance = new int[6];

      Array.Fill(distance, Int32.MaxValue);

      distance[start] = 0;

      while (true)
      {
          // 제일 좋은 후보를 찾는다 (가장 가까이에 있는)

          // 가장 유력한 후보의 거리와 번호 저장
          int closest = Int32.MaxValue;
          int now = -1;
          for (int i = 0; i < 6; i++)
          {
              // 이미 방문한 정점 싑
              if (visited[i])
                  continue;

              // 아직 발견된 적이 없거나, 기존 후보보다 멀리 있으면 스킵
              if (distance[i] == Int32.MaxValue || distance[i] >= closest)
                  continue;

              // 여태껏 발견한 가장 좋은 후보라는 의미니까, 정보를 갱신
              closest = distance[i];
              now = i;
          }

          // 다음 후보가 하나도 없다 -> 종료
          if (now == -1)
              break;

          // 제일 좋은 후보를 찾았으니까 방문한다.
          visited[now] = true;

          // 방문한 정점과 인접한 정점들을 조사해서,
          // 상황에 따라 발견한 최단거리를 갱신한다.
          for (int next = 0; next < 6; next++)
          {
              // 연결되지 않은 정점 스킵
              if (adj[now, next] == -1)
                  continue;
              // 이미 방문한 정점은 스킵
              if (visited[next])
                  continue;

              // 새로 조사된 정점의 최단거리를 계산한다.
              int nextDist = distance[now] + adj[now, next];
              // 만약에 기존에 발견한 최단거리가 새로 조사된 최단거리보다 크면, 정보를 갱신
              if (nextDist < distance[next])
              {
                  distance[next] = nextDist;
              }
          }
      }
  }
```

<br/>

### 풀소스

```c#
using System;
using System.Collections.Generic;

namespace MazeDijkstra
{
    class Graph
    {
        int[,] adj = new int[6, 6]
        {
            { -1, 15, -1, 35, -1, -1 },
            { 15, -1, 05, 10, -1, -1 },
            { -1, 05, -1, -1, -1, -1 },
            { 35, 10, -1, -1, 05, -1 },
            { -1, -1, -1, 05, -1, 05 },
            { -1, -1, -1, -1, 05, -1 },
        };

        public void Dijikstra(int start)
        {
            bool[] visited = new bool[6];
            int[] distance = new int[6];

            Array.Fill(distance, Int32.MaxValue);

            distance[start] = 0;

            while (true)
            {
                // 제일 좋은 후보를 찾는다 (가장 가까이에 있는)

                // 가장 유력한 후보의 거리와 번호 저장
                int closest = Int32.MaxValue;
                int now = -1;
                for (int i = 0; i < 6; i++)
                {
                    // 이미 방문한 정점 싑
                    if (visited[i])
                        continue;

                    // 아직 발견된 적이 없거나, 기존 후보보다 멀리 있으면 스킵
                    if (distance[i] == Int32.MaxValue || distance[i] >= closest)
                        continue;

                    // 여태껏 발견한 가장 좋은 후보라는 의미니까, 정보를 갱신
                    closest = distance[i];
                    now = i;
                }

                // 다음 후보가 하나도 없다 -> 종료
                if (now == -1)
                    break;

                // 제일 좋은 후보를 찾았으니까 방문한다.
                visited[now] = true;

                // 방문한 정점과 인접한 정점들을 조사해서,
                // 상황에 따라 발견한 최단거리를 갱신한다.
                for (int next = 0; next < 6; next++)
                {
                    // 연결되지 않은 정점 스킵
                    if (adj[now, next] == -1)
                        continue;
                    // 이미 방문한 정점은 스킵
                    if (visited[next])
                        continue;

                    // 새로 조사된 정점의 최단거리를 계산한다.
                    int nextDist = distance[now] + adj[now, next];
                    // 만약에 기존에 발견한 최단거리가 새로 조사된 최단거리보다 크면, 정보를 갱신
                    if (nextDist < distance[next])
                    {
                        distance[next] = nextDist;
                    }
                }
            }
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            // DFS (Depth First Search 깊이 우선 탐색)
            // BFS (Breadth First Search 너비 우선 탐색)
            Graph graph = new Graph();
            graph.Dijikstra(0);
            //graph.SearchAll();

        }
    }
}

```
