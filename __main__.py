#!/usr/bin/env python3
"""Run script.
"""
import logging
import os
import re
import subprocess
import sys
import typing
import zlib
from threading import Condition, Thread

import aiohttp
import requests
from clinner.command import Type as CommandType
from clinner.command import command
from clinner.inputs import bool_input
from clinner.run.main import Main
from tqdm import tqdm

logger = logging.getLogger("cli")

BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "data")
CONSENSUS_DB_URL = "https://consensus.siahub.info/consensus.db.gz"
REGEX_LOADING = re.compile(r"Finished loading.*")


class ConsensusDB:
    CHUNK_SIZE = 64 * (2 ** 10)

    def __init__(self, base_path: str, url: str):
        self.url = url

        dir_path = os.path.join(base_path, "consensus")
        os.makedirs(dir_path, exist_ok=True)
        self.file_path = os.path.join(dir_path, "consensus.db")

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()
        del self._session

    @property
    def exists(self):
        return os.path.exists(self.file_path)

    @property
    def session(self):
        if not hasattr(self, "_session"):
            raise AttributeError("Must be executed under context")

        return self._session

    async def _download_size(self) -> int:
        async with self.session.head(self.url) as response:
            return int(response.headers.get("Content-Length", "0"))

    async def _download(self) -> typing.AsyncGenerator[typing.Tuple[bytes, int], None]:
        decompress = zlib.decompressobj(16 + zlib.MAX_WBITS)

        async with self.session.get(self.url) as response:
            while True:
                chunk = await response.content.read(self.CHUNK_SIZE)
                if not chunk:
                    break

                yield (decompress.decompress(chunk), len(chunk))

        yield (decompress.flush(), 0)

    async def bootstrap(self):
        try:
            with open(self.file_path, "wb") as output, tqdm(unit="B", unit_scale=True, unit_divisor=2 ** 10) as p:
                total = await self._download_size()
                p.total = total
                percents = [(i, total / 100 * i) for i in range(10, 100, 10)]
                notify_percent, notify_value = percents.pop(0)

                p.write(f"Starting download consensus database ({total} bytes)")

                async for (chunk, size) in self._download():
                    output.write(chunk)
                    p.update(size)

                    if notify_value and p.n >= notify_value:
                        p.write(f"Downloaded {notify_percent}% ({p.n} bytes)")
                        try:
                            notify_percent, notify_value = percents.pop(0)
                        except IndexError:
                            notify_percent, notify_value = None, None

                p.write("Download finished")
        except zlib.error as e:
            logger.error(f"Failed to download the bootstrap database. %s", str(e))


def unlock(condition):
    with condition:
        condition.wait()

    try:
        with requests.session() as session:
            session.post("https://localhost:8000/wallet/unlock", json={"primaryseed": os.environ["UNLOCK_WALLET"]})
        logger.info("Unlock wallet")
    except KeyError:
        logger.error("Cannot unlock wallet. Primary seed must be specified under UNLOCK_WALLET environment variable")


@command(
    command_type=CommandType.PYTHON,
    args=(
        (("--bootstrap",), {"help": "Force bootstrap consensus database", "action": "store_true"}),
        (("--no-bootstrap",), {"help": "Do not bootstrap consensus database", "action": "store_true"}),
        (("--unlock",), {"help": "Unlock wallet", "action": "store_true"}),
    ),
    parser_opts={"help": "Start Sia daemon. Bootstrap the consensus database if it is not found."},
)
async def start(*args, **kwargs):
    os.chdir(BASE_PATH)

    consensus = ConsensusDB(base_path=BASE_PATH, url=CONSENSUS_DB_URL)

    if (
        not consensus.exists
        and not kwargs["no_bootstrap"]
        and (kwargs["bootstrap"] or bool_input("Do you want to bootstrap consensus database?"))
    ):
        logger.info("Bootstrapping consensus database")
        async with consensus:
            await consensus.bootstrap()
    else:
        logger.info("Skip bootstrap consensus database")

    try:
        condition = Condition()
        if kwargs["unlock"]:
            unlock_thread = Thread(name="unlock", target=unlock, args=(condition,))
            unlock_thread.start()

        cmd_args = f"--sia-directory {os.getcwd()} " + " ".join(args)
        cmd = f"socat tcp-listen:8000,reuseaddr,fork tcp:localhost:9980 & siad {cmd_args}"
        cmd.rstrip()
        with subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True
        ) as process:
            loading = True

            for message in process.stdout:
                print(message, end="")

                if loading and REGEX_LOADING.match(message):
                    loading = False

                    with condition:
                        condition.notify_all()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    sys.exit(Main().run())
