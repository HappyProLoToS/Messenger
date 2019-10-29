import sys
from PyQt5 import QtWidgets
from gui import design
import winsound

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver


class Client(LineOnlyReceiver):
    factory: 'Connector'
    login: str

    def connectionMade(self):
        self.factory.window.protocol = self

    def lineReceived(self, line: bytes):
        message = line.decode()
        self.factory.window.plainTextEdit.appendPlainText(message)


class Connector(ClientFactory):
    window: 'ChatWindow'
    protocol = Client

    def __init__(self, app_window):
        self.window = app_window


class ChatWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    protocol: Client
    reactor = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_handlers()

    def init_handlers(self):
        self.pushButton.clicked.connect(self.send_message)
        self.pushButton.setAutoDefault(True)
        self.lineEdit.returnPressed.connect(self.pushButton.click)
        self.send_message

    def closeEvent(self, event):
        self.reactor.callFromThread(self.reactor.stop)

    def send_message(self):
        message = self.lineEdit.text()

        self.protocol.sendLine(message.encode())
        self.lineEdit.setText('')


app = QtWidgets.QApplication(sys.argv)

import qt5reactor

window = ChatWindow()
window.show()

qt5reactor.install()

from twisted.internet import reactor

reactor.connectTCP(
    "25.29.235.139",
    1111,
    Connector(window)
)

window.reactor = reactor
reactor.run()