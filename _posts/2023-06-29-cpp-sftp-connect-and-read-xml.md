---
title: "(c++) sftp Connect & read xml"
description: "c, c++, vs, sftp, ftp, CkSFtp, xml, pugi, pugixml"
date: 2023-06-29 10:00:00 +0900
categories: [Dev, C++]
tags: [c, c++, vs, sftp, ftp, CkSFtp, xml, pugi, pugixml]
---

# sftp xml , 
- 최초 작성일: 2023년 6월 29일 (목)

## (CksFtp )

### 

- sftp 접속: CksFtp
- xml 접속: pugixml

<br/>

CksFtp 라이브러리는 상용(유료) 소프트웨어로 제공된다. 한 달 사용 후에는 해당 라이브러리를 계속 이용하려면 유료 라이선스를 구매해야 한다. 이 점을 참고하시기 바란다.

필자도 제대로 확인 안 하고 사용했다가 갑자기 작동이 안되어서 당황했다. 

그래서, 아래에 무료인 libssh  라이브러리를 사용한 버전을 구현했다.

<br/>

```c++
bool CExampleDlg::connectToServer(CkSFtp& sftp, const char* hostname, int port) {
	if (sftp.Connect(hostname, port) != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	if (sftp.AuthenticatePw("root", "fa") != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	if (sftp.InitializeSftp() != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	return true;
}

bool CExampleDlg::downloadRemoteFile(CkSFtp& sftp, const char* remoteFilePath, const char* localFilePath) {
	const char* handle = sftp.openFile(remoteFilePath, "readOnly", "openExisting");
	if (sftp.get_LastMethodSuccess() != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	if (sftp.DownloadFile(handle, localFilePath) != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	if (sftp.CloseHandle(handle) != true) {
		std::cerr << sftp.lastErrorText() << "\n";
		return false;
	}

	return true;
}

pugi::xml_document CExampleDlg::loadAndParseXml(const char* xmlFilePath) {
	pugi::xml_document doc;
	pugi::xml_parse_result result = doc.load_file(xmlFilePath);
	if (!result) {
		std::cerr << "Parsing failed with description: " << result.description() << "\n";
		return {};
	}

	return doc;
}

std::string CExampleDlg::findAndValidateNode(pugi::xml_document& doc, const char* nodeName) {
	pugi::xml_node node = doc.child("Root").child(nodeName);

	if (!node) {
		std::cerr << nodeName << " node not found." << std::endl;
		return "";
	}

	std::string nodeValue = node.text().get();

	try {
		if (std::stoi(nodeValue) >= 100 || std::stoi(nodeValue) <= -100) {
			std::cerr << "Invalid value for " << nodeName << ": " << nodeValue << std::endl;
			return "";
		}
	}
	catch (std::exception& e) {
		std::cerr << "Exception caught trying to convert " << nodeName << " to integer: " << e.what() << std::endl;
		return "";
	}

	return nodeValue;
}

std::pair<std::string, std::string> CExampleDlg::connectSftp() {
	CkSFtp sftp;

	if (!connectToServer(sftp, "192.168.8.1", 22)) {
		return { "", "" };
	}

	if (!downloadRemoteFile(sftp, "/home/pi/test/test.xml", "./xml/test.xml")) {
		return { "", "" };
	}

	pugi::xml_document doc = loadAndParseXml("./xml/test.xml");
	if (!doc) {
		return { "", "" };
	}

	std::string setPhaseCalW = findAndValidateNode(doc, "SetPhaseCalW");
	std::string setPhaseCalH = findAndValidateNode(doc, "SetPhaseCalH");

	if (setPhaseCalW.empty() || setPhaseCalH.empty()) {
		return { "", "" };
	}

	std::cout << "setPhaseCalW: " << setPhaseCalW << std::endl;
	std::cout << "setPhaseCalH: " << setPhaseCalH << std::endl;

	return { setPhaseCalW, setPhaseCalH };
}
```

<br/>

<br/>

## 2 (libssh2 )

```c++
bool CExampleDlg::connectToServer(LIBSSH2_SESSION*& session, const char* hostname, int port, const char* username, const char* password) {
	SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
	sockaddr_in sin;
	sin.sin_family = AF_INET;
	sin.sin_port = htons(port);

	// Use inet_pton instead of inet_addr
	if (inet_pton(AF_INET, hostname, &sin.sin_addr) <= 0) {
		std::cerr << "Invalid address format\n";
		return false;
	}

	if (connect(sock, (struct sockaddr*)(&sin), sizeof(struct sockaddr_in)) != 0) {
		std::cerr << "Failed to connect to " << hostname << "\n";
		return false;
	}

	session = libssh2_session_init();
	if (libssh2_session_handshake(session, sock)) {
		std::cerr << "Failed to establish SSH session\n";
		return false;
	}

	if (libssh2_userauth_password(session, username, password)) {
		std::cerr << "Authentication failed\n";
		return false;
	}

	return true;
}

bool CExampleDlg::downloadRemoteFile(LIBSSH2_SESSION*& session, const char* remoteFilePath, const char* localFilePath)
{
	LIBSSH2_SFTP* sftp_session = libssh2_sftp_init(session);
	if (!sftp_session) {
		std::cerr << "Failed to initialize SFTP session\n";
		return false;
	}
	unsigned int filename_len = static_cast<unsigned int>(strlen(remoteFilePath));
	LIBSSH2_SFTP_HANDLE* sftp_handle = libssh2_sftp_open_ex(sftp_session, remoteFilePath, filename_len, LIBSSH2_FXF_READ, 0, LIBSSH2_SFTP_OPENFILE);

	if (!sftp_handle) {
		std::cerr << "Failed to open file with SFTP\n";
		libssh2_sftp_shutdown(sftp_session);
		return false;
	}

	FILE* localFile;
	errno_t err = fopen_s(&localFile, localFilePath, "wb");
	if (err != 0 || !localFile) {
		std::cerr << "Failed to open local file\n";
		libssh2_sftp_close(sftp_handle);
		libssh2_sftp_shutdown(sftp_session);
		return false;
	}

	char buffer[1024];
	while (true) {
		ssize_t amount = libssh2_sftp_read(sftp_handle, buffer, static_cast<unsigned int>(sizeof(buffer))); // explicit cast to unsigned int
		if (amount > 0) {
			size_t result = fwrite(buffer, 1, static_cast<size_t>(amount), localFile);
			if (result != static_cast<size_t>(amount)) {
				std::cerr << "Failed to write to local file\n";
				fclose(localFile);
				libssh2_sftp_close(sftp_handle);
				libssh2_sftp_shutdown(sftp_session);
				return false;
			}
		}
		else if (amount == 0) {
			break; // EOF reached
		}
		else {
			std::cerr << "Failed to read from remote file\n";
			fclose(localFile);
			libssh2_sftp_close(sftp_handle);
			libssh2_sftp_shutdown(sftp_session);
			return false;
		}
	}

	fclose(localFile);
	libssh2_sftp_close(sftp_handle);
	libssh2_sftp_shutdown(sftp_session);

	return true;
}

pugi::xml_document CExampleDlg::loadAndParseXml(const char* xmlFilePath) {
	pugi::xml_document doc;
	pugi::xml_parse_result result = doc.load_file(xmlFilePath);
	if (!result) {
		std::cerr << "Parsing failed with description: " << result.description() << "\n";
		return {};
	}

	return doc;
}

std::string CExampleDlg::findAndValidateNode(pugi::xml_document& doc, const char* nodeName) {
	pugi::xml_node node = doc.child("Root").child(nodeName);

	if (!node) {
		std::cerr << nodeName << " node not found." << std::endl;
		return "";
	}

	std::string nodeValue = node.text().get();

	try {
		if (std::stoi(nodeValue) >= 100 || std::stoi(nodeValue) <= -100) {
			std::cerr << "Invalid value for " << nodeName << ": " << nodeValue << std::endl;
			return "";
		}
	}
	catch (std::exception& e) {
		std::cerr << "Exception caught trying to convert " << nodeName << " to integer: " << e.what() << std::endl;
		return "";
	}

	return nodeValue;
}

std::pair<std::string, std::string> CExampleDlg::connectSftp() {
	LIBSSH2_SESSION* session;

	if (!connectToServer(session, "192.168.8.1", 22, "root", "fa")) {
		return { "", "" };
	}

	if (!downloadRemoteFile(session, "/home/pi/test/test.xml", "./xml/test.xml")) {
		libssh2_session_disconnect(session, "Finished session");
		libssh2_session_free(session);
		return { "", "" };
	}

	pugi::xml_document doc = loadAndParseXml("./xml/test.xml");
	if (!doc) {
		libssh2_session_disconnect(session, "Finished session");
		libssh2_session_free(session);
		return { "", "" };
	}

	std::string setPhaseCalW = findAndValidateNode(doc, "SetPhaseCalW");
	std::string setPhaseCalH = findAndValidateNode(doc, "SetPhaseCalH");

	if (setPhaseCalW.empty() || setPhaseCalH.empty()) {
		libssh2_session_disconnect(session, "Finished session");
		libssh2_session_free(session);
		return { "", "" };
	}

	std::cout << "setPhaseCalW: " << setPhaseCalW << std::endl;
	std::cout << "setPhaseCalH: " << setPhaseCalH << std::endl;

	libssh2_session_disconnect(session, "Finished session");
	libssh2_session_free(session);

	return { setPhaseCalW, setPhaseCalH };
}
```
