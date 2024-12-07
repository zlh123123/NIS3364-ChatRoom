from Ui_py.Ui_ChatRoom import Ui_ChatRoom
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import SplitTitleBar
from qframelesswindow import FramelessWindow as Window


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
        for user in users:
            self.listWidget.addItem(user)

    def update_history(self, history):
        self.plainTextEdit_2.clear()
        for msg in history:
            self.plainTextEdit_2.append(msg)
