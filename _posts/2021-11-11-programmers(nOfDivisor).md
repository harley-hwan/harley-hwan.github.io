---
title: Programmers 약수의 개수와 덧셈
description: 월간 코드 챌린지 시즌2
date: 2021-11-11 10:00:00 +0900
categories: [Algorithm, Programmers]
tags: [programmers, 프로그래머스, algorithm, c++]
---

# Programmers 약수의 개수와 덧셈

- 최초 작성일: 2021년 11월 11일(수)
- 주소: <https://programmers.co.kr/learn/courses/30/lessons/77884>

## 목차

[TOC]

## 문제 설명

- 두 정수 `left`와 `right`가 매개변수로 주어집니다. `left`부터 `right`까지의 모든 수들 중에서, 약수의 개수가 짝수인 수는 더하고, 약수의 개수가 홀수인 수는 뺀 수를 return 하도록 solution 함수를 완성해주세요.

## 제한 사항

- 1 ≤ `left` ≤ `right` ≤ 1,000

## 입출력 예

| left | right | result |
| ---- | ----- | ------ |
| 13   | 17    | 43     |
| 24   | 27    | 52     |

##### **입출력 예에 대한 설명**

- **입출력 예 #1**	

  - 다음 표는 13부터 17까지의 수들의 약수를 모두 나타낸 것입니다.

  | 수   | 약수           | 약수의 개수 |
  | ---- | -------------- | ----------- |
  | 13   | 1, 13          | 2           |
  | 14   | 1, 2, 7, 14    | 4           |
  | 15   | 1, 3, 5, 15    | 4           |
  | 16   | 1, 2, 4, 8, 16 | 5           |
  | 17   | 1, 17          | 2           |

  - 따라서, 13 + 14 + 15 - 16 + 17 = 43을 return 해야 합니다.

- **입출력 예 #2**

  - 다음 표는 24부터 27까지의 수들의 약수를 모두 나타낸 것입니다.

  | 수   | 약수                     | 약수의 개수 |
  | ---- | ------------------------ | ----------- |
  | 24   | 1, 2, 3, 4, 6, 8, 12, 24 | 8           |
  | 25   | 1, 5, 25                 | 3           |
  | 26   | 1, 2, 13, 26             | 4           |
  | 27   | 1, 3, 9, 27              | 4           |

  - 따라서, 24 - 25 + 26 + 27 = 52를 return 해야 합니다.

## 풀이 방법

- 주어진 left에서 right까지 모두 돌며, 해당 숫자의 약수의 갯수를 세어 약수의 갯수가 짝수면 answer에 더해주고, 홀수면 빼준다.
- 간단한 문제다.

---

```c++
#include <string>
#include <vector>

using namespace std;

int howMany(int n) {
    int count = 0;
    for (int i = 1; i <= n; i++) {
        if ((n % i) == 0) {
            count++;
        }
    }
    return count;
}

int solution(int left, int right) {
    int answer = 0;
    
    for (int i = left; i <= right; i++) {
        if (howMany(i) % 2 == 0) 
            answer += i;
        else 
            answer -= i;
    }
    return answer;
}
```