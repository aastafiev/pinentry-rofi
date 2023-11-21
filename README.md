# Description

A simple pinentry program using rofi.

Inspired by [gist](https://gist.github.com/Cimbali/862a430a0f28ffe07f8ae618e8b73973) and [@plattfot/pinentry-rofi](https://github.com/plattfot/pinentry-rofi/tree/master)

## Dependencies

- Python 3.9+
- rofi
- pygobject

`pygobject` package for [Arch](https://archlinux.org/packages/extra/x86_64/python-gobject/)

## Install

1. Copy `python_rofi.py` to your `~/.local/bin`
2. `chmod +x ~/.local/bin/pinentry_rofi.py`
3. Set `pinentry-program` in `~/.gnupg/gpg-agent.conf`. For example:

    `pinentry-program <HOME>/.local/bin/pinentry_rofi.py`

4. Restart gpg-agent `gpgconf --kill gpg-agent`

## Documentation

Run `pinentry_rofi.py --help`
