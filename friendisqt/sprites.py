import pathlib
from collections import defaultdict

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QRegion, QBitmap


class Sprites:

    cache = {}
    available = {}
    sprite_paths = [
        pathlib.Path(__file__).parent / 'sprites',
        pathlib.Path('.'),
    ]

    def __init__(self, sprite_path):
        self._sprites = {}
        self._masks = {}
        self._width = 0
        self._height = 0

        activities = defaultdict(lambda: defaultdict(dict))
        for file in pathlib.Path(sprite_path).glob('*_?_*.png'):
            activity, direction, frame = file.stem.split('_')
            try:
                frame = int(frame, 10)
            except ValueError:
                continue
            image = QImage(str(file), 'png')
            size = image.size()
            self._width = max(self._width, size.width())
            self._height = max(self._height, size.height())
            mask = QRegion(QBitmap.fromImage(image.createAlphaMask()))
            activities[activity][direction][frame] = (image, mask)

        self._activities = {}
        for activity, v in activities.items():
            self._activities[activity] = {}
            for direction, frames in v.items():
                self._activities[activity][direction] = [frame for n, frame in sorted(frames.items())]

    @property
    def size(self):
        return QSize(self._width, self._height)

    @property
    def activities(self):
        """Returns iterator of activity names."""
        return self._activities.keys()

    def activity_frames(self, activity, direction):
        """Returns the number of frames in an activity/direction."""
        return len(self._activities[activity][direction])

    def __getitem__(self, item):
        """Gets the image and mask for an activity/direction/frame."""
        return self._activities[item[0]][item[1]][item[2]]

    @classmethod
    def scan_sprite_paths(cls):
        for p in cls.sprite_paths:
            for d in pathlib.Path(p).iterdir():
                if d.is_dir():
                    for f in d.iterdir():
                        if f.match('*_?_*.png'):
                            cls.available[d.name] = d
                            break

    @classmethod
    def load(cls, who):
        if who not in cls.cache:
            if who not in cls.available:
                raise FileNotFoundError(f"Can't find sprites for {who.title()}.")
            cls.cache[who] = Sprites(cls.available[who])
            print(f'Loaded sprites for {who.title()} from "{cls.available[who]}".')
        return cls.cache[who]
