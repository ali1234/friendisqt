# Friend is Qt

A cross-platform Qt remake of [Baba Friend](https://hempuli.itch.io/baba-friend)
by [Hempuli](https://www.hempuli.com/).

To use this you need to provide some sprites, such as the ones included in Baba Friend.

## Installation:

Clone this repository and run `pip install .` in the top level (preferably with a virtualenv active).

## Requirements:

- PyQt5
- Click

## Options:

`friendisqt -w <character> -p <path>`

- `-w <character>` to create an instance of that character. For example `-w baba`. 
  May be specified multiple times to get multiple instances. By default, one `baba`
  is created.
- `-p <path>` adds a directory to the sprite search path. For example
  `-p /path/to/BabaFriend/sprites`. May be specified multiple times. 
  Directories will be searched for a sprite directory with the character's
  name. Custom directories are searched in the order they are specified,
  followed by the current directory, and then the module's sprites directory.

## Implemented:

- Idling
- Walking
- Sleeping
- Dragging
- Petting

## Not Yet Implemented:

- Gravity

