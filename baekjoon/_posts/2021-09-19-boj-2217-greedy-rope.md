---
layout: post
title: Baekjoon 2217 로프
subtitle: 백준 2217 로프 (c++)
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: [star, fork, follow]
tags: [baekjoon, 백준, algorithm, greedy]
comments: true
---

# Baekjoon 2217 로프

- 최초 작성일: 2021년 9월 19일(일)
- 주소: <https://www.acmicpc.net/problem/2217>

## 목차
[TOC]

## 문제 설명
![image](https://user-images.githubusercontent.com/68185569/133917081-7483b0fb-ad82-45ba-88fc-82f6aef3633b.png)

- N(1 ≤ N ≤ 100,000)개의 로프가 있다. 이 로프를 이용하여 이런 저런 물체를 들어올릴 수 있다. 각각의 로프는 그 굵기나 길이가 다르기 때문에 들 수 있는 물체의 중량이 서로 다를 수도 있다.
- 하지만 여러 개의 로프를 병렬로 연결하면 각각의 로프에 걸리는 중량을 나눌 수 있다. k개의 로프를 사용하여 중량이 w인 물체를 들어올릴 때, 각각의 로프에는 모두 고르게 w/k 만큼의 중량이 걸리게 된다.
- 각 로프들에 대한 정보가 주어졌을 때, 이 로프들을 이용하여 들어올릴 수 있는 물체의 최대 중량을 구해내는 프로그램을 작성하시오. 모든 로프를 사용해야 할 필요는 없으며, 임의로 몇 개의 로프를 골라서 사용해도 된다.

## 입력
- 첫째 줄에 정수 N이 주어진다. 다음 N개의 줄에는 각 로프가 버틸 수 있는 최대 중량이 주어진다. 이 값은 10,000을 넘지 않는 자연수이다

![image](https://user-images.githubusercontent.com/68185569/133917085-f7fd9a13-d3c4-49b4-865c-24f0c28ef524.png)
## 알고리즘 분류

- 수학
- 그리디 알고리즘
- 정렬
- 물리학

## 풀이 방법

- 입력으로 로프가 견딜 수 있는 최대 무게가 주어지기 때문에, 아무리 허용 중량이 크다고 해도 중량이 균등하게 나누어져서 메달리기 때문에, 가장 작은 허용 중량인 로프에 무게를 맞출 수밖에 없다.
- 처음에 vector로 sort 함수로 간단히 구현하려 했으나 값들을 하나씩 빼오는 과정을 생각해보면 오름차순으로 로프를 정렬하고 가장 작은것부터 쓰고 하나씩 버린다고 가정했을 때 큐가 더 적합하다 생각들었고, 오름차순 정렬을 위해 우선 순위 큐를 사용했다.
- 그래서 가장 작은 것부터 시작하여 로프의 수 * 현재의 최소 무게 를 구하고 최소 무게로 쓰였던 무게를 버리고 (n-1) * 다음 최소 무게 를 반복하며 최대값을 구해내는 과정을 반복한다.
- 쉽게 말하면, 허용 중량이 5, 10, 15인 로프가 주어졌다면, 5 * 3 = 15, 10 * 2 = 20, 15 * 1= 15 중 최대값인 20이 출력되는 것이다.

## 알고리즘 분류

- 수학
- 그리디 알고리즘

​	

​	


```c++
#include <iostream>
#include <algorithm>
#include <queue>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);

    int n; cin >> n;
    priority_queue<int, vector<int>, greater<int>> pq;

    int w;

    for (int i = 0; i < n; i++) {
        cin >> w;
        pq.push(w);
    }

    long long ans, max = 0;
    for (int i = 0; i < pq.size(); i++) {
        ans = (n-i) * pq.top();
        max = (max < ans) ? max : ans;
        pq.pop();
    }

    cout << max << endl;


    return 0;
}
```

