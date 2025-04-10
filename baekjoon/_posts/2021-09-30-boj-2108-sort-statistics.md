---
layout: post
title: Baekjoon 2108 통계학
subtitle: 백준 2108 통계학 (정렬)
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: [star, fork, follow]
tags: [baekjoon, 백준, algorithm, sort]
comments: true
---

# Baekjoon 2108 통계학

- 최초 작성일: 2021년 9월 30일(목)
- 주소: <https://www.acmicpc.net/problem/2108>

## 목차
[TOC]

## 문제 설명
![image](https://user-images.githubusercontent.com/68185569/135301978-78dcb4a7-4112-4599-b91c-b207bb1edb7f.png)


- 수를 처리하는 것은 통계학에서 상당히 중요한 일이다. 통계학에서 N개의 수를 대표하는 기본 통계값에는 다음과 같은 것들이 있다. 단, N은 홀수라고 가정하자.

1. 산술평균 : N개의 수들의 합을 N으로 나눈 값
2. 중앙값 : N개의 수들을 증가하는 순서로 나열했을 경우 그 중앙에 위치하는 값
3. 최빈값 : N개의 수들 중 가장 많이 나타나는 값
4. 범위 : N개의 수들 중 최댓값과 최솟값의 차이

- N개의 수가 주어졌을 때, 네 가지 기본 통계값을 구하는 프로그램을 작성하시오.

## 입력
- 첫째 줄에 수의 개수 N(1 ≤ N ≤ 500,000)이 주어진다. 단, N은 홀수이다. 그 다음 N개의 줄에는 정수들이 주어진다. 입력되는 정수의 절댓값은 4,000을 넘지 않는다.

## 출력

- 첫째 줄에는 산술평균을 출력한다. 소수점 이하 첫째 자리에서 반올림한 값을 출력한다.

- 둘째 줄에는 중앙값을 출력한다.

- 셋째 줄에는 최빈값을 출력한다. 여러 개 있을 때에는 최빈값 중 두 번째로 작은 값을 출력한다.

- 넷째 줄에는 범위를 출력한다.

![image](https://user-images.githubusercontent.com/68185569/135302077-29c058dc-2da2-4eb2-9763-3da08596bf50.png)


## 알고리즘 분류

- 구현
- 정렬

## 풀이 방법

- 문제는 간단했고, 그것을 어떻게 표현하고 구현하느냐가 중요한 문제이다.
1. 산술평균
- 그냥 평균 구하면 된다. 합 구해서 / n 해줬다. 대신, 첫 째자리 수에서 반올림 해줘야 하므로, float 형식으로 합을 받아 n 을 나누고 round 함수로 반올림 해주었다.
2. 중앙값:
- 증가하는 순서로 나열했을 때 그 중앙에 위치하는 값이다. 여기서, "증가하는 순서로 나열" 말 그대로 오름차순으로 정렬해주고 거기서 인덱스 n/2 인 곳의 수를 출력해준다.
3. 최빈값
- 이게 제일 까다로웠다. 가장 빈도수가 많은 숫자를 출력하되, 중복이 있다면 두번째로 작은 것을 출력해야 한다. 즉, 세번째부터는 고려하지 않아도 된다라는 것이다. 
- 그러면 처음 숫자와 바로 인접한 수를 비교하면서 같으면 count를 1증가하고, 또 그 다음 인접한 수를 비교하는 것을 반복하다가, 같지 않으면 해당 반복되는 숫자와 반복된 횟수를 make_pair로 쌍을 만들어 vfreq라는 새로운 2차원 벡터에 넣어준다. 
- 그런 다음, count를 초기화하고 다음 것부터 다시 비교를 시작하고 방금 했던 걸 반복한다.
- 그 다음 vfreq를 count(반복횟수) 순으로 내림차순, count(반복횟수)가 같을 시 v[i](반복되는 숫자) 숫자 순으로 오름차순 해준다.
- 왜냐하면, 같을 때 두번째 작은 숫자를 출력하라했기 때문에, 위에서 말한 것처럼 정렬한 후 vfreq 벡터에서 두번째 인덱스(1번 인덱스)의 반복되는 숫자(first)를 출력한다.
- 대신 같은게 없다면, 첫번째 인덱스(0번 인덱스)의 반복되는 숫자(first)를 출력한다.
4. 범위
- 마지막으로, 범위는 그냥 오름차순 된 숫자들 중 가장 마지막 인덱스의 숫자와 가장 처음 인덱스의 숫자를 뺀 것을 출력한다.



```c++
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#define endl endl

using namespace std;

//  백준 2108번: 통계학 (정렬, 구현)


// 1. 산술평균: 평균
// 2. 중앙값:   증가하는 순서로 나열했을 때 그 중앙에 위치하는 값
// 3. 최빈값:   가장 많이 나타나는 값, 여러 개->두번째로 작은 값
// 4. 범위:     최댓값 - 최솟값

bool compare(pair <int, int> p, pair <int, int> p2) {
    if (p.first == p2.first) return p.first < p2.first;
    return p.second > p2.second;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);

    int n; cin >> n;
    int num;
    vector<int> v;
    vector<pair<int, int> > vfreq;

    for (int i = 0; i < n; i++) {
        cin >> num;
        v.push_back(num);
    }

    sort(v.begin(), v.end());
    int sum = 0;
    int count = 1;
    int freq = 1;

    for (int i = 0; i < n; i++) sum += v[i];

    cout << round(float(sum) / n) << endl;           // 평균

    cout << v[n/2] << endl;                 // 중앙값


    for (int i = 0; i < v.size()-1; i++) {
        while(1) {
            if (v[i] != v[i+1]) break;
            count++;
            i++;
        }
        vfreq.push_back(make_pair(v[i], count));
        count = 1;
    }
    vfreq.push_back(make_pair(v[v.size()-1], count));   // v.size()-2 까지만 숫자를 넣으므로, 마지막 인덱스의 숫자를 따로 수행해줌.

    sort(vfreq.begin(), vfreq.end(), compare);

    // 입력이 하나만 주어졌을 때, 인접한 비교대상의 숫자가 없으므로
    if (n==1){
        cout << v[0] << endl;
        cout << int(v[n-1] - v[0]) << endl;    // 범위
    }
    else{
        if (vfreq[0].second == vfreq[1].second)   cout << vfreq[1].first << endl;     // 최빈값
        else                                      cout << vfreq[0].first << endl;
        cout << int(v[n-1] - v[0]) << endl;    // 범위
    }
    return 0;
}
```

