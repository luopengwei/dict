# -*- coding: UTF-8 -*-
#我的dict_client.py

from socket import * 
import sys 
import getpass
import pymysql
import time

#创建网络连接
def main():

    if len(sys.argv) < 3:
        print("argv is error")
        return 
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    s = socket()
    try:
        s.connect((HOST,PORT))
    except Exception as e:
        print(e)
        return

    while True:
        print('''
            =============英英词典============

             -- 1.注册   2.登录    3.退出--

            =================================
            ''')
        
        try:
            cmd = int(input("输入选项>>"))
        except KeyboardInterrupt:
            s.close()
            print('退出')
            sys.exit(0)
        except :
            print('请输入整数') #写到这里,进行了与客户端的测试1连接测试
            continue

        if cmd <1 or cmd >3:
            print('输入有误,请重新输入')
            sys.stdin.flush() # 清除标准输入,防止恶意刷屏
            continue
        elif cmd == 1:
            r = do_register(s)
            if r == 0:
                print('注册成功')#注册成功后有两种方式登录,1注册成功自动登录,2注册成功跳回到第一界面.  现在是第一种方式
            elif r == 1:
                print('用户存在')
            else:
                print('注册失败')
        elif cmd == 2:
            r = do_login(s)
            if r == 2:
                print('用户名不存在')
            elif r == 1:
                print('密码错误')
            else:
                name = r
                print('登录成功')
                do_Login_II(s,name)

        elif cmd == 3:
            print('退出')
            sys.exit(0)

def do_Login_II(s,name):
    while True:
        print('''
            =======Welcome %s======

             1.查单词 (##退出)
             2.历史记录 
             3.退出当前用户

            ===========================
            '''%name)
        
        try:
            cmd = int(input("输入选项>>"))
        except KeyboardInterrupt:
            s.close()
            print('退出')
            sys.exit(0)
        except :
            print('请输入整数') #写到这里,进行了与客户端的测试1连接测试
            continue
        if cmd <1 or cmd >3:
            print('输入有误,请重新输入')
            sys.stdin.flush() # 清除标准输入,防止恶意刷屏
            continue
        elif cmd == 1:
            do_query(s,name)
        elif cmd == 2:
            do_history(s,name)
        elif cmd == 3:
            print('退出当前用户')
            return

def do_query(s,name):
    while True:
        word = input('请输入单词:') # 别忘记输入
        if word == '##':  # 别忘记退出
            break
        elif not word:
            break
        msg ="Q {} {}".format(name,word)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'OK':
            d = s.recv(2048).decode()
            print(d)
        else:
            print("没有查到该单词")


def do_login(s):
    while True:
        name = input(
            'User:')
        passwd = getpass.getpass('Password:')
        msg = "L {} {}".format(name,passwd)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'Login':
            return name
        elif data == 'PassError':
            return 1
        else:
            return 2

def do_register(s):
    while True:
        name = input('User:')
        passwd = getpass.getpass('Password:')
        passwd1 = getpass.getpass('Again:')
        if (' ' in name) or (' ' in passwd ):#空格会影响后续的操作
            print('\n用户名不能有空格')
            continue        
        elif passwd != passwd1 :
            print('\n两次密码不一致')
            continue
        
        msg = 'R %s %s'%(name,passwd)
        
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'OK':
            return 0
        elif data =='EXISTS':
            return 1
        else:
            return 2
#支线函数一定要return回去,继续主线的故事

def do_history(s,name):
    msg = "H {}".format(name)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'OK':
        while True:
            da = s.recv(1024).decode()
            if da == "##":
                break
            print(da)
    else:
        print('没有历史记录')





if __name__ == '__main__':
    main()

'''
一.写顺序问题:一个函数一个函数的写,写完一个验证一个.
步骤:
0,先画流程图
1搭建通信框架(就是建立连接):从服务端开始写main,再写客户端main,测试.
2,连接好之后,具体的'注册','登录'等等,都从客户端开始写,因为客户端先请求,服务端再处理请求,这样写思路清楚.客户端一个函数写完,服务端马上写对应的函数,然后测试.以此类推,一个接着一个的,逐个完成.

二.谁来do的问题
1.客户端不能直接调用数据库,只能服务端来do
2.两次密码输入不一致,客户端就能做
3.数据库直接能做的,就不用收集到列表里再判断,因为数据库本身就是列'表'.
4.任何请求都要服务端同意才OK

三.哪里用try?
1.

四.用户界面
1,最简单的是input('用户名:')
2,然后是 ---- 目录 ----

五.想想还有其它情况么?

六,每个函数代码风格要统一

七,写if语句,先写else,否则会忘.

'''