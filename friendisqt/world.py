import math

import mss
from PyQt5 import Qt

from PyQt5.QtCore import Qt, QTimer, QPoint, QSignalMapper, QRect
from PyQt5.QtGui import QPainter, QImage, QColor, QRegion, QScreen
from PyQt5.QtWidgets import QWidget

from friendisqt.friend import Friend

class World(QWidget):
    def __init__(self, app, stay):
        super().__init__()
        self._friends = []

        self.app = app
        self.stay_default = stay
        self.build_bounds()

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

    def build_bounds(self):
        bounds = QRegion()
        for screen in self.app.screens():
            bounds += screen.geometry()

        self.bb = bounds.boundingRect()
        x, y, w, h = self.bb.getRect()
        self.edge = QRegion(QRect(x-1, y-1, w+2, h+2))
        self.edge -= bounds

    def oob(self, rect):
        if self.bb.intersects(rect):
            return self.edge.intersects(rect)
        return True

    def screen_near_point(self, pos):
        screen = self.app.screenAt(pos)
        if screen:
            return screen
        dist = None
        best = None
        for screen in self.app.screens():
            x1, y1, x2, y2 = screen.geometry().getCoords()
            px = pos.x()
            py = pos.y()
            dx = max(x1 - px, 0, px - x2)
            dy = max(y1 - py, 0, py - y2)
            d = math.hypot(dx, dy)
            if dist is None or d < dist:
                dist = d
                best = screen
        return best

    def debug(self):
        self.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def add_friend(self, who):
        f = Friend(self, who, stay_on_monitor=self.stay_default)
        f.show()
        self._friends.append(f)

    def remove_friend(self, friend):
        self._friends.remove(friend)
        friend.close()
        del friend

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



