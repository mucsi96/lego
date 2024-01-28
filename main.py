from math import inf, sqrt
from os import makedirs, path
import re
from shutil import rmtree
from typing import List, Tuple
from requests import get
import fitz

type WordBlock = Tuple[int, int, int, int, str]
type ImageWithBBox = Tuple[int, int, int, int, int, str, str, str, str, int]
type Box = Tuple[int, int, int, int]


def download_pdf(url: str, save_path: str) -> None:
    response = get(url)
    with open(save_path, "wb") as pdf_file:
        pdf_file.write(response.content)


def box_distance(a: Box, b: Box) -> int:
    (ax0, ay0, ax1, ay1) = a
    (bx0, by0, bx1, by1) = b
    gapx = bx0 - ax1 if bx0 > ax0 else ax0 - bx1
    gapy = by0 - ay1 if by0 > ay0 else ay0 - by1
    if gapx < -2 and gapy < -2:
        return inf
    return max(gapx, gapy)


def get_unique_word_positions(page: fitz.Page) -> List[WordBlock]:
    return list(
        set(
            map(
                lambda word: (word[0], word[1], word[2], word[3], word[4]),
                page.get_textpage().extractWORDS(),
            )
        )
    )


def get_images_with_bbox(page: fitz.Page) -> List[ImageWithBBox]:
    return list(
        map(
            lambda image: (
                image[0],
                image[1],
                image[2],
                image[3],
                image[4],
                image[5],
                image[6],
                image[7],
                image[8],
                image[9],
                page.get_image_bbox(image[7]),
            ),
            page.get_images(full=True),
        ),
    )


def get_step(all_words: List[WordBlock], word_block: WordBlock) -> int:
    closest = None
    closest_dist = None
    for x0, y0, x1, y1, word in all_words:
        if not re.match("^\\d+$", word) or round(y1 - y0) < 30:
            continue
        dist = box_distance(
            (word_block[0], word_block[1], word_block[2], word_block[3]),
            (x0, y0, x1, y1),
        )
        if closest_dist == None or dist < closest_dist:
            closest = word
            closest_dist = dist
    return int(closest)


def get_image(all_images: List, word_block: WordBlock) -> (int, str):
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
        bbox,
    ) in all_images:
        if width < 24 or height < 24:
            continue

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
    # page_number = 17
    page_number = 10
    # page_number = 16
    page = document[page_number]
    words = get_unique_word_positions(page)
    images = get_images_with_bbox(page)
    for word_block in words:
        (
            x0,
            y0,
            x1,
            y1,
            word,
        ) = word_block
        if not re.match("^\\d+x$", word) or round(y1 - y0) != 10:
            continue

        step = get_step(words, word_block)
        (image_xref, image_name) = get_image(images, word_block)
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

    rmtree(output_folder, ignore_errors=True)

    makedirs(path.dirname(pdf_path), exist_ok=True)
    makedirs(output_folder)

    if not path.exists(pdf_path):
        download_pdf(pdf_url, pdf_path)
    extract_images_from_pdf(pdf_path, output_folder)


if __name__ == "__main__":
    main()
