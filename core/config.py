import configparser

_raw_controls = None
controls = None
resolution = None
rotation_file_path = None


def load():
    config = configparser.ConfigParser()
    config.read('settings.ini')

    if 'Controls' in config:
        global controls
        global _raw_controls
        _raw_controls = config['Controls']
        controls = [_parse_controls(key, value) for key, value in config['Controls'].items()]

    if 'Resolution' in config:
        global resolution
        resolution = [config.getint('Resolution', 'width'), config.getint('Resolution', 'height')]

    if 'Settings' in config:
        global rotation_file_path
        rotation_file_path = config['Settings'].get('rotation_file_path', None)


def save():
    config = configparser.ConfigParser()

    if _raw_controls is not None:
        config['Controls'] = _raw_controls

    if resolution is not None:
        config['Resolution'] = {'width': str(resolution[0]), 'height': str(resolution[1])}

    if rotation_file_path is not None:
        config['Settings'] = {'rotation_file_path': rotation_file_path}

    with open('settings.ini', 'w') as configfile:
        config.write(configfile)


class Control:
    def __init__(self, name, modifiers, key):
        self.name = name
        self.modifiers = modifiers
        self.scan_codes = key


def _parse_controls(name, hotkey_string):
    import keyboard

    modifiers = set()
    scan_codes = None

    for key in hotkey_string.split("+"):
        if key in {"ctrl", "shift", "alt", "cmd"}:
            modifiers.add(key)
        else:
            scan_codes = keyboard.key_to_scan_codes(key)

    return Control(name, modifiers, scan_codes)

# def _parse_hotkey(hotkey_string):
#     from pynput.keyboard import Key, KeyCode
#
#     modifiers = {
#         'ctrl': Key.ctrl,
#         'alt': Key.alt,
#         'shift': Key.shift,
#         'cmd': Key.cmd
#     }
#
#     keys = hotkey_string.lower().split('+')
#     parsed_keys = []
#
#     for key in keys:
#         if key in modifiers:
#             parsed_keys.append(modifiers[key])
#         elif hasattr(Key, key):
#             parsed_keys.append(getattr(Key, key))
#         else:
#             parsed_keys.append(KeyCode.from_char(key).vk)
#
#     return set(parsed_keys)
