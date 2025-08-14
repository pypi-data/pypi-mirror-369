from pathlib import Path
from typing import Any

import click
from eopf import EOZarrStore, OpeningMode
from xarray import DataTree

from sentineltoolbox.metadata_utils import guess_product_type
from sentineltoolbox.readers.open_datatree import open_datatree
from sentineltoolbox.tools.stb_dump_product import convert_datatree_to_structure_str
from sentineltoolbox.verification.cli_compare_products import compare_product_datatrees
from sentineltoolbox.verification.logger import get_validation_logger
from sentineltoolbox.verification.preprocessing_visitors import (
    apply_validation_visitors,
)


@click.command()
@click.argument(
    "reference",
    type=str,
    nargs=1,
)
@click.argument(
    "input",
    type=str,
    nargs=1,
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
@click.option(
    "-n",
    "--name",
    type=str,
)
@click.option(
    "-c",
    "--cache",
    type=str,
)
def main(reference: Any, input: Any, output_dir: Any, dry_run: Any, name: Any, cache: Any) -> None:
    convert_input(reference, input, output_dir, dry_run, name, cache)


def convert_input(
    reference: str | Path,
    input: str | Path,
    output_dir: str | Path | None = None,
    dry_run: bool = False,
    name: str | None = None,
    cache: Path | str | None = None,
) -> None:

    if output_dir is None:
        path_output_dir = Path(".").absolute()
    else:
        path_output_dir = Path(output_dir)

    if not path_output_dir.exists():
        path_output_dir.mkdir(parents=True, exist_ok=True)

    if cache:
        open_datatree_args: dict[str, Any] = dict(local_copy_dir=Path(cache), cache=True)
    else:
        open_datatree_args = {}

    mask_and_scale = True

    target_store_kwargs: dict[Any, Any] = {}
    target_store = EOZarrStore(Path(input).as_posix(), mask_and_scale=mask_and_scale, **target_store_kwargs)
    target_store.open(mode=OpeningMode.OPEN)
    eop = target_store.load(name="NEWMAPPING")
    eop.name = eop.get_default_file_name_no_extension()

    path_converted_prod = Path(input)
    name = path_converted_prod.stem
    dump_name = name  # [:-4] + "LAST"
    xdt_conv = open_datatree(path_converted_prod)

    products: dict[str, DataTree] = {}
    products[dump_name + "_zarr"] = xdt_conv
    # if isinstance(eop, EOProduct):
    #    products[dump_name + "_eop"] = eop.to_datatree()

    xdt_ref = open_datatree(reference, **open_datatree_args)
    ptype = guess_product_type(eop.attrs)

    products[dump_name + "_ref"] = xdt_ref
    xdt_ref, xdt_conv = apply_validation_visitors(ptype, xdt_ref, xdt_conv)
    name = name + ".diff.log"
    with open(path_output_dir / name, "w") as fp:
        failed_logger = get_validation_logger(stream=fp, fmt="TO CHECK: %(message)s")
        passed_logger = get_validation_logger(stream=fp, fmt="SUCCESS: %(message)s")
        logger = get_validation_logger(stream=fp, fmt="INFO: %(message)s")
        try:
            compare_product_datatrees(
                xdt_ref,
                xdt_conv,
                encoding=True,
                encoding_compressor=True,
                encoding_preferred_chunks=False,
                encoding_chunks=False,
                chunks=False,
                logger=logger,
                passed_logger=passed_logger,
                failed_logger=failed_logger,
            )
        except RuntimeError:
            pass

    """
    try:
        reference = PRODUCT[guess_product_type(eop.attrs)]
    except KeyError:
        pass
    else:
        products[dump_name + "_ref_metadata"] = reference
    """

    for name, datatree in products.items():
        struct_name = name + ".structure.out"
        with open(path_output_dir / struct_name, "w") as fp:
            fp.write(convert_datatree_to_structure_str(datatree))

        struct_name = name + ".structure_and_type.out"
        with open(path_output_dir / struct_name, "w") as fp:
            fp.write(convert_datatree_to_structure_str(datatree, dtype=True))

        detail_name = f"{name}.structure-details.out"
        final_path = path_output_dir / "details" / detail_name
        final_path.parent.mkdir(parents=True, exist_ok=True)
        with open(final_path, "w") as fp:
            fp.write(convert_datatree_to_structure_str(datatree, details=True, dtype=True))
