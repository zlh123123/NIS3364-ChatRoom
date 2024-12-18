# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\HP\Desktop\NIS3364-ChatRoom\client\resource\ui\ChatRoom.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    ListWidget,
    PlainTextEdit,
    PushButton,
    TransparentToolButton,
    FluentIcon,
    TextEdit,
)
from PyQt5.QtWidgets import QFileDialog, QMenu, QAction
from PyQt5.QtCore import QMetaType

from PyQt5.QtGui import QTextBlock


# 重写PlainTextEdit类，让其具备按下回车键发送消息的功能
class myplainTextEdit(PlainTextEdit):
    def __init__(self, parent=None):
        super(myplainTextEdit, self).__init__(parent)
        # self.installEventFilter(self)
        self.parent = parent

    def keyPressEvent(self, event: QKeyEvent):
        if (
            event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier
        ):  # ctrl+回车
            self.insertPlainText("\n")  # 添加换行
        elif self.toPlainText() and event.key() == Qt.Key_Return:  # 回车
            self.parent.send()
        else:
            super().keyPressEvent(event)


class Ui_ChatRoom(object):
    def setupUi(self, ChatRoom):

        ChatRoom.setObjectName("ChatRoom")
        ChatRoom.resize(875, 627)
        self.listWidget = ListWidget(ChatRoom)
        self.listWidget.setGeometry(QtCore.QRect(25, 30, 221, 541))
        self.listWidget.setObjectName("listWidget")
        self.plainTextEdit = myplainTextEdit(ChatRoom)
        self.plainTextEdit.setGeometry(QtCore.QRect(280, 410, 561, 161))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit_2 = TextEdit(ChatRoom)
        self.plainTextEdit_2.setGeometry(QtCore.QRect(280, 35, 561, 341))
        self.plainTextEdit_2.setObjectName("plainTextEdit_2")
        self.plainTextEdit_2.setReadOnly(True)
        self.toolButton = TransparentToolButton(ChatRoom)
        self.toolButton.setGeometry(QtCore.QRect(280, 380, 24, 22))
        self.toolButton.setObjectName("toolButton")
        self.toolButton_2 = TransparentToolButton(ChatRoom)
        self.toolButton_2.setGeometry(QtCore.QRect(320, 380, 24, 22))
        self.toolButton_2.setObjectName("toolButton_2")
        self.pushButton = PushButton(ChatRoom)
        self.pushButton.setGeometry(QtCore.QRect(754, 580, 91, 31))
        self.pushButton.setObjectName("pushButton")
        self.toolButton_3 = TransparentToolButton(ChatRoom)
        self.toolButton_3.setGeometry(QtCore.QRect(820, 380, 24, 22))
        self.toolButton_3.setObjectName("toolButton_3")
        self.toolButton_4 = TransparentToolButton(ChatRoom)
        self.toolButton_4.setGeometry(QtCore.QRect(360, 380, 24, 22))
        self.toolButton_4.setObjectName("toolButton_4")

        # 设置图标
        self.toolButton.setIcon(FluentIcon.GAME)
        self.toolButton_2.setIcon(FluentIcon.FOLDER)
        self.toolButton_4.setIcon(FluentIcon.MICROPHONE)
        self.toolButton_3.setIcon(FluentIcon.SYNC)

        # 信号与槽
        self.pushButton.clicked.connect(self.send)
        self.toolButton_2.clicked.connect(self.open_file_dialog)
        self.toolButton_4.clicked.connect(self.open_file_dialog_micro)
        self.toolButton.clicked.connect(self.show_emoji_menu)

        self.listWidget.itemClicked.connect(self.on_item_clicked)

        self.retranslateUi(ChatRoom)

    def retranslateUi(self, ChatRoom):
        _translate = QtCore.QCoreApplication.translate
        ChatRoom.setWindowTitle(_translate("ChatRoom", "Form"))
        self.toolButton.setText(_translate("ChatRoom", ""))
        self.toolButton_2.setText(_translate("ChatRoom", ""))
        self.pushButton.setText(_translate("ChatRoom", "Send"))
        self.toolButton_3.setText(_translate("ChatRoom", ""))
        self.toolButton_4.setText(_translate("ChatRoom", ""))

    def send(self):
        from function.login_register import send_msg

        text = self.plainTextEdit.toPlainText()
        self.plainTextEdit.clear()
        send_msg(text)

    def open_file_dialog(self):
        from function.login_register import send_file 
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "所有文件 (*)", options=options
        )
        if fileName:
            # print(f"选择的文件: {fileName}")
            send_file(fileName)

    def open_file_dialog_micro(self):
        from function.login_register import send_file_micro
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self, "选择音频", "", "音频文件 (*.mp3 *.wav *.flac)", options=options
        )
        if fileName:
            # print(f"选择的文件: {fileName}")
            send_file_micro(fileName)


    def show_emoji_menu(self):
        menu = QMenu(self)

        # 添加表情选项
        emoji_list = [
            "😀",
            "😂",
            "😍",
            "😢",
            "😎",
            "😡",
            "😜",
            "🤔",
            "😇",
            "🤗",
            "😴",
        ]
        for emoji in emoji_list:
            action = QAction(emoji, self)
            action.triggered.connect(lambda checked, e=emoji: self.select_emoji(e))
            menu.addAction(action)

        # 显示菜单
        menu.exec_(self.toolButton.mapToGlobal(self.toolButton.rect().bottomLeft()))

    def select_emoji(self, emoji):
        # print(f"选择的表情: {emoji}")
        self.plainTextEdit.insertPlainText(emoji)

    def on_item_clicked(self, item):
        from function.login_register import choose_object

        # 如果内容后有（有新消息）则去掉
        if "（有新消息）" in item.text():
            item.setText(item.text().replace("（有新消息）", ""))

        # print(item.text())
        if item.text() == "全局广播":
            choose_object("")
        else:

            choose_object(item.text())



    def update_list_item_text(self, peer):
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).text() == peer:
                self.listWidget.item(i).setText(f"{peer}（有新消息）")

    def update_broadcast_text(self):
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).text() == "全局广播":
                self.listWidget.item(i).setText("全局广播（有新消息）")
