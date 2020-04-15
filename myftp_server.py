"""
    ftp 文件服务系统
    服务端
"""
from socket import *
from multiprocessing import Process
from signal import *
from time import sleep
import sys, os

# 全局变量
HOST = "0.0.0.0"
PORT = 9699
ADDRESS = (HOST, PORT)
PATH = "/home/tarena/LCX/FTP/"
list_file = os.listdir(PATH)


# 应对客户端请求
class FTPServer(Process):
    def __init__(self, connect):
        super().__init__()
        self.connect = connect

    def do_check(self):
        """
        查看文件库
        """
        if not list_file:
            self.connect.send(b"NO")
            return
        else:
            self.connect.send(b"YES")
            sleep(0.1)
            data = "\n".join(list_file)
            self.connect.send(data.encode())

    def do_uploading(self, name):
        """
        从客户端接收上传文件
        """
        if name in list_file:
            self.connect.send(b"NO")
        else:
            self.connect.send(b"YES")
            upload_file = open(PATH + name, "wb")
            while True:
                data = self.connect.recv(1024)
                if data.decode() == "##":
                    print("接收到", name)
                    break
                upload_file.write(data)
            upload_file.close()

    def do_download(self, name):
        """
        客户端下载文件
        """
        try:
            file = open(PATH + name, "rb")
        except:
            self.connect.send(b"NO")
            return
        else:
            self.connect.send(b"YES")
            sleep(0.1)
            while True:
                download_file = file.read(1024)
                if not download_file:
                    sleep(0.1)
                    self.connect.send(b"##")
                    break
                self.connect.send(download_file)
            file.close()

    def run(self):
        while True:
            data = self.connect.recv(1024).decode()

            if not data or data == "4":
                return
            elif data == "1":
                self.do_check()
            elif data[0] == "2":
                filename = data.split(" ")[-1]
                # print(filename)
                self.do_uploading(filename)
            elif data[0] == "3":
                filename = data.split(" ")[-1]
                self.do_download(filename)


def main():
    # 创建套字
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(ADDRESS)
    sock.listen(3)

    # 处理僵尸进程
    signal(SIGCHLD, SIG_IGN)

    print("Listen the port %d" % PORT)
    # 循环链接客户端
    while True:
        try:
            connect, address = sock.accept()
            print("客户端地址：", address)
        except:
            sys.exit("服务退出!")

        # 创建子进程,处理客户端请求  handle --> 具体处理请求函数
        p = FTPServer(connect)
        p.daemon = True  # 主服务退出,其他服务也随之退出
        p.start()


if __name__ == '__main__':
    main()
