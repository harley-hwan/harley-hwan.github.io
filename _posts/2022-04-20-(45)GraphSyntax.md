---
title: "(C#) 45. 그래프 이론"
description: Graph Theory
date: 2022-04-20 10:00:00 +0900
categories: [Dev, CSharp]
tags: [c#, datastructure, graph]
---

# 그래프 (Graph)

- 최초 작성일: 2021년 4월 20일(수)

## 내용

### 그래프 개념

[현실 세계의 사물 및 추상적 개념 간]의 [연결 관계]를 표현

- 정점 (Vertex): 데이터를 표현 (사물이나 개념 등)
- 간선 (Edge): 정점 간의 연결을 표현

<br/>

### 그래프 구현

![image](https://user-images.githubusercontent.com/68185569/164148133-b487957c-01b8-45c6-94c5-3eb932b5e393.png)

#### 인스턴스 생성 (LinkedList의 Node처럼)

```c#
 // 인스턴스 생성 (LinkedList의 Node처럼)
class Vertex
{
    public List<Vertex> edges = new List<Vertex>();
}

void CreateGraph()
{
    List<Vertex> v = new List<Vertex>(6)
{
    new Vertex(),
    new Vertex(),
    new Vertex(),
    new Vertex(),
    new Vertex(),
    new Vertex(),
};
    v[0].edges.Add(v[1]);
    v[0].edges.Add(v[3]);
    v[1].edges.Add(v[0]);
    v[1].edges.Add(v[2]);
    v[1].edges.Add(v[3]);
    v[3].edges.Add(v[4]);
    v[5].edges.Add(v[4]);
}
```

<br/>

#### 리스트를 이용한 그래프 표현

```c#
// 읽는 방법: adjacent[from] -> 연결된 목록
// 리스트를 이용한 그래프 표현
// 메모리를 아낄 수 있지만, 접근 속도에서 손해를 본다.
// (간선이 적고 정점이 많은 경우 이점이 있다)
List<int>[] adjacent = new List<int>[6]
{
    new List<int> { 1, 3 },
    new List<int> { 0, 2, 3 },
    new List<int> { },
    new List<int> { 4 },
    new List<int> { },
    new List<int> { 4 },
};
```

<br/>

#### 가중치 추가

```c#
// 가중치 추가
List<Edge>[] adjacent_1 = new List<Edge>[6]
{
    new List<Edge>() { new Edge(1, 15), new Edge(3, 35) },
    new List<Edge>() { new Edge(0, 15), new Edge(2, 5), new Edge(3, 10) },
    new List<Edge>() { },
    new List<Edge>() { new Edge(4, 5) },
    new List<Edge>() { },
    new List<Edge>() { new Edge(4, 5) },
};
```

<br/>

#### 행렬을 이용한 그래프 표현 (2차원 배열)

```c#
// 읽는 방법: adjacent3[from, to]
// 행렬을 이용한 그래프 표현 (2차원 배열)
// 메모리 소모가 심하지만, 빠른 접근이 가능하다.
// (정점은 적고 간선이 많은 경우 이점이 있다)
int[,] adjacent2 = new int[6, 6]
{
    { 0, 1, 0, 1, 0, 0 },
    { 1, 0, 1, 1, 0, 0 },
    { 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 1, 0 },
    { 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 1, 0 },
};
```

<br/>

#### 가중치 부여

```c#
// 가중치 부여, 안쓰는 숫자(-1)를 사용해 연결이 끊긴 것을 표현
int[,] adjacent2_1 = new int[6, 6]
{
    { -1, 15, -1, 35, -1, -1 },
    { 15, -1, 5, 10, -1, -1 },
    { -1, -1, -1, -1, -1, -1 },
    { -1, -1, -1, -1, 5, -1 },
    { -1, -1, -1, -1, -1, -1 },
    { -1, -1, -1, -1, 5, -1 },
};
```
