---
title: "동일 파일명 존재할 시, 다음 번호의 파일 생성 (File io)"
description: "C++에서 같은 이름의 파일이 이미 있으면 번호를 하나씩 올려 다음 번호의 파일명으로 새 파일을 생성하는 방법을 정리한다."
date: 2023-02-08 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, file, rename, ifstream, ofstream]
---
- 참조: https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/nf-wlanapi-wlanopenhandle

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

```
