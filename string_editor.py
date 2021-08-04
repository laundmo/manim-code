
from werkzeug.local import LocalProxy

class EditableString(str):
    def __init__(self, string):
        self.string = string
    
    def __getitem__(self, key):
        return self.string[key]
    
    def __setitem__(self, key, value):
        l = list(self.string)
        l[key] = value
        self.string = "".join(l)
        return self.string
    
    def replace(self, pattern, replacement):
        return EditableString(self.string.replace(pattern, replacement))
    
    def __getattr__(self, name):
        try:
            return getattr(self, name)
        except AttributeError:
            return getattr(getattr(self, "string"), name)
    
    def __str__(self):
        return self.string
    
    def __add__(self, o):
        return EditableString(self.string.__add__(o))

    def __contains__(self, o) -> bool:
        return self.string.__contains__(o)
    
    def __eq__(self, o) -> bool:
        return self.string.__eq__(o)
    
    def __format__(self, format_spec: str) -> str:
        return EditableString(self.string.__format__(format_spec))
    
    def __ge__(self, o) -> bool:
        return self.string.__ge__(o)
    
    def __gt__(self, o) -> bool:
        return self.string.__gt__(o)
    
    def __iter__(self) -> iter:
        return self.string.__iter__()
    
    def __le__(self, o) -> bool:
        return self.string.__le__(o)
    
    def __len__(self) -> int:
        return len(self.string)
    
    def __lt__(self, o) -> bool:
        return self.string.__lt__(o)
    
    def __mod__(self, o):
        return self.string.__mod__(o)
    
    def __mul__(self, o):
        return EditableString(self.string.__mul__(o))
    
    def __ne__(self, o) -> bool:
        return self.string.__ne__(o)
    
    def __repr__(self) -> str:
        return f"<EditableString '{self.string}'>"
    
    def __rmod__(self, o):
        return self.string.__rmod__(o)
    
    def __rmul__(self, o):
        return self.string.__rmul__(o)


class LineColEditor():
    def __init__(self, string):
        self.lines = [EditableString(s) for s in string.split("\n")]
    
    def __str__(self) -> str:
        return "\n".join(map(str, self.lines))

    def __getitem__(self, index) -> EditableString:
        return self.lines[index]

if __name__ == "__main__":
    s = LineColEditor("""
def test(f):
    f = 1
test(1)
    """)
    s[2][4:5] = "yooooo"
    print(s)