---
title: Linux Command pipe로 변수값으로 끌고오기
description: "c++, linux, command, pipe, arp"
date: 2023-02-16 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, linux, command, pipe, arp]
---

# Linux Command pipe pipe()
- 최초 작성일: 2023년 2월 16일 (목)

## 

### 1

```c++
#include <iostream>
#include <cstdio>
#include <string>

int main() {
    FILE* pipe = popen("arp -a", "r");
    if (!pipe) return 1;

    char buffer[128];
    std::string result = "";
    while (!feof(pipe)) {
        if (fgets(buffer, 128, pipe) != nullptr)
            result += buffer;
    }

    pclose(pipe);

    std::cout << result << std::endl;
    return 0;
}
```

</br>

### 1

```c++
? (192.168.8.152) at 88:36:6c:fc:2c:4f [ether] on wlan0
? (192.168.8.114) at 5a:ff:ec:d1:cb:a4 [ether] on wlan0
```

<br/>

<br/>

### 2

```c++
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>

std::vector<std::string> getE6ServerIPpipe()
{
    std::vector<std::string> ip_list;
    //static bool initflag=false;
    //if(initflag)
    //	return ip_list;
    //initflag=true;
    int my_pipe[2];
    char* arguments[] = {"arp",NULL}; 

    if(pipe(my_pipe) == -1)
    {
        fprintf(stderr, "Error creating pipe\n");
    }

	//std::string ip;
	//system("arp -a > /home/pi/test/e6/ip.txt");

    pid_t child_id;
    child_id = fork();
    if(child_id == -1)
    {
        fprintf(stderr, "Fork error\n");
    }
    if(child_id == 0) // child process
    {
        close(my_pipe[0]); // child doesn't read
        dup2(my_pipe[1], 1); // redirect stdout

        execvp(arguments[0], arguments);

        fprintf(stderr, "Exec failed\n");
    }
    else
    {
        close(my_pipe[1]); // parent doesn't write

        char reading_buf[1024];
        char *ptr=reading_buf;
        while(read(my_pipe[0], ptr, 1) > 0)
        {
            //write(1, reading_buf, 1); // 1 -> stdout
            ptr++;
        }

        (*ptr)='\0';
        char *line=strtok(reading_buf,"\n"); // skip
        line=strtok(NULL,"\n");

        while(line)
        {
            int i;
            for(i=0;!isspace(line[i]);i++);

            line[i]='\0';
            ip_list.push_back(line);

            //printf("%s--------------------\n",line);
            line=strtok(NULL,"\n");
        }
        close(my_pipe[0]);
        wait();
    }
	return ip_list;
}
```

<br/>

### 2

```c++
192.168.8.152
192.168.8.114
```

<br/>

위 소스를 컴파일해보면, 아래와 같은 'warning'을 확인할 수 있다. 무시해도 되지만, 찝찝하다면 다음과 같은 방법으로 해결하면 된다.

```c++
warning: ISO C++ forbids converting a string constant to ‘char*’ [-Wwrite-strings]
     char* arguments[] = {"arp",NULL}; 
```

<br/>

해당 경고는 문자열 상수(string constant)를 char 포인터로 변환하는 것이 C++ 표준에 의해 금지된 것이라는 의미이다.

char* 타입의 포인터는 일반적으로 가리키는 메모리 공간을 수정할 수 있는 포인터로 간주되므로, 이러한 문자열 상수는 const char* 타입으로 선언하고 포인터에 대해 const 캐스팅을 수행해야 한다.

따라서 해당 경고를 해결하기 위해서는 다음과 같이 코드를 수정할 수 있다.

```c++
const char* arguments[] = {"arp", NULL};
```

<br/>

<br/>

### 3

```c++
std::vector<std::string> getIPList() {
    FILE* pipe = popen("arp -a", "r");
    if (!pipe) {
        std::cerr << "popen() failed!" << std::endl;
        exit(1);
    }

    std::vector<std::string> ip_list;
    char buffer[128];
    std::string arpOutput = "";
    while (!feof(pipe)) {
        if (fgets(buffer, 128, pipe) != nullptr) {
            arpOutput += buffer;
        }
    }
    pclose(pipe);

    size_t pos_left, pos_right;
    while ((pos_left = arpOutput.find("(")) != std::string::npos) {
        pos_right = arpOutput.find(")", pos_left);
        if (pos_right != std::string::npos) {
            std::string token = arpOutput.substr(pos_left + 1, pos_right - pos_left - 1);
            ip_list.push_back(token);
        }
        arpOutput.erase(0, pos_right + 1);
    }
    return ip_list;
}
```

<br/>

### 3

```c++
192.168.8.152
192.168.8.114
```

