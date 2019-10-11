# -*- coding: UTF-8 -*-
# 我的程序 dict_server.py
'''
name: Tedu
date: 2019-9-26
modules:pymongo
This is a dict project for AID
'''

from socket import *
import os
import time
import signal
import pymysql
import sys

# 定义需要的全局变量
DICT_TEXT = './dict.txt'
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST, PORT)

# 流程控制


def main():
    # 创建数据库连接
    db = pymysql.connect('localhost', 'root', '123456', 'dict')

    # 创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)

    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    while True:
        try:     # 这个try用来ctrl+c优雅退出,如果有其它错误也要打印出来,这样才知道哪出错了.
            c, addr = s.accept()
            print('Connect from', addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit('服务器退出')
        except Exception as e:
            print(e)
            continue

        pid = os.fork()
        if pid == 0:
            s.close()
            # 传参db,父子进程共同操作同一变量,会不会有影响?答:不会的,因为mysql是关系型数据库,会加锁.
            do_child(c, db)
        else:
            c.close()
            continue
# 写到这里,进行了与客户端的测试1连接测试,当时上面的do_child由sys.exit代替


def do_child(c, db):
    while True:
        data = c.recv(128).decode()
        print(c.getpeername(), ':', data)
        if (not data) or data[0] == 'E':
            c.close()
            sys.exit(0)
        elif data[0] == 'R':  # 字符串切片取值
            do_child_register(c, db, data)
        elif data[0] == 'L':
            do_child_login(c, db, data)
        elif data[0] == "Q":
            do_child_query(c, db, data)
        elif data[0] == "H":
            do_child_history(c, db, data)


def do_child_login(c, db, data):
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cur = db.cursor()

    sql = "select * from user where name='%s' and passwd='%s'" % (name, passwd)
    cur.execute(sql)
    r = cur.fetchone()
    if r:
        c.send(b'Login')
        print('%s登录成功' % name)
        return
    sql = "select * from user where name= '%s'" % name
    cur.execute(sql)
    r = cur.fetchone()
    if r:
        c.send(b'PassError')
        print('密码错误')
        return
    else:
        c.send(b'NameError')
        print('用户名错误')
        return


def do_child_register(c, db, data):
    # print("注册")
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cur = db.cursor()

    sql = "select * from user where name= '%s'" % name
    cur.execute(sql)
    r = cur.fetchone()
    if r != None:  # 说明fetchone()会返回None
        c.send(b'EXISTS')
        return

    sql_in = "insert into user (name,passwd) values('%s','%s')" % (
        name, passwd)
    try:
        cur.execute(sql_in)
        db.commit()
        c.send(b'OK')
    except Exception as e:
        print('出错了:', e)
        db.rollback()
        c.send(b'FULL')
    else:
        print('%s注册成功' % name)


def do_child_query(c, db, data):
    l = data.split(' ')
    name = l[1]
    word = l[2]
    cur = db.cursor()

    def insert_history():  # 自定义函数也是变量,要放前面才能调用.
        tm = time.ctime()
        sql = "insert into hist (name,word,time) values('%s','%s','%s')" % (
            name, word, tm)

        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print('插入失败', e)
            db.rollback()

    sql = "select * from words where word ='%s'" % word
    cur.execute(sql)
    r = cur.fetchone()
    if r:
        c.send(b'OK')
        time.sleep(0.1)
        da = "%s  %s" % (r[1], r[2])
        c.send(da.encode())
        insert_history()
    else:
        c.send(b'NO')


def do_child_history(c, db, data):
    l = data.split(' ')
    name = l[1]
    cur = db.cursor()

    sql = "select * from hist where name = '%s'" % name
    cur.execute(sql)
    r = cur.fetchall()
    print(r)
    if r:
        c.send(b'OK')
        time.sleep(0.1)
        for line in r:
            msg = "%s\t%s\t%s\n" % (line[1], line[2], line[3])
            c.send(msg.encode())
        else:
            time.sleep(0.1)
            c.send(b'##')
    else:
        c.send(b'FALL')


if __name__ == '__main__':
    main()
