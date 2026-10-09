---
title: "(C++) 로또 번호 랜덤 추출"
description: "재미로 짠 코드인데 정리하다 보니 rand() 대신 <random>을 써야 하는 이유, 모듈로 편향, 그리고 난수를 쓰는 코드는 시드를 남겨야 재현이 된다는 얘기까지 오게 됐다."
date: 2023-02-16 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, lotto, random, algorithm, mt19937, shuffle]
math: true
---
## 재미로 만든 것

재미로 만든 거니 안 됐다고 탓하지 마세요.

1부터 45까지 넣은 벡터를 섞어서 앞의 6개를 뽑는다.

```c++
#include <iostream>
#include <vector>
#include <algorithm>
#include <random>

int main() {
    // 난수 엔진 초기화
    std::random_device rd;
    std::mt19937 gen(rd());

    // 1부터 45까지의 숫자를 저장하는 벡터 생성
    std::vector<int> numbers(45);
    for (int i = 0; i < 45; i++) {
        numbers[i] = i + 1;
    }

    // 벡터를 무작위로 섞음
    std::shuffle(numbers.begin(), numbers.end(), gen);

    // 벡터에서 첫 6개의 요소를 선택하여 로또 번호로 출력
    std::cout << "로또 추천 번호: ";
    for (int i = 0; i < 6; i++) {
        std::cout << numbers[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}
```

`std::random_shuffle`은 C++14에서 폐기 예정이 되고 C++17에서 표준에서 빠졌다. 대신 `std::shuffle`과 `<random>`을 쓴다.

## rand()로 짜면 왜 안 되나

처음엔 이렇게 짜려고 했다.

```c++
srand(time(0));
int n = rand() % 45 + 1;
```

익숙한 코드인데 문제가 몇 개 있다.

**모듈로 편향.** `rand()`가 0부터 `RAND_MAX`까지 균등하게 준다고 해도, 그걸 45로 나눈 나머지는 균등하지 않다. MSVC의 `RAND_MAX`는 32767이고, 32768을 45로 나누면 728 나머지 8이다. 즉 0~7에 해당하는 값이 729번 나올 수 있고 8~44는 728번이다. 앞쪽 숫자가 아주 조금 더 자주 나온다.

차이가 0.1%대라 로또에는 별 상관없지만, 시뮬레이션에서 이런 편향은 결과를 왜곡한다.

**시드의 해상도.** `time(0)`은 초 단위다. 같은 초 안에 프로그램을 두 번 실행하면 완전히 같은 결과가 나온다. 스크립트로 여러 번 돌리면 바로 티가 난다.

**주기와 품질.** `rand()`의 구현은 표준이 정하지 않는다. 흔한 구현인 선형 합동 생성기는 하위 비트의 주기가 짧아서, `rand() % 2`가 0과 1을 번갈아 내는 경우까지 있었다.

**스레드 안전하지 않다.** 내부 상태를 전역으로 들고 있어서 여러 스레드에서 부르면 상태가 꼬인다.

## <random>의 구성

`<random>`은 역할을 둘로 나눈다.

- **엔진**: 균등한 비트열을 만든다 (`std::mt19937` 등)
- **분포**: 그 비트열을 원하는 범위와 모양으로 바꾼다 (`std::uniform_int_distribution` 등)

```c++
std::random_device rd;
std::mt19937 gen(rd());
std::uniform_int_distribution<int> dist(1, 45);

int n = dist(gen);        // 편향 없이 1~45
```

`uniform_int_distribution`은 모듈로 편향을 알아서 처리한다. 범위 밖으로 떨어지는 값이 나오면 버리고 다시 뽑는 식이다.

`std::mt19937`은 메르센 트위스터로 주기가 $2^{19937}-1$이다. 통계적 성질도 `rand()`보다 훨씬 낫다. 다만 암호학적으로 안전하지는 않다. 출력을 몇 개 보면 내부 상태를 복원할 수 있어서, 보안이 필요한 곳에는 쓰면 안 된다.

## random_device를 항상 믿을 수는 없다

`std::random_device`는 OS가 제공하는 엔트로피를 쓰라고 만든 것이다. 리눅스에서는 `/dev/urandom`, 윈도우에서는 시스템 API를 쓴다.

그런데 표준이 **결정론적 구현도 허용**한다. 실제로 오래된 MinGW의 일부 버전에서 `random_device`가 항상 같은 값을 돌려주는 것으로 알려져 있다. 그러면 매번 같은 로또 번호가 나온다.

확인하는 방법이 있다.

```c++
std::random_device rd;
if (rd.entropy() == 0) {
    // 이 구현은 진짜 엔트로피가 없을 수 있다
}
```

`entropy()`가 0이면 의심해볼 만하다. 다만 이 값도 구현이 알아서 채우는 것이라 절대적인 판정은 아니다. 확실하게 하려면 여러 소스를 섞는다.

```c++
#include <chrono>
#include <thread>

std::seed_seq seq{
    static_cast<unsigned>(std::random_device{}()),
    static_cast<unsigned>(std::chrono::high_resolution_clock::now()
                              .time_since_epoch().count()),
    static_cast<unsigned>(std::hash<std::thread::id>{}(std::this_thread::get_id()))
};
std::mt19937 gen(seq);
```

`seed_seq`를 쓰는 이유가 하나 더 있다. `mt19937`의 내부 상태는 624개의 32비트 워드인데, `gen(rd())`처럼 32비트 하나로 시드하면 실제로 도달 가능한 초기 상태가 $2^{32}$가지뿐이다. `seed_seq`는 여러 값을 받아 상태 전체를 채운다.

## 시드를 남겨야 재현이 된다

이게 실무에서 제일 중요한 부분이다.

난수를 쓰는 코드는 실행할 때마다 다르게 동작한다. 테스트가 어쩌다 한 번 실패했을 때, 그 입력을 다시 만들 수 없으면 원인을 못 찾는다.

시드를 기록해두면 재현이 된다.

```c++
const unsigned seed = std::random_device{}();
std::cout << "seed = " << seed << '\n';      // 로그에 남긴다
std::mt19937 gen(seed);
```

실패한 실행의 로그에서 시드를 꺼내 그대로 넣으면 같은 수열이 나온다. 메르센 트위스터는 완전히 결정론적이라 같은 시드면 같은 결과가 보장된다.

측정 데이터에 잡음을 주입해서 알고리즘을 시험할 때 이 방식을 썼다. 어떤 잡음 패턴에서 검출이 실패하는지 찾으려면 그 패턴을 다시 만들 수 있어야 한다. 시드 하나만 적어두면 된다.

명령줄 인자로 시드를 받을 수 있게 해두면 더 편하다.

```c++
unsigned seed = (argc > 1) ? std::stoul(argv[1]) : std::random_device{}();
```

## 셔플 대신 부분 셔플

45개를 다 섞어놓고 앞의 6개만 쓰는 건 조금 낭비다. `std::shuffle`은 Fisher-Yates 알고리즘이라 앞에서부터 순서대로 확정해 나가므로, 6개만 확정하고 멈춰도 된다.

```c++
for (int i = 0; i < 6; ++i) {
    std::uniform_int_distribution<int> d(i, 44);
    std::swap(numbers[i], numbers[d(gen)]);
}
```

45개면 차이가 없지만, 100만 개 중에서 10개를 뽑아야 하는 상황이면 이야기가 다르다.

표준에도 이 용도의 함수가 있다.

```c++
std::vector<int> picked(6);
std::sample(numbers.begin(), numbers.end(), picked.begin(), 6, gen);   // C++17
```

`std::sample`은 원본을 안 바꾸고 6개를 뽑아준다. 다만 뽑힌 순서가 원본 순서를 유지해서, 이미 정렬된 결과가 나온다. 로또 번호는 어차피 정렬해서 보는 게 편하니 오히려 잘 맞았다.

```c++
std::sort(numbers.begin(), numbers.begin() + 6);   // shuffle 방식이면 이렇게
```

## 정리하면

- `rand() % n`은 모듈로 편향이 있고, `time(0)` 시드는 초 단위라 같은 초에 실행하면 같은 결과가 나온다
- `<random>`은 엔진과 분포를 분리한다. `uniform_int_distribution`이 편향을 처리해준다
- `random_device`가 결정론적인 구현도 있다. 여러 소스를 `seed_seq`로 섞으면 안전하다
- 32비트 하나로 시드하면 `mt19937`의 초기 상태 공간을 다 못 쓴다
- 난수를 쓰는 코드는 **시드를 로그에 남겨야** 실패를 재현할 수 있다
- 전체를 섞어 앞부분만 쓸 거면 `std::sample`이나 부분 셔플이 낫다
