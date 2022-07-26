import random

from PyQt5.QtCore import QPoint, Qt, QTimer, QSignalMapper
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QAction, QApplication, QWidget

from friendisqt.sprites import Sprites


class Friend(QWidget):
    def __init__(self, world, who='baba', where=None, stay_on_monitor=False):
        super().__init__(world,
                         Qt.FramelessWindowHint |
                         Qt.WindowSystemMenuHint |
                         Qt.WindowStaysOnTopHint |
                         Qt.NoDropShadowWindowHint |
                         Qt.BypassWindowManagerHint |
                         Qt.Tool )
        self.world = world
        self.sprites = Sprites.load(who)

        self.resize(self.sprites.size)
        if where is None:
            rec = QApplication.desktop().rect()
            pos = QPoint(random.randint(100, rec.width() - 100),
                         random.randint(100, rec.height() - 100))

            if stay_on_monitor:
                self.move(self.clamp_to_screen(pos, self.world.screen_near_point(pos)))
            else:
                self.move(self.clamp_to_desktop(pos))

        self.add_mapper = QSignalMapper(self)
        self.add_mapper.mapped[str].connect(self.world.add_friend)

        for friend in sorted(self.sprites.available):
            action = QAction(f"{friend.title()}", self, triggered=self.add_mapper.map)
            self.add_mapper.setMapping(action, friend)
            self.addAction(action)

        self.stay_action = QAction("&Stay on Monitor", self, shortcut="Ctrl+S", checkable=True, checked=stay_on_monitor)
        self.addAction(self.stay_action)

        debug_action = QAction("&Debug", self, shortcut="Ctrl+D", triggered=self.world.debug)
        self.addAction(debug_action)

        quit_action = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=QApplication.instance().quit)
        self.addAction(quit_action)

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

        self.thinktimer = QTimer(self)
        self.thinktimer.timeout.connect(self.think)
        self.thinktimer.start(random.randint(1000, 5000))

        self.speed = 240 // world.refresh_rate
        # falling is not implemented yet
        # so allow vertical walking instead
        self.vspeed = 0

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

    def pos(self):
        return self.geometry().topLeft()

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
            self.drag_start = event.globalPos() - self.pos()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
            self.activity = 'idle'
            event.accept()

    def clamp_to_screen(self, pos, screen):
        """Returns an adjusted pos, keeping self.rect() entirely on the specified screen."""
        sx1, sy1, sx2, sy2 = screen.geometry().getCoords()
        return QPoint(max(sx1, min(pos.x(), sx2 - self.rect().width())),
                      max(sy1, min(pos.y(), sy2 - self.rect().height())))

    def clamp_to_desktop(self, pos, screen_pos=None):
        """Returns an adjusted pos, keeping self.rect() entirely on the screen nearest screen_pos."""
        if self.world.oob(self.rect().translated(pos)):
            if screen_pos is None:
                screen_pos = pos
            return self.clamp_to_screen(pos, self.world.screen_near_point(screen_pos))
        return pos

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            mouse_pos = event.globalPos()
            self.move(self.clamp_to_desktop(mouse_pos - self.drag_start, mouse_pos))
            event.accept()
        elif event.buttons() == Qt.NoButton:
            self.pet(event.pos().x())

    def paintEvent(self, event):
        """Redraws the image to the window."""
        painter = QPainter(self)
        painter.drawImage(QPoint(0, 0), self._image)

    def refresh(self):
        """Updates pet factor, updates the window shape and triggers a paint event."""
        self._frame = self._frame % self.sprites.activity_frames(self.activity, self.direction)
        self._image, mask = self.sprites[self.activity, self.direction, self._frame]
        self.setMask(mask)
        self.update()

    def animate(self):
        """Updates the current animation frame."""
        self._frame += 1
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
            pos = self.pos()
            pos.setX(pos.x() + (self.speed if self._direction == 'r' else -self.speed))
            pos.setY(pos.y() + self.vspeed)
            if self.stay_action.isChecked():
                self.move(self.clamp_to_screen(pos, self.screen()))
            else:
                self.move(self.clamp_to_desktop(pos))
