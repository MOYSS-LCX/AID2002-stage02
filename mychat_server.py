"""
    聊天室 服务端
"""
from socket import *

# 服务器地址
HOST = "0.0.0.0"
PORT = 9696
ADDRESS = (HOST, PORT)

user = {}  # 用户信息存储  {name : address}
list_sensitive_word = ["xx", "aa", "bb", "oo"]  # 敏感词列表
list_warning = {}  # 监控敏感词字典{被警告的用户：警告次数}


# 处理进入聊天室
def do_login(s, name, address):
    if name in user:
        s.sendto("该用名已经存在".encode(), address)
        return
    else:
        s.sendto(b'OK', address)
        # 告知其他人
        msg = "欢迎 %s 进入聊天室" % name
        for i in user:
            s.sendto(msg.encode(), user[i])
        user[name] = address  # 用户字典中增加一项
        list_warning[name] = 0  # 监控敏感词字典增加一项
        print(user)


# 处理聊天
def do_chat(s, name, text):
    if text not in list_sensitive_word:
        msg = "N \n%s : %s" % (name, text)
        for i in user:
            # 除去本人
            if i != name:
                s.sendto(msg.encode(), user[i])
    else:
        list_warning[name] += 1
        if list_warning[name] < 3:
            msg = "N \n%s 您发布敏感词汇，警告%d次" % (name, list_warning[name])
            s.sendto(msg.encode(), user[name])
        else:
            msg = "NN \n 由于您发布敏感词次数较多,你已被踢出群聊"
            s.sendto(msg.encode(), user[name])
            del user[name]  # 删除用户
            msg = "N \n 由于%s发布敏感词次数过多，已被踢出群聊" % name
            for i in user:
                s.sendto(msg.encode(), user[i])


# 处理退出
def do_quit(s, name):
    del user[name]  # 删除用户
    msg = "\n%s 退出聊天室" % name
    for i in user:
        s.sendto(msg.encode(), user[i])


# 接收客户端请求
def request(s):
    print("服务器已启动")
    while True:
        try:
            data, address = s.recvfrom(1024)  # 接收请求
            tmp = data.decode().split(" ", 2)  # 对请求解析
            if tmp[0] == "L":
                do_login(s, tmp[1], address)
            elif tmp[0] == "C":
                do_chat(s, tmp[1], tmp[2])
            elif tmp[0] == "Q":
                do_quit(s, tmp[1])
        except KeyboardInterrupt:
            print("服务器异常退出！")


# 搭建基本结构
def main():
    # 创建一个udp套接字
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(ADDRESS)
    request(s)


if __name__ == '__main__':
    main()
