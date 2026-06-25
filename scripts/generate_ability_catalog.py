from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


PLAYABLE_HERO_EXCLUDE_SUFFIXES = ("BundleProduct",)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a versioned Heroes ability catalog from extracted game files.")
    parser.add_argument(
        "--catalog-root",
        type=Path,
        required=True,
        help="Root containing extracted mods/, for example /tmp/hots_catalog_extract_97039.",
    )
    parser.add_argument("--build", type=int, required=True, help="Heroes build number, for example 97039.")
    parser.add_argument("--out", type=Path, required=True, help="Python module to write.")
    return parser.parse_args()


def _parse_xml(path: Path) -> ElementTree.Element | None:
    try:
        return ElementTree.parse(path).getroot()
    except ElementTree.ParseError:
        return None


def _game_strings(catalog_root: Path) -> dict[str, str]:
    strings: dict[str, str] = {}
    for path in sorted(catalog_root.glob("mods/**/enus.stormdata/localizeddata/gamestrings.txt")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            strings[key] = value.strip()
    return strings


def _is_playable_hero(hero_id: str) -> bool:
    return not hero_id.endswith(PLAYABLE_HERO_EXCLUDE_SUFFIXES)


def _hero_records(path: Path, strings: dict[str, str]) -> list[tuple[str, str]]:
    root = _parse_xml(path)
    if root is None:
        return []
    records = []
    for element in root:
        if element.tag != "CHero":
            continue
        hero_id = element.attrib.get("id")
        if not hero_id or not _is_playable_hero(hero_id):
            continue
        records.append((hero_id, strings.get(f"Hero/Name/{hero_id}", hero_id)))
    return records


def _hero_catalog_files(catalog_root: Path, strings: dict[str, str]) -> list[tuple[Path, list[tuple[str, str]]]]:
    files: list[tuple[Path, list[tuple[str, str]]]] = []
    heroes_data = catalog_root / "mods/heroesdata.stormmod/base.stormdata/gamedata/heroes"
    for path in sorted(heroes_data.glob("*data/*data.xml")):
        records = _hero_records(path, strings)
        if records:
            files.append((path, records))

    hero_mods = catalog_root / "mods/heromods"
    for mod_path in sorted(hero_mods.glob("*.stormmod")):
        for path in sorted((mod_path / "base.stormdata/gamedata").glob("*.xml")):
            records = _hero_records(path, strings)
            if records:
                files.append((path, records))
    return files


def _button_face(element: ElementTree.Element) -> str | None:
    for child in element.iter():
        if child.tag == "CmdButtonArray" and child.attrib.get("DefaultButtonFace"):
            return child.attrib["DefaultButtonFace"]
    return None


def _ability_display_name(ability_id: str, element: ElementTree.Element, strings: dict[str, str]) -> str:
    face = _button_face(element)
    return (
        strings.get(f"Button/Name/{ability_id}")
        or (strings.get(f"Button/Name/{face}") if face else None)
        or strings.get(f"Abil/Name/{ability_id}")
        or ability_id
    ).strip()


def _ability_rows_for_file(
    path: Path,
    heroes: list[tuple[str, str]],
    strings: dict[str, str],
) -> list[tuple[str, str, str, str]]:
    root = _parse_xml(path)
    if root is None:
        return []

    rows: list[tuple[str, str, str, str]] = []
    for element in root:
        if not element.tag.startswith("CAbil") or element.attrib.get("default") == "1":
            continue
        ability_id = element.attrib.get("id")
        if not ability_id:
            continue

        owners = heroes
        if len(heroes) > 1:
            prefixed_owners = [hero for hero in heroes if ability_id.startswith(hero[0])]
            if prefixed_owners:
                owners = prefixed_owners

        display_name = _ability_display_name(ability_id, element, strings)
        rows.extend((ability_id, hero_id, hero_name, display_name) for hero_id, hero_name in owners)
    return rows


def _global_ability_rows(catalog_root: Path, strings: dict[str, str]) -> list[tuple[str, None, None, str]]:
    path = catalog_root / "mods/heroesdata.stormmod/base.stormdata/gamedata/abildata.xml"
    root = _parse_xml(path)
    if root is None:
        return []

    rows: list[tuple[str, None, None, str]] = []
    for element in root:
        if not element.tag.startswith("CAbil") or element.attrib.get("default") == "1":
            continue
        ability_id = element.attrib.get("id")
        if not ability_id:
            continue
        rows.append((ability_id, None, None, _ability_display_name(ability_id, element, strings)))
    return rows


def _unique_rows(rows: Iterable[tuple[str, str | None, str | None, str]]) -> list[tuple[str, str | None, str | None, str]]:
    seen: set[tuple[str, str | None]] = set()
    unique = []
    for ability_id, hero_id, hero_name, display_name in rows:
        key = (ability_id, hero_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append((ability_id, hero_id, hero_name, display_name))
    return unique


def _module_text(build: int, rows: list[tuple[str, str | None, str | None, str]]) -> str:
    hero_ids = sorted({hero_id for _, hero_id, _, _ in rows if hero_id is not None})
    hero_ability_count: defaultdict[str, int] = defaultdict(int)
    for _, hero_id, _, _ in rows:
        if hero_id is not None:
            hero_ability_count[hero_id] += 1

    lines = [
        "from __future__ import annotations",
        "",
        "# Generated by scripts/generate_ability_catalog.py.",
        f"# Source build: {build}.",
        f"# Current playable heroes: {len(hero_ids)}.",
        f"# Current hero ability catalog rows: {sum(hero_ability_count.values())}.",
        "",
        f"ABILITY_CATALOG_ROWS_{build}: tuple[tuple[str, str | None, str | None, str], ...] = (",
    ]
    for row in rows:
        lines.append(f"    {row!r},")
    lines.extend(
        [
            ")",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = _parse_args()
    strings = _game_strings(args.catalog_root)
    hero_files = _hero_catalog_files(args.catalog_root, strings)

    rows: list[tuple[str, str | None, str | None, str]] = []
    rows.extend(_global_ability_rows(args.catalog_root, strings))
    for path, heroes in hero_files:
        rows.extend(_ability_rows_for_file(path, heroes, strings))

    args.out.write_text(_module_text(args.build, _unique_rows(rows)), encoding="utf-8")


if __name__ == "__main__":
    main()
