---
title: "(C++) iomanip을 이용한 표 형식 출력 구현"
description: "setw와 cout.setf를 활용한 정렬된 출력 포맷팅"
date: 2023-02-10 10:00:00 +0900
categories: [Dev, C++]
tags: [cpp, iomanip, formatting, output, console]
---
<br/>

## 소개
C++의 iomanip 라이브러리를 사용하여 콘솔 출력을 표 형식으로 정렬한다. setw와 cout.setf를 활용하여 데이터를 일정한 간격으로 정렬하고 표시한다.

<br/>

## 구현 코드
정렬된 표 형식으로 시스템 정보를 출력하는 구현이다. 원래는 장비 검사 프로그램에서 발췌한 코드라서, 검사 결과와 버전 값은 예시로 채워 넣었다.

```cpp
#include <iostream>
#include <iomanip>
#include <string>

using namespace std;

int main() {
    // 왼쪽 정렬 설정
    cout.setf(ios_base::left);

    // 검사 결과 및 버전 값 (예시)
    string resCameraPass = "Pass";
    string degreebuffer = "0.3";
    string resdiagPass = "Pass";
    string strErrCode = "0x00";
    string SWVer = "1.0.0";
    string FWVer = "2.1.3";
    string E6Ver = "1.0.5";

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

## 주요 기능 설명

cout.setf(ios_base::left)로 왼쪽 정렬을 설정하면 모든 열의 내용이 왼쪽에서 시작한다. 각 열의 너비는 setw()로 지정하는데, 번호열 3칸, 항목열 10칸, 내용열 12칸, 결과열과 비고열은 각 15칸이다.

테이블은 5개의 열로 구성되고, 각 행은 시스템의 서로 다른 구성 요소를 나타낸다. 값이 없는 자리는 공백 문자로 채워 열 간격을 유지한다.

#### 실행 결과
![표 형식 출력 결과](/assets/img/posts/cpp-table-format-output-with-setw/001-218002463-c66dc783-8de1-4220-a3b3-5d4a7f14aa33.png)
