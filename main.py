from math import sqrt
from os import makedirs, path
import re
from shutil import rmtree
from requests import get
import fitz

type WordBlock = tuple[int, int, int, int, str, int, int, int]
type Box = tuple[int, int, int, int]


def download_pdf(url: str, save_path: str) -> None:
    response = get(url)
    with open(save_path, "wb") as pdf_file:
        pdf_file.write(response.content)


def box_distance(a: Box, b: Box) -> int:
    (ax0, ay0, ax1, ay1) = a
    (bx0, by0, bx1, by1) = b
    dx = (bx1 + (bx1 - bx0) / 2) - (ax1 + (ax1 - ax0) / 2)
    dy = (by1 + (by1 - by0) / 2) - (ay1 + (ay1 - ay0) / 2)
    return sqrt(dx * dx + dy * dy)


def get_step(page: fitz.Page, word_block: WordBlock) -> int:
    closest = None
    closest_dist = None
    for (
        x0,
        y0,
        x1,
        y1,
        word,
        block_no,
        line_no,
        word_no,
    ) in page.get_textpage().extractWORDS():
        height = round(y1 - y0)
        dist = box_distance(
            (word_block[0], word_block[1], word_block[2], word_block[3]),
            (x0, y0, x1, y1),
        )
        if (
            re.match("^\\d+$", word)
            and height == 32
            and (closest_dist == None or dist < closest_dist)
        ):
            closest = word
            closest_dist = dist
    return int(closest)


def get_image(page: fitz.Page, word_block: WordBlock) -> (int, str):
    closest = None
    closest_dist = None
    for (
        xref,
        smask,
        width,
        height,
        bpc,
        colorspace,
        altColorspace,
        name,
        filter,
        referencer,
    ) in page.get_images(full=True):
        bbox = page.get_image_bbox(name)
        dist = box_distance(
            (word_block[0], word_block[1], word_block[2], word_block[3]),
            (bbox.x0, bbox.y0, bbox.x1, bbox.y1),
        )
        if closest_dist == None or dist < closest_dist:
            closest = (xref, name)
            closest_dist = dist
    return closest


def extract_images_from_pdf(pdf_path: str, output_folder: str) -> None:
    document = fitz.open(pdf_path)
    # for page_number in range(document.page_count):
    page_number = 10
    page = document[page_number]
    for word_block in page.get_textpage().extractWORDS():
        (
            x0,
            y0,
            x1,
            y1,
            word,
            block_no,
            line_no,
            word_no,
        ) = word_block
        height = round(y1 - y0)
        if re.match("^\\d+x$", word) and height == 10:
            step = get_step(page, word_block)
            (image_xref, image_name) = get_image(page, word_block)
            extracted_image = document.extract_image(image_xref)
            with open(
                path.join(
                    output_folder,
                    f'{page_number+1}_{step}_{word}_{image_name}.{extracted_image["ext"]}',
                ),
                "wb",
            ) as img_file:
                img_file.write(extracted_image["image"])
            print(step, word, image_name)


def main():
    pdf_url = "https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6429215.pdf"
    pdf_path = ".cache/10305-lions-knights-castle.pdf"
    output_folder = "images"

    rmtree(output_folder)

    makedirs(path.dirname(pdf_path), exist_ok=True)
    makedirs(output_folder)

    if not path.exists(pdf_path):
        download_pdf(pdf_url, pdf_path)
    extract_images_from_pdf(pdf_path, output_folder)


if __name__ == "__main__":
    main()
