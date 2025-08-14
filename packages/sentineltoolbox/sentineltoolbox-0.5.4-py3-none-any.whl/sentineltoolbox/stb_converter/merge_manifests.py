import xml.etree.ElementTree as ET
from pathlib import Path

import click
from defusedxml.ElementTree import fromstring, parse, tostring

from sentineltoolbox.resources.data import XML_NAMESPACES

for ns, path in XML_NAMESPACES.items():
    ET.register_namespace(ns, path)


def merge_manifests(*manifests: ET.ElementTree) -> ET.ElementTree:
    """Merge multiple Sentinel-1 IW manifest files into a single one.

    This function combines multiple Sentinel-1 IW (Interferometric Wide swath) manifest files,
    typically representing different polarizations (e.g., HH, HV, VH, VV), into a unified
    manifest by duplicating entire xmlData blocks for each polarization.

    The merging strategy:
    - Uses the first manifest as the base structure
    - Duplicates complete xmlData blocks from additional manifests
    - Combines data objects from all manifests into shared sections
    - Preserves original IDs by working with complete xmlData duplications

    Args:
        *manifests: Variable number of manifest files as ElementTree objects.
                   First manifest is used as base, others are merged into it.

    Returns:
        ET.ElementTree: Merged manifest file as ElementTree containing
                       all elements from all input manifests

    Raises:
        ValueError: If no manifests provided or manifests have incompatible structure
    """
    if not manifests:
        raise ValueError("At least one manifest must be provided")

    if len(manifests) == 1:
        return manifests[0]

    # Create a deep copy of the first manifest as the base
    merged = ET.ElementTree(fromstring(tostring(manifests[0].getroot())))
    merged_root = merged.getroot()

    # Process each additional manifest
    for manifest in manifests[1:]:
        manifest_root = manifest.getroot()

        # Duplicate entire xmlData blocks for different metadata objects
        merge_data(merged_root, manifest_root)

    return merged


def merge_data(merged_root: ET.Element, source_root: ET.Element) -> None:
    """Duplicate the entire xmlData block for general product information.

    This function creates a complete copy of the xmlData block from the source
    manifest and appends it to the generalProductInformation metadataWrap.

    Args:
        merged_root: Root element of the merged manifest
        source_root: Root element of the source manifest

    Note:
        Modifies merged_root in place by adding complete xmlData blocks

    <xfdu:XFDU xmlns:xfdu="urn:ccsds:schema:xfdu:1">
    <metadataSection>
        <metadataObject ID="generalProductInformation" classification="DESCRIPTION" category="DMD">
            <metadataWrap mimeType="text/xml" vocabularyName="SAFE">
                <xmlData>
    """

    for bloc_path, children_name in [
        (".//metadataObject[@ID='generalProductInformation']/metadataWrap", "xmlData"),
        (".//metadataObject[@ID='processing']/metadataWrap", "xmlData"),
        (".//metadataObject[@ID='measurementQualityInformation']/metadataWrap", "xmlData"),
        ("./dataObjectSection", "dataObject"),
    ]:
        # Find the metadataWrap for generalProductInformation in merged manifest
        merged_bloc = merged_root.find(bloc_path)
        # Find the xmlData in source manifest
        source_bloc_children = source_root.findall(f"{bloc_path}/{children_name}")

        if merged_bloc and source_bloc_children:
            for source_bloc_child in source_bloc_children:
                merged_bloc.append(source_bloc_child)


@click.command()
@click.argument("manifest_paths", type=click.Path(exists=True), nargs=-1)
@click.option("-o", "--output-path", type=click.Path(), required=True)
def main(manifest_paths: tuple[str, ...], output_path: Path) -> None:
    """Merge multiple Sentinel-1 IW manifest files into a single manifest file.

    Args:
        manifest_paths: Paths to input manifest files
        output_path: Path where merged manifest will be saved
    """
    manifests = [parse(str(path)) for path in manifest_paths]

    merged_manifest = merge_manifests(*manifests)
    merged_manifest.write(str(output_path))


if __name__ == "__main__":
    main()
