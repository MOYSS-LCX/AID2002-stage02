"""
    聊天室 客户端
"""
from socket import *
from multiprocessing import Process, Queue
import sys

# 服务器地址
ADDRESS = ("127.0.0.1", 9696)

q = Queue(1)


# 接收消息
def recv_msg(s):
    while True:
        data, addr = s.recvfrom(1024)
        tmp = data.decode().split(" ", 1)
        if tmp[0] == "NN":
            print(tmp[1])
            q.put(tmp[0],False)
            break
        else:
            print(tmp[1] + "\n >>", end="")


# 发送消息
def send_msg(s, name):
    while True:
        if q.full():
            sys.exit()
        else:
            text = input(">>")
            if text == "quit":
                msg = "Q %s %s" % (name, text)
                s.sendto(msg.encode(), ADDRESS)
                sys.exit("退出聊天室")  # 进程结束
            msg = "C %s %s" % (name, text)
            s.sendto(msg.encode(), ADDRESS)


# 网络结构
def main():
    # 创建一个udp套接字
    s = socket(AF_INET, SOCK_DGRAM)
    # 进入聊天室
    while True:
        name = input("请输入姓名>>")
        msg = "L " + name  # 根据协议，重新组织发送信息
        s.sendto(msg.encode(), ADDRESS)
        data, address = s.recvfrom(120)  # 接收服务端反馈
        if data.decode() == "OK":
            print("您已进入聊天室")
            break
        else:
            print(data.decode())

    # 创建一个新的进程
    p = Process(target=recv_msg, args=(s,))  # 子进程接收消息
    p.daemon = True  # 子进程随父进程退出
    p.start()
    # 发送消息
    send_msg(s, name)  # 发送消息由父进程执行


if __name__ == '__main__':
    main()
