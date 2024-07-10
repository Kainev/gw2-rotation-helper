import base64
import re


class Template:
    def __init__(self, build_template=None):
        self._build_template = None  # initialized in self._parse

        self.profession = 0

        self.skills = {
            'terrestrial': {
                'healing_skill': 0,
                'utility_skill_1': 0,
                'utility_skill_2': 0,
                'utility_skill_3': 0,
                'elite_skill': 0
            },
            'aquatic': {
                'healing_skill': 0,
                'utility_skill_1': 0,
                'utility_skill_2': 0,
                'utility_skill_3': 0,
                'elite_skill': 0
            },
        }

        self.specializations = [
            {'id': 0, 'traits': [0, 0, 0]},
            {'id': 0, 'traits': [0, 0, 0]},
            {'id': 0, 'traits': [0, 0, 0]}
        ]

        self.specific = [0] * 16

        if build_template:
            self._parse(build_template)

    @property
    def build_template(self):
        self._build_template = self.to_string()
        return self._build_template

    @build_template.setter
    def build_template(self, template):
        self._parse(template)

    def _parse(self, build_template):
        chat_code_regex = r"\[&([A-Za-z0-9+/=]+)\]"
        match = re.match(chat_code_regex, build_template)

        if not match or len(match.groups()) != 1:
            raise ValueError("Invalid Format")

        bytes_ = list(base64.b64decode(match.group(1)))

        if len(bytes_) > 0 and bytes_[0] != 0x0D:
            raise ValueError("Unsupported Header")

        if len(bytes_) < 44:
            raise ValueError("Invalid Build Template")

        self.profession = bytes_[1]

        for specialization_index in range(3):
            offset = specialization_index * 2
            traits = [(bytes_[offset + 3] >> (trait_index * 2)) & 0x03 for trait_index in range(3)]

            self.specializations[specialization_index]['id'] = bytes_[offset + 2]
            self.specializations[specialization_index]['traits'] = traits

        self.skills['terrestrial']['healing_skill'] = bytes_[8] + (bytes_[9] << 8)
        self.skills['aquatic']['healing_skill'] = bytes_[10] + (bytes_[11] << 8)

        for utility_index in range(3):
            offset = utility_index * 4 + 12
            self.skills['terrestrial']['utilities'][utility_index] = bytes_[offset] + (bytes_[offset + 1] << 8)
            self.skills['aquatic']['utilities'][utility_index] = bytes_[offset + 2] + (bytes_[offset + 3] << 8)

        self.skills['terrestrial']['elite'] = bytes_[24] + (bytes_[25] << 8)
        self.skills['aquatic']['elite'] = bytes_[26] + (bytes_[27] << 8)

        self.specific = bytes_[28:]

        self._build_template = build_template

    def to_string(self):
        retval = [0x0D, self.profession]

        for specialization_index in range(3):
            retval.append(self.specializations[specialization_index]['id'])
            retval.append(self.specializations[specialization_index]['traits'][2] << 4 |
                          self.specializations[specialization_index]['traits'][1] << 2 |
                          self.specializations[specialization_index]['traits'][0])

        retval.extend([self.skills['terrestrial']['healing_skill'] & 0xFF,
                       self.skills['terrestrial']['healing_skill'] >> 8 & 0xFF])

        retval.extend([self.skills['aquatic']['healing_skill'] & 0xFF,
                       self.skills['aquatic']['healing_skill'] >> 8 & 0xFF])

        for utility_index in range(3):
            retval.extend([self.skills['terrestrial'][f'utility_skill_{utility_index}'] & 0xFF,
                           self.skills['terrestrial'][f'utility_skill_{utility_index}'] >> 8 & 0xFF])
            retval.extend([self.skills['aquatic'][f'utility_skill_{utility_index}'] & 0xFF,
                           self.skills['aquatic'][f'utility_skill_{utility_index}'] >> 8 & 0xFF])

        retval.extend([self.skills['terrestrial']['elite_skill'] & 0xFF,
                       self.skills['terrestrial']['elite_skill'] >> 8 & 0xFF])

        retval.extend([self.skills['aquatic']['elite_skill'] & 0xFF,
                       self.skills['aquatic']['elite_skill'] >> 8 & 0xFF])

        retval.extend(self.specific)

        return "[&" + base64.b64encode(bytes(retval)).decode('utf-8') + "]"
