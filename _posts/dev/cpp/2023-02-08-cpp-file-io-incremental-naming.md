---
title: "(C++) 동일 파일명 존재할 시, 다음 번호의 파일 생성 (File I/O)"
description: "결과 파일이 덮어써지는 걸 막으려고 번호를 하나씩 올려가며 빈 이름을 찾는 코드를 짰다. 잘 돌긴 했는데 파일이 쌓이면 느려지고, 프로그램을 두 개 띄우면 같은 번호를 쓴다. 그 두 문제를 어떻게 정리했는지 남긴다."
date: 2023-02-08 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, file, rename, ifstream, ofstream, filesystem]
---
## 덮어쓰기 때문에 시작했다

결과를 `Final_Total_Normal_PSNR.txt` 한 파일에 쓰고 있었는데, 파라미터를 바꿔가며 여러 번 돌리다 보니 매번 앞 결과가 날아갔다. 비교를 하려면 이전 것이 남아 있어야 해서 파일명 뒤에 번호를 붙이기로 했다.

## 처음 짠 코드

```c++
void AnalyzePSNR::RetrieveProcessedFiles()
{
  ifstream fin;
  ofstream fout;
  char filename[255];
  bool OpenFileSuccess = false;
  int i = 0;
  while (OpenFileSuccess == false)
  {
    sprintf_s(filename, "Final_Total_Normal_PSNR_%d.txt", i);
    fin.open(filename);
    
    if(!(fin.is_open()))
    {
      OpenFileSuccess = true;
    }
    else
    {
      i++;
    }
    fin.close();
  }
  fout.open(filename);
  
  fout << "Normal_PSNR" << "\t" << "\t" << "Average_Normal_PSNR: " << Average_Normal_PSNR << endl;
  for (int i = 0; i < this->number_of_frames_in_Processed_GOP; i++)
  {
    fout << Normal_Processed_PSNR[i] << endl;
  }
  fout.close();
}
```

0번부터 순서대로 열어보다가 안 열리는 번호가 나오면 거기가 빈 자리라고 판단하고, 그 이름으로 쓴다. 의도한 대로 동작했다.

`OpenFileSuccess`라는 변수명은 지금 보면 반대로 붙어 있다. 파일 열기에 **실패**했을 때 true가 되니까 `FoundEmptySlot` 정도가 맞다. 이런 이름이 나중에 코드를 다시 볼 때 제일 헷갈린다.

## 나중에 걸린 문제 두 개

### 파일이 쌓이면 시작이 느려진다

이 루프는 파일 개수만큼 `open`을 시도한다. 결과가 수천 개 쌓이면 프로그램을 켤 때마다 수천 번 파일을 여닫는다. 로컬 SSD에서는 체감이 잘 안 되는데, 네트워크 드라이브에 결과를 쌓기 시작하니 눈에 띄게 느려졌다.

### 두 개를 동시에 띄우면 같은 번호를 쓴다

더 큰 문제는 이쪽이다. 확인하는 시점과 파일을 만드는 시점 사이에 틈이 있다. 두 프로세스가 거의 동시에 "7번이 비었네"라고 판단하면 둘 다 7번에 쓰고, 나중에 연 쪽이 앞의 결과를 덮는다. 덮어쓰기를 막으려고 만든 코드가 정확히 그 상황을 만든다.

## 존재 확인은 filesystem으로

C++17부터는 파일 존재 확인에 스트림을 열 필요가 없다.

```cpp
#include <filesystem>
namespace fs = std::filesystem;

if (fs::exists("result.txt")) { ... }
```

`ifstream`으로 확인하면 두 가지가 애매하다. 파일이 있는데 권한이 없어서 못 여는 경우도 "없음"으로 판정되고, 디렉토리를 열려고 하면 구현마다 결과가 다르다. `fs::exists`는 그런 모호함이 없고, 열고 닫는 비용도 없다.

## 원자적으로 확보하기

경쟁 문제를 없애려면 "확인하고 만들기"를 두 단계로 쪼개면 안 된다. 운영체제에 "없을 때만 만들어라"라고 한 번에 요청해야 한다.

POSIX에는 `O_EXCL`이 있다.

```cpp
#include <fcntl.h>
#include <unistd.h>
#include <cstdio>

int create_next(char* out, size_t n, const char* pattern)
{
    for (int i = 0; i < 100000; ++i) {
        std::snprintf(out, n, pattern, i);
        int fd = ::open(out, O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (fd >= 0) return fd;          // 내가 만든 게 확실하다
        if (errno != EEXIST) return -1;  // 다른 이유의 실패는 바로 중단
    }
    return -1;
}
```

`O_CREAT | O_EXCL` 조합은 파일이 이미 있으면 실패하고 `errno`를 `EEXIST`로 설정한다. 확인과 생성이 커널 안에서 한 번에 끝나기 때문에 두 프로세스가 같은 번호를 잡을 수 없다. 윈도우는 `CreateFile`의 `CREATE_NEW`가 같은 역할을 한다.

```cpp
HANDLE h = CreateFileA(name, GENERIC_WRITE, 0, nullptr,
                       CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr);
// 이미 있으면 INVALID_HANDLE_VALUE, GetLastError() == ERROR_FILE_EXISTS
```

`EEXIST`가 아닌 실패에서 바로 빠져나오는 게 중요하다. 디렉토리가 없거나 권한이 없으면 모든 번호에서 실패하는데, 그 검사가 없으면 10만 번을 헛돈다.

`ofstream`에는 이런 모드가 없다. `std::ios::app`이나 `std::ios::trunc`는 있어도 "없을 때만"이 없어서, 원자적으로 잡으려면 결국 OS API를 직접 부르게 된다.

## 이진 탐색으로 줄이기

원자적 생성을 쓰더라도 빈 번호를 찾는 건 여전히 순차 탐색이다. 파일이 N개면 N번 시도한다. 번호가 0부터 빈틈없이 이어진다는 가정이 성립하면 이진 탐색으로 줄일 수 있다.

```cpp
// 존재하는 마지막 번호를 log 시간에 찾는다
int find_upper_bound(const char* pattern)
{
    int hi = 1;
    while (exists(pattern, hi)) hi *= 2;    // 지수적으로 늘려 상한을 잡고

    int lo = hi / 2;
    while (lo + 1 < hi) {                    // 그 안에서 이진 탐색
        int mid = lo + (hi - lo) / 2;
        (exists(pattern, mid) ? lo : hi) = mid;
    }
    return hi;
}
```

파일이 1000개면 순차 탐색은 1000번, 이 방식은 20번 정도다. 다만 중간 번호가 지워져 구멍이 나면 결과가 틀린다. 지운 파일이 있을 수 있는 디렉토리라면 순차 탐색이 맞다.

## 결국은 타임스탬프로 갔다

번호를 붙이는 방식은 근본적으로 불편한 점이 하나 더 있다. 파일명만 봐서는 언제 만든 건지 알 수 없다. 3번과 7번 중 어느 게 어제 것인지 확인하려면 탐색기에서 수정 시각을 봐야 한다.

지금은 타임스탬프를 쓴다.

```cpp
#include <chrono>
#include <ctime>
#include <iomanip>
#include <sstream>

std::string timestamped(const std::string& prefix, const std::string& ext)
{
    const auto now = std::chrono::system_clock::to_time_t(
                         std::chrono::system_clock::now());
    std::tm tm{};
#if defined(_WIN32)
    localtime_s(&tm, &now);
#else
    localtime_r(&now, &tm);
#endif
    std::ostringstream ss;
    ss << prefix << '_' << std::put_time(&tm, "%Y%m%d_%H%M%S") << ext;
    return ss.str();
}

// Final_Total_Normal_PSNR_20230208_143052.txt
```

장점이 여러 개다. 탐색 자체가 필요 없어서 파일이 몇 개든 시작 시간이 같고, 이름 순 정렬이 곧 시간 순 정렬이 되고, 파일명만 봐도 언제 것인지 안다. 같은 초에 두 번 돌 가능성이 있으면 밀리초까지 붙이거나 뒤에 PID를 붙이면 된다.

`localtime`은 정적 버퍼를 돌려주는 데다 스레드 안전하지 않아서, 윈도우는 `localtime_s`, POSIX는 `localtime_r`로 갈라 썼다. 인자 순서가 서로 반대라 매번 헷갈리는데, 윈도우 쪽이 `(출력, 입력)`이고 POSIX 쪽이 `(입력, 출력)`이다.

## 정리하면

- 존재 확인은 스트림을 열지 말고 `std::filesystem::exists`를 쓴다
- 확인과 생성을 나누면 프로세스가 둘이 될 때 같은 이름을 잡는다. `O_CREAT|O_EXCL` 또는 `CREATE_NEW`로 한 번에 처리한다
- `EEXIST` 이외의 실패에서 루프를 빠져나오지 않으면 조용히 오래 돈다
- 결과 파일을 계속 쌓을 거면 번호보다 타임스탬프가 낫다. 탐색이 없어지고 정렬이 시간순이 된다

파일명을 만드는 방법 자체는 [동적 파일명 생성 및 파일 열기 구현](/posts/cpp-file-naming-methods/)에 따로 정리해두었다.
