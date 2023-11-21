#!/usr/bin/env python

import argparse
import os
import subprocess
import sys
import urllib.parse
from itertools import chain
from typing import Optional, Tuple

from gi.repository import GLib


__version__ = '0.1.4'

rofi_init_args = {'-dmenu': '', '-input': '/dev/null', '-password': '', '-disable-history': '', '-mesg': '', '-l': '0'}


def assuan_send(mesg: str):
    print(mesg, flush=True)


def run_rofi(rofi_args: dict) -> bool:
    rofi = ['rofi', *chain.from_iterable(args for args in rofi_args.items())]
    status = subprocess.run(rofi, capture_output=True)
    if status.returncode:
        assuan_send("ERR 83886179 Operation cancelled <rofi>")
        return False
    pw = status.stdout.decode().rstrip('\n')
    status.stdout and assuan_send(f"D {pw}")
    del pw
    return True


def handle_command(action: str, arg: Optional[str], rofi_args: dict, *, is_test: bool = False) -> dict:  # noqa: C901
    ok = True
    if action == 'OPTION':
        try:
            opt, val = arg.split('=', 1)
        except ValueError:
            opt, val = arg, True
        if opt == 'ttyname':
            os.environ['GPG_TTY'] = val
        if opt == 'ttytype':
            os.environ['GPG_TERM'] = val
        if opt == 'lc-ctype':
            os.environ['LC_CTYPE'] = val
        if opt == 'lc-messages':
            os.environ['LC_MESSAGES'] = val
    elif action == 'GETINFO' and arg == 'pid':
        assuan_send(f'D {os.getpid()}')
    elif action == 'GETINFO' and arg == 'ttyinfo':
        assuan_send(f"D {os.environ['GPG_TTY']} {os.environ.get('GPG_TERM', '')} {os.environ['DISPLAY']}")
    elif action == 'GETINFO' and arg == 'flavor':
        assuan_send('D keyring')
    elif action == 'GETINFO' and arg == 'version':
        assuan_send(f'D {__version__}')
    elif action == 'SETPROMPT':
        if '-p' not in rofi_args:
            rofi_args['-p'] = arg.replace(':', '')
    elif action == 'SETDESC':
        rofi_args['-mesg'] = GLib.markup_escape_text(urllib.parse.unquote(arg).replace('\n', '\r'))
    elif action == 'GETPIN':
        ok = is_test or run_rofi(rofi_args)
    elif action == 'SETERROR':
        sep = '\r***************************\r'
        prev_msg = rofi_args['-mesg'].split(sep)[-1]
        rofi_args['-mesg'] = sep.join((arg, prev_msg))
    elif action == 'SETKEYINFO':
        pass
    elif action == 'BYE':
        pass
    else:
        ok = False

    if ok:
        assuan_send('OK')
    else:
        assuan_send('BYE')
        exit(1)
    return rofi_args


def handle_request(line: str) -> Tuple[str, Optional[str]]:
    line_spl = line.rstrip('\n').split(None, 1)
    if len(line_spl) == 2:
        action, arg = line_spl
    else:
        action, arg = line_spl[0], None
    return action, arg


def add_args(parser: argparse.ArgumentParser):
    parser.add_argument('-d', '--display', default=os.getenv('DISPLAY', ':0'), type=str,
                        help='Set display, default is ":0"')
    parser.add_argument('-p', '--prompt', default=os.getenv('PINENTRY_USER_DATA'), type=str,
                        help='Set rofi prompt, default takes from PINENTRY_USER_DATA environment variable.'
                             ' If environment variable not set, uses SETPROMPT argument.')


def handle_args(arg_parser: Optional[argparse.ArgumentParser] = None):
    args = arg_parser.parse_args()
    rofi_args = {**rofi_init_args, '-display': args.display}
    if args.prompt:
        rofi_args['-p'] = args.prompt
    return rofi_args


def pinentry(rofi_args: list = None):
    rofi_args = rofi_args or rofi_init_args
    assuan_send('OK Please go ahead')
    for line in sys.stdin:
        action, arg = handle_request(line)
        handle_command(action, arg, rofi_args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''
A simple pinentry program using rofi

INSTALL.

1. Copy `pinentry_rofi.py` to your `~/.local/bin`
2. `chmod +x ~/.local/bin/pinentry_rofi.py`
3. Set `pinentry-program` in `~/.gnupg/gpg-agent.conf`. For example:
   `pinentry-program <HOME>/.local/bin/pinentry_rofi.py`
4. Restart gpg-agent `gpgconf --kill gpg-agent`''',
    )
    add_args(parser)
    rofi_args = handle_args(parser)
    pinentry(rofi_args)
