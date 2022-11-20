import sys

from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QLabel, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView

class Madoka(QWidget):
    def __init__(self):
        super().__init__()
        self.webview = QWebEngineView(self)
        self.webview.setGeometry(10, 10, 500, 500)
        self.webview.load(QUrl("https://bridges.torproject.org/bridges/?transport=obfs4"))
        self.webview.show()
        self.webview.adjustSize()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.periodic)
        self.timer.start()

    def periodic(self):
        print("wow")
        self.webview.page().runJavaScript("document.getElementById('bridgelines').innerText", self.retrieve_bridges)

    def retrieve_bridges(self, arg):
        if arg != None:
            with open("bridges.txt", "w") as f:
                f.write(arg)
            self.close()


qAp = QApplication(sys.argv)
mado = Madoka()
mado.show()
qAp.exec()
