"""Чтение файла вариантов УИР 1.

Файл `!_УИР1_Варианты_с.xlsx` — семь листов, на каждом столбцы-варианты
(заголовок строки 1 — номер варианта) и по 300 наблюдений в строках 2..301.
На некоторых листах ниже 301-й строки лежат служебные расчёты автора
(мат. ожидание, дисперсия, СКО, коэффициент вариации) — они отбрасываются.

Читается stdlib-средствами: xlsx это zip с XML, отдельная зависимость не нужна.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

FIRST_DATA_ROW = 2
LAST_DATA_ROW = 301  # 300 наблюдений; ниже — служебные расчёты автора файла

_CELL_RE = re.compile(r"([A-Z]+)(\d+)")


def _sheet_paths(zf: zipfile.ZipFile) -> list[str]:
    """Пути к листам в порядке книги, через workbook.xml.rels."""
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    targets = {r.get("Id"): r.get("Target") for r in rels}
    book = ET.fromstring(zf.read("xl/workbook.xml"))
    paths = []
    for sheet in book.iter(f"{NS}sheet"):
        target = targets[sheet.get(f"{REL_NS}id")]
        paths.append("xl/" + target.lstrip("/").removeprefix("xl/"))
    return paths


def load_variants(xlsx: str | Path) -> dict[int, list[float]]:
    """{номер варианта: список из 300 наблюдений}."""
    variants: dict[int, list[float]] = {}
    with zipfile.ZipFile(xlsx) as zf:
        for path in _sheet_paths(zf):
            sheet = ET.fromstring(zf.read(path))
            header: dict[str, int] = {}
            columns: dict[str, list[float]] = {}
            for cell in sheet.iter(f"{NS}c"):
                value = cell.find(f"{NS}v")
                if value is None or value.text is None:
                    continue
                col, row_text = _CELL_RE.match(cell.get("r")).groups()
                row = int(row_text)
                if row == 1:
                    if cell.get("t") != "s":  # строковые заголовки — не варианты
                        header[col] = int(float(value.text))
                elif FIRST_DATA_ROW <= row <= LAST_DATA_ROW:
                    columns.setdefault(col, []).append(float(value.text))
            for col, number in header.items():
                if col in columns:
                    variants[number] = columns[col]
    return variants


def load_variant(xlsx: str | Path, number: int) -> list[float]:
    """Наблюдения одного варианта."""
    variants = load_variants(xlsx)
    if number not in variants:
        available = f"{min(variants)}..{max(variants)}"
        raise KeyError(f"варианта {number} нет в файле (есть {available})")
    return variants[number]
