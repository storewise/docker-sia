#!/usr/bin/env python3
"""Run script.
"""
import os
import subprocess
import sys
import zlib

import requests
from clinner.command import Type as CommandType
from clinner.command import command
from clinner.inputs import bool_input
from clinner.run.main import Main
from tqdm import tqdm

BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "data")
CONSENSUS_PATH = os.path.join(BASE_PATH, 'consensus')
CONSENSUS_FILE = os.path.join(CONSENSUS_PATH, "consensus.db")
DB_URL = "https://consensus.siahub.info/consensus.db.gz"


@command(
    command_type=CommandType.PYTHON,
    args=(
        (("--bootstrap",), {"help": "Bootstrap consensus database", "action": "store_true"}),
        (("--no-bootstrap",), {"help": "Do not bootstrap consensus database", "action": "store_true"}),
        (("--modules",), {"help": "Run only specific modules"}),
    ),
    parser_opts={"help": "Start Sia daemon"},
)
def start(*args, **kwargs):
    os.chdir(BASE_PATH)

    if not os.path.exists(CONSENSUS_FILE):

        if not kwargs["no_bootstrap"] and (
            kwargs["bootstrap"] or bool_input("Do you want to bootstrap consensus database?")
        ):
            decompress = zlib.decompressobj(16 + zlib.MAX_WBITS)
            os.makedirs(CONSENSUS_PATH, exist_ok=True)
            try:
                with open(CONSENSUS_FILE, "wb") as output_file, requests.get(DB_URL, stream=True) as r, \
                        tqdm(unit="B", unit_scale=True, unit_divisor=2 ** 10) as pbar:
                    total = int(r.headers.get("content-length", 0))
                    pbar.total = total
                    percents = [(i, total / 100 * i) for i in range(10, 100, 10)]
                    notify_percent, notify_value = percents.pop(0)

                    pbar.write(f"Starting download consensus database ({total} bytes)")

                    for data in r.iter_content(32 * (2 ** 10)):
                        output_file.write(decompress.decompress(data))
                        pbar.update(len(data))

                        if notify_value and pbar.n >= notify_value:
                            pbar.write(f"Downloaded {notify_percent}% ({pbar.n} bytes)")
                            try:
                                notify_percent, notify_value = percents.pop(0)
                            except IndexError:
                                notify_percent, notify_value = None, None

                    output_file.write(decompress.flush())
                    pbar.write("Download finished")
            except zlib.error as e:
                print(f"Failed to download the bootstrap database: {e}")

    modules = "--modules {}".format(kwargs["modules"]) if kwargs["modules"] else ""
    subprocess.run(
        "socat tcp-listen:8000,reuseaddr,fork tcp:localhost:9980 "
        "& siad --sia-directory {} {} {}".format(os.getcwd(), modules, " ".join(args)),
        shell=True,
    )


if __name__ == "__main__":
    sys.exit(Main().run())
