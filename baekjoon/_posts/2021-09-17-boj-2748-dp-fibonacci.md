---
layout: post
title: Baekjoon 2748 fibonacci number 2 (dp)
subtitle: 백준 2748 피보나치 수 2 (동적 계획법) (c++)
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: [star, fork, follow]
tags: [baekjoon, 백준, algorithm, dp]
comments: true
---

<<https://www.acmicpc.net/problem/2748>>

![image](https://user-images.githubusercontent.com/68185569/133781257-263004ba-099f-4af9-9e28-f7e781db7b50.png)


### 피보나치 수 2 (다이나믹 프로그래밍, 동적 계획법)



### 풀이 과정

+ 우선 피보나치 수는 이웃하는 두 수의 합이 다음 숫자가 되는 규칙으로 변화하는 숫자들을 나타낸다.
+ 피보나치 수는 아래와 같은 규칙으로 증가한다.
+ 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89 ...
+ 일단, 0, 1은 규칙을 적용할 수 없기 때문에, 임의로 0, 1번 인덱스에 직접 넣어준다.
+ 그 다음부터는 본인 위치에서 -1, -2 인덱스의 숫자를 더해가는 것을 반복한다.
+ n번째 숫자를 구하기 위해서는, n번째 피오나치 수를 저장해줄 fibonacci 배열을 선언해주고, fibo라는 함수로 현재 위치에서 -1, -2 위치의 숫자를 더해주기 위해 fibo함수를 재귀함수로 불러준다.
+ 입력값인 n은 90 미만으로 주어진다고 했는데, 피오나치 수를 나열한 것 중 90번 째의 숫자는 int로 cover가 안되기 때문에 long long을 사용해주어야 한다.

---


```c++
#include <iostream>
#define MAX 100
using namespace std;

long long fibonacci[MAX] = {0, 1,};

// 백준 2748: 피보나치 수 2

long long fibo(int n) {
    if (n==0 || n==1) return fibonacci[n];
    else if (fibonacci[n] == 0) fibonacci[n] = fibo(n-1) + fibo(n-2);
    return fibonacci[n];

}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);

    int n; cin >> n;

    cout << fibo(n) << "\n";;

    return 0;
}
```
