import threading
import hashlib
import socket
import time

import function.utils as utils

from PyQt5.QtWidgets import QMessageBox
import re
from function.chatroom import ChatRoom
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication

s = None
user = ""
current_object = ""
users = []
chatroom_window = None


def shutdown():
    global s
    if s:
        utils.send(s, {"action": "shutdown"})
        s.shutdown(2)
        s.close()
        s = None


def ishostright(host, port):
    # 检查host是否为合法的ip地址, port是否为合法的端口号
    if (
        re.match(
            r"^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$",
            host,
        )
        and 0 < int(port) < 65536
    ):
        return True

    return False


def login(host, port, username, password):
    if not ishostright(host, port):
        QMessageBox.critical(None, "登录失败", "请输入正确的ip地址或端口号！")

        return
    global s, user, chatroom_window
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)  # 设置超时时间
    if username != "" and password != "":
        s.connect((host, int(port)))
        utils.send(
            s,
            {
                "action": "login",
                "username": username,
                "password": hashlib.md5(password.encode()).hexdigest(),  # 用md5加密密码
            },
        )
        response = utils.recv(s)
        if response["response"] == "ok":
            user = username

            # 显示登录成功的对话框
            QMessageBox.information(None, "登录成功", "您已成功登录！")

            # 显示主窗口并关闭登录窗口
            chatroom_window = ChatRoom()

            chatroom_window.show()
            QApplication.instance().activeWindow().close()

            utils.send(s, {"action": "get_all_users"})
            utils.send(s, {"action": "get_history", "object": ""})

            # 开启异步进程，根据服务器返回的数据进行处理
            t = threading.Thread(target=handle_server_response, args=())
            t.daemon = True  # 设置为守护线程，主线程结束时，守护线程也会结束
            t.start()

            QCoreApplication.instance().aboutToQuit.connect(shutdown)

        elif response["response"] == "fail":
            QMessageBox.critical(None, "登录失败", response["reason"])

            shutdown()

    else:
        QMessageBox.critical(None, "登录失败", "用户名或密码不能为空！")
        shutdown()


def register(host, port, username, password):
    if not ishostright(host, port):
        QMessageBox.critical(None, "登录失败", "请输入正确的ip地址或端口号！")
        return
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    if username != "" and password != "":
        s.connect((host, int(port)))
        utils.send(
            s,
            {
                "action": "register",
                "username": username,
                "password": hashlib.md5(password.encode()).hexdigest(),
            },
        )
        response = utils.recv(s)
        if response["response"] == "ok":
            QMessageBox.information(None, "注册成功", "您已成功注册！")

        elif response["response"] == "fail":
            QMessageBox.critical(None, "注册失败", response["reason"])

    else:
        QMessageBox.critical(None, "注册失败", "用户名或密码不能为空！")

    shutdown()


def handle_server_response():
    global s, users, current_object, chatroom_window
    while True:
        data = utils.recv(s)
        if data["action"] == "get_all_users":
            users = data["data"]
            # print(users)

            chatroom_window.update_users(users)

        elif data["action"] == "get_history":
            if data["object"] == current_object:
                chatroom_window.update_history(data["data"])

        elif data["action"] == "person_join":
            users.append(data["object"])
            chatroom_window.update_users(users)
        
        elif data["action"] == "person_left":
            users.remove(data["object"])
            chatroom_window.update_users(users)
