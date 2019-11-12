import argparse
from collections import namedtuple
import math
import sys

PAGE_HEADER = "SHEET {}: {}"
PAGE_ROW = (
"""+-----+-----+
| {} | {} |""")
PAGE_BOTTOM = "+-----+-----+"
NO_CONTENT = "X"


Sheet = namedtuple("Sheet", ["front", "back"])
Spread = namedtuple("Spread", ["left", "right"])


def pad_to_n(s, n):
    s = str(s)
    padding = " " * (n - len(s))
    return s + padding


def thresh(num, thresh):
    if num < thresh:
        return num
    return NO_CONTENT


def round_up(n, base=1):
    return int(base * math.ceil(n / float(base)))


def get_layout(content_n, offset, per_page):
    pages_n = round_up(content_n, 4)
    fronts = [[NO_CONTENT, NO_CONTENT] for _ in range(round_up((pages_n // 4), per_page))]
    backs = [[NO_CONTENT, NO_CONTENT] for _ in range(round_up((pages_n // 4), per_page))]
    for i in range(pages_n // 2):
        if i % 2 == 0:
            left, right = pages_n - (i + 1), i
            if left < content_n:
                fronts[i // 2][0] = left + offset
            if right < content_n:
                fronts[i // 2][1] = right + offset
        else:
            left, right = i, pages_n - (i + 1)
            if left < content_n:
                backs[i // 2][0] = left + offset
            if right < content_n:
                backs[i // 2][1] = right + offset
    pages = []
    for i in range(0, len(fronts), per_page):
        front = tuple([Spread(*fronts[j]) for j in range(i, i + per_page)])
        back = tuple([Spread(*backs[j]) for j in range(i, i + per_page)])
        pages.append(Sheet(front, back))
    return pages


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", "-p", type=int)
    parser.add_argument("--offset", "-o", type=int, default=0)
    parser.add_argument("--spreads_per_sheet", "-s", type=int, default=2)
    namespace = parser.parse_args(sys.argv[1:])
    pages = get_layout(namespace.pages, namespace.offset, namespace.spreads_per_sheet)
    for page in pages:
        print(page)
    for index, (front, back) in enumerate(pages):
        print()
        print(PAGE_HEADER.format(index, "FRONT"))
        for row in front:
            print(PAGE_ROW.format(pad_to_n(row[0], 3), pad_to_n(row[1], 3)))
        print(PAGE_BOTTOM)
        print()
        print(PAGE_HEADER.format(index, "BACK"))
        for row in back:
            print(PAGE_ROW.format(pad_to_n(row[0], 3), pad_to_n(row[1], 3)))
        print(PAGE_BOTTOM)