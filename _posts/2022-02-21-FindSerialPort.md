---
title: (MFC) 자동으로 시리얼 번호 스캔
description: 레지스트리 값으로 시리얼 번호 스캔
date: 2022-02-21 10:00:00 +0900
categories: [Dev, MFC]
tags: [c++, mfc, serialport, registry]
---

# [MFC] 레지스트리 값으로 시리얼 번호 자동으로 찾기

- 최초 작성일: 2022년 2월 21일 (월)

## 목적

컴퓨터에 USB를 통해 하드웨어 연결시 'COMXX' 식의 시리얼 번호를 확인할 수 있는데,

프로그램 실행시 이 포트 번호를 자동으로 찾아 설정해주는 기능을 구현하고자 한다.

![image](https://user-images.githubusercontent.com/68185569/154872501-83b591f9-97b0-448c-965f-cb270c728332.png)

<br/>

## 구현

시리얼 포트를 스캔하기 위해서는 레지스트리의

HKEY_LOCALMACHINE\HARDWARE\DEVICEMAP\SERIALCOMM 항목을 찾아보면 된다.

<br/>

```c++
int findComPortList(int *list)
{
	HKEY  hSerialCom;
	TCHAR buffer[_MAX_PATH];
	char data[_MAX_PATH];
	DWORD len, type, dataSize;
	long  i;
	char idata[3];

	int port_list_count = 0;

	if (::RegOpenKeyEx(HKEY_LOCAL_MACHINE, _T("HARDWARE\\DEVICEMAP\\SERIALCOMM"), 0, KEY_ALL_ACCESS, &hSerialCom) == ERROR_SUCCESS)
	{
		for (i = 0, len = dataSize = _MAX_PATH;
			::RegEnumValue(hSerialCom, i, buffer, &len, NULL, &type, (BYTE *)data, &dataSize) == ERROR_SUCCESS;
			i++, len = dataSize = _MAX_PATH)
		{
			RegQueryValueEx(hSerialCom, buffer, &len, NULL, (BYTE *)data, &dataSize);
			int tmp = _tcslen(buffer);
			if (tmp > 17)
			{
				buffer[17] = '\0';
				tmp++;
			}

			if (_tcscmp(buffer, _T("\\Device\\USBSER000")) == 0)
			{
				//int l_size = dataSize - 4;
				//int i;
				//for (i = 0; i < l_size; i++)
				//{					
				//	idata[i] = data[i + 3];
				//}
				//idata[i] = '\0';
				int cnt = 0;
				for (i = 0; i < dataSize; i++)
				{
					if (data[i] >= 0x30 && data[i] <= 0x39)
					{
						idata[cnt] = data[i];
						cnt++;
					}
				}
				if(cnt == 2)
					idata[cnt] = '\0';
				else if (cnt == 1)
				{
					idata[cnt] = '\0';
					idata[cnt+1] = '\0';
				}

				list[port_list_count] = atoi(idata);

				port_list_count++;
			}
		}::RegCloseKey(hSerialCom);
	}
	return port_list_count;
}

char * byIndexComPort(int xPort)
{
	static char PortName[30] = { 0, };
	TCHAR PortName2[30];

//	sprintf_s(PortName, 30, "\\\\.\\COM%d", xPort);
	wsprintf(PortName2, TEXT("\\\\.\\COM%d"), xPort);
	
//	MultiByteToWideChar(CP_ACP, MB_PRECOMPOSED, PortName, strlen(PortName), PortName2, 60);

	return PortName;
}

BOOL open_comport()
{
	int portList[10];
	int candidateSize = 0;

	candidateSize = findComPortList(portList);

	if (candidateSize == 0)
	{
		m_portfound = FALSE;
		m_Comportnum = 10;
	}
	else if (candidateSize == 1)
	{
		m_portfound = TRUE;
		m_Comportnum = portList[0];
	}
	else
	{
		m_portfound = TRUE;
		m_Comportnum = 10;
	}
	//serial.iBaudRate = 1; //9600
	//serial.iDataBit = 3; //8
	//serial.iStopBit = 1;//ONE5STOPBITS
	//serial.iParity = 0; //NOPARITY

	if (m_pCom1)
	{
		m_Connected = FALSE;

		delete m_pCom1;
		m_pCom1 = NULL;
	}

	TCHAR PortName2[30];
	wsprintf(PortName2, _T("\\\\.\\COM%d"), m_Comportnum);
	m_pCom1 = new CSerialPort(PortName2);
	if (m_pCom1 == NULL)
		return FALSE;
	else
	{
		m_pCom1->SetBaudRate(CBR_9600);//테스트용
		m_pCom1->SetBufferSizes(4096, 4096);
		m_pCom1->SetParityDataStop(NOPARITY, EIGHTDATABITS, ONE5STOPBITS);
		m_pCom1->SetFlowControl(PCF_XONXOFF);
		m_pCom1->SetBufferSizes(SP_INBUFSIZE, SP_OUTBUFSIZE);
		m_pCom1->SetReadTimeouts(MAXDWORD, 0, 0);
		m_pCom1->SetWriteTimeouts(0, SP_WRITETIMEOUT);
		m_pCom1->StartCommThread(Com1Reader, 0);

		m_Connected = TRUE;
		m_realtimestart = FALSE;
		return m_pCom1->IsValid();
	}		
}

void close_comport()
{
	Sleep(100);
	if (m_pCom1)
	{
		if (m_pCom1->IsValid())
		{
			m_pCom1->PurgeComm(PURGE_RXCLEAR);
			m_pCom1->StopCommThread();
		}
		delete m_pCom1;
		m_pCom1 = NULL;

		m_Connected = FALSE;
	}
}
```

<br/>
