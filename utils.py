#!/bin/python3
import os
from unicodedata import name
from PIL import Image
from bs4 import BeautifulSoup
import minify_html


def convert_image(path: str):
    name, ext = os.path.splitext(path)
    assert ext != ".webp"
    print("Convert image", os.path.split(path)[1])
    try:
        image = Image.open(path)
        image.convert("RGB")
        image.save(
            name + ".webp",
            format="webp",
            optimize=True,
            quality=50,
            method=6,
        )
        os.remove(path)
    except Exception as e:
        print("error occured in image process: {}".format(e))


def convert_link(path: str):
    print(f"Convert links in {path}")
    with open(path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, features="lxml")
        # special treat style.css, because '?' seems to be reserved in browser environment
        style = soup.select('link[href^="/static/css/style.css"]')
        if len(style) >= 1:
            assert len(style) == 1
            style = style[0]
            style["href"] = style["href"].split("?")[0]
        # redirect static resources to local files
        for static in soup.select('[href^="/static"]'):
            static["href"] = "../.." + static["href"]
        # tag_a are mostly links to courses, teachers, users
        # since we do not mirror these things, simply redirect them to origin site
        for tag in soup.select('a[href^="/"]'):
            tag["href"] = "https://icourse.club" + tag["href"]
        # redirect image src to local files
        for img in soup.select('img[src^="/uploads/images"]'):
            img["src"] = "../.." + img["src"].split(".")[0] + ".webp"
        # remove javascripts to reduce file size
        for script in soup.find_all("script"):
            script.decompose()

    # compress text to reduce size
    with open(path, "w") as file:
        file.write(minify_html.minify(str(soup), remove_processing_instructions=True))

def remove_template(path: str):
    print(f"try remove template in {path}")
    with open(path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, features="lxml")
        if soup.head: soup.head.decompose()
        nav = soup.find("nav")
        if nav: nav.decompose()
        for signin in soup.select('#signin, #footer'):
            signin.decompose()
    
    # compress text to reduce size
    with open(path, "w") as file:
        file.write(minify_html.minify(str(soup), remove_processing_instructions=True))

