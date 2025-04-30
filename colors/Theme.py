import re
from re import Match
from typing import Callable

from colors.Color import Color


class Theme:

    def __init__(self, colors, color_roles:dict[str, Color]):
        self.keys = [Color.from_hex(x) for x in colors]
        self.roles = {x: Color.from_hex(y) for x,y in  color_roles.items()}

    FUNCTIONS = {
        "HUE_SHIFT": Color.hue_shift,
        "LERP": Color.lerp,
        "TINT": Color.tint,
        "SHADE": Color.shade,
        "COMPLEMENTARY": Color.complementary,
        "TRIADIC": Color.triadic,
        "TETRADIC": Color.tetradic,
        "ANALOGOUS": Color.analogous
    }

    def process_template(self, template: str) -> str:
        def p(s: str) -> list:
            return [float(x) for x in s.split(',') if x.strip()]

        def lam(func):
            return lambda match: str(func(Color.from_rgb(*p(match.group(1))),*p(match.group(2))).rgb).strip("[]")

        # A function to map regex patterns to replacement functions
        match_to_func: dict[re.Pattern, Callable] = {}

        for name, f in self.FUNCTIONS.items():
            match_to_func[re.compile(r'(\d+, ?\d+, ?\d+)\.' + name + r'\((.*?)\)')] = lam(f)

        # This pattern is for matching ROLE(role_name)
        match_to_func[re.compile(r'ROLE\((\w+)\)')] = lambda match: str(self.roles.get(match.group(1)).rgb).strip("[]")
        change = True
        while change:
            change = False
            for pattern, f in match_to_func.items():
                new_template = pattern.sub(f, template)
                new_template= re.sub(r'#.*$', '0,0,0;', new_template, flags=re.MULTILINE)
                if new_template != template:
                    change = True
                    template = new_template
        return template