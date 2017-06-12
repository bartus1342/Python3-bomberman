from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QNetworkInterface, QHostAddress

# todo dokończyć cały system multiplayer(łączenie po IP, synchronizacja gry)
class Connect(QWidget):
    def __init__(self, parent):
        super(Connect, self).__init__()
        self.parent = parent
        self.width = 300
        self.height = 200
        self.setFixedSize(self.width, self.height)

        self.create_button = QPushButton("Stworz serwer", self)
        self.create_button.move(40, 20)
        self.create_button.clicked.connect(self.create_server)

        self.join_button = QPushButton("Połącz sie z serwerem", self)
        self.join_button.move(140, 20)
        self.join_button.clicked.connect(self.join_server)

        self.back_button = QPushButton("Cofnij", self)
        self.back_button.move((self.width - self.back_button.width())/2, 170)
        self.back_button.clicked.connect(self.main)

        self.your_ip = QLabel(self)
        self.your_ip.setAlignment(Qt.AlignCenter)
        self.your_ip.setFont(QFont("Arial", 16))
        self.your_ip.setFixedSize(300, 50)
        self.your_ip.move((self.width - self.your_ip.width())/2, 50)


        self.your_port = QLabel(self)
        self.your_port.setAlignment(Qt.AlignCenter)
        self.your_port.setFont(QFont("Arial", 16))
        self.your_port.setFixedSize(300, 50)
        self.your_port.move((self.width - self.your_ip.width())/2, 100)

        self.ip_label = QLabel("Podaj nr ip: ", self)
        self.ip_label.move(40, 30)


        self.ip = QTextEdit(self)
        self.ip.setFixedSize(170, 25)
        self.ip.move(100, 30)

        self.port_label = QLabel("Podaj nr portu: ", self)

        self.port = QTextEdit(self)

        self.main()


    def main(self):
        self.create_button.setVisible(True)
        self.join_button.setVisible(True)
        self.back_button.setVisible(False)
        self.your_ip.setVisible(False)
        self.your_port.setVisible(False)
        self.ip_label.setVisible(False)
        self.ip.setVisible(False)
        self.port_label.setVisible(False)
        self.port.setVisible(False)

    def create_server(self):
        self.server = QTcpServer(self)
        self.server.newConnection.connect(self.connect_with)
        ipadd = None
        lista = QNetworkInterface.allAddresses()
        for i in range(len(lista)):
            if not lista[i] == QHostAddress.LocalHost and lista[i].toIPv4Address():
                ipadd = lista[i].toString()
                break
        if ipadd == None:
             ipadd = QHostAddress(QHostAddress.LocalHost).toString()
        self.ipAddress = QHostAddress()
        self.ipAddress.setAddress(ipadd)
        self.ipAddress.toIPv4Address()
        self.create_button.setVisible(False)
        self.join_button.setVisible(False)
        self.back_button.setVisible(True)
        port_nr = 10020
        self.server.listen(self.ipAddress, port_nr)
        self.your_ip.setText("Twój nr ip:  {}".format(ipadd))
        self.your_port.setText("Twój port:  {}".format(port_nr))
        self.your_ip.setVisible(True)
        self.your_port.setVisible(True)

    def join_server(self):
        self.client = QTcpSocket(self)
        self.create_button.setVisible(False)
        self.join_button.setVisible(False)
        self.back_button.setVisible(True)
        self.ip_label.setVisible(True)
        self.ip.setVisible(True)
        print("joined")

    def connect_with(self):
        self.get_client = self.server.nextPendingConnection()
        self.get_client.disconnect.connect(QObject.deleteLater)