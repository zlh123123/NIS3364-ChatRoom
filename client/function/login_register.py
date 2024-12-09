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
from PyQt5.QtCore import QMetaObject, Qt

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

            QCoreApplication.instance().aboutToQuit.connect(
                shutdown
            )  # 关闭窗口时关闭socket
            utils.send(s, {"action": "get_all_users"})
            utils.send(s, {"action": "get_history", "object": ""})

            # 开启异步进程，根据服务器返回的数据进行处理
            t = threading.Thread(target=handle_server_response, args=())
            t.daemon = True  # 设置为守护线程，主线程结束时，守护线程也会结束
            t.start()

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


def send_msg(msg):
    global s, user, current_object
    if msg != "":
        if current_object == "":
            utils.send(s, {"action": "chat", "peer": "", "msg": msg})
        else:
            utils.send(s, {"action": "chat", "peer": current_object, "msg": msg})
            # 将发送的消息显示在聊天框中
        chatroom_window.append_message(
            [user, current_object, time.strftime("%m月%d日%H:%M"), msg], current_object
        )
    else:
        QMessageBox.critical(None, "发送失败", "消息不能为空！")


def choose_object(object):
    global current_object, s
    current_object = object
    utils.send(s, {"action": "get_history", "object": object})


# def handle_server_response():
#     global s, users, current_object, chatroom_window, user
#     while True:
#         try:
#             data = utils.recv(s)
#             if data["action"] == "get_all_users":
#                 users = data["data"]
#                 chatroom_window.update_users(users)

#             elif data["action"] == "get_history":
#                 chatroom_window.update_history(data["data"], current_object)

#             elif data["action"] == "person_join":
#                 users.append(data["object"])
#                 chatroom_window.update_users(users)

#             elif data["action"] == "person_left":
#                 users.remove(data["object"])
#                 chatroom_window.update_users(users)

#             elif data["action"] == "msg":
#                 # 如果当前频道是发送消息的对象，则显示消息
#                 if current_object == data["peer"]:
#                     chatroom_window.append_message(
#                         [
#                             user,
#                             current_object,
#                             time.strftime("%m月%d日%H:%M"),
#                             data["msg"],
#                         ],
#                         current_object,
#                     )
#                 # 如果不是，就在列表中显示有消息的对象，在名字后面加上（有新消息）
#                 else:
#                     chatroom_window.update_list_item_text(data["peer"])

#             elif data["action"] == "broadcast":
#                 # 如果当前频道是全局广播，则显示消息
#                 if current_object == "":
#                     chatroom_window.append_message(
#                         [
#                             data["peer"],
#                             "",
#                             time.strftime("%m月%d日%H:%M"),
#                             data["msg"],
#                         ],
#                         "",
#                     )
#                 # 如果不是，就在全局广播后面加上（有新消息）
#                 else:
#                     chatroom_window.update_broadcast_text()

#         except Exception as e:
#             print(f"Exception in handle_server_response: {e}")
#             break


from PyQt5.QtCore import QEvent, QObject, QCoreApplication


class UpdateUIEvent(QEvent):
    def __init__(self, callback, *args):
        super().__init__(QEvent.User)
        self.callback = callback
        self.args = args

    def execute(self):
        self.callback(*self.args)


class UIUpdater(QObject):
    def event(self, event):
        if isinstance(event, UpdateUIEvent):
            event.execute()
            return True
        return super().event(event)


ui_updater = UIUpdater()


def post_update_ui(callback, *args):
    event = UpdateUIEvent(callback, *args)
    QCoreApplication.postEvent(ui_updater, event)


def handle_server_response():
    global s, users, current_object, chatroom_window, user
    while True:
        try:
            data = utils.recv(s)
            if data["action"] == "get_all_users":
                users = data["data"]
                post_update_ui(chatroom_window.update_users, users)

            elif data["action"] == "get_history":
                post_update_ui(
                    chatroom_window.update_history, data["data"], current_object
                )
                #print(data["data"])
                

            elif data["action"] == "person_join":
                users.append(data["object"])
                post_update_ui(chatroom_window.update_users, users)

            elif data["action"] == "person_left":
                users.remove(data["object"])
                post_update_ui(chatroom_window.update_users, users)

            elif data["action"] == "msg":
                if current_object == data["peer"]:
                    post_update_ui(
                        chatroom_window.append_message,
                        [
                            user,
                            current_object,
                            time.strftime("%m月%d日%H:%M"),
                            data["msg"],
                        ],
                        current_object,
                    )
                else:
                    post_update_ui(chatroom_window.update_list_item_text, data["peer"])

            elif data["action"] == "broadcast":
                if current_object == "":
                    post_update_ui(
                        chatroom_window.append_message,
                        [data["peer"], "", time.strftime("%m月%d日%H:%M"), data["msg"]],
                        "",
                    )
                else:
                    post_update_ui(chatroom_window.update_broadcast_text)

        except Exception as e:
            print(f"Exception in handle_server_response: {e}")
            break
