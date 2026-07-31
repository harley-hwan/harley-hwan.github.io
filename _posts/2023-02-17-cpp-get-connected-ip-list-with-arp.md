---
title: "(C++) 현재 연결된 IP 목록 뽑아보기 (arp)"
description: "같은 망의 장비 IP를 찾으려고 arp 출력을 파싱하다 'Too many open files'에 막혔다. system → popen → fork/exec를 거치며 계속 같은 에러가 났고, 결국 프로세스를 안 띄우는 방향으로 돌아선 기록이다."
date: 2023-02-17 10:00:00 +0900
categories: [Dev, C++]
tags: [c-language, cpp, linux, command, arp, system, ip, serverip, file-descriptor, proc]
---
## 하려던 것

보드에서 도는 프로그램이 같은 망에 붙어 있는 다른 장비의 IP를 찾아야 했다. 장비는 DHCP로 주소를 받으니 고정 IP를 박아둘 수 없다. 브로드캐스트로 찾는 프로토콜을 따로 만들 수도 있었지만, 이미 통신이 오간 상대라면 ARP 테이블에 남아 있으니 그걸 읽으면 된다고 봤다.

결과부터 적으면, 처음 세 가지 방법은 다 같은 에러에 막혔고 마지막에 접근을 바꿔서 해결했다.

## 1차: system() + 파일 리다이렉션

제일 먼저 떠오른 방법이다. 명령 결과를 파일로 뽑고 그 파일을 읽는다.

```c++
std::vector<std::string> getE6ServerIP()
{
    std::vector<std::string> ip_list;
	std::string ip;
	std::ifstream ifs;
    
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
	return ip_list;
}
```

`arp -a`의 출력에서 IP가 괄호 안에 있다는 걸 이용해, 구분자를 `(`와 `)`로 준 `getline`으로 잘라낸다.

돌아가긴 했는데 마음에 안 드는 부분이 세 개 있었다.

`while (!ifs.eof())`는 마지막에 한 번 더 돈다. `eof()`는 읽기가 실패한 다음에야 참이 되기 때문에, 마지막 줄을 읽은 직후에는 아직 거짓이다. 그래서 빈 문자열이 하나 더 들어가고, 그걸 지우려고 `ip_list.pop_back()`을 붙였다. 증상을 원인 자리에서 고치지 않고 결과에서 지우는 코드라 계속 걸렸다. 실제로 파일 끝에 개행이 없으면 이 `pop_back`이 멀쩡한 IP를 지운다.

임시 파일 경로가 코드에 박혀 있는 것도 문제였다. 그 디렉토리가 없으면 리다이렉션이 실패하고, `ifs.open`도 실패해서 빈 목록이 나온다. 원인은 안 보인다.

그리고 파일을 거치니 명령 실행과 읽기 사이에 디스크가 낀다. 보드의 SD 카드에 초당 한 번씩 쓰는 것도 별로다.

## 2차: popen

파일을 안 거치도록 바꿨다.

```c++
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

출력에서 괄호 안만 뽑는다.

```c++
std::vector<std::string> getIPList() {
    std::vector<std::string> ip_list;
    std::string arpOutput = exec("arp -a");

    size_t pos_left, pos_right;
    while ((pos_left = arpOutput.find("(")) != std::string::npos) {
        pos_right = arpOutput.find(")", pos_left);
        if (pos_right != std::string::npos) {
            ip_list.push_back(arpOutput.substr(pos_left + 1, pos_right - pos_left - 1));
        }
        arpOutput.erase(0, pos_right + 1);
    }
    return ip_list;
}
```

임시 파일이 없어졌고 `pop_back` 같은 보정도 없어졌다. `popen`을 쓰는 방법 자체는 [Linux Command pipe로 변수값으로 끌고오기](/posts/cpp-linux-command-pipe-to-variable/)에 따로 정리해뒀다.

여기에도 함정이 하나 남아 있다. 닫는 괄호를 못 찾으면 `pos_right`가 `npos`이고, `erase(0, npos + 1)`은 `npos + 1 == 0`이라 아무것도 안 지운다. 그러면 같은 위치를 계속 찾아서 무한 루프다. 출력이 중간에 잘리면 프로그램이 멈춘다.

## 그리고 막혔다

이 함수를 1초마다 호출하는 루프에 넣고 한참 돌려놨더니 이런 게 찍히기 시작했다.

```text
/proc/net/arp: Too many open files
wasipEmpty
```

한 번이 아니라 그 뒤로 계속이었다. IP가 안 나오니 `wasipEmpty`가 따라 붙는다.

처음엔 이 메시지가 내 프로그램 것인 줄 알았다. 아니었다. `arp` 명령이 `/proc/net/arp`를 열려다 실패해서 자기가 찍은 것이다. 즉 **자식 프로세스가 파일을 못 열고 있다**.

자식은 부모의 파일 디스크립터 테이블을 그대로 물려받는다. 부모가 열어둔 게 한도까지 차 있으면 자식은 새로 열 게 없다. 그러니 실제로 새는 쪽은 내 프로그램이었다.

## 3차: fork/exec를 직접

셸을 안 거치면 나아질까 싶어서 파이프를 직접 짰다.

```c++
vector<string> getARPList() {
    vector<string> ip_list;

    int my_pipe[2];
    const char* arguments[] = {"arp", "-a", NULL}; 

    if(pipe(my_pipe) == -1) {
        fprintf(stderr, "Error creating pipe\n");
        return ip_list;
    }

    pid_t child_id = fork();
    if(child_id == -1) {
        fprintf(stderr, "Fork error\n");
        return ip_list;
    }
    if(child_id == 0) // child process
    {
        close(my_pipe[0]);
        dup2(my_pipe[1], 1);
        execvp(arguments[0], const_cast<char**>(arguments));
        fprintf(stderr, "Exec failed\n");
        exit(1);
    }
    else
    {
        close(my_pipe[1]);

        char* reading_buf = new char[1024];
        char *ptr=reading_buf;
        while(read(my_pipe[0], ptr, 1) > 0) {
            ptr++;
        }
        (*ptr)='\0';

        char *line=strtok(reading_buf,"\n");
        while(line) {
            char* ip_start = strstr(line, "(");
            if(ip_start) {
                char* ip_end = strstr(ip_start, ")");
                if(ip_end) {
                    ip_list.push_back(string(ip_start + 1, ip_end - ip_start - 1));
                }
            }
            line=strtok(NULL,"\n");
        }

        delete[] reading_buf;
        close(my_pipe[0]);
        waitpid(child_id, NULL, 0);
    }

    return ip_list;
}
```

결과는 같았다.

```text
/proc/net/arp: Too many open files
/proc/net/arp: Too many open files
/proc/net/arp: Too many open files
```

당시에는 여기서 원인을 못 찾고 다른 방향으로 돌아섰다. 지금 다시 보면 확인해봤어야 할 게 몇 가지 있다.

## 지금이라면 이렇게 확인한다

파일 디스크립터가 새는지는 세어보면 바로 안다. 리눅스는 프로세스가 연 것들을 파일로 보여준다.

```bash
ls /proc/<pid>/fd | wc -l
```

이걸 몇 분 간격으로 찍어서 늘어나면 새는 것이고, 일정하면 다른 문제다. 뭐가 열려 있는지는 `ls -l /proc/<pid>/fd`나 `lsof -p <pid>`로 보인다. 소켓인지 파이프인지 파일인지가 나오니 어느 코드가 범인인지 좁혀진다.

현재 한도는 이걸로 본다.

```bash
ulimit -n              # 소프트 한도 (보통 1024)
cat /proc/<pid>/limits # 실제 적용값
```

1초에 한 번 호출하는데 한 호출에 하나씩 새면, 1024초 즉 17분쯤 뒤에 터진다. 실제로 "한참 돌려놨더니" 나기 시작한 것과 시간대가 맞는다.

새는 자리로 의심되는 곳도 있다. 위 코드에서 `fork()`가 실패하면 그대로 `return`하는데, 그 직전에 만든 파이프 두 개를 안 닫는다. 아주 드물지만 한 번 일어날 때마다 두 개가 샌다.

더 넓게 보면, 이 함수가 실제로는 다른 통신 코드와 같은 프로세스 안에서 돌고 있었다는 점이 중요하다. 소켓을 열고 닫는 코드가 근처에 여러 개 있었고, 그중 하나가 예외 경로에서 안 닫혔다면 `arp`를 띄우는 이 함수는 그냥 **먼저 비명을 지른 쪽**일 뿐이다. 자식 프로세스는 파일을 하나만 열면 되니까 한도에 제일 먼저 부딪힌다.

그래서 "arp 호출부를 계속 고치는" 방향 자체가 틀렸다. 프로세스 전체의 fd 수를 먼저 봤어야 했다.

`ulimit -n`을 올리는 건 임시방편이다. 새는 걸 안 고치면 시간만 늘어난다. 다만 새지 않는데도 동시에 여는 개수가 많아 부족한 경우에는 이게 맞는 해결이다. 둘을 구분하려면 결국 시간에 따라 fd 수가 늘어나는지 봐야 한다.

## 명령을 안 쓰고 커널에 직접 물어보려던 시도

명령을 띄우는 게 문제라면 아예 안 띄우면 되지 않을까 싶어서, 소켓과 `ioctl`로 ARP 항목을 직접 조회해봤다.

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

이건 방향이 틀렸다. `getifaddrs`가 주는 건 **내 인터페이스 목록**이지 상대 목록이 아니다. 그 주소로 `SIOCGARP`를 물어보면 "내 IP가 ARP 테이블에 있는가"를 확인하는 셈이라, 찾으려던 다른 장비는 애초에 후보에 없다.

`SIOCGARP`는 특정 IP 하나의 MAC을 조회하는 용도다. 테이블 전체를 훑는 기능이 아니다. 그러니 후보 IP를 이미 알고 있어야 쓸 수 있다.

`hwaddr` 변수도 만들어놓고 안 쓴다. MAC을 꺼내려던 흔적인데 `inet_ntop`으로 IP만 담고 끝난다.

소켓을 인터페이스마다 새로 열고 닫는 것도 마음에 안 든다. `close`가 다 있어서 새지는 않지만, 하나만 만들어 재사용하면 될 일이다.

그다음에는 절충안으로 popen + 정규식으로 IP를 모은 뒤, 각 IP를 `SIOCGARP`로 한 번씩 확인하는 형태도 만들어봤다. 그런데 그 루프가 이렇게 생겼다.

```c++
for (const auto &ip : ip_list) {
    // ... arpreq 준비 ...
    if (ioctl(sock_fd, SIOCGARP, &arp) == -1) {
        // ARP 테이블에 없는 IP 주소일 경우
        close(sock_fd);
        continue;
    }
    // ARP 테이블에 있는 IP 주소일 경우
    close(sock_fd);
}
return ip_list;
```

**검사 결과로 아무것도 안 한다.** 있으면 `close`하고, 없어도 `close`하고 `continue`한다. `ip_list`에서 빼지도 않고 다른 목록에 담지도 않는다. 결국 `ioctl`을 부르기 전과 정확히 같은 목록이 반환된다.

주석에는 "ARP 테이블에 있는 IP 주소일 경우"라고 분기가 나뉜 것처럼 적혀 있어서, 코드를 훑을 때는 걸러지는 줄 알았다. 주석이 의도를 적고 코드가 그걸 안 하면 읽는 사람이 속는다.

방향이 틀렸다는 걸 알고 나서 "테이블 전체를 주는 곳이 어디인가"를 다시 찾았고, 그게 다음 절이다.

## 4차: 프로세스를 안 띄우기

에러의 원인과 별개로, `arp` 명령을 초당 한 번씩 띄우는 것 자체가 과했다. 매번 `fork`하고 `exec`하고 회수하는 비용을 내면서 얻는 게 텍스트 몇 줄이다.

같은 정보를 커널이 파일로 준다.

```text
$ cat /proc/net/arp
IP address       HW type     Flags       HW address            Mask     Device
192.168.8.152    0x1         0x2         88:36:6c:fc:2c:4f     *        wlan0
192.168.8.114    0x1         0x0         00:00:00:00:00:00     *        wlan0
```

프로세스를 안 띄우고, 열었다 닫는 파일이 하나뿐이고, 열 위치가 고정이라 파싱이 단순하다. 무엇보다 `arp` 명령의 출력 형식이나 로케일에 안 휘둘린다.

```c++
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

std::vector<std::string> getArpEntries(bool only_resolved = true)
{
    std::vector<std::string> ips;
    std::ifstream f("/proc/net/arp");
    if (!f) return ips;

    std::string line;
    std::getline(f, line);                 // 헤더 한 줄 버린다

    while (std::getline(f, line)) {
        std::istringstream ss(line);
        std::string ip, hwtype, flags, hw, mask, dev;
        if (!(ss >> ip >> hwtype >> flags >> hw >> mask >> dev)) continue;

        // flags 의 0x2 (ATF_COM) 가 서 있어야 MAC 이 확정된 항목이다
        if (only_resolved && std::stoul(flags, nullptr, 16) != 0x2) continue;

        ips.push_back(ip);
    }
    return ips;
}
```

`flags`를 보는 게 중요하다. `0x0`인 항목은 ARP 요청을 보냈지만 아직 응답을 못 받은 상태라 MAC이 `00:00:00:00:00:00`이다. 명령 출력에서는 `<incomplete>`로 보이는 것들이다. 이걸 안 거르면 응답 없는 IP가 목록에 섞인다. 처음 `arp -a`를 파싱할 때 `incomplete`라는 문자열을 찾아서 걸렀던 것과 같은 처리인데, 플래그 비교가 훨씬 명확하다.

`/proc` 파일은 실제 디스크 파일이 아니라 읽을 때마다 커널이 만들어주는 내용이라, 열어놓고 재사용하면 안 된다. 매번 열고 닫아야 최신 값이 나온다. 대신 여는 비용이 프로세스를 띄우는 것보다 훨씬 싸다.

## ARP 테이블은 만능이 아니다

방향을 바꾸고 나서 알게 된 한계도 적어둔다.

ARP 테이블에는 **최근에 통신한 상대만** 남는다. 장비가 켜져 있어도 한 번도 패킷을 주고받지 않았으면 항목이 없다. 그리고 리눅스는 오래된 항목을 정리하기 때문에, 몇 분 조용하면 사라지거나 `incomplete`가 된다.

그래서 실제로는 이렇게 썼다. 먼저 브로드캐스트나 서브넷 스윕으로 한 번 건드려서 ARP 테이블을 채우고, 그다음에 테이블을 읽는다.

```c++
// 서브넷을 한 번 훑어 ARP 테이블을 채운다 (응답은 안 봐도 된다)
for (int i = 1; i < 255; ++i) {
    // UDP 소켓으로 아무 포트에 한 바이트 보내면 ARP 가 먼저 나간다
}
```

이 방식도 결국 소켓을 많이 열게 되니, 여기서야말로 fd 관리를 조심해야 한다. 앞의 에러를 겪고 나서는 소켓을 만드는 자리마다 RAII로 감쌌다.

```c++
struct Fd {
    int fd = -1;
    Fd() = default;
    explicit Fd(int f) : fd(f) {}
    ~Fd() { if (fd >= 0) ::close(fd); }
    Fd(const Fd&) = delete;
    Fd& operator=(const Fd&) = delete;
    Fd(Fd&& o) noexcept : fd(o.fd) { o.fd = -1; }
    explicit operator bool() const { return fd >= 0; }
};
```

이걸 쓰기 시작한 뒤로는 같은 종류의 문제가 안 생겼다. 어디로 빠져나가든, 예외가 나든 닫힌다.

더 정확하게 하려면 netlink 소켓으로 `RTM_GETNEIGH`를 물어보는 방법이 있다. 커널과 직접 이야기하니 텍스트 파싱이 아예 없고 이웃 상태(`NUD_REACHABLE`, `NUD_STALE` 등)까지 세분해서 준다. `/proc/net/arp`로 충분해서 거기까지는 안 갔지만, IPv6까지 다뤄야 하면 `/proc/net/arp`에는 IPv6가 안 나오므로 netlink가 필요하다.

## 윈도우도 같이 지원해야 했다

검사 프로그램은 윈도우에서 돌아서, 같은 기능을 양쪽에 맞춰야 했다. 명령 이름만 갈라주고 파싱은 정규식으로 통일한 버전이다.

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

`unique_ptr`에 `pclose`를 삭제자로 물려둔 게 [2차 시도](#2차-popen)보다 나아진 부분이다. 중간에 예외가 나도 파이프가 닫힌다. 앞에서 fd 한도에 부딪힌 뒤로 생긴 습관이다.

`#ifdef` 양쪽의 정규식이 완전히 같아서 밖으로 뺄 수 있다. 갈라지는 건 명령 이름뿐이다.

이렇게 정규식으로 IP를 긁는 방식으로 잠깐 썼는데, 두 가지가 걸렸다.

윈도우 `arp -a` 출력에는 맨 위에 `인터페이스: 192.168.0.5 --- 0x5`처럼 **자기 IP가 먼저** 나온다. 정규식이 그것까지 잡아서 목록에 자기 자신이 들어간다. 그리고 `_popen`은 콘솔 창을 띄우기 때문에, GUI 프로그램에서 1초마다 부르면 검은 창이 계속 깜빡인다.

윈도우에는 API가 따로 있다. `GetIpNetTable2`가 ARP 테이블을 구조체 배열로 준다. 프로세스도 안 띄우고 파싱도 없다.

```c++
#include <netioapi.h>
#pragma comment(lib, "iphlpapi.lib")

MIB_IPNET_TABLE2* table = nullptr;
if (GetIpNetTable2(AF_INET, &table) == NO_ERROR) {
    for (ULONG i = 0; i < table->NumEntries; ++i) {
        const auto& e = table->Table[i];
        if (e.State == NlnsReachable || e.State == NlnsStale) {
            // e.Address.Ipv4.sin_addr, e.PhysicalAddress
        }
    }
    FreeMibTable(table);
}
```

결국 양쪽 다 "명령을 띄워서 출력을 파싱한다"에서 "OS가 주는 구조화된 데이터를 읽는다"로 갔다. 코드가 갈리긴 하지만 각각은 더 짧고 안정적이다.

## 정리하면

- `Too many open files`가 자식 프로세스에서 났다면 새는 쪽은 부모다. 자식은 fd 테이블을 물려받는다
- fd 누수는 `ls /proc/<pid>/fd | wc -l`을 시간에 따라 찍어보면 바로 판별된다. 늘어나면 누수, 일정하면 한도 부족이다
- `ulimit -n`을 올리는 건 누수를 안 고치면 시간만 늘린다
- 에러를 낸 코드가 원인인 코드가 아닐 수 있다. 파일을 하나만 여는 쪽이 먼저 비명을 지른다
- 명령 출력을 파싱하기 전에 `/proc/net/arp`(리눅스), `GetIpNetTable2`(윈도우)처럼 구조화된 경로가 있는지 본다
- ARP 테이블에는 최근 통신한 상대만 남는다. 조회 전에 한 번 건드려서 채워야 한다
- 소켓과 파일은 처음부터 RAII로 감싸두면 이 종류의 문제 자체가 안 생긴다
