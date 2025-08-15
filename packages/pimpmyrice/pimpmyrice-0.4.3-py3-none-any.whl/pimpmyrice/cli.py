import logging
from pathlib import Path
from typing import Any

from docopt import DocoptExit, docopt

from pimpmyrice.config_paths import SERVER_PID_FILE
from pimpmyrice.doc import __doc__ as cli_doc
from pimpmyrice.edit_args import process_edit_args
from pimpmyrice.logger import deserialize_logrecord
from pimpmyrice.utils import is_locked

log = logging.getLogger(__name__)


def send_to_server(
    args: dict[str, Any], address: str = "http://127.0.0.1:5000"
) -> None:
    import requests

    if "IMAGE" in args and args["IMAGE"]:
        args["IMAGE"] = [
            (
                img
                if img.startswith(("http://", "https://"))
                else str(Path(img).absolute())
            )
            for img in args["IMAGE"]
        ]

    if args["OUT_DIR"]:
        args["OUT_DIR"] = str(Path(args["OUT_DIR"]).absolute())

    log.debug(f"connecting to {address}")

    try:
        with requests.post(
            f"{address}/v1/cli_command", json=args, stream=True
        ) as response:
            if response.status_code == 200:
                for chunk in response.iter_content(chunk_size=8192):
                    log_record = deserialize_logrecord(chunk.decode())
                    if log_record.levelno >= log.getEffectiveLevel():
                        log.handle(log_record)

    except Exception as e:
        log.exception(e)
    finally:
        log.debug("closing connection")


async def cli() -> None:
    try:
        args = docopt(cli_doc)
    except DocoptExit:
        log.info(cli_doc)
        return

    if args["--verbose"]:
        logging.getLogger().setLevel(logging.DEBUG)

    if args["edit"]:
        await process_edit_args(args)
        return

    server_running, server_pid = is_locked(SERVER_PID_FILE)

    try:
        if server_running:
            send_to_server(args)
        else:
            from pimpmyrice.args import process_args
            from pimpmyrice.theme import ThemeManager

            tm = ThemeManager()
            await process_args(tm, args)
    except Exception as e:
        log.debug("exception:", exc_info=e)
        log.error(e)
