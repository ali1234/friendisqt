import math
import random

from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QAction, QApplication, QWidget

from friendisqt.sprites import load_sprites


class Friend(QWidget):
    def __init__(self, world, who='baba', where=None):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint | Qt.Tool )
        self.world = world
        self.sprites = load_sprites(who)

        refresh_rate = math.floor(self.screen().refreshRate())

        self.resize(self.sprites.size)
        if where is None:
            rec = QApplication.desktop().rect()
            x = random.randint(100, rec.width() - 100)
            y = random.randint(100, rec.height() - 100)
            self.move(x, y)

        quit_action = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=QApplication.instance().quit)
        self.addAction(quit_action)
        debug_action = QAction("&Debug", self, shortcut="Ctrl+D", triggered=self.world.debug)
        self.addAction(debug_action)

        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setToolTip(f"Drag {who.title()} with the left mouse button.\n"
                "Use the right mouse button to open a context menu.")
        self.setWindowTitle(who.title())
        self.setMouseTracking(True)
        self.setCursor(Qt.OpenHandCursor)

        self._activity = 'idle'
        self._direction = 'l'
        self._frame = 0
        self._pet_factor = 0
        self._last_pet = None
        self.animate()

        self.animtimer = QTimer(self)
        self.animtimer.timeout.connect(self.animate)
        self.animtimer.start(150)

        self.thinktimer = QTimer(self)
        self.thinktimer.timeout.connect(self.think)
        self.thinktimer.start(random.randint(1000, 5000))

        self.speed = 240 // refresh_rate
        # falling is not implemented yet
        # so allow vertical walking instead
        self.vspeed = 0

        self.movetimer = QTimer(self)
        self.movetimer.timeout.connect(self.movement)
        self.movetimer.start(2000//refresh_rate)

    @property
    def activity(self):
        return self._activity

    @activity.setter
    def activity(self, a):
        if a not in self.sprites.activities:
            raise ValueError(f"No sprites for activity {a}.")
        if a == self._activity:
            return
        self._activity = a
        self.refresh()

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, d):
        self._direction = d
        self.refresh()

    def pet(self, x):
        if self._last_pet is not None:
            self._pet_factor += abs(self._last_pet - x)
        self._last_pet = x
        if self._pet_factor > 700:
            self.activity = 'pet'
            self.thinktimer.setInterval(4000)
            self._pet_factor = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.activity = 'drag'
            self.setCursor(Qt.ClosedHandCursor)
            self.drag_start = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
            self.activity = 'idle'
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start)
            event.accept()
        elif event.buttons() == Qt.NoButton:
            self.pet(event.pos().x())

    def paintEvent(self, event):
        """Redraws the image to the window."""
        painter = QPainter(self)
        painter.drawImage(QPoint(0, 0), self._image)

    def refresh(self):
        """Updates pet factor, updates the window shape and triggers a paint event."""
        self._image, mask = self.sprites[self.activity, self.direction, self._frame]
        self.setMask(mask)
        self.update()

    def animate(self):
        """Updates the current animation frame."""
        self._frame = (self._frame + 1) % 4
        self.refresh()

    def think(self):
        """Changes the current action and possibly direction."""
        self.thinktimer.setInterval(random.randint(1000, 5000))

        # If happy, become idle.
        if self.activity == 'pet':
            self._last_pet = None
            self._activity = 'idle'
            return

        # Maybe change direction if walking or idle.
        if self.activity in ['walk', 'idle']:
            if random.randint(0, 1):
                self.direction = random.choice(['l', 'r'])
                self.vspeed = random.randint(-1, 1) * self.speed
                return

        # Otherwise change action if not dragging, falling, or petting.
        if self.activity not in ['drag', 'fall', 'pet']:
            self.activity = random.choice(['walk', 'idle', 'sleep'])

    def movement(self):
        """Moves the window according to the current action."""
        if self.activity == 'walk':
            pos = self.mapToGlobal(QPoint(0, 0))
            pos.setX(pos.x() + (self.speed if self._direction == 'r' else -self.speed))
            pos.setY(pos.y() + self.vspeed)
            self.move(pos)
