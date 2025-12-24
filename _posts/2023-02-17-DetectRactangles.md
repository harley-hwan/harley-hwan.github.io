---
title: opencv(c++) 19. 직사각형 검출 알고리즘 (python/MFC 환경 포함)
description: "Mat, cvtColor, GaussianBlur, Canny, findContours, approxPolyDP, drawContours, detectRectangle, mfc"
date: 2023-02-17 10:00:00 +0900
categories: [Dev, OpenCV]
tags: [opencv, Mat, cvtColor, GaussianBlur, Canny, findContours, approxPolyDP, drawContours, detectRectangle]
---

# opencv c++ 

- 최초 작성일: 2023년 2월 17일(금)

## 

MFC에서 opencv 를 활용한 이미지 처리를 통한 직사각형 검출 알고리즘을 만들어보자.

<br/>

---

## 

C++과 OpenCV를 사용하여 이미지에서 직사각형을 검출하는 함수를 만들어

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

이후 findContours 함수를 사용하여 이미지에서 컨투어를 검출한다.

approxPolyDP 함수를 사용하여 검출된 컨투어의 근사치를 구하고, 

isContourConvex 함수를 사용하여 해당 근사치가 볼록한 도형인지 확인한다. 

이후 boundingRect 함수를 사용하여 근사치를 감싸는 직사각형을 구하고, std::vector<cv::Rect>에 추가한다.

이렇게 구해진 직사각형 정보를 std::vector<cv::Rect> 형태로 반환한다.

<br/>

### MFC 

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

    // 결과 출력
    cv::namedWindow("Image", cv::WINDOW_NORMAL);
    cv::setWindowProperty("Image", cv::WND_PROP_ASPECT_RATIO, cv::WINDOW_KEEPRATIO);
    cv::resizeWindow("Image", 800, 600);
    OnDrawImage(image, AfxGetMainWnd());

    cv::waitKey(0);
    cv::destroyAllWindows();

    return 0;
}

```

<br/>

이 코드에서는 MFC 환경에서 OpenCV를 사용하기 위해 opencv2/opencv.hpp 헤더 파일을 포함한다. 

이후 CImage 객체를 사용하여 이미지를 읽어오고, cv::Mat 객체로 변환한다.

cv::cvtColor 함수를 사용하여 이미지를 그레이스케일로 변환하고, cv::GaussianBlur 함수를 사용하여 노이즈를 제거한다.

이후 cv::Canny 함수를 사용하여 에지 검출을 수행한다.

cv::findContours 함수를 사용하여 이미지에서 컨투어를 검출하고, cv::approxPolyDP 함수를 사용하여 검출된 컨투어의 근사치를 구. 

이 때 approx.size() 값이 4인 경우에만 직사각형으로 판단하여, cv::drawContours 함수를 사용하여 해당

<br/>

<br/>

### python 

```python
import cv2

# 
image = cv2.imread("이미지 파일 경로")

# 
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
canny = cv2.Canny(blur, 50, 150)

# 
contours, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for contour in contours:
    approx = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
    if len(approx) == 4:
        cv2.drawContours(image, [approx], 0, (0, 255, 0), 3)

# 
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

```

<br/>

이 코드에서는 cv2.imread 함수를 사용하여 이미지를 읽어오고, cv2.cvtColor 함수를 사용하여 이미지를 그레이스케일로 변환한다.

이후 cv2.GaussianBlur 함수를 사용하여 노이즈를 제거하고, cv2.Canny 함수를 사용하여 에지 검출을 수행한다.

cv2.findContours 함수를 사용하여 이미지에서 컨투어를 검출하고, cv2.approxPolyDP 함수를 사용하여 검출된 컨투어의 근사치를 구한다.

이 때 len(approx) 값이 4인 경우에만 직사각형으로 판단하여, cv2.drawContours 함수를 사용하여 해당 컨투어를 직사각형으로 그린다.

마지막으로, cv2.imshow 함수를 사용하여 결과 이미지를 출력한다.

cv2.waitKey 함수를 사용하여 키 입력을 대기하고, cv2.destroyAllWindows 함수를 사용하여 모든 윈도우를 닫는다.
