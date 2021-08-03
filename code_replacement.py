import re
from textwrap import dedent

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


def make_manim_map(string):
    stripped = re.findall("( +|[^ ])", string)
    char_manim_map = {}
    count = 0
    for i, c in enumerate(stripped):
        for j, _ in enumerate(c):
            char_manim_map[count + j] = i
        count += len(c)
    return char_manim_map


class llist(list):
    def __getitem__(self, index):
        return super().__getitem__(index % len(self))


class ReplacementCode:

    COLORS = llist(["#FF0000", "#00FF00", "#0000FF", "#FF00FF", "#FFFF00", "#00FFFF"])

    def __init__(self, scene, code):
        self.scene = scene
        self.code = None
        self.color_index = 0
        self.update(code.replace("\n", " \n"))

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

    def show_from_regex(self, source_re, dest_re, alternative_dest=None):
        source_match, source_line, span = regex_line_span(
            source_re, self.code.code_string
        )
        dest_match, dest_line, span2 = regex_line_span(dest_re, self.code.code_string)

        linediff = source_line - dest_line
        coldiff = span[0] - span2[0]
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

        st = self.code.code_string
        source_manim_map = make_manim_map(st[source_match.start() : source_match.end()])

        dest_manim_map = make_manim_map(st[dest_match.start() : dest_match.end()])

        self.show_and_replace(
            self.code.code.chars[source_line][
                source_manim_map[span[0]] : source_manim_map[span[1]]
            ],
            self.code.code.chars[dest_line][
                dest_manim_map[span2[0]] : dest_manim_map[span2[1]]
            ],
            direction,
            color=self.COLORS[self.color_index],
        )
        self.color_index += 1

        st = (
            st[: dest_match.start(1)]
            + st[source_match.start(1) : source_match.end(1)]
            + st[dest_match.end(1) :]
        )

        self.update(st)

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
