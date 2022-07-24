import pathlib
from collections import defaultdict

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QRegion, QBitmap


class Sprites:
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


sprites = {}

search_paths = [
    pathlib.Path(__file__).parent / 'sprites',
    pathlib.Path('.'),
]

def load_sprites(who):
    if who not in sprites:
        for p in reversed(search_paths):
            p = pathlib.Path(p)
            if (p / who).exists():
                sprites[who] = Sprites(p / who)
                print(f'Loaded sprites for {who.title()} from "{p / who}".')
                break
        else:
            raise FileNotFoundError(f"Can't find sprites for {who.title()}.")
    return sprites[who]
