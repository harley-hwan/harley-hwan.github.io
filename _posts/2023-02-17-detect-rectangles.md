---
title: opencv(c++) 19. 직사각형 검출 알고리즘 (python/MFC 환경 포함)
description: "C++과 OpenCV로 이미지에서 직사각형을 검출하는 함수를 만들고, 같은 알고리즘을 MFC와 파이썬 환경에서 구현한 예제를 정리한다."
date: 2023-02-17 10:00:00 +0900
slug: 'DetectRactangles'
categories: [Dev, OpenCV]
series: opencv
series_order: 19
tags: [opencv, mat, cvt-color, gaussian-blur, canny, find-contours, approx-poly-dp, draw-contours, rectangle-detection]
---
## 목표

MFC에서 opencv 를 활용한 이미지 처리를 통한 직사각형 검출 알고리즘을 만들어보자.

<br/>

---

## 내용

C++과 OpenCV를 사용하여 이미지에서 직사각형을 검출하는 함수를 만든다.

이 함수는 cv::Mat 객체를 입력으로 받아서, 직사각형 검출 결과를 std::vector<cv::Rect> 형태로 반환한다.

```c++
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

std::vector<cv::Rect> detectRectangles(cv::Mat& inputImage)
{
    // 이미지 전처리
    cv::Mat grayImage, blurredImage, cannyImage;
    cv::cvtColor(inputImage, grayImage, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(grayImage, blurredImage, cv::Size(5, 5), 0);
    cv::Canny(blurredImage, cannyImage, 50, 150);

    // 컨투어 검출
    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(cannyImage, contours, hierarchy, cv::RETR_TREE, cv::CHAIN_APPROX_SIMPLE);

    // 직사각형 검출
    std::vector<cv::Rect> rectangles;
    for (int i = 0; i < contours.size(); i++)
    {
        std::vector<cv::Point> contour = contours[i];
        std::vector<cv::Point> approx;
        cv::approxPolyDP(contour, approx, cv::arcLength(contour, true) * 0.02, true);

        if (approx.size() == 4 && cv::isContourConvex(approx))
        {
            cv::Rect rect = cv::boundingRect(approx);
            rectangles.push_back(rect);
        }
    }

    return rectangles;
}

```

이 코드에서는 입력 이미지를 그레이스케일로 변환한 후, 

노이즈를 제거하기 위해 가우시안 블러를 적용하고, 

에지 검출을 위해 Canny 알고리즘을 적용한다.

이후 findContours로 컨투어를 검출하고, 각 컨투어를 approxPolyDP로 근사한 뒤 isContourConvex로 볼록한 도형인지 확인한다.

조건을 만족하면 boundingRect로 근사치를 감싸는 직사각형을 구해 std::vector<cv::Rect>에 추가하고, 이 벡터를 반환한다.

<br/>

### MFC 환경에서 구현

MFC(C++)에서 OpenCV를 사용하여 이미지에서 직사각형을 검출하는 코드는 다음과 같다.

이 코드는 MFC 환경에서 이미지에서 직사각형을 검출하는 과정을 보여주는 간단한 예시이다.

```c++
#include "stdafx.h"
#include <opencv2/opencv.hpp>

using namespace cv;

void OnProcessImage(cv::Mat& image)
{
    // 이미지 전처리
    cv::Mat gray, blur, canny;
    cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(gray, blur, cv::Size(5, 5), 0);
    cv::Canny(blur, canny, 50, 150);

    // 직사각형 검출
    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(canny, contours, hierarchy, cv::RETR_TREE, cv::CHAIN_APPROX_SIMPLE);

    for (size_t i = 0; i < contours.size(); i++)
    {
        std::vector<cv::Point> approx;
        cv::approxPolyDP(contours[i], approx, 0.01 * cv::arcLength(contours[i], true), true);
        if (approx.size() == 4)
        {
            cv::drawContours(image, contours, i, cv::Scalar(0, 255, 0), 3);
        }
    }
}

void OnDrawImage(cv::Mat& image, CWnd* pWnd)
{
    CRect rect;
    pWnd->GetClientRect(&rect);

    cv::Mat resized_image;
    cv::resize(image, resized_image, cv::Size(rect.Width(), rect.Height()));

    cv::imshow("Image", resized_image);
}

int main()
{
    // 이미지 읽어오기
    cv::Mat image = cv::imread("이미지 파일 경로");

    // 이미지 처리
    OnProcessImage(image);

    // 결과 출력 (실제 MFC 앱에서는 OnDrawImage(image, this) 형태로 호출)
    cv::namedWindow("Image", cv::WINDOW_NORMAL);
    cv::setWindowProperty("Image", cv::WND_PROP_ASPECT_RATIO, cv::WINDOW_KEEPRATIO);
    cv::resizeWindow("Image", 800, 600);
    cv::imshow("Image", image);

    cv::waitKey(0);
    cv::destroyAllWindows();

    return 0;
}

```

<br/>

이 코드에서는 MFC 환경에서 OpenCV를 사용하기 위해 opencv2/opencv.hpp 헤더 파일을 포함한다. 

cv::imread로 이미지를 읽어와 cv::Mat 객체에 담은 뒤, 그레이스케일 변환과 가우시안 블러로 전처리하고 Canny 에지 검출을 수행한다.

cv::findContours로 이미지에서 컨투어를 검출하고, cv::approxPolyDP로 검출된 컨투어의 근사치를 구한다. 

이 때 approx.size() 값이 4인 경우에만 직사각형으로 판단하여, cv::drawContours로 해당 컨투어를 이미지 위에 그린다.

OnDrawImage는 전달받은 윈도우의 클라이언트 영역 크기에 맞춰 이미지를 리사이즈해 출력하는 함수다. 위 예시는 흐름을 보여주기 위해 main 함수에서 cv::imshow로 결과를 띄우지만, 실제 MFC 앱이라면 CWinApp 초기화가 끝난 뒤 다이얼로그나 뷰 클래스의 핸들러에서 같은 흐름을 호출하고, OnDrawImage에는 해당 윈도우의 CWnd 포인터를 넘기면 된다.

<br/>

<br/>

### python 환경에서 구현

```python
import cv2

# 이미지 읽어오기
image = cv2.imread("이미지 파일 경로")

# 이미지 전처리
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
canny = cv2.Canny(blur, 50, 150)

# 직사각형 검출
contours, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for contour in contours:
    approx = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
    if len(approx) == 4:
        cv2.drawContours(image, [approx], 0, (0, 255, 0), 3)

# 결과 출력
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

```

<br/>

파이썬에서도 흐름은 같다. cv2.imread로 이미지를 읽어온 뒤 그레이스케일 변환, 가우시안 블러, Canny 에지 검출 순으로 전처리한다.

cv2.findContours로 컨투어를 검출하고 각 컨투어를 cv2.approxPolyDP로 근사한 뒤, len(approx) 값이 4인 경우에만 직사각형으로 판단하여 cv2.drawContours로 이미지 위에 그린다.

마지막으로 cv2.imshow로 결과 이미지를 출력하고, cv2.waitKey로 키 입력을 대기했다가 cv2.destroyAllWindows로 모든 윈도우를 닫는다.
