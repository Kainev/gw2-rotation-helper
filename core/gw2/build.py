import base64
import re

from .api import get_skill, get_profession


class Build(object):
    def __init__(self, code=None):
        self.profession_template = 1
        self.specializations_template = [
            {'id': 0, 'traits': [0, 0, 0]},
            {'id': 0, 'traits': [0, 0, 0]},
            {'id': 0, 'traits': [0, 0, 0]}
        ]
        self.skills_template = {
            'terrestrial': {'heal': 0, 'utilities': [0, 0, 0], 'elite': 0},
            'aquatic': {'heal': 0, 'utilities': [0, 0, 0], 'elite': 0}
        }
        self.specific_template = [0] * 16

        self.profession = None
        self.specializations = None
        self.skills = {
            'terrestrial': {'heal': None, 'utilities': [None, None, None], 'elite': None},
            'aquatic': {'heal': None, 'utilities': [None, None, None], 'elite': None}
        }
        self.specific = None

        if code:
            self.parse(code)

    def parse(self, code):
        chat_code_regex = r"\[&([A-Za-z0-9+/=]+)\]"
        match = re.match(chat_code_regex, code)
        if match and len(match.groups()) == 1:
            byte_string = base64.b64decode(match.group(1))
            bytes_ = list(byte_string)

            if len(bytes_) > 0 and bytes_[0] != 0x0D:
                raise ValueError("Wrong header type")
            elif len(bytes_) >= 44:
                self.profession_template = bytes_[1]

                for s in range(3):
                    offset = s * 2
                    self.specializations_template[s]['id'] = bytes_[offset + 2]
                    for t in range(3):
                        self.specializations_template[s]['traits'][t] = (bytes_[offset + 3] >> (t * 2)) & 0x03

                self.skills_template['terrestrial']['heal'] = bytes_[8] + (bytes_[9] << 8)
                self.skills_template['aquatic']['heal'] = bytes_[10] + (bytes_[11] << 8)

                for u in range(3):
                    offset = u * 4 + 12
                    self.skills_template['terrestrial']['utilities'][u] = bytes_[offset] + (bytes_[offset + 1] << 8)
                    self.skills_template['aquatic']['utilities'][u] = bytes_[offset + 2] + (bytes_[offset + 3] << 8)

                self.skills_template['terrestrial']['elite'] = bytes_[24] + (bytes_[25] << 8)
                self.skills_template['aquatic']['elite'] = bytes_[26] + (bytes_[27] << 8)

                self.specific_template = bytes_[28:]

                # Load skill information directly into self.skills
                self.load_skill_info()
            else:
                raise ValueError("Invalid build template")
        else:
            raise ValueError("Invalid format")

    def load_skill_info(self):
        profession_data = get_profession()
        profession = profession_data[self.profession_template]

        if not profession:
            raise ValueError("Profession not found")

        skill_palette = {pair[0]: pair[1] for pair in profession['skills_by_palette']}

        def get_skill(skill_id):
            return get_skill(skill_palette[skill_id]) if skill_id in skill_palette else None

        self.skills['terrestrial']['heal'] = get_skill(self.skills_template['terrestrial']['heal'])
        self.skills['aquatic']['heal'] = get_skill(self.skills_template['aquatic']['heal'])

        for idx, util_id in enumerate(self.skills_template['terrestrial']['utilities']):
            self.skills['terrestrial']['utilities'][idx] = get_skill(util_id)
        for idx, util_id in enumerate(self.skills_template['aquatic']['utilities']):
            self.skills['aquatic']['utilities'][idx] = get_skill(util_id)

        self.skills['terrestrial']['elite'] = get_skill(self.skills_template['terrestrial']['elite'])
        self.skills['aquatic']['elite'] = get_skill(self.skills_template['aquatic']['elite'])

        self.profession = self.profession_template
        self.specializations = self.specializations_template
        self.specific = self.specific_template

    def to_string(self):
        retval = [0x0D, self.profession_template]

        for s in range(3):
            retval.append(self.specializations_template[s]['id'])
            retval.append(self.specializations_template[s]['traits'][2] << 4 |
                          self.specializations_template[s]['traits'][1] << 2 |
                          self.specializations_template[s]['traits'][0])

        retval.extend([self.skills_template['terrestrial']['heal'] & 0xFF,
                       self.skills_template['terrestrial']['heal'] >> 8 & 0xFF])
        retval.extend(
            [self.skills_template['aquatic']['heal'] & 0xFF, self.skills_template['aquatic']['heal'] >> 8 & 0xFF])

        for u in range(3):
            retval.extend([self.skills_template['terrestrial']['utilities'][u] & 0xFF,
                           self.skills_template['terrestrial']['utilities'][u] >> 8 & 0xFF])
            retval.extend([self.skills_template['aquatic']['utilities'][u] & 0xFF,
                           self.skills_template['aquatic']['utilities'][u] >> 8 & 0xFF])

        retval.extend([self.skills_template['terrestrial']['elite'] & 0xFF,
                       self.skills_template['terrestrial']['elite'] >> 8 & 0xFF])
        retval.extend(
            [self.skills_template['aquatic']['elite'] & 0xFF, self.skills_template['aquatic']['elite'] >> 8 & 0xFF])

        retval.extend(self.specific_template)

        return "[&" + base64.b64encode(bytes(retval)).decode('utf-8') + "]"

# class Build(object):
#     def __init__(self, code=None):
#         self.profession = 1
#         self.specializations = [
#             {'id': 0, 'traits': [0, 0, 0]},
#             {'id': 0, 'traits': [0, 0, 0]},
#             {'id': 0, 'traits': [0, 0, 0]}
#         ]
#         self.skills = {
#             'terrestrial': {'heal': 0, 'utilities': [0, 0, 0], 'elite': 0},
#             'aquatic': {'heal': 0, 'utilities': [0, 0, 0], 'elite': 0}
#         }
#         self.specific = [0] * 16
#
#         if code:
#             self.parse(code)
#
#     def parse(self, code):
#         chat_code_regex = r"\[&([A-Za-z0-9+/=]+)\]"
#         match = re.match(chat_code_regex, code)
#         if match and len(match.groups()) == 1:
#             byte_string = base64.b64decode(match.group(1))
#             bytes_ = list(byte_string)
#
#             if len(bytes_) > 0 and bytes_[0] != 0x0D:
#                 raise ValueError("Wrong header type")
#             elif len(bytes_) >= 44:
#                 self.profession = bytes_[1]
#
#                 for s in range(3):
#                     offset = s * 2
#                     self.specializations[s]['id'] = bytes_[offset + 2]
#                     for t in range(3):
#                         self.specializations[s]['traits'][t] = (bytes_[offset + 3] >> (t * 2)) & 0x03
#
#                 self.skills['terrestrial']['heal'] = bytes_[8] + (bytes_[9] << 8)
#                 self.skills['aquatic']['heal'] = bytes_[10] + (bytes_[11] << 8)
#
#                 for u in range(3):
#                     offset = u * 4 + 12
#                     self.skills['terrestrial']['utilities'][u] = bytes_[offset] + (bytes_[offset + 1] << 8)
#                     self.skills['aquatic']['utilities'][u] = bytes_[offset + 2] + (bytes_[offset + 3] << 8)
#
#                 self.skills['terrestrial']['elite'] = bytes_[24] + (bytes_[25] << 8)
#                 self.skills['aquatic']['elite'] = bytes_[26] + (bytes_[27] << 8)
#
#                 self.specific = bytes_[28:]
#             else:
#                 raise ValueError("Invalid build template")
#         else:
#             raise ValueError("Invalid format")
#
#     def to_string(self):
#         retval = [0x0D, self.profession]
#
#         for s in range(3):
#             retval.append(self.specializations[s]['id'])
#             retval.append(self.specializations[s]['traits'][2] << 4 |
#                           self.specializations[s]['traits'][1] << 2 |
#                           self.specializations[s]['traits'][0])
#
#         retval.extend([self.skills['terrestrial']['heal'] & 0xFF, self.skills['terrestrial']['heal'] >> 8 & 0xFF])
#         retval.extend([self.skills['aquatic']['heal'] & 0xFF, self.skills['aquatic']['heal'] >> 8 & 0xFF])
#
#         for u in range(3):
#             retval.extend([self.skills['terrestrial']['utilities'][u] & 0xFF, self.skills['terrestrial']['utilities'][u] >> 8 & 0xFF])
#             retval.extend([self.skills['aquatic']['utilities'][u] & 0xFF, self.skills['aquatic']['utilities'][u] >> 8 & 0xFF])
#
#         retval.extend([self.skills['terrestrial']['elite'] & 0xFF, self.skills['terrestrial']['elite'] >> 8 & 0xFF])
#         retval.extend([self.skills['aquatic']['elite'] & 0xFF, self.skills['aquatic']['elite'] >> 8 & 0xFF])
#
#         retval.extend(self.specific)
#
#         return "[&" + base64.b64encode(bytes(retval)).decode('utf-8') + "]"
