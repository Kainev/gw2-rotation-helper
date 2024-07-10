GW2_WINDOW_TITLE = 'Guild Wars 2'
GW2RH_WINDOW_TITLE = 'Guild Wars 2 Rotation Helper'

_BASE_ACTION_HIGHLIGHTS = {
    'weapon_skill_1': [955, 1365, 54, 54],
    'weapon_skill_2': [1011, 1365, 54, 54],
    'weapon_skill_3': [1066, 1365, 53, 53],
    'weapon_skill_4': [1121, 1365, 54, 54],
    'weapon_skill_5': [1176, 1365, 54, 54],
    'healing_skill': [1330, 1365, 53, 54],
    'utility_skill_1': [1385, 1365, 54, 53],
    'utility_skill_2': [1440, 1365, 54, 54],
    'utility_skill_3': [1495, 1365, 53, 54],
    'elite_skill': [1550, 1365, 53, 54],
    'swap_weapons': [914, 1365, 39, 40],
    'profession_skill_1': [1028, 1296, 40, 40],
    'profession_skill_2': [1078, 1296, 40, 40],
    'profession_skill_3': [1128, 1296, 40, 40],
}

ACTION_HIGHLIGHTS = {}

_ACTION_HIGHLIGHTS_BASE_RESOLUTION = [2560, 1440]

ACTION_NAMES = list(ACTION_HIGHLIGHTS.keys())


def calculate_highlight_regions(width, height, beastmode):
    width_ratio = _ACTION_HIGHLIGHTS_BASE_RESOLUTION[0] / width
    height_ratio = _ACTION_HIGHLIGHTS_BASE_RESOLUTION[1] / height

    global ACTION_HIGHLIGHTS
    ACTION_HIGHLIGHTS = {
        key: [
            _BASE_ACTION_HIGHLIGHTS[key][0] * width_ratio,
            _BASE_ACTION_HIGHLIGHTS[key][1] * height_ratio,
            _BASE_ACTION_HIGHLIGHTS[key][2] * width_ratio,
            _BASE_ACTION_HIGHLIGHTS[key][3] * height_ratio
        ] for key in _BASE_ACTION_HIGHLIGHTS.keys()
    }
