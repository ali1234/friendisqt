import random
import sys

import click

from PyQt5.QtWidgets import QApplication

from friendisqt.sprites import Sprites
from friendisqt.world import World


@click.command()
@click.option('-w', '--who', metavar='NAME', type=str, multiple=True, help='Name of character to add.')
@click.option('--all', '_all', is_flag=True, default=0, help='Add one of each friend.')
@click.option('--party', metavar='N', type=int, default=0, help='Add N random friends.')
@click.option('-s', '--stay', is_flag=True, help='Friends stay within the monitor they are placed on.')
@click.option('-p', '--path', type=click.Path(exists=True), multiple=True, help='Add a path to search for sprites.')
@click.option('--debug', is_flag=True, help='Start with the debug window open.')
def main(path, who, debug, _all, party, stay):
    app = QApplication(sys.argv)
    Sprites.sprite_paths.extend(reversed(path))
    Sprites.scan_sprite_paths()
    avail = list(Sprites.available.keys())

    if len(avail) == 0:
        raise FileNotFoundError("No sprite sheets were found.")

    world = World(app, stay)
    if debug:
        world.debug()

    if _all:
        for w in avail:
            world.add_friend(w)

    if party:
        for n in range(party):
            world.add_friend(random.choice(avail))

    for w in who:
        try:
            world.add_friend(w)
        except FileNotFoundError as e:
            print(e)
            sys.exit(-1)

    if not any((_all, party, who)):
        if 'baba' in avail:
            world.add_friend('baba')
        else:
            world.add_friend(avail[0])

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
