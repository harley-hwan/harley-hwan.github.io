---
title: Programmers 실패율
description: 2019 KAKO BLIND RECRUITMENT
date: 2021-11-10 10:00:00 +0900
categories: [Algorithm, Programmers]
tags: [programmers, 프로그래머스, algorithm, c++]
---

# Programmers 

- 최초 작성일: 2021년 11월 10일(수)
- 주소: <https://programmers.co.kr/learn/courses/30/lessons/42889>

## 

- 슈퍼 게임 개발자 오렐리는 큰 고민에 빠졌다. 그녀가 만든 프랜즈 오천성이 대성공을 거뒀지만, 요즘 신규 사용자의 수가 급감한 것이다. 원인은 신규 사용자와 기존 사용자 사이에 스테이지 차이가 너무 큰 것이 문제였다
- 이 문제를 어떻게 할까 고민 한 그녀는 동적으로 게임 시간을 늘려서 난이도를 조절하기로 했다. 역시 슈퍼 개발자라 대부분의 로직은 쉽게 구현했지만, 실패율을 구하는 부분에서 위기에 빠지고 말았다. 오렐리를 위해 실패율을 구하는 코드를 완성하라.
  - 실패율은 다음과 같이 정의한다.
    - 스테이지에 도달했으나 아직 클리어하지 못한 플레이어의 수 / 스테이지에 도달한 플레이어 수
- 전체 스테이지의 개수 N, 게임을 이용하는 사용자가 현재 멈춰있는 스테이지의 번호가 담긴 배열 stages가 매개변수로 주어질 때, 실패율이 높은 스테이지부터 내림차순으로 스테이지의 번호가 담겨있는 배열을 return 하도록 solution 함수를 완성하라.
- 

## 

- 스테이지의 개수 N은 `1` 이상 `500` 이하의 자연수이다.

- stages의 길이는 `1` 이상 `200,000` 이하이다.

- stages에는 `1` 이상  `N + 1` 이하의 자연수가 담겨있다.

  - 각 자연수는 사용자가 현재 도전 중인 스테이지의 번호를 나타낸다.
  - 단, `N + 1` 은 마지막 스테이지(N 번째 스테이지) 까지 클리어 한 사용자를 나타낸다.

- 만약 실패율이 같은 스테이지가 있다면 작은 번호의 스테이지가 먼저 오도록 하면 된다.

- 스테이지에 도달한 유저가 없는 경우 해당 스테이지의 실패율은 `0` 으로 정의한다.

  

## 

| N    | stages                   | result      |
| ---- | ------------------------ | ----------- |
| 5    | [2, 1, 2, 6, 2, 4, 3, 3] | [3,4,2,1,5] |
| 4    | [4,4,4,4,4]              | [4,1,2,3]   |

## 

- 우선, 계산의 편의를 위해 주어진 stages 벡터를 오름차순으로 정렬해준다.
- 정렬된 stages를 처음부터 돌며, 임의로 1이라고 선언해준 num 변수를 증가시키면서 비교하여, arr 빈배열에 num을 인덱스로 하여 해당 인덱스의 값을 증가시켜준다.
- 예를 들어, stages = {2, 1, 2, 6, 2, 4, 3, 3} 이 주어졌다면, arr[1] = 1, arr[2] = 3, arr[3] = 2. arr[4] = 1, arr[5] = 0, arr[6] = 1 이런식으로 된다.
- 그 다음 NN 이라는 정수 변수에 stages의 사이즈(처음 사용자 수)를 선언해주고, 주어진 N (스테이지 갯수) 만큼 arr배열을 돌며, 아래의 연산을 반복하며 ( (double)해당 인덱스의 값 / NN, 인덱스) 형태로 pair를 만들어 answer 2중 벡터에 차례대로, 넣어준다.
- 해당 인덱스의 값 / NN 을 수행했으면, NN - 해당 인덱스의 값을 해준다. 다시 말해, 총 8명의 플레이어 중 1명이 1단계를 클리어 못했다면, 다음 단계에서는 1명을 뺀 나머지 7명 중에서 확률을 구해야 한다.
- 그렇게 2중 벡터가 완성이 되면, 거기서 확률을 기준으로 내림차순 해주고, 같은 확률일 때에는 인덱스 기준으로 오름차순 해준다.
- 마지막으로, 정렬된 answer 2중 벡터에서 second 값들만 따로 result 빈 벡터에 넣어주어 출력해준다.

* 처음에 그냥 sort로 정렬해주었을 때에는 자꾸 테스트 케이스에서 틀렸다고 나와 뭐가 틀렸는지 몰라 해매다가 단지 sort를 stable_sort로만 바꿔주었는데 모든 테스트 케이스를 통과했다. 솔직히 이해안된다.

---

```c++
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

using namespace std;

int arr[501];
int brr[501];

bool compare(pair<double, int> a, pair<double, int> b){
    if (a.first == b.first){
        return a.second < b.second;
    }
    else
        return a.first > b.first;
}

vector<int> solution(int N, vector<int> stages) {
    vector<pair<double, int> > answer;
    vector<int> result;

    sort(stages.begin(), stages.end());
    
    int num = 1;
    for (int i = 0; i < stages.size(); i++) {
        while(1) {
            if (stages[i] == num) {
                arr[num]++;
                break;
            }  
            else
                num++;
        }
    }
    int NN = stages.size();
    
    for (int i = 1; i <= N; i++) {
        answer.push_back(make_pair((double)arr[i] / NN, i));
        NN -= arr[i];
    }

    stable_sort(answer.begin(), answer.end(), compare);

    for (auto x : answer)
        result.push_back(x.second);
    
    return result;
}
```
