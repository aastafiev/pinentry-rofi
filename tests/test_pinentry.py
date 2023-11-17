import argparse
import os

from pinentry_rofi import __version__, add_args, handle_args, handle_command, handle_request, rofi_init_args


assuan_action_mapping = {
    'OPTION grab': {'out': 'OK'},
    'OPTION ttyname=/dev/pts/1': {'out': 'OK'},
    'OPTION ttytype=tmux-256color': {'out': 'OK'},
    'OPTION lc-messages=C': {'out': 'OK'},
    'OPTION allow-external-password-cache': {'out': 'OK'},
    'OPTION default-ok=_OK': {'out': 'OK'},
    'OPTION default-cancel=_Cancel': {'out': 'OK'},
    'OPTION default-yes=_Yes': {'out': 'OK'},
    'OPTION default-no=_No': {'out': 'OK'},
    'OPTION default-prompt=PIN:': {'out': 'OK'},
    'OPTION default-pwmngr=_Save in password manager': {'out': 'OK'},
    'OPTION default-cf-visi=Do you really want to make your passphrase visible on the screen?': {'out': 'OK'},
    'OPTION default-tt-visi=Make passphrase visible': {'out': 'OK'},
    'OPTION default-tt-hide=Hide passphrase': {'out': 'OK'},
    'OPTION touch-file=/run/user/1000/gnupg/S.gpg-agent': {'out': 'OK'},
    'GETINFO pid': {'out': f'D {os.getpid()}\nOK'},
    'GETINFO ttyinfo': {'out': f"D /dev/pts/1 tmux-256color {os.environ['DISPLAY']}\nOK"},
    'GETINFO flavor': {'out': 'D keyring\nOK'},
    'GETINFO version': {'out': f'D {__version__}\nOK'},
    'SETPROMPT Passphrase:': {
        'out': 'OK',
        'rofi_args': {'-dmenu': '', '-input': '/dev/null', '-password': '', '-disable-history': '', '-mesg': '',
                      '-l': '0', '-p': 'Passphrase'},
    },
    'SETDESC Please enter the passphrase for the ssh key%0A  ke:yf:in:ge:rp:ri:nt %22<email@yhoo.com>%22': {
        'out': 'OK',
        'rofi_args': {'-dmenu': '', '-input': '/dev/null', '-password': '', '-disable-history': '',
                      '-mesg': 'Please enter the passphrase for the ssh key\r'
                               '  ke:yf:in:ge:rp:ri:nt &quot;&lt;email@yhoo.com&gt;&quot;',
                      '-l': '0', '-p': 'Passphrase'},
    },
    'GETPIN': {
        'out': 'OK',
        'rofi_args': {'-dmenu': '', '-input': '/dev/null', '-password': '', '-disable-history': '',
                      '-mesg': 'Please enter the passphrase for the ssh key\r'
                               '  ke:yf:in:ge:rp:ri:nt &quot;&lt;email@yhoo.com&gt;&quot;',
                      '-l': '0', '-p': 'Passphrase'},
    },
    'SETERROR Bad Passphrase (try 2 of 3)': {
        'out': 'OK',
        'rofi_args': {'-dmenu': '', '-input': '/dev/null', '-password': '', '-disable-history': '',
                      '-mesg': 'Bad Passphrase (try 2 of 3)\r***************************\r'
                               'Please enter the passphrase for the ssh key\r'
                               '  ke:yf:in:ge:rp:ri:nt &quot;&lt;email@yhoo.com&gt;&quot;',
                      '-l': '0', '-p': 'Passphrase'},
    },
    'SETKEYINFO': {'out': 'OK'},
    'BYE': {'out': 'OK'},
    'error': {'out': 'BYE'},
}


def test_pinenntry(capsys):
    rofi_args = rofi_init_args.copy()
    for request, etalon in assuan_action_mapping.items():
        action, arg = handle_request(request)
        # with pytest.raises(SystemExit):
        try:
            rofi_args = handle_command(action, arg, rofi_args, is_test=True)
        except SystemExit:
            pass
        if etalon_rofi_args := etalon.get('rofi_args'):
            assert etalon_rofi_args == rofi_args
        captured = capsys.readouterr()
        assert f"{etalon['out']}\n" == captured.out, f'Error in request: {request}'


def test_args(mocker):
    etalon_rofi_args = {'-dmenu': '', '-input': '/dev/null', '-password': '', '-disable-history': '', '-mesg': '',
                        '-l': '0', '-display': ':1', '-p': 'custom_prompt'}
    mocker.patch(
        "sys.argv",
        [
            "pinentry_rofi.py",
            "--display",
            ":1",
            "--prompt",
            "custom_prompt",
        ],
    )

    test_arg_parser = argparse.ArgumentParser('pinentry_rofi.py')
    add_args(test_arg_parser)
    rofi_args = handle_args(test_arg_parser)

    assert etalon_rofi_args == rofi_args


def test_env_args(mocker):
    etalon_rofi_args = {'-dmenu': '', '-input': '/dev/null', '-password': '', '-disable-history': '', '-mesg': '',
                        '-l': '0', '-display': ':1', '-p': 'custom_prompt'}
    os.environ['DISPLAY'] = ':1'
    os.environ['PINENTRY_USER_DATA'] = 'custom_prompt'
    mocker.patch("sys.argv", ["pinentry_rofi.py"])

    test_arg_parser = argparse.ArgumentParser('pinentry_rofi.py')
    add_args(test_arg_parser)
    rofi_args = handle_args(test_arg_parser)

    assert etalon_rofi_args == rofi_args
