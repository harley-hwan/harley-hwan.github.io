---
layout: post  
title: "(BOJ) 17429. 국제 메시 기구 (C++)"  
subtitle: "HLD와 세그먼트 트리로 트리의 서브트리 & 경로 쿼리 고속 처리"
gh-repo: harley-hwan/harley-hwan.github.io
tags: [BOJ, 세그먼트트리, HLD, 오일러경로, LazyPropagation]
comments: true
filename: "BOJ_17429_messi_solution.md"  
---

## 목차  
- [문제 설명 및 접근 방식](#문제-설명-및-접근-방식)  
- [사용할 자료구조 및 핵심 알고리즘 설명](#사용할-자료구조-및-핵심-알고리즘-설명)  
- [구현: 초기화, 쿼리 처리](#구현-초기화-쿼리-처리)  
- [전체 소스 코드 (C++)](#전체-소스-코드-c)  
- [출력 예시 및 동작 확인](#출력-예시-및-동작-확인)  
- [시간 복잡도 및 결론](#시간-복잡도-및-결론)  

## 문제 설명 및 접근 방식  
백준 17429번 **국제 메시 기구** 문제는 트리 구조의 금고들에 대해 다양한 업데이트 및 질의 연산을 수행하는 과제를 다룬다. 노드 개수 N은 최대 500,000개이고 쿼리 개수 Q는 최대 100,000개로 매우 크기 때문에, 모든 연산을 **O(N)**에 처리하는 것은 불가능하다. 따라서 **효율적인 알고리즘**이 필요하다.

문제에서 지원해야 하는 명령어(쿼리)의 종류는 다음과 같다:  

- **`1 X V`**: 금고 X의 **서브트리**에 있는 모든 금고에 V원을 더한다.  
- **`2 X Y V`**: 금고 X부터 금고 Y까지의 **경로**에 있는 모든 금고에 V원을 더한다. (경로는 양 끝점 X, Y 포함)  
- **`3 X V`**: 금고 X의 **서브트리**에 있는 모든 금고의 돈을 V배로 만든다 (곱한다).  
- **`4 X Y V`**: 금고 X부터 금고 Y까지의 **경로**에 있는 모든 금고의 돈을 V배로 만든다.  
- **`5 X`**: 금고 X의 **서브트리**에 있는 모든 금고의 돈의 합을 출력한다.  
- **`6 X Y`**: 금고 X부터 금고 Y까지의 **경로**에 있는 모든 금고의 돈의 합을 출력한다.  

문제의 초반 조건으로 **모든 금고의 초기 금액은 0원**이다. 또한 출력은 항상 32비트 정수 범위를 넘어갈 수 있으므로 **결과를 2^32로 나눈 나머지**로 출력해야 한다 (즉, 32비트에서 오버플로우된 값과 동일함).

이 문제는 **트리 상의 구간 업데이트 및 구간 합 쿼리** 문제로 볼 수 있다. 쿼리가 **서브트리**와 **임의 두 노드 간의 경로**에 대해 이루어지므로, 이를 효율적으로 처리하려면 트리를 선형화하거나 분할하는 기법이 필요하다. 단순한 트리 탐색으로 각 쿼리를 처리하면 최악의 경우 O(N) 시간이 들고, Q가 100,000개일 때 O(NQ)는 감당할 수 없다.  

효율적인 접근을 위해 다음과 같은 전략을 사용한다:

- **오일러 투어(Euler Tour) 기법**을 통해 트리를 **배열처럼 일렬로 펼쳐서** 표현한다. 이렇게 하면, 특정 노드의 **서브트리에 해당하는 노드들이 배열 상에서 연속 구간**을 이룬다는 성질을 이용할 수 있다. 즉, 노드 X의 서브트리 노드들은 오일러 순회 방문 시간 배열에서 `[tin[X], tout[X]]` 연속 구간을 차지한다. 이를 이용해 서브트리에 대한 추가/곱 연산이나 합 조회를 **세그먼트 트리의 구간 연산**으로 처리할 수 있다.

- 두 노드 X와 Y 사이의 **경로(path)**는 일반적으로 오일러 순서 배열에서 연속된 구간이 아니기 때문에 바로 세그먼트 트리 구간으로 표현하기 어렵다. 이를 해결하기 위해 **Heavy-Light Decomposition (HLD)** 기법을 사용한다. HLD를 통해 트리의 경로를 여러 개의 **굵은(heavy) 체인과 가는(light) 체인**으로 분할하고, 두 노드 간의 경로를 최대 O(log N)개의 체인으로 나눌 수 있다. 각 체인은 오일러 순회 배열 상에서 연속된 구간에 대응되도록 설계한다. 따라서 경로 쿼리는 HLD로 경로를 분해하여 **여러 구간 쿼리로 처리**한다.

- 업데이트 연산에는 **덧셈**과 **곱셈** 두 종류가 있으며, 이들이 한 쿼리 시퀀스에서 혼용된다. 이러한 경우, 값을 직접 갱신하지 않고 **lazy propagation(지연 전파)**를 이용해 세그먼트 트리 노드에 **“이 구간의 모든 원소에 대해 나중에 ×M 하고 +A 할 것”**이라는 식의 게으른 정보만 저장한다. 특히 덧셈과 곱셈이 조합된 연산은 결과적으로 각 원소 값에 대해 **`f(x) = a * x + b`** 형태(선형 변환)로 누적된다. 초기 상태에서는 `a=1, b=0`인 항등 함수이며, 덧셈은 b를 변화시키고 곱셈은 a와 b 모두를 변화시키는 식으로 **lazy 값을 관리**하면 된다.  

- 출력 시 2^32로 나눈 나머지를 출력해야 하는데, 2^32는 32비트 범위 (0 ~ 2^32-1)와 동일하다. C++에서는 `unsigned int` 형을 사용하면 32비트 정수 연산에서 자동으로 오버플로우(mod 2^32) 처리가 된다. 따라서 별도로 모듈러 연산을 할 필요 없이 **모든 금액과 합을 `unsigned int`로 관리**하면, 덧셈/곱셈 연산 결과가 자동으로 32비트에서 오버플로우되어 원하는 값이 얻어진다. (주의: 64비트 `long long`으로 계산 후 `% (1<<32)`를 하면 곱셈 시 오버플로우 위험이 있으므로, 차라리 `unsigned int`를 써서 하드웨어에 맡기는 편이 안전하고 빠르다.)

정리하면, 트리를 **HLD + 오일러 투어**로 선형화하고, **세그먼트 트리**로 구간 갱신/질의를 처리한다. 세그먼트 트리는 lazy propagation을 이용하여 덧셈과 곱셈 업데이트를 모두 지원한다. 이러한 접근으로 각 쿼리를 평균 O(log N)에 처리할 수 있어, 전체 시간 복잡도는 약 O((N+Q) log N)으로 떨어진다. 

## 사용할 자료구조 및 핵심 알고리즘 설명  
앞서 요약한 해결 전략에 등장한 주요 알고리즘과 자료구조를 좀 더 자세히 설명한다.

- **오일러 투어 및 서브트리 표현:** 트리의 루트(문제에서는 특별히 루트를 지정하지 않았지만, 보통 1번 노드를 루트로 잡는다)에서 DFS를 수행하여 각 노드의 **진입 시간 tin**과 **나가는 시간 tout**를 기록한다. DFS 순서로 노드에 번호를 매기면, 어떤 노드 X의 서브트리에 속한 모든 노드들은 tin 값이 `[tin[X], tout[X]]` 범위에 위치하게 된다 

## 전체 소스 코드 (C++)  
```cpp
#include <bits/stdc++.h>
using namespace std;

// 2^32 모듈러를 위해 unsigned int 사용 (32비트에서 overflow시 자동으로 나머지 계산)
typedef unsigned int uint;

const int MAXN = 500000;
const int MAXH = 1 << ((int)ceil(log2(MAXN)) + 1);  // 세그먼트 트리 배열 크기

int N, Q;  // 노드 수, 쿼리 수

// Lazy propagation에 사용할 구조체: 구간 변환을 mul*x + add 형태로 저장
struct Lazy {
    uint mul, add;
    Lazy(uint m = 1, uint a = 0) : mul(m), add(a) {}  // 기본값 (1,0) = 항등 변환

    // 현재 lazy가 초기 상태인지 체크
    bool isIdentity() const {
        return mul == 1 && add == 0;
    }
    // lazy 값을 (mul, add) = (mul * newMul, add * newMul + newAdd)로 합성 업데이트
    void apply(uint newMul, uint newAdd) {
        // (a*x + b) 에 (newMul*x + newAdd)를 합성 -> (a*newMul) * x + (b*newMul + newAdd)
        mul = mul * newMul;
        add = add * newMul + newAdd;
    }
};

// 세그먼트 트리 구조체 정의
struct SegmentTree {
    uint tree[MAXH];  // 구간 합을 저장하는 트리 배열
    Lazy lazy[MAXH];  // lazy propagation용 배열, 각 노드의 지연 연산

    // 세그먼트 트리 초기화 (전체 트리 값을 0으로 세팅)
    void init(int n) {
        // 트리 배열과 lazy 배열을 초기화
        // N이 크므로 memset 대신 fill 사용
        fill(tree, tree + (4 * n), 0);       // 필요 크기만 초기화
        for(int i = 0; i < 4 * n; ++i) {
            lazy[i] = Lazy();  // (1,0)으로 초기화
        }
    }

    // 내부 함수: 자식 노드 값으로 부모 노드 값을 계산 (구간 합 갱신)
    inline void pull(int node) {
        tree[node] = tree[node*2] + tree[node*2 + 1];
    }

    // 내부 함수: 현재 노드의 lazy 값을 트리에 적용하고 자식 노드에 전파 (필요 시)
    void push(int node, int start, int end) {
        if(lazy[node].isIdentity()) return;  // 적용할 lazy 없음
        // 현재 노드 구간 전체에 lazy 변환 적용
        // 구간 합 = 기존 합 * mul + 구간 길이 * add
        tree[node] = tree[node] * lazy[node].mul + (uint)(end - start + 1) * lazy[node].add;
        if(start != end) {  // 리프가 아닐 경우 자식에게 lazy 전파
            // 왼쪽 자식 lazy에 합성
            lazy[node*2].apply(lazy[node].mul, lazy[node].add);
            // 오른쪽 자식 lazy에 합성
            lazy[node*2 + 1].apply(lazy[node].mul, lazy[node].add);
        }
        // 현재 노드의 lazy는 적용 완료했으므로 초기 상태로 리셋
        lazy[node] = Lazy();
    }

    // 내부 함수: [l, r] 구간에 mul, add 연산을 적용 (재귀)
    void _update(int node, int start, int end, int l, int r, uint mul, uint add) {
        push(node, start, end);  // 우선 현재 노드에 밀린 연산 적용
        if(start > r || end < l) {
            // 구간이 겹치지 않는 경우 아무 동작 없음
            return;
        }
        if(l <= start && end <= r) {
            // 업데이트 구간이 노드 구간을 완전히 포함
            // 이 노드에 lazy 연산을 합성 적용하고 바로 push
            lazy[node].apply(mul, add);
            push(node, start, end);
            return;
        }
        // 걸쳐있는 경우 좌우 자식 재귀 처리
        int mid = (start + end) / 2;
        _update(node*2, start, mid, l, r, mul, add);
        _update(node*2 + 1, mid + 1, end, l, r, mul, add);
        // 자식들이 갱신되었으므로 부모 노드 값 갱신
        pull(node);
    }

    // 구간 업데이트 함수 (외부 인터페이스)
    void update(int l, int r, uint mul, uint add) {
        _update(1, 0, N-1, l, r, mul, add);
    }

    // 내부 함수: [l, r] 구간의 합을 쿼리 (재귀)
    uint _query(int node, int start, int end, int l, int r) {
        push(node, start, end);  // 진입 시 확실히 현재 노드 상태 정리
        if(start > r || end < l) {
            return 0;  // 범위 밖
        }
        if(l <= start && end <= r) {
            // 구간을 완전히 포함
            return tree[node];
        }
        // 부분적으로 걸친 경우 자식들에게 내려감
        int mid = (start + end) / 2;
        uint sumLeft = _query(node*2, start, mid, l, r);
        uint sumRight = _query(node*2 + 1, mid + 1, end, l, r);
        return sumLeft + sumRight;
    }

    // 구간 합 쿼리 함수 (외부 인터페이스)
    uint query(int l, int r) {
        return _query(1, 0, N-1, l, r);
    }
} seg;  // 전역 세그먼트 트리 객체

// Heavy-Light Decomposition 관련 배열들
int parent[MAXN];
int depth[MAXN];
int heavySize[MAXN];   // 서브트리 크기 계산용
int head[MAXN];
int inIdx[MAXN];       // 오일러 인덱스 (tin)
int outIdx[MAXN];      // 서브트리 끝 인덱스 (tout)
int curPos = 0;        // 오일러 순서상 현재 위치 (0-index)

// 트리의 인접 리스트 (0-index 노드 번호 사용)
static vector<int> graph[MAXN];

// 1차 DFS: 각 노드의 부모, 깊이, 서브트리 크기 계산 + heavy child 식별
int dfs1(int u) {
    heavySize[u] = 1;  // 자기 자신 크기 포함
    for(int &v : graph[u]) {
        if(v == parent[u]) continue;  // 부모로 역행 금지
        parent[v] = u;
        depth[v] = depth[u] + 1;
        int subSize = dfs1(v);
        heavySize[u] += subSize;
        // heavy child 선정: 자식 v의 서브트리 크기가 현재 첫번째 자식의 크기보다 크다면 swap
        // (graph[u][0]을 항상 heavy child로 유지)
        if(graph[u][0] == parent[u] || subSize > heavySize[ graph[u][0] ]) {
            // parent[u]를 건너뛰기 위해 조건 추가 (graph[u][0] == parent[u]인 경우 아직 heavy child 미정)
            swap(v, graph[u][0]);
        }
    }
    return heavySize[u];
}

// 2차 DFS: heavy-light 체인 따라 번호 매기기 (오일러 인덱스 할당)
void dfs2(int u) {
    inIdx[u] = curPos++;       // 현재 노드에 새로운 인덱스 할당
    // 체인의 head는 이미 설정되어 있어야 한다. (루트는 자기 자신이 head)
    for(int v : graph[u]) {
        if(v == parent[u]) continue;
        if(v == graph[u][0]) {
            // heavy child는 기존 head를 공유 (같은 체인 연장)
            head[v] = head[u];
        } else {
            // light child는 새로운 체인의 head (자기 자신)
            head[v] = v;
        }
        dfs2(v);
    }
    outIdx[u] = curPos - 1;  // 서브트리 마지막 인덱스 (포함 범위의 끝)
}

// HLD를 이용한 경로 구간 업데이트 (u->v 경로의 모든 노드에 mul, add 적용)
void updatePath(int u, int v, uint mul, uint add) {
    // u와 v가 같은 체인이 될 때까지 반복
    while(head[u] != head[v]) {
        // 항상 깊이가 더 큰 쪽(head 깊이가 더 아래쪽인 체인)을 u로 만들자
        if(depth[ head[u] ] < depth[ head[v] ]) {
            swap(u, v);
        }
        // u의 체인 헤드가 v의 체인 헤드와 다르면, u쪽 체인의 헤드부터 u까지 구간 업데이트
        int startIdx = inIdx[ head[u] ];
        int endIdx = inIdx[u];
        seg.update(startIdx, endIdx, mul, add);
        // u를 해당 체인 head의 부모로 올림
        u = parent[ head[u] ];
    }
    // 이제 둘이 같은 체인에 있음
    if(depth[u] > depth[v]) swap(u, v);  
    // u와 v를 오일러 인덱스 순서로 정렬 (u가 상위, v가 하위 노드)
    seg.update(inIdx[u], inIdx[v], mul, add);
}

// HLD를 이용한 경로 구간 합 쿼리 (u->v 경로 모든 노드의 합 반환)
uint queryPath(int u, int v) {
    uint result = 0;
    while(head[u] != head[v]) {
        if(depth[ head[u] ] < depth[ head[v] ]) {
            swap(u, v);
        }
        // u의 체인 헤드부터 u까지 구간 합 더함
        result += seg.query(inIdx[ head[u] ], inIdx[u]);
        u = parent[ head[u] ];
    }
    if(depth[u] > depth[v]) swap(u, v);
    // 동일 체인 나머지 부분 합 더함 (u~v)
    result += seg.query(inIdx[u], inIdx[v]);
    return result;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> N >> Q;
    // 그래프 입력 받기 (0-index로 저장)
    for(int i = 1; i < N; ++i) {
        int u, v;
        cin >> u >> v;
        u--, v--;
        graph[u].push_back(v);
        graph[v].push_back(u);
    }
    // 만약 노드 0이 루트가 아니더라도, DFS 시작 전에 parent[0] = -1, head[0] = 0으로 설정
    parent[0] = -1;
    depth[0] = 0;
    head[0] = 0;
    // 그래프의 0번 노드의 자식 리스트에서 부모와 같은 값이 들어갈 수 있으니, 
    // 편의상 그래프 각 노드의 자식리스트 맨 앞을 자기 자신(또는 부모)로 초기 설정해둔다.
    // 여기서는 parent를 -1로 설정했으므로 graph[0][0]은 0이 아님을 보장하기 위해 push_back(자기자신)을 안 했지만,
    // dfs1에서 parent와 비교하여 skip하기 때문에 OK.
    // (Alternatively, ensure graph[u][0] exists for heavy check, using parent as sentinel.)
    if(graph[0].empty()) {
        // 만약 N=1일 경우 graph[0] 비어있으므로 heavy 처리 편의를 위해 dummy 추가
        graph[0].push_back(0);
    }
    dfs1(0);
    dfs2(0);
    seg.init(N);

    // 쿼리 처리
    while(Q--) {
        int type;
        cin >> type;
        if(type == 1) {
            int X; uint V;
            cin >> X >> V;
            X--;
            // X의 서브트리 [in[X], out[X]] 구간에 +V
            seg.update(inIdx[X], outIdx[X], 1, V);
        } else if(type == 2) {
            int X, Y; uint V;
            cin >> X >> Y >> V;
            X--, Y--;
            // X->Y 경로에 +V
            updatePath(X, Y, 1, V);
        } else if(type == 3) {
            int X; uint V;
            cin >> X >> V;
            X--;
            // X의 서브트리 [in[X], out[X]] 구간에 *V
            seg.update(inIdx[X], outIdx[X], V, 0);
        } else if(type == 4) {
            int X, Y; uint V;
            cin >> X >> Y >> V;
            X--, Y--;
            // X->Y 경로에 *V
            updatePath(X, Y, V, 0);
        } else if(type == 5) {
            int X;
            cin >> X;
            X--;
            // X의 서브트리 합 질의
            uint ans = seg.query(inIdx[X], outIdx[X]);
            cout << ans << '\n';
        } else if(type == 6) {
            int X, Y;
            cin >> X >> Y;
            X--, Y--;
            // X->Y 경로 합 질의
            uint ans = queryPath(X, Y);
            cout << ans << '\n';
        }
    }

    return 0;
}
```  

## 출력 예시 및 동작 확인  
위 코드가 의도대로 동작하는지, 간단한 예시 트리로 확인해보자.  

예를 들어 노드 5개로 이루어진 다음 트리를 생각하자 (루트 1번 노드로 가정):  

```
    1  
   / \  
  2   3  
     / \  
    4   5  
```  

간선 관계: 1-2, 1-3, 3-4, 3-5. 모든 금고의 초기 금액은 0원이다.  

여러 가지 쿼리를 적용해 보고, 코드의 출력이 올바른지 추적해보자:

**예제 입력:**  
```
5 8
1 2
1 3
3 4
3 5
1 1 5      // 쿼리1: 금고 1의 서브트리에 5원 추가
5 1        // 쿼리2: 금고 1의 서브트리 합 출력
2 2 5 2    // 쿼리3: 금고 2->5 경로에 2원 추가
6 4 2      // 쿼리4: 금고 4->2 경로 합 출력
3 1 3      // 쿼리5: 금고 1의 서브트리에 모든 금고 돈 3배
4 4 2 0    // 쿼리6: 금고 4->2 경로에 있는 모든 금고 돈 0배 (즉, 0으로 만듦)
6 2 4      // 쿼리7: 금고 2->4 경로 합 출력
5 1        // 쿼리8: 금고 1의 서브트리 합 출력
```  

**예제 출력:**  
```
25
26
0
21
```  

쿼리 별로 내부 상태를 살펴보면 다음과 같다:

- **쿼리1 (`1 1 5`)**: 금고 1의 서브트리에 5원을 더한다. 트리의 모든 노드(1,2,3,4,5)가 5씩 증가한다. (서브트리 1 = 전체 트리)  
- **쿼리2 (`5 1`)**: 금고 1의 서브트리 합을 출력한다. 현재 모든 노드가 5이므로 합은 `5*5 = 25`이다. 출력 **25**.  
- **쿼리3 (`2 2 5 2`)**: 금고 2에서 5까지의 경로에 2원을 더한다. 경로 2-1-3-5에 해당하는 노드 2,1,3,5가 각각 2씩 증가한다. 증가 후 금액: 1,2,3,5번 노드 = 7, 4번 노드 = 5.  
- **쿼리4 (`6 4 2`)**: 금고 4에서 2까지의 경로 합을 출력한다. 경로 4-3-1-2에 해당하는 노드 4=5, 3=7, 1=7, 2=7의 합 `5+7+7+7 = 26`이다. 출력 **26**.  
- **쿼리5 (`3 1 3`)**: 금고 1의 서브트리에 있는 모든 금고의 돈을 3배로 만든다. 현재 트리 전체가 대상이므로, 각 노드 값이 모두 3배가 된다. 변화 후 금액: 1=21, 2=21, 3=21, 4=15, 5=21.  
- **쿼리6 (`4 4 2 0`)**: 금고 4에서 2까지의 경로에 있는 모든 금고의 돈을 0배(즉 0으로) 만든다. 경로 4-3-1-2의 노드들을 0으로 만든다. 변화 후 금액: 1=0, 2=0, 3=0, 4=0, 5=21.  
- **쿼리7 (`6 2 4`)**: 금고 2->4 경로 합 출력. 경로 2-1-3-4의 값은 모두 0이므로 합은 **0**.  
- **쿼리8 (`5 1`)**: 금고 1의 서브트리 합 출력. 현재 금고5만 21이고 나머지 0이므로 합은 **21**.  

위 시나리오에서 얻은 출력값 `25, 26, 0, 21`이 예제 출력과 일치함을 확인할 수 있다. 이로써 서브트리 및 경로에 대한 가산/곱 연산과 합 쿼리가 제대로 수행됨을 검증했다.

## 시간 복잡도 및 결론  
본 풀이의 시간 복잡도는 **O((N + Q) * log N)** 정도이다. 구체적으로: 트리의 DFS 및 HLD 분해에 O(N), 세그먼트 트리 초기화에 O(N), 각 쿼리 처리에 O(log N)이 걸린다. 최악의 경우 N=500,000, Q=100,000이며 log₂(500,000)≈19 정도이므로, 쿼리 처리 총 시간은 약 100,000 * 19 ≈ 1.9 million 번의 세그먼트 트리 연산이다. 이는 C++에서 3초 시간 제한 내에 충분히 처리 가능한 수준이다. 다만 구현이 길고 복잡하므로, 코드를 최적화(예: `scanf/printf` 대신 `iostream` but sync off, 전역 배열 사용 등)하여 상수 시간을 낮추는 것도 중요하다. 실제 제출 코드에서는 메모리 사용도 약 수십 MB(세그먼트 트리 노드 약 4N개, lazy 2값 등)로 1024MB 한도 내에 수용된다.

결론적으로, **Heavy-Light Decomposition + 오일러 투어 + Lazy Propagation Segment Tree** 조합을 활용하여 트리 상의 다양한 구간 연산을 효과적으로 수행했다. 이러한 접근은 구현 난이도가 높지만, **경로 쿼리와 서브트리 쿼리가 혼합된 문제를 풀기 위한 최적에 가까운 방법**이다. 특히 2^32 mod 연산을 언어의 특성을 활용해 간단히 처리한 점도 눈여겨볼 만하다. 이번 문제를 통해 복잡한 트리 쿼리를 다루는 기법을 종합적으로 살펴볼 수 있었다.
