"""
    ftp 文件服务系统
    客户端
C/S模式  客户端 --> 发消息

客户端与服务端交互的三个阶段:
    1.客户端发送请求，
    2.服务端反馈请求是否可以完成(YES or NO)，
    3.完成请求
"""
from socket import *
import sys, time

# 全局变量
ADDRESS = ("127.0.0.1", 9699)


class FTPServer:
    """
    FTP客户端功能类
    """

    def __init__(self, sockfd):
        self.s = sockfd

    def do_check(self):
        """
        查看功能
        """
        self.s.send("1".encode())
        data = self.s.recv(1024)
        if data.decode() == "NO":
            print("文件库为空")
        elif data.decode() == "YES":
            data = self.s.recv(4096)
            print(data.decode())

    def do_uploading(self):
        """
        上传功能
        """
        filename = input("请输入您想上传的文件：")
        try:
            file = open(filename, "rb")
        except:
            print("文件不存在!")
            return

        filename = filename.split("/")[-1]  # 以 / 切割获取文件名称
        msg = "2 %s" % filename
        self.s.send(msg.encode())
        data = self.s.recv(128).decode()
        if data == "YES":
            while True:
                upload_file = file.read(1024)
                if not upload_file:
                    time.sleep(0.1)
                    self.s.send("##".encode())
                    print("上传完毕")
                    file.close()
                    break
        else:
            print("该文件已存在")

    def do_download(self):
        """
        下载功能
        """
        filename = input("请输入您要下载的文件：")
        msg = "3 %s" % filename
        self.s.send(msg.encode())
        data = self.s.recv(128).decode()  # 接收服务端的反馈信息
        if data == "YES":
            file = open(filename, "wb")
            while True:
                data = self.s.recv(1024)
                if data == b"##":
                    break
                file.write(data)
            print("下载完成!")
            file.close()
        else:
            print("没有该文件！")

    def do_exit(self):
        """
        退出功能
        """
        self.s.send("4".encode())
        self.s.close()
        sys.exit("客户端退出!!!")  # 退出进程


def main():
    sockfd = socket()
    sockfd.connect(ADDRESS)

    ftp = FTPServer(sockfd)

    while True:
        print("输入: 1 ---> 查看")
        print("输入: 2 ---> 上传")
        print("输入: 3 ---> 下载")
        print("输入: 4 ---> 退出")

        try:
            select = input(">>")
            if select == "1":
                ftp.do_check()
            elif select == "2":
                ftp.do_uploading()
            elif select == "3":
                ftp.do_download()
            elif select == "4":
                ftp.do_exit()
            else:
                print("请输入正确选项")
        except KeyboardInterrupt:
            print("异常退出!")
            break


if __name__ == '__main__':
    main()
