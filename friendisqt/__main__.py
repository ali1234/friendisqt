import random
import sys

import click

from PyQt5.QtWidgets import QApplication

from friendisqt import sprites
from friendisqt.friend import Friend


@click.command()
@click.option('-p', '--path', type=click.Path(exists=True), multiple=True, help='Add a path to search for sprites.')
@click.option('-w', '--who', type=str, multiple=True, default=['baba'], help='Name of character to add.')
def main(path, who):
    app = QApplication(sys.argv)
    sprites.search_paths.extend(reversed(path))
    try:
        friends = [Friend(w) for w in who]
    except FileNotFoundError as e:
        print(e)
        sys.exit(-1)
    else:
        for f in friends:
            f.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
