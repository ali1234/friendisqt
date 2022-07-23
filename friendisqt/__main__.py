import random
import sys

import click

from PyQt5.QtWidgets import QApplication

from friendisqt import sprites
from friendisqt.world import World


@click.command()
@click.option('-p', '--path', type=click.Path(exists=True), multiple=True, help='Add a path to search for sprites.')
@click.option('-w', '--who', type=str, multiple=True, default=['baba'], help='Name of character to add.')
@click.option('-d', '--debug', is_flag=True, help='Start with the debug window open.')
def main(path, who, debug):
    app = QApplication(sys.argv)
    sprites.search_paths.extend(reversed(path))
    world = World()
    if debug:
        world.debug()
    for w in who:
        try:
            world.add_friend(w)
        except FileNotFoundError as e:
            print(e)
            sys.exit(-1)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
