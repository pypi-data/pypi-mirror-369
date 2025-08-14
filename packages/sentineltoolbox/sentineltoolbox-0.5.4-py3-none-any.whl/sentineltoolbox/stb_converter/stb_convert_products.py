import ast
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import click
from colorlog import ColoredFormatter

from sentineltoolbox.stb_converter.universal_convert import convert_sentinel_products
from sentineltoolbox.typedefs import fix_datetime


def parse_converter_args(args_str: str) -> dict[str, Any]:
    result: dict[str, Any] = {}

    # Split the string by ':' to separate the product_type (e.g., "XXX")
    try:
        product_type, arguments = args_str.split(":", 1)
    except ValueError:
        raise click.BadParameter(f"Invalid format for argument '{args_str}'. Expected 'SECTION: a=1; b=2'")

    product_type = product_type.strip()  # Clean product_type name
    result[product_type] = {}

    # Split arguments by ';' and process key-value pairs
    for arg in arguments.split(";"):
        arg = arg.strip()
        if not arg:
            continue
        try:
            key, value = arg.split("=", 1)
            result[product_type][key.strip()] = ast.literal_eval(value.strip())
        except ValueError:
            raise click.BadParameter(f"Invalid key-value format in '{arg}'. Expected 'key=value'")

    return result


@click.command()
@click.argument(
    "inputs",
    type=str,
    nargs=-1,
)
@click.option(
    "-i",
    "--input-dir",
    type=str,
)
@click.option(
    "-o",
    "--output-dir",
    type=str,
)
@click.option(
    "--dry-run",
    is_flag=True,
    show_default=True,
    default=False,
)
@click.option("--hash", type=int, help="[EXPERIMENTAL, DO NOT USE]")
@click.option("--creation-date", type=str, help="[EXPERIMENTAL, DO NOT USE]")
@click.option(
    "-m",
    "--map",
    multiple=True,
    type=(str, str),
    help="Mapping legacy -> dpr. For example OL_1_EFR -> OLCEFR",
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    show_default=True,
    default=False,
    help="Read input directory recursivly",
)
@click.option(
    "-t",
    "--templates",
    is_flag=True,
    show_default=True,
    default=False,
    help="[EXPERIMENTAL, DO NOT USE] Also generate templates for each products",
)
@click.option(
    "-z",
    "--zip",
    is_flag=True,
    show_default=True,
    default=False,
    help="[EXPERIMENTAL, DO NOT USE] Zip output zarr product (available for S3 converter)",
)
@click.option(
    "--args",
    multiple=True,
    help="Arguments in the format 'PRODUCT_TYPE: param1=val1; param2=val2'"
    "For example: --args=\"MSIL1A: detector_ids=('d01',)\"",
)
@click.option(
    "--secret-alias",
    help="[EXPERIMENTAL, DO NOT USE] secret alias to use for inputs (defined in secrets.json)",
)
def main(
    inputs: list[str | Path],
    input_dir: str,
    output_dir: str,
    dry_run: bool,
    hash: int,
    creation_date: str | datetime | None,
    map: dict[str, str],
    recursive: bool,
    templates: bool,
    zip: bool,
    args: Any,
    secret_alias: str | None,
) -> None:
    user_map = dict(map)

    # Create handlers
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_handler.setFormatter(ColoredFormatter("%(log_color)s%(levelname)-10s%(message)s%(reset)s"))

    logger = logging.getLogger("stb_convert_products")
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.addHandler(c_handler)

    logger = logging.getLogger("sentineltoolbox")
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.addHandler(c_handler)

    logger = logging.getLogger("xarray_eop")
    logger.setLevel(logging.INFO)

    converter_args = {}
    for arg_str in args:
        converter_args.update(parse_converter_args(arg_str))

    if creation_date:
        creation_date = fix_datetime(creation_date)
    else:
        creation_date = None

    convert_sentinel_products(
        inputs,
        input_dir=input_dir,
        output_dir=output_dir,
        dry_run=dry_run,
        force_hash=hash,
        force_creation_date=creation_date,
        user_map=user_map,
        recursive=recursive,
        templates=templates,
        zip=zip,
        converter_args=converter_args,
        secret_alias=secret_alias,
    )
