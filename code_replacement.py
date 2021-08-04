import re
from textwrap import dedent
from string_editor import LineColEditor

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Code,
    Create,
    CurvedArrow,
    CyclicReplace,
    FadeOut,
    Scene,
    SurroundingRectangle,
    Uncreate,
)


def regex_line_span(regex, string, group=1):
    m = re.search(regex, string)
    lineno = string.count("\n", 0, m.start(group))
    lines = string.split("\n")
    previous_line_chars = sum(map(len, lines[0:lineno])) + len(lines[0:lineno]) - 1

    char_start = (m.start(group) - 1) - previous_line_chars
    char_stop = char_start + ((m.end(group) - 1) - (m.start(group) - 1))
    return m, lineno, (char_start, char_stop)

class sliceabledict(dict):
    def __getitem__(self, val):
        if isinstance(val, slice):
            return slice(self[val.start], self[val.stop])
        return super().__getitem__(val)

def make_manim_map(string):
    stripped = re.findall("( +|[^ ])", string)
    char_manim_map = {}
    count = 0
    for i, c in enumerate(stripped):
        for j, _ in enumerate(c):
            char_manim_map[count + j] = i
        count += len(c)
    return sliceabledict(char_manim_map)

def mid(a: int, b: int) -> int:
    return a + (abs(a - b) / 2)

class ReplacementCode:

    COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FF00FF", "#FFFF00", "#00FFFF"]

    def __init__(self, scene, code):
        self.scene = scene
        self.code = None
        self.color_index = 0
        self.update(code.replace("\n", " \n"))

    @property
    def color(self):
        col = self.COLORS[self.color_index % len(self.COLORS)]
        self.color_index += 1
        return col
    
    def update(self, code):
        if self.code:
            self.scene.remove(self.code)
        self.code = Code(
            code=dedent(code),
            scale_factor=1,
            tab_width=4,
            language="Python",
            font="Monospace",
            line_spacing=0.6,
        )
        self.scene.add(self.code)
    
    def normalise_col(self, *args):
        return [(arg, arg + 1) if isinstance(arg, int) else arg for arg in args]

    def decide_directions(self, source_line, source_col, dest_line, dest_col): 
        source_col, dest_col = self.normalise_col(source_col, dest_col)
        
        linediff = source_line - dest_line
        coldiff = mid(*source_col) - mid(*dest_col)

        if abs(linediff) > abs(coldiff):
            if linediff > 0:
                direction = (DOWN, UP)
            else:
                direction = (UP, DOWN)
        else:
            if coldiff > 0:
                direction = (RIGHT, LEFT)
            else:
                direction = (LEFT, RIGHT)
        
        return direction

    def show_from_spans(self, source_line, source_col, dest_line, dest_col):
        source_col, dest_col = self.normalise_col(source_col, dest_col)
        direction = self.decide_directions(source_line, source_col, dest_line, dest_col)
        lines = LineColEditor(self.code.code_string)
        
        source_manim_map = make_manim_map(lines[source_line])
        dest_manim_map = make_manim_map(lines[dest_line])
        
        
        self.show_and_replace(
            self.code.code.chars[source_line][
                source_manim_map[slice(*source_col)]
            ],
            self.code.code.chars[dest_line][
                dest_manim_map[slice(*dest_col)]
            ],
            direction,
            color=self.color,
        )
        self.color_index += 1
        
        lines = LineColEditor(self.code.code_string)
        lines[dest_line][slice(*dest_col)] = lines[source_line][slice(*source_col)]
        self.update(str(lines))
        
    def show_from_regex(self, source_re, dest_re, alternative_dest=None):
        source_match, source_line, span = regex_line_span(
            source_re, self.code.code_string
        )
        dest_match, dest_line, span2 = regex_line_span(dest_re, self.code.code_string)

        direction = self.decide_directions(source_line, span, dest_line, span2)

        self.show_from_spans(source_line, span, dest_line, span2)

    def from_to_chars(self, chars1, chars2, direction, color="#FFFFFF"):
        rect1 = SurroundingRectangle(chars1, color=color)
        rect2 = SurroundingRectangle(chars2, color=color)
        arrow = CurvedArrow(
            rect1.get_edge_center(direction[1]),
            rect2.get_edge_center(direction[0]),
            color=color,
        )
        self.scene.play(Create(rect1), Create(rect2), Create(arrow))
        self.scene.wait(2)
        return (Uncreate(rect1), Uncreate(rect2), Uncreate(arrow))

    def show_and_replace(self, chars1, chars2, direction, color="#FFFFFF", run_time=2):
        uncreate = self.from_to_chars(chars1, chars2, direction, color=color)

        self.scene.play(
            CyclicReplace(
                chars1.copy(),
                chars2,
                run_time=run_time,
            ),
            FadeOut(chars2),
            *uncreate
        )

    def __enter__(self):
        return self

    def __exit__(self, *arg):
        if self.code:
            self.scene.remove(self.code)
