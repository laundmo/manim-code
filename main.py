from manim import Scene

from code_replacement import ReplacementCode


class CodeFromString(Scene):
    def construct(self):

        with ReplacementCode(
            self,
            """\
            def my_function(x):
                r = x + 2
                return r
            
            y = my_function(5)
            print(y)
        """,
        ) as r:
            r.show_from_regex(r"y = my_function\((5)\)", r"def my_function\((x)\):")
            r.show_from_regex(r"def my_function\((5)\):", r"    r \= (x) \+ 2")
        with ReplacementCode(
            self,
            """\
            def my_function(5):
                r = 7
                return r
            
            y = my_function(5)
            print(y)
        """,
        ) as r:
            r.show_from_regex(r"    r \= (7)", r"    (r) \= 7")
            r.show_from_regex(r"    (7) \= 7", r"    return (r)")
            r.show_from_regex(r"    return (7)", r"y = (my_function\(5\))")
            r.show_from_regex(r"y = (7)", r"(y) = 7")
