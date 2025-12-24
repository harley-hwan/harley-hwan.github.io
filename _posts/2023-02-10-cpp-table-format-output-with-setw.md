---
title: "(C++) iomanip을 이용한 표 형식 출력 구현"
description: "setw와 cout.setf를 활용한 정렬된 출력 포맷팅"
date: 2023-02-10 10:00:00 +0900
categories: [Dev, C++]
tags: [c++, iomanip, formatting, output, console]
---

# iomanip 
- 최초 작성일: 2024년 1월 6일 (월)

<br/>

## 
C++의 iomanip 라이브러리를 사용하여 콘솔 출력을 표 형식으로 정렬한다. setw와 cout.setf를 활용하여 데이터를 일정한 간격으로 정렬하고 표시한다.

<br/>

## 
정렬된 표 형식으로 시스템 정보를 출력하는 구현이다.

```cpp
#include <iostream>
#include <iomanip>
#include <string>

using namespace std;

int main() {
    // 왼쪽 정렬 설정
    cout.setf(ios_base::left);

    // 결과 문자열 구성
    string resCamera = resCameraPass + "(" + degreebuffer + ")";    // 카메라 검증 결과
    string resdiag = resdiagPass + "(" + strErrCode + ")";         // 진단 결과

    // 테이블 헤더 출력
    cout << setw(3)  << " "   << setw(10) << "항목"    
         << setw(12) << "내용"    << setw(15) << "결과"    
         << setw(15) << "비고"    << endl;

    // 카메라 정보
    cout << setw(3)  << "1"   << setw(10) << "카메라"    
         << setw(12) << "Roll"    << setw(15) << resCamera 
         << setw(15) << "Threshold 2" << endl;

    // 진단 정보
    cout << setw(3)  << "2"   << setw(10) << "진단"    
         << setw(12) << "ErrCode" << setw(15) << resdiag  
         << setw(15) << " "       << endl;

    // 버전 정보
    cout << setw(3)  << "3"   << setw(10) << "버전"    
         << setw(12) << "SW Ver"  << setw(15) << SWVer   
         << setw(15) << " "       << endl;
    cout << setw(3)  << " "   << setw(10) << " "       
         << setw(12) << "FW Ver"  << setw(15) << FWVer   
         << setw(15) << " "       << endl;
    cout << setw(3)  << " "   << setw(10) << " "       
         << setw(12) << "E6 Ver"  << setw(15) << E6Ver   
         << setw(15) << " "       << endl;

    // 추가 정보
    cout << setw(3)  << "4"   << setw(10) << "위상캘"   
         << setw(12) << " "       << setw(15) << resdiag 
         << setw(15) << " "       << endl;
    cout << setw(3)  << "5"   << setw(10) << "IMU"     
         << setw(12) << " "       << setw(15) << resdiag 
         << setw(15) << " "       << endl;

    return 0;
}
```

<br/>

## 

1. **출력 정렬 설정**
   - cout.setf(ios_base::left)로 왼쪽 정렬을 설정한다
   - 모든 열의 내용이 왼쪽에서 시작하도록 한다

2. **열 너비 설정**
   - setw() 함수로 각 열의 너비를 지정한다
   - 번호열: 3칸
   - 항목열: 10칸
   - 내용열: 12칸
   - 결과열: 15칸
   - 비고열: 15칸

3. **테이블 구조**
   - 5개의 열로 구성된 테이블 형식을 사용한다
   - 각 행은 시스템의 다른 구성 요소를 나타낸다
   - 빈 행은 공백 문자로 채워진다

#### :
![표 형식 출력 결과](https://user-images.githubusercontent.com/68185569/218002463-c66dc783-8de1-4220-a3b3-5d4a7f14aa33.png)

이 구현을 통해 데이터를 정렬된 표 형식으로 출력할 수 있다. setw 함수로 열 너비를 일정하게 유지하고, cout.setf로 정렬 방식을 지정하여 가독성 높은 출력을 생성한다.
