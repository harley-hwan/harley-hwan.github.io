---
layout: post
title: Baekjoon 18870 좌표 압축
subtitle: 백준 18870 좌표 압축
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: [star, fork, follow]
tags: [baekjoon, 백준, algorithm, sort]
comments: true
---

# Baekjoon 18870 좌표 압축

- 최초 작성일: 2021년 10월 1일(금)
- 주소: <https://www.acmicpc.net/problem/18870>

## 목차
[TOC]

## 문제 설명
![image](https://user-images.githubusercontent.com/68185569/135610736-7e1b2301-2372-4c38-9f75-d12dbbd528a3.png)


- 수직선 위에 N개의 좌표 X1, X2, ..., XN이 있다. 이 좌표에 좌표 압축을 적용하려고 한다.
- Xi를 좌표 압축한 결과 X'i의 값은 Xi > Xj를 만족하는 서로 다른 좌표의 개수와 같아야 한다.
- X1, X2, ..., XN에 좌표 압축을 적용한 결과 X'1, X'2, ..., X'N를 출력해보자.

## 입력
- 첫째 줄에 N이 주어진다.
- 둘째 줄에는 공백 한 칸으로 구분된 X1, X2, ..., XN이 주어진다.

## 출력

- 첫째 줄에 X'1, X'2, ..., X'N을 공백 한 칸으로 구분해서 출력한다.

![image](https://user-images.githubusercontent.com/68185569/135610758-7976d06e-2baf-4da9-8457-67a4bf32f89d.png)

## 알고리즘 분류

- 정렬
- 값 / 좌표 압축

## 풀이 방법

- 이 문제는 주어지는 숫자들을 정렬하며 작은 순으로 순서를 매겨주면 되는 문제다.
- 하지만, 주어진 입력 순서 그대로 다시 출력해주어야 하기 때문에 정렬 하기 전 해당 숫자의 인덱스를 기억해줘야 한다.
- 그래서 2중 벡터(v)에 입력을 넣을 때 인덱스를 같이 저장해둔다.
- 그러고 난뒤 입력값을 기준으로 오름차순으로 정렬해주고, 인접한 숫자와 같은지를 비교해 같지 않으면 cnt를 1씩 증가시키고 같으면 현재 cnt 값 그대로를 새로운 이중 벡터(order)에 이전에 저장했던 인덱스와 함께 저장한다. 
- 마지막으로, order 벡터의 second값(입력 순서를 기억하는 인덱스값)을 기준으로 오름차순 해주고 그대로 출력하면 된다.




```c++
#include <iostream>
#include <vector>
#include <map>
#include <algorithm>

using namespace std;

bool compare(const pair<int, int> p1, const pair<int, int> p2)
{
    return p1.second < p2.second;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);

    int n; cin >> n;
    vector<int> x;
    vector<pair<int, int> > v;

    for (int i = 0; i < n; i++) {
        int X; cin >> X;
        v.push_back(make_pair(X,i));
    }

    sort(v.begin(), v.end());

    // for (auto a : v) {
    //     cout << a.first << " " << a.second << "\n";
    // }

    int cnt = 0;
    vector<pair<int, int> > order;

    order.push_back(make_pair(0, v[0].second));

    for (int i = 1; i < v.size(); i++) {
        if (v[i].first != v[i-1].first) {
            cnt++;
            order.push_back(make_pair(cnt, v[i].second));
            continue;
        }
        order.push_back(make_pair(cnt, v[i].second));
    }
    
    sort(order.begin(), order.end(), compare);

    for (auto a : order) {
        cout << a.first << " ";
    }
    return 0;
}
```

