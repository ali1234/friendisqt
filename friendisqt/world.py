import math

import mss
from PyQt5 import Qt

from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QImage, QColor
from PyQt5.QtWidgets import QWidget

from friendisqt.friend import Friend

class World(QWidget):
    def __init__(self):
        super().__init__()
        self._friends = []

        self.refresh_rate = math.floor(self.screen().refreshRate())

        self._mss = mss.mss()
        self.screengrab()
        self.setFixedSize(self.img.width // 4, self.img.height // 4)
        self.setWindowTitle("Friend World Debug")
        self.setWindowFlag(Qt.WindowMinMaxButtonsHint, False)

        self.animtimer = QTimer(self)
        self.animtimer.timeout.connect(self.animate)
        self.animtimer.start(150)

        self.movetimer = QTimer(self)
        self.movetimer.timeout.connect(self.movement)
        self.movetimer.start(2000 // self.refresh_rate)

        self.screengrabtimer = QTimer(self)
        self.screengrabtimer.timeout.connect(self.screengrab)
        self.screengrabtimer.start(500)

    def debug(self):
        self.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def add_friend(self, who):
        f = Friend(self, who)
        f.show()
        self._friends.append(f)

    def animate(self):
        for friend in self._friends:
            friend.animate()

    def movement(self):
        for friend in self._friends:
            friend.movement()

    def screengrab(self):
        self.img = self._mss.grab(self._mss.monitors[0])
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        img = QImage(self.img.raw, self.img.width, self.img.height, QImage.Format_RGB32)
        #img = img.scaled(self.img.width//4, self.img.height//4)
        painter.scale(0.25, 0.25)
        painter.drawImage(QPoint(0, 0), img)
        painter.setOpacity(0.2)
        for f in self._friends:
            #painter.drawRect(f.frameGeometry())
            painter.fillRect(f.frameGeometry(), QColor("red"))



