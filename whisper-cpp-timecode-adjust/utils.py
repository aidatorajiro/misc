def to_timecode(x: float):
    h = x // 3600
    x -= h * 3600
    m = x // 60
    x -= m * 60
    s = int(x)
    x -= s
    return (int(h), int(m), s, x)

def from_timecode(tc: tuple[int, int, int, float]):
    (h, m, s, x) = tc
    return h * 3600 + m * 60 + s + x

def print_timecode(tc: tuple[int, int, int, float]):
    print("≫≫≫{}hour{}min{}sec.{}".format(tc[0], tc[1], tc[2], int(tc[3] * 1000)))