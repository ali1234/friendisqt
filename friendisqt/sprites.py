import pathlib

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QRegion, QBitmap


class Sprites:
    activities = [
        'drag', 'fall', 'idle', 'pet', 'sleep', 'walk'
    ]
    def __init__(self, sprite_path):
        self._sprites = {}
        self._masks = {}
        self._width = 0
        self._height = 0
        for act in self.activities:
            for d in ['l', 'r']:
                for frame in range(4):
                    image = QImage(str(sprite_path / f'{act}_{d}_{frame}.png'), 'png')
                    size = image.size()
                    self._width = max(self._width, size.width())
                    self._height = max(self._height, size.height())
                    mask = QRegion(QBitmap.fromImage(image.createAlphaMask()))
                    self._sprites[act, d, frame] = image
                    self._masks[act, d, frame] = mask

    @property
    def size(self):
        return QSize(self._width, self._height)

    def __getitem__(self, item):
        return self._sprites[item], self._masks[item]


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
