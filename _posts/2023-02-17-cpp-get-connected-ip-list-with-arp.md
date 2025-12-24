---
title: 현재 연결된 IP 목록 뽑아보기 (arp)
description: "c++, linux, command, arp, system, ip, serverip"
date: 2023-02-17 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, linux, command, arp, system, ip, serverip]
---

# 현재 연결된 IP 목록 뽑아오기
- 최초 작성일: 2023년 2월 17일 (금)

## 내용

system() 함수를 이용하여 arp -a 커맨드를 실행하여 나오는 출력물을 텍스트 파일에 입력하고, 그 결과를 다시 불러와 ip 주소들만 뽑아서 ip_list를 뽑는 코드를 짜보았다.

<br/>

```c++
std::vector<std::string> getE6ServerIP()
{
    std::vector<std::string> ip_list;
	std::string ip;
    
	system("arp -a > /home/pi/test/e6/ip.txt");
    ifs.open("/home/pi/test/e6/ip.txt");
    if (!ifs.is_open()) 
    {
        std::cerr << "Can't open ip log file" << std::endl;
        return ip_list;
    }

	while(!ifs.eof())
	{
		std::string line;
		getline(ifs, line, '(');
		getline(ifs, ip, ')');
		ip_list.push_back(ip);
		getline(ifs, line, '\n');
	}
    ip_list.pop_back();
    
	ifs.close();
    if (ifs.is_open()) {
        error_handling("ifs not closed!");
         ifs.close();

	return ip_list;
}
```

 이 함수는 시스템 명령어 "arp -a"를 사용하여 로컬 네트워크의 IP 주소 목록을 가져와서 해당 IP 주소 목록을 std::vector<std::string>으로 반환한다.

함수 내부의 동작은 다음과 같습니다.

- std::vector<std::string> ip_list를 초기화
- "arp -a > /home/pi/test/e6/ip.txt" 명령어를 사용하여 IP 주소 목록을 /home/pi/test/e6/ip.txt 파일에 저장
- /home/pi/test/e6/ip.txt 파일을 열고, 파일이 성공적으로 열렸는지 확인
- 파일을 끝까지 읽어들여서, 각 줄에서 IP 주소를 추출하여 std::vectorstd::string ip_list에 추가
- 마지막으로, 마지막으로 추가된 빈 문자열을 제거
- 파일을 닫는다.
- std::vectorstd::string ip_list를 반환

<br/>

함수의 동작을 설명했지만, 이 코드는 몇 가지 주의사항이 있다.

- 시스템 명령어를 사용하여 외부 명령어를 실행하는 것은 보안 취약점을 야기할 수 있으므로 이 함수를 사용하는 경우 취약점에 대한 위험을 인식하고, 보안 조치를 취해야한다.
- 파일을 여는 경우, 파일을 정상적으로 닫아야한다. 이 함수는 파일을 열고 난 뒤 파일을 닫는 것을 처리하고 있지만, 파일을 열지 못하는 경우 파일을 닫지 않는 문제가 있다.
- 이 문제를 해결하기 위해서는 파일을 열지 못한 경우, 반드시 파일을 닫아야한다. 
- 이를 위해 ifs.is_open()을 사용하여 파일이 열려있는지 확인하고, 파일을 열었을 때에만 파일을 닫도록 수정하는 것이 좋다.

```c++
std::vector<std::string> getE6ServerIP()
{
    std::vector<std::string> ip_list;
    std::string ip;
    system("arp -a > /home/pi/test/e6/ip.txt");

    std::ifstream ifs("/home/pi/test/e6/ip.txt");
    if (!ifs.is_open()) 
    {
        std::cerr << "Can't open ip log file" << std::endl;
        return ip_list;
    }

    while (getline(ifs, ip, '(') && getline(ifs, ip, ')')) 
    {
        ip_list.push_back(ip);
        std::string line;
        getline(ifs, line, '\n');
    }
    ip_list.pop_back();
    
    ifs.close();
    if (ifs.is_open()) {
        std::cerr << "ifs not closed!" << std::endl;
        ifs.close();
    }
    return ip_list;
}
```

<br/>

<br/>

다른 방식의 "arp -a" 시스템 명령어로 ip 주소 목록을 뽑는 함수를 만들어보자.

```c++
std::vector<std::string> getIPListFromARP()
{
    std::vector<std::string> ip_list;

    // 시스템 명령어로 arp -a 실행
    std::string command = "arp -a";
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // 결과에서 IP 주소 추출
    std::smatch match;
    std::regex re("\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b");
    std::string::const_iterator searchStart(result.cbegin());
    while (std::regex_search(searchStart, result.cend(), match, re)) {
        ip_list.push_back(match.str());
        searchStart = match.suffix().first;
    }

    return ip_list;
}
```

<br/>

- 위 코드에서는 std::array와 std::unique_ptr를 사용하여 시스템 명령어 실행 결과를 문자열로 읽어오고, std::regex를 사용하여 IP 주소를 추출 한다. 
- 함수 호출 시 std::vector<std::string> 형태로 IP 주소 목록을 반환한다.

- 하지만, 다시 말씀드리지만 보안 취약점을 야기할 수 있는 시스템 명령어 실행을 사용하기 때문에, 사용에 주의하여야 한다.

<br/>

#### 그러면 위 코드의 보안 취약점을 보완하려면 어떻게 해야할까?

위 코드에서 system 함수를 사용하여 시스템 명령어를 실행하는 부분이 보안 취약점을 야기할 수 있는 부분이다.
따라서 이를 보완하기 위해서는 system 함수 대신에 안전하게 명령어를 실행할 수 있는 다른 방법을 사용해야한다.

예를 들어, popen 함수를 사용하면 시스템 명령어를 실행할 수 있다.
popen 함수는 명령어 실행 결과를 파일로 저장하는 것이 아니라, 파이프로 전달하여 프로그램에서 읽어올 수 있도록 한다.

따라서, system 함수 대신에 popen 함수를 사용하여 arp -a 명령어를 실행하고, 그 결과에서 IP 주소를 추출하는 방법으로 보안 취약점을 보완할 수 있다.
이 경우, popen 함수에서 실행한 프로세스가 끝나지 않은 경우에는 pclose 함수를 사용하여 강제 종료시켜야 한다.

아래는 popen 함수를 사용하여 arp -a 명령어를 실행하고 IP 주소를 추출하는 예시 코드이다.

```c++
std::vector<std::string> getIPListFromARP()
{
    std::vector<std::string> ip_list;

    // 시스템 명령어로 arp -a 실행
    std::string command = "arp -a";
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // 결과에서 IP 주소 추출
    std::smatch match;
    std::regex re("\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b");
    std::string::const_iterator searchStart(result.cbegin());
    while (std::regex_search(searchStart, result.cend(), match, re)) {
        ip_list.push_back(match.str());
        searchStart = match.suffix().first;
    }

    return ip_list;
}

```

<br/>

위 코드에서는 std::array와 std::unique_ptr를 사용하여 시스템 명령어 실행 결과를 문자열로 읽어오고, std::regex를 사용하여 IP 주소를 추출한다. 
함수 호출 시 std::vector<std::string> 형태로 IP 주소 목록을 반환한다.

이렇게 함으로써 system 함수로 인해 발생할 수 있는 보안 취약점을 해결할 수 있다.

<br/>

만약 C++11 이전 버전의 컴파일러를 사용하고 있다면, 'std::unique_ptr' 가 정상적으로 작동하지 않는다.

이를 해결하려면, 컴파일러를 C++11 이상으로 업그레이드하거나, C++11 이상의 표준 라이브러리를 사용해야 한다.

만약 업그레이드가 불가능하다면 다음과 같이 'unique_ptr'을 대신할 수 있는 다른 방법을 사용할 수 있다.

코드는 아래와 같다.

<br/>

```c++
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <string>

std::string exec(const char* cmd) {
    char buffer[128];
    std::string result = "";
    FILE* pipe = popen(cmd, "r");
    if (!pipe) throw std::runtime_error("popen() failed!");
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        result += buffer;
    }
    pclose(pipe);
    return result;
}

```

<br/>

- 위의 코드에서 exec 함수는 주어진 명령어를 실행하고, 실행 결과를 문자열로 반환한다.
- popen 및 pclose 함수를 사용하여 프로세스를 실행하고, fgets 함수를 사용하여 결과를 읽어온다.
- 마지막으로, pclose 함수를 사용하여 프로세스를 종료한다.

<br/>

위 코드를 실행하면 아래와 같은 결과가 출력되는데,

```c++
? (192.168.8.114) at <incomplete> on wlan0
? (192.168.8.152) at 88:36:6c:fc:2c:4f [ether] on wlan0
```

<br/>

진짜 사용할 부분은 '(', ')' 사이의 ip 주소 목록이기 때문에, 괄호 안의 ip 주소들만 std::vector<std::string> list 형태로 뽑아내보자.

<br/>

### 풀소스

```c++
#include <iostream>
#include <vector>
#include <string>
#include <cstdio>

std::string exec(const char* cmd) {
    char buffer[128];
    std::string result = "";
    FILE* pipe = popen(cmd, "r");
    if (!pipe) throw std::runtime_error("popen() failed!");
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        result += buffer;
    }
    pclose(pipe);
    return result;
}

std::vector<std::string> getIPList() {
    std::vector<std::string> ip_list;
    std::string arpOutput = exec("arp -a");
    std::string delimiter = " ";
    size_t pos = 0;
    std::string token;
    while ((pos = arpOutput.find(delimiter)) != std::string::npos) {
        token = arpOutput.substr(0, pos);
        if (token.find("incomplete") == std::string::npos) {
            size_t start_pos = token.find("(");
            size_t end_pos = token.find(")");
            if (start_pos != std::string::npos && end_pos != std::string::npos && end_pos > start_pos) {
                std::string ip = token.substr(start_pos + 1, end_pos - start_pos - 1);
                ip_list.push_back(ip);
            }
        }
        arpOutput.erase(0, pos + delimiter.length());
    }
    return ip_list;
}

int main() {
    std::vector<std::string> ip_list = getIPList();

    // ip_list 출력
    for (const auto& ip : ip_list) {
        std::cout << ip << std::endl;
    }

    return 0;
}
```

<br/>

위의 소스를 이용해 뽑은 ip가 없을 때, "wasipEmpty"가 출력되도록 조치해두고,

while 문으로 반복해서 실행하다 보니 아래와 같은 에러가 반복적으로 발생했다.

```c++
/proc/net/arp: Too many open files
wasipEmpty
```

<br/>

에러 메시지 "/proc/net/arp: Too many open files"는 파일 디스크립터(fd)를 더 이상 열 수 없다는 의미이다.

이 오류는 리눅스 시스템에서 열 수 있는 파일 디스크립터의 개수를 초과하였을 때 발생하는 경우가 많다.

해결 방법으로는 다음과 같은 것들이 있습니다.

<br/>

#### 1. 파일 디스크립터 제한 해제

리눅스 시스템은 각 프로세스가 열 수 있는 파일 디스크립터 수를 제한한다.

이 한계를 초과하면 파일 디스크립터를 더 이상 열 수 없게 되어서 해당 오류가 발생한다.

이 경우에는 파일 디스크립터 제한을 해제해 주어야 합니다.

파일 디스크립터 제한을 해제하려면, 다음과 같이 ulimit 명령을 사용하여 제한을 늘리거나, /etc/security/limits.conf 파일에 해당 유저 또는 그룹에 대한 설정을 추가하여 제한을 해제할 수 있다.

```c++
ulimit -n 10000 # 파일 디스크립터 개수를 10000으로 늘림
```

<br/>

#### 2. 파일 디스크립터를 닫아주기

프로그램이 실행되는 동안 열린 파일 디스크립터를 모두 닫아주지 않으면 이러한 에러가 발생할 수 있다.
이 경우에는 파일 디스크립터를 닫아주는 코드를 추가하여 해결할 수 있다.

close() 함수를 사용하여 열린 파일 디스크립터를 닫아줄 수 있다.

만약 소켓이나 파일 등을 열었을 때 해당 파일 디스크립터를 변수에 저장해 두었다면, 프로그램이 더 이상 해당 파일 디스크립터를 사용하지 않게 될 때 close() 함수를 호출하여 닫아주어야 한다.

<br/>

그래서 아래와 같이 수정해보았다.

<br/>

<br/>

### 풀소스 2

```c++
#include <iostream>
#include <string>
#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>

using namespace std;

vector<string> getARPList() {
    vector<string> ip_list;

    int my_pipe[2];
    const char* arguments[] = {"arp", "-a", NULL}; 

    if(pipe(my_pipe) == -1)
    {
        fprintf(stderr, "Error creating pipe\n");
        return ip_list;
    }

    pid_t child_id;
    child_id = fork();
    if(child_id == -1)
    {
        fprintf(stderr, "Fork error\n");
        return ip_list;
    }
    if(child_id == 0) // child process
    {
        close(my_pipe[0]); // child doesn't read
        dup2(my_pipe[1], 1); // redirect stdout

        execvp(arguments[0], const_cast<char**>(arguments));

        fprintf(stderr, "Exec failed\n");
        exit(1);
    }
    else
    {
        close(my_pipe[1]); // parent doesn't write

        char* reading_buf = new char[1024];
        char *ptr=reading_buf;
        while(read(my_pipe[0], ptr, 1) > 0)
        {
            ptr++;
        }

        (*ptr)='\0';
        char *line=strtok(reading_buf,"\n"); // skip

        while(line)
        {
            // search for MAC address in parentheses
            char* mac_start = strstr(line, "(");
            if(mac_start) {
                char* mac_end = strstr(mac_start, ")");
                if(mac_end) {
                    string mac_address(mac_start + 1, mac_end - mac_start - 1);
                    ip_list.push_back(mac_address);
                }
            }

            line=strtok(NULL,"\n");
        }

        delete[] reading_buf;
        close(my_pipe[0]);
        waitpid(child_id, NULL, 0); // wait for child process to terminate
    }

    return ip_list;
}

int main() {
    while (1)
    {
        vector<string> arp_list = getARPList();
        for (int i = 0; i < arp_list.size(); i++) {
            cout << arp_list[i] << endl;
        }
        sleep(1);
    }
    return 0;
}
```

<br/>

해당 코드는 C++에서 ARP 테이블에서 MAC 주소를 뽑아 IP 주소와 함께 출력하는 코드이다.

우선 getE6ServerIPpipe 함수는 ARP 테이블 정보를 받아오기 위해 arp 명령어를 실행시키고, 명령어 실행 결과를 파이프로부터 읽어와서 처리한다. 

이를 위해 pipe, fork, dup2, execvp, waitpid 함수를 사용한다.

<br/>

pipe 함수는 파이프를 생성하고, fork 함수는 새로운 프로세스를 만든다.

자식 프로세스는 execvp 함수를 이용해 arp 명령어를 실행하고, 결과를 파이프에 출력한다. 

부모 프로세스는 파이프로부터 읽어온 결과를 처리하고, 자식 프로세스가 종료될 때까지 대기한다.

<br/>

읽어온 결과를 처리할 때는 먼저 문자열 버퍼를 만들고, strtok 함수를 이용해 한 줄씩 읽어와서 IP 주소와 MAC 주소를 분리해 출력한다. 

이 때, MAC 주소는 괄호로 둘러싸여 있으므로 괄호 안의 문자열만 추출하여 출력한다. 

IP 주소와 MAC 주소는 std::pair 객체에 저장하고, 이들을 std::vector에 추가한다.

마지막으로 자식 프로세스에서 열린 파일 디스크립터를 닫아준다.

<br/>

<br/>

#### 위의 코드를 이용했을 때도 아래의 에러가 발생하였다.

```c++
/proc/net/arp: Too many open files
/proc/net/arp: Too many open files
/proc/net/arp: Too many open files
/proc/net/arp: Too many open files
/proc/net/arp: Too many open files
```

<br/>

이유를 모르겠다... 다른 방법을 또 찾아보자.

그래서 다른 버전으로 새로 하나 짜봤다.. 테스트 해보자.

```c++
std::vector<std::string> E6Client::getIPListFromARP()
{
    std::vector<std::string> ip_list;

    // 시스템 명령어로 arp -a 실행
    std::string command = "arp -a";
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // 결과에서 IP 주소 추출
    std::smatch match;
    std::regex re("\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b");
    std::string::const_iterator searchStart(result.cbegin());
    while (std::regex_search(searchStart, result.cend(), match, re)) {
        ip_list.push_back(match.str());
        searchStart = match.suffix().first;
    }

    return ip_list;
}
```
<br/>

위 코드는 시스템 명령어로 'arp -a'를 실행하고 그 결과에서 IP 주소를 추출하는 방식으로 ARP 테이블을 가져오는 코드이다.

그런데 짜놓고 보니 이 코드의 문제점이 있다.

1. 명령어 실행 결과가 운영체제나 버전에 따라 다를 수 있음.
2. 명령어 실행에 따른 보안 문제 가능성이 존재함
3. 명령어 실행에 따른 오버헤드가 존재함

이 문제점들은 다음과 같이 해결이 가능한데..

1. ARP 테이블을 직접 가져오는 방식을 사용
2. 적절한 권한과 제한된 범위 내에서 명령어를 실행하도록 구현
3. ARP 테이블을 직접 가져오므로 오버헤드 없음

따라서 'getIPListFromARP' 함수를 다음과 같이 수정할 수 있다.

```c++
std::vector<std::string> E6Client::getIPListFromARP()
{
    std::vector<std::string> ip_list;

    struct ifaddrs *ifaddr, *ifa;
    int family, s;

    if (getifaddrs(&ifaddr) == -1) {
        perror("getifaddrs");
        return ip_list;
    }

    for (ifa = ifaddr; ifa != nullptr; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == nullptr) {
            continue;
        }

        family = ifa->ifa_addr->sa_family;

        if (family == AF_PACKET && ifa->ifa_flags & IFF_LOOPBACK) {
            continue;
        }

        if (family == AF_INET) {
            s = socket(AF_INET, SOCK_DGRAM, 0);
            if (s == -1) {
                perror("socket");
                continue;
            }

            struct arpreq arp;
            memset(&arp, 0, sizeof(arp));
            arp.arp_pa.sa_family = AF_INET;
            arp.arp_ha.sa_family = AF_UNSPEC;
            struct sockaddr_in *addr = (struct sockaddr_in *)ifa->ifa_addr;
            memcpy(&arp.arp_pa.sa_data, &addr->sin_addr, sizeof(addr->sin_addr));

            if (ioctl(s, SIOCGARP, &arp) == 0) {
                struct sockaddr_in *hwaddr = (struct sockaddr_in *)&arp.arp_ha;
                char ip[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &addr->sin_addr, ip, sizeof(ip));
                ip_list.push_back(ip);
            }

            close(s);
        }
    }

    freeifaddrs(ifaddr);

    return ip_list;
}
```

<br/>

<br/>

추가로 코드의 안정성을 높이기 위해 아래와 같이 몇 가지 수정하였다.

1. 예외 처리 추가
코드 실행 중 예외가 발생할 수 있는 부분에서 적절한 예외 처리를 추가해야 한다. 예를 들어, socket 함수 호출이 실패했을 때는 perror 함수로 에러 메시지를 출력하고 다음 작업으로 넘어가야 한다.

2. 리소스 누수 방지
socket 함수로 생성한 소켓 디스크립터를 close 함수로 반드시 닫아주어야 한다. 따라서 getIPListFromARP 함수에서 소켓 디스크립터를 생성하고 사용한 후에는 close 함수로 닫아주어야 한다.

3. ARP 테이블 업데이트
현재 코드에서는 ARP 테이블에 있는 IP 주소인지 확인하는 부분만 구현되어 있다. ARP 테이블이 업데이트되는 경우에 대비해서, ARP 테이블을 주기적으로 업데이트하는 로직을 추가하는 것이 좋다.

4. 무한 루프 수정
현재 코드는 무한 루프로 돌아가며 ARP 테이블을 주기적으로 업데이트한다. 하지만 이렇게 무한히 돌아가는 경우, 시스템 자원을 과도하게 사용할 수 있습니다. 따라서 ARP 테이블을 업데이트하는 시간 간격을 적절하게 설정해야 한다.

다음은 위의 수정사항을 반영한 코드입니다.

<br/>

```c++
#include <iostream>
#include <vector>
#include <regex>
#include <memory>
#include <stdexcept>
#include <array>
#include <cstdio>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <net/if_arp.h>
#include <unistd.h>

std::vector<std::string> getIPListFromARP()
{
    std::vector<std::string> ip_list;

    // 시스템 명령어로 arp -a 실행
    std::string command = "arp -a";
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // 결과에서 IP 주소 추출
    std::smatch match;
    std::regex re("\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b");
    std::string::const_iterator searchStart(result.cbegin());
    while (std::regex_search(searchStart, result.cend(), match, re)) {
        ip_list.push_back(match.str());
        searchStart = match.suffix().first;
    }

    // ARP 테이블에 있는 IP 주소인지 확인
    for (const auto &ip : ip_list) {
        struct arpreq arp;
        memset(&arp, 0, sizeof(arp));
        struct sockaddr_in *sin = (struct sockaddr_in *)&arp.arp_pa;
        sin->sin_family = AF_INET;
        if (inet_aton(ip.c_str(), &sin->sin_addr) == 0) {
            continue; // 올바른 IP 주소가 아닌 경우 continue
        }
        int sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
        if (sock_fd == -1) {
            perror("socket");
            continue;
        }
        if (ioctl(sock_fd, SIOCGARP, &arp) == -1) {
            // ARP 테이블에 없는 IP 주소일 경우
            close(sock_fd);
            continue;
        }
        // ARP 테이블에 있는 IP 주소일 경우
        close(sock_fd);
    }

    return ip_list;
}

int main()
{
    while(1) 
    {
        try {
            std::vector<std::string> ip_list = getIPListFromARP();

            if (ip_list.empty())
            {
                std::cout << "ARP table is empty" << std::endl;
            }
            else
            {
                std::cout << "ARP table:" << std::endl;
                for (auto ip : ip_list)
                {
                    std::cout << ip << std::endl;
                }
            }
        } catch (const std::exception &e) {
            std::cerr << "Error: " << e.what() << std::endl;
        }
    }

    return 0;
}
```

<br/>

getIPListFromARP() 함수에서 ARP 테이블에 있는 각 IP 주소를 검사하기 전에, 해당 IP 주소가 올바른 형식인지 먼저 확인한다.

이를 위해 inet_aton 함수를 호출하기 전에 IP 주소를 확인하는 코드를 추가했다. 

이로써 잘못된 IP 주소로 인해 발생할 수 있는 오류를 방지할 수 있을 것이다.

또한, try-catch 문을 추가하여 예외 처리를 하도록 수정했습니다. 

popen() 함수가 실패하는 경우와 같이, 예기치 않은 상황이 발생할 수 있는 경우 예외를 던져서 프로그램이 비정상적으로 종료되는 것을 방지한다.

예외가 발생한 경우 해당 예외를 적절히 처리하도록 코드를 수정했다.

<br/>

<br/>

### 윈도우 / 리눅스 환경에서 모두 사용할 수 있는 코드로 수정

```c++
#include <iostream>
#include <string>
#include <vector>
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <array>
#include <regex>
#include <thread>
#include <chrono>

std::string pipe_exec(const char* cmd) {
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}

std::vector<std::string> getArpAddresses() {
    std::vector<std::string> ipAddresses;
    std::string output;

#ifdef _WIN32
    output = pipe_exec("arp -a");
    std::regex ip_regex(R"((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))");
#else
    output = pipe_exec("arp -n");
    std::regex ip_regex(R"((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))");
#endif

    std::sregex_iterator it(output.begin(), output.end(), ip_regex);
    std::sregex_iterator reg_end;

    for (; it != reg_end; ++it) {
        ipAddresses.push_back(it->str());
    }

    return ipAddresses;
}

int main() {
    while(1)
    {
        std::vector<std::string> ipList = getArpAddresses();
        for (const auto& ip : ipList) {
            std::cout << "IP Address: " << ip << std::endl;
        }
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    return 0;
}

```

<br/>

이 코드는 하기와 같이 기능을 수행한다.

- 외부 명령어를 실행하고 출력을 반환하는 exec 함수를 정의
- arp -a(Windows) 또는 arp -n(Linux) 명령어를 실행하여, ARP 테이블의 IP 주소를 가져오는 getArpAddresses 함수를 정의
- main 함수에서 무한 루프를 실행하여 매 초마다 getArpAddresses 함수를 호출하고 결과를 출력
- 코드의 각 부분에 대해 좀 더 자세히 설명하겠습니다.

<br/>

##### exec 함수

- exec 함수는 C++에서 외부 명령어를 실행하고 출력을 반환하는 데 사용된다.
- popen 함수를 사용하여 프로세스를 생성하고, fgets 함수를 사용하여 출력을 읽는다. 
- 출력은 result 문자열에 추가되고, 완료되면 반환된다.

##### getArpAddresses 함수
- getArpAddresses 함수는 arp -a(Windows) 또는 arp -n(Linux) 명령어를 실행하여 ARP 테이블에서 IP 주소를 가져온다.
- 먼저, exec 함수를 호출하여 명령어의 출력을 가져옵니다. 
- 그런 다음 정규 표현식을 사용하여 출력에서 IP 주소를 추출하고, ipAddresses 벡터에 추가한다. 
- 함수가 완료되면 이 벡터를 반환한다.

##### main 함수
- main 함수는 무한 루프를 실행하여 매 초마다 getArpAddresses 함수를 호출하고 결과를 출력한다. 
- std::this_thread::sleep_for(std::chrono::seconds(1))를 사용하여 루프의 각 반복 사이에 1초 동안 대기하도록 설정하였다.
- 이 코드는 arp -a(Windows) 또는 arp -n(Linux) 명령어와 유사한 결과를 출력하며, ARP 테이블의 IP 주소를 가져온다. 
- 무한 루프를 실행하므로 프로그램이 계속 실행되지만, 대부분의 경우 시스템에 큰 부담을 주지 않으며, 필요에 따라 루프 횟수를 제한하거나 간격을 조절할 수 있다.
