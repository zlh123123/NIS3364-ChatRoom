from Ui_py.Ui_ChatRoom import Ui_ChatRoom
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import SplitTitleBar
from qframelesswindow import FramelessWindow as Window
import function.utils as utils


class ChatRoom(Window, Ui_ChatRoom):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setTitleBar(SplitTitleBar(self))
        self.titleBar.raise_()

        self.setWindowTitle("ChatRoom")
        self.setWindowIcon(QIcon(":/images/logo.png"))

        self.titleBar.titleLabel.setStyleSheet(
            """
            QLabel{
                background: transparent;
                font: 13px 'Segoe UI';
                padding: 0 4px;
                color: black
            }
        """
        )

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def update_users(self, users):

        self.listWidget.clear()
        self.listWidget.addItem("全局广播")
        for user in users:
            self.listWidget.addItem(user)

    def update_history(self, history, current_object):
        # print("当前频道：", current_object)
        self.plainTextEdit_2.clear()
        for msg in history:
            if isinstance(msg, list):
                sender, receiver, time, content = msg
                if current_object in [sender, receiver] or receiver == "":
                    formatted_msg = f"{sender} - {time}\n{content}\n\n"
                    self.plainTextEdit_2.insertPlainText(formatted_msg)
            else:
                formatted_msg = msg + "\n\n"
                self.plainTextEdit_2.insertPlainText(formatted_msg)

    def append_message(self, msg, current_object):
        # print("当前频道：", current_object)
        if isinstance(msg, list):
            sender, receiver, time, content = msg
            if current_object in [sender, receiver] or receiver == "":
                formatted_msg = f"{sender} - {time}\n{content}\n\n"
                self.plainTextEdit_2.insertPlainText(formatted_msg)
        else:
            formatted_msg = msg + "\n\n"
            self.plainTextEdit_2.insertPlainText(formatted_msg)
