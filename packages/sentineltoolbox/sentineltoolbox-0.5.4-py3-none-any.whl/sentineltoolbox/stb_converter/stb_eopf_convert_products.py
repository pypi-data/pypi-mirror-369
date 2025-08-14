from pathlib import Path
from typing import Any

import click
from eopf import EOSafeStore, EOZarrStore, OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.store.mapping_factory import EOPFMappingFactory
from eopf.store.mapping_manager import EOPFMappingManager


@click.command()
@click.argument(
    "input",
    type=str,
    nargs=1,
)
@click.option(
    "-m",
    "--mapping",
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
def main(input: Any, mapping: Any, output_dir: Any, dry_run: Any, name: Any, cache: Any) -> None:
    convert_input(input, mapping, output_dir, dry_run, name, cache)


def convert_input(
    input: str | Path,
    mapping: str | None = None,
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

    print(f"{input=}, {mapping=}, {path_output_dir=}, {dry_run=}")
    mask_and_scale = True

    if mapping:
        # add tutorial mapping files to mapping manager
        mp = AnyPath(mapping)
        mf = EOPFMappingFactory(mapping_path=mp)
        mm = EOPFMappingManager(mf)
    else:
        mm = None
    product_path = AnyPath.cast(input)
    safe_store = EOSafeStore(
        product_path,
        mask_and_scale=True,
        mapping_manager=mm,
    )  # legacy store to access a file on the given URL

    eop = safe_store.load(name="NEWMAPPING")  # create and return the EOProduct
    target_store_kwargs: dict[Any, Any] = {}
    target_store = EOZarrStore(path_output_dir.as_posix(), mask_and_scale=mask_and_scale, **target_store_kwargs)
    target_store.open(mode=OpeningMode.CREATE_OVERWRITE)
    if not name:
        product_type = eop.attrs["stac_discovery"]["properties"]["product:type"]
        if product_type in [
            "S01RFCANC",
            "S01SM1RAW",
            "S01SM2RAW",
            "S01SM3RAW",
            "S01SM4RAW",
            "S01SM5RAW",
            "S01SM6RAW",
            "S01N1RAW_",
            "S01N2RAW_",
            "S01N3RAW_",
            "S01N4RAW_",
            "S01N5RAW_",
            "S01N6RAW_",
        ]:
            datatake_id = hex(eop.attrs["stac_discovery"]["properties"]["eopf:datatake_id"]).replace("0x", "").zfill(5)
            mission_specific = f"{datatake_id.upper()}_DH"
            name = eop.get_default_file_name_no_extension(mission_specific=mission_specific)
            name = name[:-12] + "000" + name[-9:]
        else:
            name = eop.get_default_file_name_no_extension()[:-3] + "000"
    target_store[name] = eop
    target_store.close()
