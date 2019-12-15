import argparse
from enum import Enum
import os
from PIL import Image, ImageDraw, ImageFont
import re
import sys

from pagifier import get_layout, Sheet, Spread, NO_CONTENT

# Top level formatting
DEFAULT_DPI = 300

WIDTH_INCHES = 4.25
FOOTER_HEIGHT_INCHES = 0.5
TOTAL_HEIGHT_INCHES = 5.5
PADDING_INCHES = 0.2125

WIDTH = int(WIDTH_INCHES * DEFAULT_DPI)
FOOTER_HEIGHT = int(FOOTER_HEIGHT_INCHES * DEFAULT_DPI)
TOTAL_HEIGHT = int(TOTAL_HEIGHT_INCHES * DEFAULT_DPI)
PADDING = int(PADDING_INCHES * DEFAULT_DPI)

FILE_REGEX = r"^(\d+)_(?P<author>.*)\.(?P<extension>png|jpeg|jpg)$"


class Style(Enum):
    REGULAR = 0
    BOLD = 1
    ITALIC = 2


class Helvetica:
    ttf = {
        Style.REGULAR: "assets/helvetica.ttf",
        Style.BOLD: "assets/helvetica_bold.ttf",
        Style.ITALIC: "assets/helvetica_italic.ttf",
    }

    def __init__(self, style: Style, size: int):
        self.truetype = ImageFont.truetype(self.ttf[style], size)


def right_align(image, text: str, style: Style, size: int, right_padding: int, bottom_padding: int):
    draw = ImageDraw.Draw(image)
    font = Helvetica(style, size).truetype
    textw, texth = draw.textsize(text, font)
    texth = size
    imgw, imgh = image.size
    draw.text((imgw - (textw + right_padding), imgh - (texth + bottom_padding)), text, font=font, fill="black")


def left_align(image, text: str, style: Style, size: int, left_padding: int, bottom_padding: int):
    draw = ImageDraw.Draw(image)
    font = Helvetica(style, size).truetype
    textw, texth = draw.textsize(text, font)
    texth = size
    imgw, imgh = image.size
    draw.text((left_padding, imgh - (texth + bottom_padding)), text, font=font, fill="black")


def layout_page(image_path, page, left_page, file_format=None, width=WIDTH, height=TOTAL_HEIGHT, footer_height=FOOTER_HEIGHT, padding=PADDING):
    match = re.match(FILE_REGEX, os.path.basename(image_path))
    author = match.group("author")
    body_height = height

    img = Image.new("RGB", (width, height), color = (255, 255, 255))
    page_string = str(page) if page > 0 else ""
    if left_page:
        left_align(img, page_string, Style.BOLD, 48, padding, padding)
        right_align(img, author, Style.ITALIC, 48, padding, padding)
    else:
        right_align(img, page_string, Style.BOLD, 48, padding, padding)
        left_align(img, author, Style.ITALIC, 48, padding, padding)

    if page_string or author:
        body_height -= footer_height

    content = Image.open(image_path)
    cw, ch = content.size
    max_width = width - 2 * padding
    max_height = body_height - padding
    width_ratio = cw / max_width
    height_ratio = ch / max_height
    if width_ratio > height_ratio:
        cw /= width_ratio
        ch /= width_ratio
    else:
        cw /= height_ratio
        ch /= height_ratio
    cw, ch = int(cw), int(ch)

    content = content.resize((cw, ch))
    midw = max_width // 2
    midh = max_height // 2
    coord = padding + midw - (cw // 2), padding + midh - (ch // 2)
    img.paste(content, box=coord)
    if isinstance(file_format, str):
        img.save(file_format.format(page))
    return img


def create_sheet(spreads: tuple, sheet_width: int, sheet_height: int):
    img = Image.new("RGB", (sheet_width, sheet_height), color=(255, 255, 255))
    num_spreads = len(spreads)
    spread_height = sheet_height // num_spreads
    for i, spread in enumerate(spreads):
        num_pages = len(spread)
        page_width = sheet_width // num_pages
        y_pos = i * spread_height
        for j, page in enumerate(spread):
            if page is not None:
                x_pos = j * page_width
                img.paste(page, box=(x_pos, y_pos, x_pos + page_width, y_pos + spread_height))
    return img

def layout_spread(img_files, spread, offset, file_format=None):
    left_layout = None
    right_layout = None
    if spread.left != NO_CONTENT:
        left_layout = layout_page(image_path=img_files[spread.left], page=spread.left + offset, left_page=True, file_format=file_format)
    if spread.right != NO_CONTENT:
        right_layout = layout_page(image_path=img_files[spread.right], page=spread.right + offset, left_page=False, file_format=file_format)
    return Spread(left=left_layout, right=right_layout)

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--images", type=str, help="Folder containing input images.")
    parser.add_argument("-o", "--outdir", type=str, help="Folder to dump resulting files into.")
    parser.add_argument("-n", "--offset", type=int, default=0, help="Page number for first page in layout.")
    parser.add_argument("-f", "--file_format", type=str, default=None, help="File format for page PNGs. Must contain '{}' for page key.")

    namespace = parser.parse_args(sys.argv[1:])
    img_files = []
    for f in sorted(os.listdir(namespace.images)):
        if re.match(FILE_REGEX, f):
            img_files.append(os.path.join(namespace.images, f))
    
    offset = namespace.offset
    outdir = namespace.outdir
    file_format = os.path.join(outdir, namespace.file_format)

    sheet_img_spreads = []
    for sheet in get_layout(len(img_files), offset=0, per_page=2):
        front = [layout_spread(img_files, spread, offset, file_format) for spread in sheet.front]
        back = [layout_spread(img_files, spread, offset, file_format) for spread in sheet.back]
        sheet_img_spreads.append(Sheet(front=front, back=back))

    sheets = []
    for sheetno, (front, back) in enumerate(sheet_img_spreads):
        # for 
        front_img = create_sheet(front, int(8.5 * DEFAULT_DPI), int(11 * DEFAULT_DPI))
        back_img = create_sheet(back, int(8.5 * DEFAULT_DPI), int(11 * DEFAULT_DPI))
        sheets += [front_img, back_img]

    if sheets:
        sheets[0].save(os.path.join(namespace.outdir, "sheets.pdf"))
        for sheet in sheets[1:]:
            sheet.save(os.path.join(namespace.outdir, "sheets.pdf"), append=True)
    else:
        print("No sheet PDF generated...")
        

if __name__ == "__main__":
    main(sys.argv)
