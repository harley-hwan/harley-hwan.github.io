---
layout: post
title: Baekjoon 2437 저울 (그리디)
subtitle: 백준 2437 저울 (그리디) (c++)
gh-repo: harley-hwan/harley-hwan.github.io
gh-badge: [star, fork, follow]
tags: [baekjoon, 백준, algorithm, greedy]
comments: true
---

<https://www.acmicpc.net/problem/2437>

![image](https://user-images.githubusercontent.com/68185569/133775215-3b6ccc8a-16ea-4782-9f0d-99c226d3c20b.png)




### 저울 (그리디 알고리즘 & 정렬)
+ 주어진 추들로 측정할 수 없는 양의 정수 무게 중 최솟값 구하기




### 풀이 과정

+ 이 문제는 주어진 추들로 측정할 수 없는 양의 정수 무게 중 최솟값을 구하는 문제이다.
+ 처음에 이 문제를 풀 때, 나는 주어진 저울추로 모든 조합을 만들어보고, 그것을 오름차순으로 정렬하여 무게 1부터 쭉 증가하면서 없는 조합을 찾아 그것을 출력하면 된다고 생각했다.
+ 하지만 이 방법은 비효율적인 방법이었꼬, 메모리 초과의 결과를 가져왔다.
+ 아래의 코드가 실패했던 코드이다.



```c++
// 메모리 초과

int wt[1001];
int nums[1001];
vector<int> psbNums;

int n, w, sum;

void comb(int num, int idx, int k) {
    if (idx > k)
    {
        sum = 0;
        for (int i = 1; i <= k; i++) sum += nums[i];
        psbNums.push_back(sum);
        return;
    }

    if (num > n) return;
    
    nums[idx] = wt[num];

    comb(num + 1, idx + 1, k);
    comb(num + 1, idx, k);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);

    cin >> n;
    
    for (int i = 1; i <= n; i++) { 
        cin >> wt[i];
    }
    
    for(int i = 1; i <= n; i++) {
        comb(1, 1, i);
    }    
    sort(psbNums.begin(), psbNums.end());
    psbNums.erase(unique(psbNums.begin(), psbNums.end()), psbNums.end());

    // for(int i = 0; i < psbNums.size(); i++) {
    //     cout << psbNums[i] << " ";
    // }
    int cnt = 1;
    for (int i = 0; i < psbNums.size(); i++) {
        if (psbNums[i] != cnt) {
            cout << cnt << "\n";
            return 0;
        }
        cnt++;
    }

    return 0;
}
```



+ 그래서 다른 방법을 생각해보았고, 일단 저울추를 제일 작은 것부터 이용해야한다 생각하여 주어진 저울추를 오름차순으로 정렬해주었다.
+ 그리고나서 아래와 같은 규칙을 적용했다.
  
    + 내가 가진 저울추로 1~K무게 모두 만들 수 있다 가정.
    + 다음 저울추 (1)가 K무게보다 같거나 작으면,
    + 다음 추로 (1 + L) ~ (K + L) 무게를 모두 만들 수 있다.
    + 그러므로, 총 1 ~ (K + L)무게를 모두 만들 수 있다가 된다.

+ 이걸 다시 이해하기 쉽게 설명하자면, 
    + 1, 2, 3, 4 무게를 만들수 있따.
    + 다음 저울추가 5면 -> 5, 6, 7, 8, 9 무게를 만들 수 있다.
    + 따라서 1 ~ 9 무게 모두 만들 수 있다.
    + 하지만 다음 추가 6이면 무게 5는 불가능.



```c++
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

// 백준 2437번: 저울 (그리디 알고리즘, 정렬)

int n;
int arr[1001];

int main() {

    // 저울추 입력
    cin >> n;
    for (int i = 0; i < n; i++) cin >> arr[i];

    // 저울추 정렬
    sort(arr, arr + n);

    int answer = 1;
    for (int i = 0; i < n; i++) {
        if (arr[i] > answer) break;
        answer += arr[i];
        cout << "arr[i]: " << arr[i] << "\n";
        cout << "answer: " << answer << "\n";
    }
    cout << answer;
    return 0;
}

```
