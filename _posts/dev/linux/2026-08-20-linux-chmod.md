---
title: "chmod — 리눅스 파일 권한의 구조와 사용법"
description: "리눅스 권한이 어디에 어떤 모양으로 저장되고 커널이 그것으로 무엇을 판정하는지 정리했다. ls -l 열 글자와 열두 개의 모드 비트, 세 벌 가운데 한 벌만 보고 끝내는 판정 순서, 파일과 디렉터리에서 갈리는 rwx 의 뜻, 삭제 권한이 디렉터리에 있는 이유, umask, setuid·setgid·sticky, 재귀 적용에서 어긋나는 자리까지."
date: 2026-08-20 10:00:00 +0900
slug: 'linux-chmod'
categories: [Dev, Linux]
tags: [linux, chmod, permission, umask, setuid, setgid, sticky-bit, file-system, shell, security]
---

이번에는 chmod 를 정리해 두겠다. 명령 자체는 `chmod 755 파일` 한 줄이라 외우면 그만인 것처럼 보이는데, 실제로 막히는 자리는 명령이 아니라 그 뒤에 있다. 파일에 쓰기 권한이 없는데도 남이 지워 가고, 스크립트에 setuid 를 걸었는데 아무 일도 일어나지 않고, 새로 만든 파일은 늘 644 로 나온다. 그래서 권한이 어디에 어떤 모양으로 저장되고 커널이 그것으로 무엇을 판단하는지부터 보고, 명령은 그다음에 보겠다.

아래 출력은 GNU coreutils 9.4 를 쓰는 Debian 계열 리눅스 6.18 기준이다. `alice` 와 `bob` 은 일반 사용자, `shared` 는 둘이 함께 속한 그룹이다.

* * *

## 1. 권한은 파일마다 붙은 열두 개의 비트다

파일 하나에 딸린 관리 정보는 아이노드(inode)라는 자리에 모여 있다. 크기, 만든 시각, 데이터가 어느 블록에 있는지 같은 것들인데 그 가운데 `st_mode` 라는 필드가 권한을 담는다.

이 필드가 통째로 권한인 것은 아니다. 위쪽은 파일의 종류를 적어 두는 자리다.

```text
st_mode = 0100644   =   010 (보통 파일)  +  0644 (권한)
st_mode = 0040755   =   004 (디렉터리)   +  0755 (권한)
```

위쪽 세 자리가 종류고 아래 네 자리가 권한이다. 종류는 만들 때 정해져 나중에 바꿀 수 없다. chmod 가 건드리는 것은 아래 네 자리, 곧 열두 개의 비트뿐이다.

열두 개는 세 개씩 네 벌로 나뉜다. 특수 비트 한 벌과 소유자·그룹·그 밖 세 벌이다. `ls -l` 이 찍는 열 글자가 이 비트를 그대로 옮겨 적은 것이다.

![모드 비트 구조](/assets/img/posts/linux-chmod/fig1-mode-bits.svg){: width="860"}
_그림 1. 맨 앞 한 글자는 파일의 종류라서 chmod 가 손대지 못한다. 나머지 아홉 글자가 세 벌로 끊어져 8진수 세 자리와 하나씩 대응한다._

비트마다 8진수 자릿값이 붙어 있다. 읽기가 4, 쓰기가 2, 실행이 1이고 한 벌 안에서 켜진 것을 더하면 그 자리의 숫자가 된다. 8진수를 쓰는 이유는 세 비트가 정확히 8진수 한 자리에 들어맞기 때문이다.

| 세 글자 | 값 | 더한 내역 |
| :--- | ---: | :--- |
| `rwx` | 7 | 4 + 2 + 1 |
| `rw-` | 6 | 4 + 2 |
| `r-x` | 5 | 4 + 1 |
| `r--` | 4 | 4 |
| `-wx` | 3 | 2 + 1 |
| `-w-` | 2 | 2 |
| `--x` | 1 | 1 |
| `---` | 0 | 0 |

자주 쓰는 값을 `ls -l` 문자열과 나란히 놓으면 이렇게 된다.

| 8진수 | 권한 아홉 글자 | 흔히 쓰는 자리 |
| ---: | :--- | :--- |
| 600 | `rw-------` | 개인 설정 파일, SSH 개인키 |
| 644 | `rw-r--r--` | 보통의 문서와 소스 파일 |
| 664 | `rw-rw-r--` | 같은 그룹이 함께 고치는 파일 |
| 700 | `rwx------` | 나만 쓰는 디렉터리, `~/.ssh` |
| 750 | `rwxr-x---` | 그룹까지만 들여보내는 디렉터리 |
| 755 | `rwxr-xr-x` | 실행 파일, 공개 디렉터리 |
| 775 | `rwxrwxr-x` | 그룹이 함께 쓰는 디렉터리 |
| 777 | `rwxrwxrwx` | 쓸 일이 거의 없다 |

앞의 한 글자는 종류라서 파일이면 `-`, 디렉터리면 `d` 가 붙는다.

한 가지 갈라 둘 것이 있다. 소유자와 그룹이 누구인지는 권한 비트가 아니라 아이노드의 다른 필드에 uid 와 gid 로 들어 있다. 그것을 바꾸는 명령은 `chown` 과 `chgrp` 이고 chmod 는 손대지 않는다. chmod 는 이미 정해진 그 세 부류에게 무엇을 허락할지만 정한다.

* * *

## 2. 커널은 세 벌 가운데 한 벌만 본다

여기가 가장 자주 잘못 알려져 있는 자리다. 커널은 세 벌을 모두 보고 그 가운데 가장 넉넉한 것을 골라 주지 않는다. 위에서부터 내려가다 **처음 걸리는 한 벌만 보고 판정을 끝낸다.**

![접근 판정 순서](/assets/img/posts/linux-chmod/fig2-access-check.svg){: width="860"}
_그림 2. 소유자에 걸리면 그룹과 그 밖은 아예 읽지 않는다. 어느 자리에서 멈추느냐가 결과를 정한다._

그래서 자기 파일인데도 못 읽는 일이 생긴다. alice 가 가진 파일에 소유자 자리만 비워 두면 그룹과 그 밖에 읽기가 열려 있어도 alice 는 막힌다.

```bash
$ ls -l t1
----r--r-- 1 alice alice 7 Aug 20 02:24 t1

$ cat t1
cat: t1: Permission denied
```

소유자 자리에 읽기를 넣어 주면 그제야 열린다.

```bash
$ chmod 444 t1 && cat t1
secret
```

그룹도 같다. 아래 파일은 그룹 자리가 비어 있고 그 밖에는 읽기가 열려 있다. alice 는 `shared` 그룹에 속해 있으므로 그룹 자리에서 판정이 끝나고, 그 밖의 `r` 은 보지도 않는다.

```bash
$ ls -l t2
-r-----r-- 1 root shared 6 Aug 20 02:25 t2

$ id -nG alice
alice shared

$ cat t2
cat: t2: Permission denied
```

반대로 그 그룹에 속하지 않은 사람은 그 밖 자리를 보게 되므로 읽을 수 있다. **자기 자리를 좁게 잡으면 남보다 못한 권한을 갖게 된다.** 흔치는 않지만 특정 프로세스만 못 건드리게 막을 때 일부러 쓰기도 한다.

### root 와 CAP_DAC_OVERRIDE

root 는 `CAP_DAC_OVERRIDE` 라는 능력을 가지고 있어서 권한 비트를 무시하고 읽고 쓴다. 000 인 파일도 그냥 열린다. 다만 한 군데 예외가 있다. **실행 비트가 세 벌 어디에도 없으면 root 도 실행하지 못한다.**

```bash
# stat -c '%a %n' tbin
644 tbin
# ./tbin
bash: ./tbin: Permission denied

# chmod 744 tbin && ./tbin
(정상 실행)
```

읽기와 쓰기는 뚫어 주면서 실행만 막는 이유는, 실행 비트가 없는 파일은 애초에 프로그램으로 쓸 의도가 아니었다고 보기 때문이다. 실수로 데이터 파일을 실행해 버리는 것을 커널이 한 겹 막아 준다.

이 예외는 디렉터리에는 걸리지 않는다. 디렉터리의 `x` 는 실행이 아니라 통행이라서 그쪽은 그대로 뚫리고, root 는 000 인 디렉터리도 지나간다.

### 권한을 검사하는 시점

권한은 `open()` 이 불릴 때 검사하고, 그렇게 열린 파일 서술자에는 다시 묻지 않는다. 이미 열려 있는 파일의 권한을 000 으로 내려도 그 서술자로는 계속 읽을 수 있다.

```python
f = open('fdtest')
os.chmod('fdtest', 0o000)
print(f.read())      # 'payload\n' 이 그대로 나온다
```

돌고 있는 프로세스의 접근을 끊으려고 chmod 를 거는 것은 그래서 소용이 없다. 그 프로세스가 파일을 다시 열 때부터 걸린다.

### 모드를 바꿀 수 있는 사람

쓰기 권한이 있다고 chmod 를 할 수 있는 것이 아니다. 모드를 바꾸는 것은 소유자와 root 만 할 수 있다. 666 인 남의 파일에 내용은 얼마든지 써 넣을 수 있지만 권한은 못 바꾼다.

```bash
$ chmod 600 own
chmod: changing permissions of 'own': Operation not permitted
```

`Permission denied` 가 아니라 `Operation not permitted` 가 나오는 것이 표시다. 앞의 것은 권한 비트에 막힌 것이고, 뒤의 것은 애초에 그 일을 할 자격이 없다는 뜻이다.

* * *

## 3. 파일과 디렉터리에서 rwx 는 다른 것을 뜻한다

같은 세 글자인데 대상이 디렉터리면 뜻이 통째로 바뀐다. 디렉터리는 내용이 들어 있는 상자가 아니라 이름과 아이노드 번호를 짝지어 둔 표이기 때문이다.

![파일과 디렉터리의 rwx](/assets/img/posts/linux-chmod/fig3-file-vs-dir.svg){: width="860"}
_그림 3. 디렉터리의 x 는 실행이 아니라 통행이다. 이 한 글자가 목록을 보는 일과 안으로 들어가는 일을 갈라놓는다._

`r` 과 `x` 를 따로 떼어 보면 차이가 분명해진다. 읽기만 있고 실행이 없는 디렉터리에서는 이름은 보이는데 그 이름으로 아무것도 못 한다.

```bash
$ stat -c '%a %n' d_r
444 d_r

$ ls d_r
known

$ ls -l d_r
ls: cannot access 'd_r/known': Permission denied
total 0
-????????? ? ? ? ?            ? known

$ cat d_r/known
cat: d_r/known: Permission denied
```

`ls` 는 이름만 읽으면 되니 통과하고, `ls -l` 은 각 항목의 크기와 시각을 알아야 하므로 디렉터리를 지나 아이노드까지 닿아야 한다. 그 통행이 막혀서 물음표만 찍힌다.

반대로 실행만 있고 읽기가 없으면 목록은 못 보는데 이름을 알고 있으면 닿는다.

```bash
$ stat -c '%a %n' d_x
111 d_x

$ ls d_x
ls: cannot open directory 'd_x': Permission denied

$ cat d_x/known
inside
```

`711` 인 홈 디렉터리가 이 성질을 쓴 것이다. 남이 내 홈에 무엇이 있는지 훑어보지는 못하지만, 웹 서버가 `~/public_html/index.html` 처럼 정확한 경로로는 지나갈 수 있다.

경로를 따라가는 데에는 중간에 있는 모든 디렉터리의 `x` 가 필요하다. `/a/b/c/file` 을 열려면 `/`, `/a`, `/a/b`, `/a/b/c` 를 차례로 지나야 하고, 한 곳이라도 막히면 그 아래가 아무리 열려 있어도 닿지 못한다. 권한 문제를 쫓을 때 파일만 보고 있으면 답이 안 나오는 이유가 대개 여기에 있다.

> 접근이 막혔는데 파일 권한이 멀쩡해 보이면 `namei -l /긴/경로/파일` 을 찍어 본다. 경로 구성 요소의 권한을 한 줄씩 보여 주므로 어느 단계에서 막혔는지 바로 보인다.
{: .prompt-tip }

* * *

## 4. 삭제 권한은 디렉터리에 있다

파일을 지우는 일은 파일을 건드리는 일이 아니다. 디렉터리라는 표에서 이름 한 줄을 빼는 일이다. 그래서 필요한 것은 그 파일의 `w` 가 아니라 **그 파일이 담긴 디렉터리의 `w`** 다.

![삭제 권한](/assets/img/posts/linux-chmod/fig4-delete-permission.svg){: width="860"}
_그림 4. 왼쪽은 아무도 못 읽는 파일인데 지워지고 오른쪽은 누구나 고칠 수 있는 파일인데 안 지워진다. 판정을 쥔 쪽은 언제나 바깥의 디렉터리다._

한쪽은 mode 000 인 root 소유 파일이 777 인 디렉터리에 들어 있다. alice 는 그 파일을 읽지도 쓰지도 못하지만 지울 수는 있다.

```bash
$ ls -ld del1 && ls -l del1/victim
drwxrwxrwx 2 root root 4096 Aug 20 02:25 del1
---------- 1 root root    2 Aug 20 02:25 del1/victim

$ rm -f del1/victim && ls del1
(빈 목록)
```

다른 쪽은 정반대다. 777 인 파일이 755 인 디렉터리에 들어 있으면 내용은 마음대로 고치는데 지우지는 못한다.

```bash
$ ls -ld del2 && ls -l del2/fortress
drwxr-xr-x 2 root root 4096 Aug 20 02:25 del2
-rwxrwxrwx 1 root root    2 Aug 20 02:25 del2/fortress

$ rm -f del2/fortress
rm: cannot remove 'del2/fortress': Permission denied

$ echo pwned >> del2/fortress
(성공한다)
```

파일 이름을 바꾸는 것도 같다. `mv` 는 한쪽 디렉터리에서 이름을 빼고 다른 쪽에 넣는 일이라 두 디렉터리의 `w` 를 모두 요구한다.

이 규칙에는 실용적인 문제가 하나 따라온다. `/tmp` 처럼 누구나 파일을 만들어야 하는 디렉터리는 `w` 를 모두에게 열어야 하는데, 그러면 서로의 파일을 지울 수 있게 된다. 7절의 sticky 비트가 그 자리를 메운다.

* * *

## 5. 8진수로 적는 법과 기호로 적는 법

chmod 에 모드를 넘기는 방법은 두 가지다.

**8진수는 최종 상태를 통째로 지정한다.** 지금 값이 무엇이든 상관없이 적은 대로 덮어쓴다.

```bash
chmod 644 report.txt
chmod 755 deploy.sh
chmod 700 ~/.ssh
```

**기호 표기는 지금 값에서 무엇을 더하고 뺄지 지정한다.** `[누구][연산][무엇]` 순서로 적고 쉼표로 여러 벌을 이어 붙인다.

| 자리 | 쓸 수 있는 글자 |
| :--- | :--- |
| 누구 | `u` 소유자, `g` 그룹, `o` 그 밖, `a` 셋 모두 |
| 연산 | `+` 더한다, `-` 뺀다, `=` 그 자리를 적은 것으로 맞춘다 |
| 무엇 | `r`, `w`, `x`, `X`, `s` setuid·setgid, `t` sticky, 그리고 `u`·`g`·`o` |

640 인 파일에 하나씩 걸어 본 결과다.

| 명령 | 결과 | 하는 일 |
| :--- | ---: | :--- |
| `chmod u+x` | 740 | 소유자에게 실행을 더한다 |
| `chmod g+w` | 660 | 그룹에게 쓰기를 더한다 |
| `chmod go-rwx` | 600 | 소유자 밖의 모든 권한을 뗀다 |
| `chmod a=r` | 444 | 셋 다 읽기만 남긴다 |
| `chmod u=rw,go=r` | 644 | 두 벌을 한 줄에 지정한다 |
| `chmod o=u` | 646 | 소유자 자리를 그 밖 자리에 복사한다 |

마지막 줄처럼 `u`, `g`, `o` 를 오른쪽에 두면 다른 자리의 값을 그대로 베껴 온다. 8진수를 세지 않고 "그룹은 소유자와 같게" 를 그대로 적을 수 있다. 파일 하나의 권한을 다른 파일에 통째로 옮길 때는 `chmod --reference=원본 대상` 이 있다. 특수 비트까지 함께 복사된다.

기호 표기의 쓸모는 **나머지를 건드리지 않는다**는 데 있다. `chmod 755` 는 지금 무엇이 걸려 있든 지우고 덮어쓰지만 `chmod u+x` 는 실행 비트 하나만 켠다. 스크립트에서 다른 사람이 설정한 권한을 지우고 싶지 않을 때는 기호 표기 쪽이 안전하다.

### 누구를 생략하면 umask 가 끼어든다

`chmod +x` 처럼 앞의 `u`, `g`, `o`, `a` 를 빼면 `a` 와 같아 보이지만 같지 않다. POSIX 는 생략했을 때 현재 umask 에 켜져 있는 비트를 빼고 적용하도록 정해 두었고 GNU chmod 도 그렇게 동작한다. 640 인 파일에 걸어 보면 갈린다.

| umask | `chmod +x` | `chmod a+x` |
| :--- | ---: | ---: |
| 022 | 751 | 751 |
| 077 | 740 | 751 |

umask 077 은 그룹과 그 밖을 모두 막아 둔 상태라 `+x` 는 소유자에게만 실행을 붙인다. 셸마다 umask 가 다를 수 있으므로 **스크립트에서는 `a` 를 반드시 적어 준다.** 손으로 칠 때 한 글자 아낀 것이 자동화에서는 재현되지 않는 동작이 된다.

* * *

## 6. 새로 만들어지는 것의 기본 권한은 umask 가 정한다

파일을 만들 때 프로그램은 원하는 권한을 `open()` 이나 `mkdir()` 에 인자로 넘긴다. 커널은 그 값을 그대로 쓰지 않고 프로세스마다 들고 있는 umask 에 켜진 비트를 걷어 낸 뒤에 적용한다.

![umask 동작](/assets/img/posts/linux-chmod/fig5-umask.svg){: width="860"}
_그림 5. umask 에 1 이 선 자리는 결과에서 반드시 0 이 된다. 요구한 값에 없던 비트가 새로 생기는 일은 없다._

umask 값을 바꿔 가며 파일과 디렉터리를 만들어 보면 이렇게 나온다.

| umask | `touch` 한 파일 | `mkdir` 한 디렉터리 |
| :--- | ---: | ---: |
| 000 | 666 | 777 |
| 002 | 664 | 775 |
| 007 | 660 | 770 |
| 022 | 644 | 755 |
| 077 | 600 | 700 |

파일이 666 에서 시작하고 디렉터리가 777 에서 시작하는 것은 umask 와 상관없는 별개의 사실이다. `touch` 를 비롯한 대부분의 프로그램이 파일을 만들 때 0666 을 요구하도록 짜여 있고, `mkdir` 은 0777 을 요구한다. **새 파일에 실행 비트가 없는 것은 umask 가 깎아서가 아니라 프로그램이 애초에 요구하지 않기 때문이다.** 실제로 0777 을 요구하는 프로그램을 만들어 돌리면 umask 022 에서 755 인 파일이 나온다.

```python
# umask 022 에서
os.open('a', os.O_CREAT | os.O_WRONLY, 0o777)   # 결과 0755
os.open('b', os.O_CREAT | os.O_WRONLY, 0o666)   # 결과 0644
```

### umask 가 실제로 하는 연산

umask 를 "요구한 값에서 빼는 수" 로 외우면 대개는 맞고 가끔 틀린다. 실제 연산은 뺄셈이 아니라 `요구값 AND NOT umask` 라는 비트 연산이다.

| umask | 뺄셈으로 짐작한 값 | 실제 값 |
| :--- | ---: | ---: |
| 023 | 643 | 644 |
| 111 | 555 | 666 |

umask 023 의 마지막 자리 3은 쓰기와 실행을 막으라는 뜻인데, 요구값 666 의 그 밖 자리에는 애초에 실행이 없으므로 실제로 빠지는 것은 쓰기 하나뿐이고 4가 남는다. umask 111 은 실행만 막으라는 뜻이고 666 에는 실행 비트가 없으니 아무것도 안 지워져 666 그대로 나온다. **umask 는 없는 권한을 더 깎지 못하고, 있는 권한을 새로 만들지도 못한다.**

### 값은 어디서 오는가

umask 는 프로세스마다 들고 있고 자식 프로세스가 그대로 물려받는다. 로그인할 때의 초깃값은 이 환경에서는 `/etc/login.defs` 에 있고 PAM 의 `pam_umask` 모듈이 적용한다.

```bash
$ grep -E 'UMASK|USERGROUPS_ENAB' /etc/login.defs
UMASK           022
USERGROUPS_ENAB yes
```

`USERGROUPS_ENAB yes` 는 사용자마다 자기 이름과 같은 전용 그룹을 주는 배포판에서 그룹 비트를 열어 주는 설정이다. 그래서 같은 시스템인데도 로그인한 사람에 따라 값이 다르게 나온다.

```bash
# id -un && umask
root
0022

$ id -un && umask
alice
0002
```

셸에서 `umask 077` 로 바꾸면 그 셸과 그 아래에서 만들어지는 것에만 적용된다. 서비스 데몬의 기본 권한을 바꾸려면 그 서비스를 띄우는 자리에서 지정해야 한다. systemd 유닛이라면 `UMask=` 항목이 그 자리다.

* * *

## 7. 특수 비트 셋

앞쪽 8진수 자리에 들어가는 세 비트는 각각 다른 일을 한다. 값이 하나씩 4000, 2000, 1000 이다.

![특수 비트](/assets/img/posts/linux-chmod/fig6-special-bits.svg){: width="860"}
_그림 6. 셋 다 x 자리를 빌려 쓴다. 소문자면 그 자리에 x 가 함께 있는 것이고 대문자면 x 없이 특수 비트만 있는 것이다._

`ls -l` 에서 이들은 자기 칸을 따로 갖지 않고 `x` 자리에 겹쳐 나온다.

| 8진수 | `ls -l` | 읽는 법 |
| ---: | :--- | :--- |
| 4755 | `-rwsr-xr-x` | setuid, 소유자 실행 있음 |
| 4644 | `-rwSr--r--` | setuid, 소유자 실행 없음 |
| 2755 | `-rwxr-sr-x` | setgid, 그룹 실행 있음 |
| 2644 | `-rw-r-Sr--` | setgid, 그룹 실행 없음 |
| 1777 | `drwxrwxrwt` | sticky, 그 밖 실행 있음 |
| 1644 | `-rw-r--r-T` | sticky, 그 밖 실행 없음 |

대문자가 보인다면 실행 비트 없이 특수 비트만 걸린 상태다. 대개 의도한 조합이 아니므로 눈에 띄면 한 번 확인해 볼 자리다.

### setuid 4000

실행 파일에 걸면 그 프로그램이 실행하는 사람이 아니라 **파일 소유자의 권한으로 돈다.** 프로세스는 두 개의 uid 를 들고 있는데, 누가 실행했는지를 적어 둔 실제 uid 는 그대로고 권한 판정에 쓰이는 실효 uid 만 파일 소유자로 바뀐다.

```bash
$ ls -l showid
-rwsr-xr-x 1 root root 16048 Aug 20 02:25 showid

$ ./showid
ruid=1002 euid=0
```

`passwd` 가 이 방식으로 돈다. 일반 사용자는 `/etc/shadow` 를 읽지도 못하지만 자기 비밀번호는 바꿀 수 있어야 하므로, root 소유의 setuid 프로그램을 하나 두고 그 안에서만 필요한 만큼 손대게 한다.

```bash
$ ls -l /usr/bin/passwd /usr/bin/sudo /usr/bin/mount
-rwsr-xr-x 1 root root  64152 May 30  2024 /usr/bin/passwd
-rwsr-xr-x 1 root root 277936 Mar  2 12:56 /usr/bin/sudo
-rwsr-xr-x 1 root root  51584 Mar  6 16:00 /usr/bin/mount
```

setuid 는 권한 상승을 정식으로 열어 주는 장치라서 위험도 그만큼 크다. 이 프로그램에 버그가 있으면 그 버그는 곧바로 root 권한이 된다. 그래서 두 가지를 지킨다. 내가 만든 프로그램에 함부로 걸지 않는 것이 하나고, 시스템에 걸린 것이 늘지 않았는지 가끔 훑어보는 것이 다른 하나다.

```bash
# find / -xdev -perm -4000 -type f
/usr/lib/polkit-1/polkit-agent-helper-1
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/bin/gpasswd
/usr/bin/sudo
/usr/bin/newgrp
/usr/bin/chfn
/usr/bin/umount
/usr/bin/mount
/usr/bin/passwd
/usr/bin/chsh
/usr/bin/su
```

이 환경에서는 열한 개다. 목록이 늘어나 있다면 무엇이 언제 왜 들어왔는지 짚어 볼 일이다.

**셸 스크립트에는 걸어도 소용이 없다.** `#!` 로 시작하는 파일에 setuid 를 붙이면 비트는 남지만 리눅스 커널이 무시한다.

```bash
$ ls -l suid.sh
-rwsr-xr-x 1 root root 71 Aug 20 02:47 suid.sh

$ ./suid.sh
실효 uid = 1002
실제 uid = 1002
```

앞의 C 프로그램에서는 실효 uid 가 0으로 바뀌었는데 같은 비트를 건 스크립트에서는 둘 다 alice 의 uid 그대로다.

커널이 인터프리터를 띄우고 그 인터프리터가 스크립트 파일을 다시 여는 사이에 파일을 바꿔치기할 수 있기 때문이다. 그 틈을 막을 방법이 마땅치 않아 아예 무시하는 쪽을 택했다. 스크립트에 권한이 필요하면 sudo 규칙을 쓰거나 setuid 를 건 작은 C 래퍼를 따로 둔다.

요즘은 setuid 대신 file capability 를 쓰는 쪽이 낫다. root 권한을 통째로 주는 대신 그 프로그램에 필요한 능력 하나만 준다. 원시 소켓을 열어야 하는 프로그램이라면 예전에는 setuid root 로 만들었지만 지금은 `cap_net_raw` 만 붙이면 된다.

```bash
setcap cap_net_raw+ep ./myping
getcap ./myping
```

`getcap -r /usr/bin` 으로 어떤 프로그램에 무엇이 붙어 있는지 훑어볼 수 있다. setuid 목록과 함께 이쪽도 같이 보는 편이 낫다.

### setgid 2000

실행 파일에 걸면 setuid 와 같은 일을 그룹에 대해 한다. 그런데 실무에서 훨씬 자주 쓰이는 것은 디렉터리에 걸었을 때다. 그 디렉터리 안에 새로 만들어지는 것은 만든 사람의 기본 그룹이 아니라 **디렉터리의 그룹을 물려받는다.**

```bash
$ ls -ld proj
drwxrwsr-x 2 root shared 4096 Aug 20 02:25 proj

$ (cd proj && umask 002 && touch f1 && mkdir sub1)
$ stat -c '%a %U %G %n' proj/f1 proj/sub1
664 alice shared f1
2775 alice shared sub1
```

`f1` 의 그룹이 alice 가 아니라 shared 로 붙었다. 그리고 새로 만들어진 디렉터리 `sub1` 은 그룹뿐 아니라 setgid 비트까지 물려받아 2775 가 되었다. 그래서 한 번만 걸어 두면 그 아래 어디에 무엇을 만들어도 그룹이 유지된다.

setgid 를 걸지 않은 같은 구성에서는 이렇게 나온다.

```bash
$ stat -c '%a %U %G %n' noproj/f1 noproj/sub1
664 alice alice f1
775 alice alice sub1
```

여럿이 함께 쓰는 디렉터리는 그래서 세 가지를 같이 건다. 디렉터리 그룹을 팀 그룹으로 바꾸고, setgid 를 걸고, umask 를 002 로 두어 그룹 쓰기가 살아남게 한다.

```bash
chgrp -R team /srv/project
chmod -R g+rwX /srv/project
find /srv/project -type d -exec chmod g+s {} +
```

### sticky 1000

디렉터리에 걸면 **그 안의 항목을 지우거나 이름을 바꾸는 일을 그 항목의 소유자, 디렉터리의 소유자, root 로 제한한다.** 4절에서 본 문제, 곧 누구나 쓸 수 있는 디렉터리에서 남의 파일이 지워지는 문제를 이 비트가 막는다.

```bash
$ ls -ld shr && ls -l shr/alicefile
drwxrwxrwt 2 root  root  4096 Aug 20 02:25 shr
-rw-rw-rw- 1 alice alice    2 Aug 20 02:25 shr/alicefile

$ rm -f shr/alicefile              # bob 이 지우려 한다
rm: cannot remove 'shr/alicefile': Operation not permitted
```

같은 디렉터리에서 sticky 만 떼면 바로 지워진다. `/tmp` 가 `1777` 인 이유가 이것이다.

```bash
$ ls -ld /tmp
drwxrwxrwt 8 root root 4096 Aug 20 02:25 /tmp
```

보통 파일에 걸리는 sticky 는 리눅스에서 아무 일도 하지 않는다. 옛 유닉스에서 실행 이미지를 스왑에 남겨 두라는 뜻으로 쓰던 흔적이다.

### 커널이 특수 비트를 지워 버리는 자리

setuid 와 setgid 는 소유 관계가 흔들리면 커널이 알아서 떨어뜨린다. 소유자를 바꾸거나, 권한 없는 사용자가 그 파일에 쓰면 사라진다.

```bash
# stat -c '%a %A' g4
6755 -rwsr-sr-x

# chown alice g4 && stat -c '%a %A' g4
755 -rwxr-xr-x
```

setuid 프로그램의 내용이나 소유자가 바뀌었는데 비트가 그대로 남으면 그것이 곧바로 권한 상승에 쓰이기 때문이다. 이 규칙은 보통 파일에만 걸린다. 디렉터리는 `chown` 을 해도 setgid 가 그대로 남으므로, 공유 디렉터리에 `chgrp -R` 을 돌려도 설정이 깨지지 않는다. **setuid 파일을 배포할 때는 `chown` 을 먼저 하고 `chmod` 를 나중에 한다.** 순서를 뒤집으면 방금 건 비트가 조용히 사라진다.

* * *

## 8. 재귀 적용과 자주 어긋나는 자리

### `chmod -R 777` 을 쓰지 않는다

권한 문제를 만나면 가장 빨리 넘어가는 방법이 777 이고, 그래서 가장 자주 저지르는 실수이기도 하다. 문제가 사라지는 것이 아니라 아무나 고칠 수 있는 상태로 덮이는 것이다. 게다가 재귀로 걸면 디렉터리에 필요한 `x` 를 주려다가 데이터 파일까지 전부 실행 파일이 된다.

디렉터리에는 `x` 가 필요하고 대부분의 파일에는 필요 없다는 것이 문제의 핵심이다. 두 가지 해법이 있다.

**대문자 `X` 를 쓴다.** 소문자 `x` 와 달리 **대상이 디렉터리이거나, 이미 어느 자리에든 실행 비트가 하나라도 켜져 있을 때만** 실행을 붙인다.

```bash
$ find tr2 -printf '%m %y %p\n'      # 걸기 전
700 d tr2
600 f tr2/note.txt
700 f tr2/run.sh
700 d tr2/sub
600 f tr2/sub/data.bin

$ chmod -R go+rX tr2

$ find tr2 -printf '%m %y %p\n'      # 걸고 나서
755 d tr2
644 f tr2/note.txt
755 f tr2/run.sh
755 d tr2/sub
644 f tr2/sub/data.bin
```

디렉터리와 원래 실행 파일이던 `run.sh` 만 `x` 를 받았고 `note.txt` 와 `data.bin` 은 644 로 남았다. 같은 자리에 `a+x` 를 걸었다면 다섯 개가 전부 755 가 된다.

**아니면 `find` 로 종류를 갈라 건다.** 값을 정확히 못 박아야 할 때는 이쪽이 확실하다.

```bash
find /srv/site -type d -exec chmod 755 {} +
find /srv/site -type f -exec chmod 644 {} +
```

`-exec ... +` 는 인자를 모아 chmod 를 몇 번만 부르고, `-exec ... \;` 는 파일마다 한 번씩 부른다. 파일이 많으면 차이가 크므로 `+` 를 쓴다.

### 8진수 세 자리는 디렉터리의 setuid·setgid 를 지우지 못한다

여기서 한 번씩 걸린다. GNU chmod 는 디렉터리에 8진수 모드를 걸 때 setuid 와 setgid 를 일부러 남긴다. `chmod 755` 로도, 앞에 0을 붙인 `chmod 0755` 로도 안 지워진다.

```bash
$ stat -c %a D
6755
$ chmod 755 D  && stat -c %a D
6755
$ chmod 0755 D && stat -c %a D
6755
$ chmod 00755 D && stat -c %a D
755
```

앞자리 0을 하나 더 붙여 `00755` 라고 적어야 지워진다. 자릿수가 다섯 이상이면 보존을 하지 않는다는 규칙이다. 보통 파일에서는 이런 예외가 없어서 `chmod 755` 한 번에 전부 떨어진다. **디렉터리에서 특수 비트를 확실히 떼려면 8진수를 세지 말고 `chmod g-s` 처럼 기호로 적는다.** 공유 디렉터리에 setgid 를 걸어 두었다면 나중에 누가 `chmod -R 755` 를 돌려도 그 비트만은 살아남는다. 다만 그룹 쓰기가 함께 날아가 2775 가 2755 로 바뀌므로 공유 설정 자체는 어차피 깨진다.

### 심볼릭 링크에는 걸리지 않는다

리눅스에서 심볼릭 링크 자체의 권한 비트는 아무 뜻이 없고 늘 777 로 보인다. `chmod` 에 링크를 넘기면 링크가 가리키는 대상의 권한이 바뀐다.

```bash
$ ln -s tgt lnk && chmod 777 lnk
$ stat -c %a tgt
777
```

재귀로 돌 때는 반대다. `chmod -R` 은 내려가다 만난 심볼릭 링크를 건너뛴다. 링크를 타고 트리 밖으로 나가서 엉뚱한 파일의 권한을 바꾸는 사고를 막기 위해서다.

### 실행 권한을 날려 먹었을 때

`chmod` 자신이나 셸이 쓰는 도구에서 실행 비트를 지우면 그것을 되돌릴 도구까지 같이 못 쓰게 된다. 동적 링커를 직접 불러서 빠져나올 수 있다. 링커는 프로그램을 읽어서 메모리에 올릴 뿐이라 대상 파일의 실행 비트를 요구하지 않는다.

```bash
$ ./mychmod 755 mychmod
bash: ./mychmod: Permission denied

$ /lib64/ld-linux-x86-64.so.2 ./mychmod 755 mychmod
$ stat -c %a mychmod
755
```

읽기 권한은 있어야 한다. 링커 경로는 `ldd /bin/chmod` 로 확인한다. busybox 가 깔려 있다면 `busybox chmod` 를 써도 되고, 컨테이너라면 다시 만드는 편이 빠르다.

> `chmod 000 /` 나 `chmod -R 000 /usr` 처럼 시스템 전체에 재귀로 거는 명령은 복구가 아주 어렵다. GNU chmod 의 `--preserve-root` 는 `/` 자체에 재귀로 도는 것만 막아 줄 뿐 `/usr` 아래는 막아 주지 않는다.
{: .prompt-warning }

### chmod 로 표현되지 않는 것

권한을 셋으로 나눈 이 구조로는 "alice 와 bob 에게만 쓰기를 준다" 같은 요구를 적을 수 없다. 그룹을 새로 하나 파거나, POSIX ACL 을 쓴다.

ACL 을 걸면 `ls -l` 끝에 `+` 가 붙고, 그때부터 그룹 자리에 보이는 값은 그룹의 권한이 아니라 ACL 항목 전체의 상한을 정하는 마스크다.

```bash
$ setfacl -m u:alice:rw aclf && ls -l aclf
-rw-rw-r--+ 1 root root 0 ... aclf

$ getfacl aclf | grep -E 'group::|mask'
group::r--
mask::rw-

$ chmod g-w aclf && getfacl aclf | grep -E 'alice|mask'
user:alice:rw-      #effective:r--
mask::r--
```

`ls -l` 의 그룹 자리가 `rw-` 인데 실제 그룹 권한은 `r--` 이다. 여기에 `chmod g-w` 를 걸면 마스크가 내려가면서 이름을 지정해 준 alice 의 쓰기까지 함께 깎인다. 두 가지를 섞어 쓸 때 `ls -l` 만 보면 안 되는 이유다.

SELinux 나 AppArmor 가 켜진 시스템에서는 권한 비트를 통과한 뒤에 정책 검사가 한 번 더 있다는 것도 알아 둘 자리다.

* * *

## 9. 정리

| 질문 | 답 |
| :--- | :--- |
| chmod 가 바꾸는 것은 무엇인가 | 아이노드 모드 필드의 아래 열두 비트다. 파일 종류와 소유자·그룹은 건드리지 않는다 |
| 왜 내 파일인데 못 읽는가 | 커널이 소유자·그룹·그 밖 순서로 내려가다 처음 걸리는 한 벌만 보고 끝내기 때문이다 |
| root 는 다 되는가 | 읽고 쓰는 것은 다 된다. 실행 비트가 어디에도 없는 파일만은 실행하지 못한다 |
| 디렉터리의 x 는 무엇인가 | 실행이 아니라 통행이다. 경로 중간의 모든 디렉터리에 필요하다 |
| 파일을 지우려면 무엇이 필요한가 | 그 파일의 w 가 아니라 담긴 디렉터리의 w 다 |
| 남이 못 지우게 하려면 | 디렉터리에 sticky 를 건다. `/tmp` 가 1777 인 이유다 |
| 왜 새 파일은 644 인가 | 프로그램이 0666 을 요구하고 umask 022 가 그룹과 그 밖의 w 를 걷어 낸다 |
| umask 를 뺄셈으로 봐도 되는가 | 대개 맞지만 틀릴 때가 있다. 실제 연산은 `요구값 AND NOT umask` 다 |
| 스크립트에 setuid 를 걸면 | 아무 일도 없다. 리눅스 커널이 무시한다. sudo 규칙이나 C 래퍼를 쓴다 |
| 공유 디렉터리는 어떻게 잡는가 | 그룹을 맞추고 디렉터리에 setgid 를 걸고 umask 를 002 로 둔다 |
| setuid 파일을 배포할 때 순서는 | `chown` 을 먼저, `chmod` 를 나중에. 반대로 하면 커널이 비트를 지운다 |
| 재귀로 걸 때는 | `777` 대신 대문자 `X` 를 쓰거나 `find` 로 디렉터리와 파일을 갈라 건다 |
| 디렉터리 setgid 를 8진수로 떼려면 | `755` 나 `0755` 로는 안 떨어진다. `00755` 또는 `g-s` 를 쓴다 |

* * *

## 참고 자료

- W. R. Stevens, S. A. Rago, *Advanced Programming in the UNIX Environment*, Addison-Wesley — `st_mode` 필드 구조, 접근 판정 순서, `umask` 와 파일 생성 시 모드 결정
- M. Kerrisk, *The Linux Programming Interface*, No Starch Press — setuid·setgid 의 커널 처리, 스크립트에서 무시되는 이유, 디렉터리의 sticky 비트, capabilities
- GNU Coreutils Manual, *chmod invocation* — 기호 표기 문법, 대문자 `X`, 디렉터리에서 setuid·setgid 가 8진수 모드에 보존되는 규칙
- Linux `man 2 open`, `man 2 path_resolution`, `man 7 capabilities` — 생성 모드와 umask 의 관계, 경로 해석에 필요한 실행 권한, `CAP_DAC_OVERRIDE` 의 실행 예외
- The Open Group, *POSIX.1-2017 chmod* — `who` 를 생략한 기호 표기에 umask 가 적용되는 규정
