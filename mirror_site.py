#!/bin/python3

import os
from os import path, cpu_count
import subprocess
import argparse
from functools import reduce
from itertools import chain
from multiprocessing import Pool
from utils import convert_link, convert_image


def convert_links(n_thread: int):
    workload = reduce(
        chain,
        map(
            lambda walk: map(lambda file: path.join(walk[0], file), walk[2]),
            os.walk("./icourse.club/course"),
        ),
    )

    with Pool(n_thread) as p:
        p.map(convert_link, workload)


def convert_images(n_thread: int):
    workload = filter(
        lambda file: not file.endswith(".webp"),
        reduce(
            chain,
            map(
                lambda walk: map(lambda file: path.join(walk[0], file), walk[2]),
                os.walk("./icourse.club/uploads/images"),
            ),
        ),
    )

    with Pool(n_thread) as p:
        p.map(convert_image, workload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", help="min popular page to fetch", action="store")
    parser.add_argument(
        "--max", help="max popular page to fetch", action="store", required=True
    )
    parser.add_argument("-n", help="threads to use in download", action="store")
    parser.add_argument(
        "--convert-links",
        help="convert links in html file",
        action="store_const",
        const=True,
    )
    parser.add_argument(
        "--convert-images",
        help="convert images downloaded to webp",
        action="store_const",
        const=True,
    )
    args = parser.parse_args()

    if not os.path.exists("./icourse.club/uploads/images"):
        os.makedirs("./icourse.club/uploads/images")
    if not os.path.exists("./icourse.club/static/image"):
        os.makedirs("./icourse.club/static/image")
    if not os.path.exists("./icourse.club/course"):
        os.makedirs("./icourse.club/course")

    if os.path.exists("./mirrorsite"):
        subprocess.run(
            [
                "./mirrorsite",
                "--min={}".format(args.min if args.min is not None else 1),
                "--max={}".format(args.max),
                "-n={}".format(args.n if args.n is not None else 10),
            ],
            check=True,
            env=os.environ.copy(),
        )
    elif os.path.exists("./target/release/mirrorsite"):
        subprocess.run(
            [
                "cargo",
                "run",
                "--release",
                "--",
                "--min={}".format(args.min if args.min is not None else 1),
                "--max={}".format(args.max),
                "-n={}".format(args.n if args.n is not None else 10),
            ],
            check=True,
            env=os.environ.copy(),
        )
    else:
        raise Exception("Cannot find mirrorsite binary")

    if args.convert_links:
        convert_links(cpu_count())

    if args.convert_images:
        convert_images(cpu_count())
