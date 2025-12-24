---
title: (c++) 파일 생성 이벤트 모니터링 (linux)
description: "c, c++, vs, linux, inotify, inotify_init, IN_CREATE, IN_ISDIR, inotify_rm_watch"
date: 2023-07-27 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, vs, linux, inotify, inotify_init, IN_CREATE, IN_ISDIR, inotify_rm_watch]
---

# 
- 최초 작성일: 2023년 7월 27일 (수)

## 

리눅스에서 제공하는 inotify 기능을 사용하여 특정 디렉터리에서 파일 생성 이벤트를 모니터링하는 프로그램. 

이 프로그램은 특정 디렉토리에서 'rbf' 확장자를 가진 새로운 파일이 생성되는 것을 감시하고, 해당 이벤트가 발생하면 추가 작업을 수행한다.

<br/>

### 

- 먼저, inotify 시스템을 초기화하고, 감시할 디렉토리(/path)를 등록한다. 그 후, 무한루프를 돌며 read() 함수를 통해 inotify 이벤트를 읽는다.
- 무한루프를 돌며 버퍼에서 inotify 이벤트를 하나씩 처리하며, 만약 이 이벤트가 파일 생성(IN_CREATE) 이벤트이고 디렉토리가 아니면, 그 파일의 확장자가 'rbf'인지 확인합니다. (확장자는 원하는대로 변경 가능)
- 그 파일의 확장자가 rbf라면 원하는 기능을 수행한다.
- 프로그램을 종료하려면 감시 중인 디렉토리를 감시 목록에서 제거하고, inotify 인스턴스를 닫아야 한다. 그러기 위해선 무한루프에서 빠져나오는 조건을 추가하면 된다.
- inotify 초기화나 감시할 디렉토리 등록 시 오류가 발생하면 해당 오류 메시지를 출력하고 프로그램을 종료한다. 디렉토리 생성 중 오류가 발생하면 이에 대한 오류 메시지를 출력하고 프로그램을 종료한다.

<br/>

## 

```c++
#include <iostream>
#include <sys/inotify.h>
#include <sys/stat.h>
#include <cstring>
#include <unistd.h>

// Size of read buffer
#define BUF_LEN 1024
#define EVENT_SIZE (sizeof(struct inotify_event))

int main(int argc, char* argv[]) 
{
    // Create an INOTIFY instance
    int fd = inotify_init();

    // Check for error
    if (fd < 0) {
        perror("inotify_init");
        return 1;
    }

    // Add /path directory into watch list.
    int wd = inotify_add_watch(fd, "/path", IN_CREATE);

    if (wd < 0) {
        perror("inotify_add_watch");
        return 1;
    }

    char buffer[BUF_LEN];

    while (1) 
    {
        int length = read(fd, buffer, BUF_LEN);
        if (length < 0) {
            perror("read");
            continue;  // If read failed, try to continue to the next read
        }

        int i = 0;
        while (i < length) {
            struct inotify_event* event = (struct inotify_event*)&buffer[i];
            if (event->len) {
                if (event->mask & IN_CREATE) {
                    if (!(event->mask & IN_ISDIR)) {
                        std::string file_name = event->name;
                        if (file_name.substr(file_name.find_last_of(".") + 1) == "rbf")
                        {
                            // 원하는 기능 삽입
                        }
                    }
                }
            }
            i += EVENT_SIZE + event->len;
        }
    }

    // Removing the “/home/dbgftp/ShotDB” directory from the watch list.
    inotify_rm_watch(fd, wd);

    // Close the INOTIFY instance
    close(fd);

    return 0;
}

```
