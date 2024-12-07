import socketserver
import pickle
import time
import sqlite3

import utils

# 数据库初始化
conn = sqlite3.connect("chat.db")
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)"""
)
c.execute(
    """CREATE TABLE IF NOT EXISTS history (sender TEXT, receiver TEXT, timestamp TEXT, message TEXT)"""
)
conn.commit()


def load_users():
    c.execute("SELECT username, password FROM users")
    return dict(c.fetchall())


class Handler(socketserver.BaseRequestHandler):
    clients = {}  # 保存所有客户端的socket

    def setup(self):
        self.username = ""
        self.file_peer = ""
        self.authed = False  # authed表示是否已经登录
        self.conn = sqlite3.connect("chat.db")
        self.c = self.conn.cursor()

    def handle(self):
        while True:
            data = utils.recv(self.request)
            # 如果没有登录
            if not self.authed:
                self.user = data["username"]
                if data["action"] == "login":
                    if self.validate(data["username"], data["password"]):
                        utils.send(self.request, {"response": "ok"})
                        self.authed = True
                        for user in Handler.clients.keys():
                            # 发送给其他客户端，有新用户加入
                            utils.send(
                                Handler.clients[user].request,
                                {"action": "person_join", "object": self.user},
                            )
                        Handler.clients[self.user] = self  # 将客户端加入clients字典
                    elif self.isUserExist(data["username"]):
                        utils.send(
                            self.request,
                            {"response": "fail", "reason": "用户不存在"},
                        )
                    else:
                        utils.send(
                            self.request,
                            {"response": "fail", "reason": "密码错误"},
                        )
                elif data["action"] == "register":
                    print(data)
                    if self.register(data["username"], data["password"]):
                        utils.send(self.request, {"response": "ok"})
                    else:
                        utils.send(
                            self.request, {"response": "fail", "reason": "账号已存在！"}
                        )
            else:
                if data["action"] == "get_all_users":
                    users = []
                    for user in Handler.clients.keys():
                        if user != self.user:
                            users.append(user)
                    utils.send(self.request, {"action": "get_all_users", "data": users})
                elif data["action"] == "get_history":
                    utils.send(
                        self.request,
                        {
                            "action": "get_history",
                            "object": data["object"],
                            "data": self.get_history(self.user, data["object"]),
                        },
                    )
                elif data["cmd"] == "chat" and data["peer"] != "":
                    utils.send(
                        Handler.clients[data["peer"]].request,
                        {"type": "msg", "peer": self.user, "msg": data["msg"]},
                    )
                    self.append_history(self.user, data["peer"], data["msg"])
                elif data["cmd"] == "chat" and data["peer"] == "":
                    for user in Handler.clients.keys():
                        if user != self.user:
                            utils.send(
                                Handler.clients[user].request,
                                {
                                    "type": "broadcast",
                                    "peer": self.user,
                                    "msg": data["msg"],
                                },
                            )
                    self.append_history(self.user, "", data["msg"])
                elif data["action"] == "shutdown":
                    self.finish()

    def finish(self):
        if self.authed:
            self.authed = False
            if self.user in Handler.clients.keys():
                del Handler.clients[self.user]
            for user in Handler.clients.keys():
                utils.send(
                    Handler.clients[user].request,
                    {"action": "person_left", "peer": self.user},
                )
        self.conn.close()

    def register(self, usr, pwd):
        if usr not in users.keys():
            self.c.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)", (usr, pwd)
            )
            self.conn.commit()
            return True
        else:
            return False

    def validate(self, usr, pwd):
        self.c.execute("SELECT password FROM users WHERE username=?", (usr,))
        result = self.c.fetchone()
        if result and result[0] == pwd:
            return True
        return False

    def isUserExist(self, usr):
        self.c.execute("SELECT username FROM users WHERE username=?", (usr,))
        result = self.c.fetchone()
        if result:
            return True
        return False

    def append_history(self, sender, receiver, msg):
        timestamp = time.strftime("%m月%d日%H:%M", time.localtime(time.time()))
        self.c.execute(
            "INSERT INTO history (sender, receiver, timestamp, message) VALUES (?, ?, ?, ?)",
            (sender, receiver, timestamp, msg),
        )
        self.conn.commit()

    def get_history(self, sender, receiver):
        # 若receiver为空，则返回所有的历史记录
        if receiver == "":
            self.c.execute(
                "SELECT sender, receiver, timestamp, message FROM history WHERE sender=? OR receiver=?",
                (sender, sender),
            )
        else:
            self.c.execute(
                "SELECT sender, receiver, timestamp, message FROM history WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)",
                (sender, receiver, receiver, sender),
            )
        return self.c.fetchall()


if __name__ == "__main__":
    users = load_users()
    app = socketserver.ThreadingTCPServer(("0.0.0.0", 12345), Handler)
    app.serve_forever()
