---
title: Programmers 3진법 뒤집기
description: 월간 코드 챌린지 시즌1
date: 2021-11-11 10:00:00 +0900
categories: [Algorithm, Programmers]
tags: [programmers, 프로그래머스, algorithm, c++]
---

# Programmers 3진법 뒤집기

- 최초 작성일: 2021년 11월 11일(수)
- 주소: <https://programmers.co.kr/learn/courses/30/lessons/68935>

## 목차

[TOC]

## 문제 설명

- 자연수 n이 매개변수로 주어집니다. n을 3진법 상에서 앞뒤로 뒤집은 후, 이를 다시 10진법으로 표현한 수를 return 하도록 solution 함수를 완성해주세요.


## 제한 사항

- n은 1 이상 100,000,000 이하인 자연수입니다.

## 입출력 예

| n    | result |
| ---- | ------ |
| 45   | 7      |
| 125  | 229    |

##### **입출력 예에 대한 설명**

- 입출력 예 #1

  - 답을 도출하는 과정은 다음과 같습니다.

  | n (10진법) | n (3진법) | 앞뒤 반전(3진법) | 10진법으로 표현 |
  | ---------- | --------- | ---------------- | --------------- |
  | 45         | 1200      | 0021             | 7               |

  - 따라서 7을 return 해야 합니다.

- 입출력 예 #2

  - 답을 도출하는 과정은 다음과 같습니다.

  | n (10진법) | n (3진법) | 앞뒤 반전(3진법) | 10진법으로 표현 |
  | ---------- | --------- | ---------------- | --------------- |
  | 125        | 11122     | 22111            | 229             |

  - 따라서 229를 return 해야 합니다.

## 풀이 방법

- 주어진 자연수 n에서 3으로 나눴을 때 나머지값을 빈 vector v에 하나씩 넣어준다.
- 그리고, n을 3으로 나눈 값을 다시 n으로 선언한다.
- 그럼 이미 vector에는 역순으로 저장이 된다.
- 그럼 0번 인덱스로부터 3진법을 10진법으로 바꾸는 방법대로 3의 제곱수들과 곱해 answer에 더해준다.
- 예를 들면, 3진법 2100 이란 수가 나왔다면, (2 * 3^3) + (1 * 3^2) + (0 * 3^1) + (0 * 3^0) = 52 + 9 + 0 + 0 = 61 이 출력된다.

---

```c++
#include <iostream>
#include <string>
#include <vector>
#include <cmath>

using namespace std;

int solution(int n) {
    int answer = 0;
    vector<int> v;
    
    while (n >= 3) {
        v.push_back(n % 3);
        n /= 3;
    }
    v.push_back(n);
    
    int num = v.size()-1;
    
    for (int i = 0; i < v.size(); i++) {
        answer += (v[i] * pow(3, num));
        num--;
    }
    
    return answer;
}
```