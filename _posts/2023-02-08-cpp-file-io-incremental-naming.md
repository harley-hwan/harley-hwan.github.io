---
title: "동일 파일명 존재할 시, 다음 번호의 파일 생성 (File io)"
description: "wifi, connect, wlan, msdn, c++, c"
date: 2023-02-08 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, file, rename, ifstream, ofstream]
---

# 파일명 존재할 시, 다음 번호의 파일 생성 (file io)
- 최초 작성일: 2023년 2월 8일 (수)
- 참조: https://cpp.hotexamples.com/examples/-/-/WlanOpenHandle/cpp-wlanopenhandle-function-examples.html

## 내용

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
}

```
