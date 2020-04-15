"""
web server

提供一个服务端使用类,通过这个类可以快速的搭建一个web server服务,用以展示自己的简单网页
"""
from socket import *
from select import *
import re


class HTTPServer:
    def __init__(self, host='0.0.0.0', port=80, html=None):
        self.host = host
        self.port = port
        self.html = html
        self.create_socket()
        self.bind()
        self.dict_fd = {self.sockfd.fileno(): self.sockfd}
        self.ep = epoll()

    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setblocking(False)

    def bind(self):
        self.address = (self.host, self.port)
        self.sockfd.bind(self.address)

    def start(self):
        self.sockfd.listen(3)
        print("Listen the port %s" % self.port)
        self.ep.register(self.sockfd, EPOLLIN)
        while True:
            # 对IO进行监控
            events = self.ep.poll()
            # 遍历列表分情况讨论
            for fd, event in events:
                if fd == self.sockfd.fileno():
                    # 监听套接字就绪
                    connect, addr = self.dict_fd[fd].accept()
                    print("Connect from", addr)
                    # 添加客户端链接套接字作为监控对象
                    connect.setblocking(False)
                    self.ep.register(connect, EPOLLIN | EPOLLET)
                    self.dict_fd[connect.fileno()] = connect
                else:
                    # 客户端链接套接字就绪
                    self.handle(self.dict_fd[fd])

    # 对每一个客户端请求的具体处理
    def handle(self, connect):
        request = connect.recv(1024).decode()
        # print(request)
        pattern = r"[A-Z]+\s+(/\S*)"
        try:
            info = re.match(pattern, request).group(1)
            # print("info-->",info)
        except:
            del self.dict_fd[connect.fileno()]
            connect.close()
            return
        else:
            self.get_http(connect,info)

    def get_http(self,connect,info):
        if info == "/":
            filename = self.html + "/index.html"
        else:
            filename = self.html + info
        try:
            file = open(filename,"rb")
        except:
            response_heads = "HTTP/1.1 404 NO\r\n"
            response_heads += "Content-type: text-html\r\n"
            response_heads += "\r\n"
            response_content = "Not Found"
            response = response_heads.encode() + response_content.encode()
        else:
            response_heads = "HTTP/1.1 200 YES\r\n"
            response_heads += "Content-type: text-html\r\n"
            response_heads += "\r\n"
            response_content= file.read()
            response = response_heads.encode() + response_content
            file.close()
        finally:
            connect.send(response)


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 9696
    path = "./static"

    # 实例化对象[
    http = HTTPServer(host=host, port=port, html=path)

    # 调用方法启动服务
    http.start()
