---
title: Programmers 없는 숫자 더하기
description: 월간 코드 챌린지 시즌3
date: 2021-10-26 10:00:00 +0900
categories: [Algorithm, Programmers]
tags: [programmers, 프로그래머스, algorithm, c++]
---

# Programmers 없는 숫자 더하기

- 최초 작성일: 2021년 10월 26일(화)
- 주소: <https://programmers.co.kr/learn/courses/30/lessons/86051>

## 목차



## 문제 설명

- 0부터 9까지의 숫자 중 일부가 들어있는 배열 `numbers`가 매개변수로 주어집니다. 

- numbers`에서 찾을 수 없는 0부터 9까지의 숫자를 모두 찾아 더한 수를 return 하도록 solution 함수를 완성해주세요..

  

## 제한사항

- 1 ≤ `numbers`의 길이 ≤ 9

- 0 ≤ `numbers`의 모든 수 ≤ 9

- `numbers`의 모든 수는 서로 다릅니다.

  

## 입출력 예

| numbers             | result |
| ------------------- | ------ |
| `[1,2,3,4,6,7,8,0]` | 14     |
| `[5,8,4,0,6,7,9]`   | 6      |

## 풀이 방법 1

- 주어지는 numbers들 중 0~9 사이의 숫자 중 없는 것을 골라 합을 구하는 문제로 아주 쉬운 문제이다.
- numbers 벡터를 돌며 0~9사이의 숫자와 비교하여 일치하는 순간 isvisited 라는 배열의 해당 숫자 인덱스의 값을 1로 바꿔주고 break하여 다음 작업을 이어서 한다.
- break를 하는 이유는, 예를 들어 해당 숫자가 5인 걸 알았다면, 6~9까지의 작업은 할 필요가 없기 때문이다.
- 그렇게 isvisited의 값들 중의 1이 아닌 것들의 수들을 더해 return한다.

---

```c++
#include <iostream>
#include <string>
#include <vector>

using namespace std;

int isvisited[10];

int solution(vector<int> numbers) {
    int answer = 0;

    for (auto n : numbers) {
        for (int i = 0; i < 10; i++) {
            if (n == i) {
                isvisited[i] = 1;
                break;
            }
        }
    }

    for (int i = 0; i < 10; i++) {
        if (isvisited[i] != 1) {
            answer += i;
        }
    }
    return answer;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0); cout.tie(0);

    vector<int> numbers = {1, 2, 3, 4, 6, 7, 8, 0};

    cout << solution(numbers) << '\n';

    return 0;
}
```
