#!/usr/bin/env python3
"""Validate HoYoLAB source identities against Official canonical identities.

This module is an integration harness, not an Identity Resolution SSOT.
Official domain collections own source aliases. The harness consumes a small
normalized alias projection and checks that Account source facts resolve
uniquely into the current Official masters.

readiness mode: missing owner-provided aliases are PENDING; contradictions fail.
strict mode: all required primary aliases must resolve; PENDING also fails.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

PROVIDER = "hoyolab"
KNOWN_ENTITY_KINDS = {
    "character",
    "weapon",
    "artifact_set",
    "artifact_slot",
    "artifact_piece",
}


@dataclass(frozen=True)
class AliasRow:
    provider: str
    entity_kind: str
    source_id: str
    canonical_id: str
    origin: str


@dataclass
class Finding:
    level: str  # ERROR | PENDING | INFO
    code: str
    message: str


@dataclass
class ValidationReport:
    mode: str
    counts: dict[str, int] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)

    def error(self, code: str, message: str) -> None:
        self.findings.append(Finding("ERROR", code, message))

    def pending(self, code: str, message: str) -> None:
        self.findings.append(Finding("PENDING", code, message))

    def info(self, code: str, message: str) -> None:
        self.findings.append(Finding("INFO", code, message))

    @property
    def error_count(self) -> int:
        return sum(item.level == "ERROR" for item in self.findings)

    @property
    def pending_count(self) -> int:
        return sum(item.level == "PENDING" for item in self.findings)

    @property
    def overall(self) -> str:
        if self.error_count:
            return "FAIL"
        if self.pending_count:
            return "FAIL" if self.mode == "strict" else "PENDING"
        return "PASS"

    @property
    def exit_code(self) -> int:
        return 0 if self.overall in {"PASS", "PENDING"} else 1


@dataclass(frozen=True)
class Paths:
    fixture: Path
    character_master_dir: Path
    weapon_master: Path
    artifact_set_master: Path
    artifact_piece_master: Path
    alias_files: tuple[Path, ...] = ()


@dataclass
class Masters:
    character_ids: set[str]
    weapon_ids: set[str]
    artifact_set_ids: set[str]
    artifact_piece_ids: set[str]
    artifact_piece_by_set_slot: dict[tuple[str, str], str]
    artifact_slots: set[str]


def _stringify(value: Any, *, field_name: str, origin: str) -> str:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{origin}: {field_name} must be a string/number, got {value!r}")
    if isinstance(value, (str, int)):
        text = str(value).strip()
        if text:
            return text
    raise ValueError(f"{origin}: {field_name} must be a non-empty string/number")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _require_columns(rows: list[dict[str, str]], required: set[str], *, path: Path) -> None:
    if rows:
        columns = set(rows[0])
    else:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle), [])
        columns = set(header)
    missing = sorted(required - columns)
    if missing:
        raise ValueError(f"{path}: missing required columns: {', '.join(missing)}")


def _load_character_master(path: Path, report: ValidationReport) -> set[str]:
    if not path.is_dir():
        raise ValueError(f"{path}: character master directory not found")
    ids: set[str] = set()
    for profile_path in sorted(path.glob("*/profile.json")):
        with profile_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        char_id = _stringify(
            payload.get("character_id"),
            field_name="character_id",
            origin=str(profile_path),
        )
        if char_id in ids:
            report.error("character_master_duplicate_id", f"duplicate character_id: {char_id}")
        ids.add(char_id)
    if not ids:
        raise ValueError(f"{path}: no character profile.json records found")
    return ids


def _load_masters(paths: Paths, report: ValidationReport) -> Masters:
    character_ids = _load_character_master(paths.character_master_dir, report)

    weapon_rows = _read_csv(paths.weapon_master)
    _require_columns(weapon_rows, {"weapon_id"}, path=paths.weapon_master)
    weapon_ids: set[str] = set()
    for index, row in enumerate(weapon_rows, start=2):
        weapon_id = _stringify(
            row.get("weapon_id"),
            field_name="weapon_id",
            origin=f"{paths.weapon_master}:{index}",
        )
        if weapon_id in weapon_ids:
            report.error("weapon_master_duplicate_id", f"duplicate weapon_id: {weapon_id}")
        weapon_ids.add(weapon_id)
    if not weapon_ids:
        report.pending("weapon_master_empty", f"{paths.weapon_master} has no weapon rows")

    set_rows = _read_csv(paths.artifact_set_master)
    _require_columns(set_rows, {"set_id"}, path=paths.artifact_set_master)
    artifact_set_ids: set[str] = set()
    for index, row in enumerate(set_rows, start=2):
        set_id = _stringify(
            row.get("set_id"),
            field_name="set_id",
            origin=f"{paths.artifact_set_master}:{index}",
        )
        if set_id in artifact_set_ids:
            report.error("artifact_set_master_duplicate_id", f"duplicate set_id: {set_id}")
        artifact_set_ids.add(set_id)

    piece_rows = _read_csv(paths.artifact_piece_master)
    _require_columns(piece_rows, {"piece_id", "set_id", "slot"}, path=paths.artifact_piece_master)
    artifact_piece_ids: set[str] = set()
    by_set_slot: dict[tuple[str, str], str] = {}
    artifact_slots: set[str] = set()
    for index, row in enumerate(piece_rows, start=2):
        origin = f"{paths.artifact_piece_master}:{index}"
        piece_id = _stringify(row.get("piece_id"), field_name="piece_id", origin=origin)
        set_id = _stringify(row.get("set_id"), field_name="set_id", origin=origin)
        slot = _stringify(row.get("slot"), field_name="slot", origin=origin)
        if piece_id in artifact_piece_ids:
            report.error("artifact_piece_master_duplicate_id", f"duplicate piece_id: {piece_id}")
        artifact_piece_ids.add(piece_id)
        artifact_slots.add(slot)
        if set_id not in artifact_set_ids:
            report.error(
                "artifact_piece_unknown_set",
                f"artifact piece {piece_id} references unknown set_id {set_id}",
            )
        key = (set_id, slot)
        previous = by_set_slot.get(key)
        if previous is not None:
            report.error(
                "artifact_piece_nonunique_set_slot",
                f"{set_id} + {slot} maps to both {previous} and {piece_id}",
            )
        else:
            by_set_slot[key] = piece_id

    if not artifact_set_ids:
        raise ValueError(f"{paths.artifact_set_master}: no artifact set rows")
    if not artifact_piece_ids:
        raise ValueError(f"{paths.artifact_piece_master}: no artifact piece rows")

    return Masters(
        character_ids=character_ids,
        weapon_ids=weapon_ids,
        artifact_set_ids=artifact_set_ids,
        artifact_piece_ids=artifact_piece_ids,
        artifact_piece_by_set_slot=by_set_slot,
        artifact_slots=artifact_slots,
    )


def _normalize_alias_record(raw: dict[str, Any], *, origin: str) -> AliasRow:
    provider = _stringify(raw.get("provider"), field_name="provider", origin=origin).lower()
    entity_kind = _stringify(
        raw.get("entity_kind", raw.get("source_entity_kind")),
        field_name="entity_kind/source_entity_kind",
        origin=origin,
    ).lower()
    source_id = _stringify(
        raw.get("source_id", raw.get("source_code")),
        field_name="source_id/source_code",
        origin=origin,
    )
    canonical_id = _stringify(
        raw.get("canonical_id", raw.get("canonical_slot")),
        field_name="canonical_id/canonical_slot",
        origin=origin,
    )
    if entity_kind not in KNOWN_ENTITY_KINDS:
        raise ValueError(f"{origin}: unsupported entity_kind {entity_kind!r}")
    return AliasRow(provider, entity_kind, source_id, canonical_id, origin)


def _iter_alias_records(path: Path) -> Iterable[tuple[dict[str, Any], str]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for index, row in enumerate(csv.DictReader(handle), start=2):
                yield dict(row), f"{path}:{index}"
        return
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, dict):
            payload = payload.get("aliases")
        if not isinstance(payload, list):
            raise ValueError(f'{path}: JSON must be a list or {{"aliases": [...]}}')
        for index, row in enumerate(payload):
            if not isinstance(row, dict):
                raise ValueError(f"{path}: aliases[{index}] must be an object")
            yield row, f"{path}:aliases[{index}]"
        return
    raise ValueError(f"{path}: alias projection must be .json or .csv")


def _load_aliases(
    paths: Sequence[Path], report: ValidationReport
) -> dict[tuple[str, str, str], AliasRow]:
    aliases: dict[tuple[str, str, str], AliasRow] = {}
    for path in paths:
        if not path.is_file():
            raise ValueError(f"{path}: alias file not found")
        for raw, origin in _iter_alias_records(path):
            row = _normalize_alias_record(raw, origin=origin)
            key = (row.provider, row.entity_kind, row.source_id)
            previous = aliases.get(key)
            if previous is not None:
                report.error(
                    "duplicate_alias_key",
                    f"{key} duplicated in {previous.origin} and {row.origin}",
                )
                continue
            aliases[key] = row
    return aliases


def _load_fixture(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    required = {"character", "weapon", "artifact_set", "artifact_piece"}
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: identity inventory must be a JSON object")
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"{path}: missing fixture sections: {', '.join(missing)}")
    for section in required:
        if not isinstance(payload[section], list):
            raise ValueError(f"{path}: {section} must be an array")
    return payload


def _fixture_rows_with_ids(
    rows: list[Any], *, section: str, report: ValidationReport
) -> list[tuple[dict[str, Any], str]]:
    result: list[tuple[dict[str, Any], str]] = []
    seen: set[str] = set()
    for index, raw in enumerate(rows):
        if not isinstance(raw, dict):
            report.error("fixture_invalid_row", f"{section}[{index}] must be an object")
            continue
        try:
            source_id = _stringify(
                raw.get("source_id"),
                field_name="source_id",
                origin=f"{section}[{index}]",
            )
        except ValueError as exc:
            report.error("fixture_invalid_source_id", str(exc))
            continue
        if source_id in seen:
            report.error("fixture_duplicate_source_id", f"{section} duplicate source_id {source_id}")
        seen.add(source_id)
        result.append((raw, source_id))
    return result


def _alias(
    aliases: dict[tuple[str, str, str], AliasRow], entity_kind: str, source_id: str
) -> AliasRow | None:
    return aliases.get((PROVIDER, entity_kind, source_id))


def _pending_missing_aliases(
    report: ValidationReport, entity_kind: str, missing: list[str], total: int
) -> None:
    if not missing:
        return
    sample = ", ".join(missing[:5])
    suffix = "..." if len(missing) > 5 else ""
    report.pending(
        f"{entity_kind}_aliases_missing",
        f"{len(missing)}/{total} required {entity_kind} aliases missing; sample: {sample}{suffix}",
    )


def _validate_character(
    fixture: dict[str, Any],
    aliases: dict[tuple[str, str, str], AliasRow],
    masters: Masters,
    report: ValidationReport,
) -> None:
    rows = _fixture_rows_with_ids(fixture["character"], section="character", report=report)
    missing: list[str] = []
    resolved = 0
    variant_resolved = 0
    for row, source_id in rows:
        alias = _alias(aliases, "character", source_id)
        if alias is None:
            missing.append(source_id)
            continue
        if alias.canonical_id in masters.character_ids:
            resolved += 1
            continue
        element_raw = row.get("element")
        element = element_raw.strip().lower() if isinstance(element_raw, str) else ""
        variant_id = f"{alias.canonical_id}_{element}" if element else ""
        if variant_id and variant_id in masters.character_ids:
            resolved += 1
            variant_resolved += 1
            continue
        report.error(
            "character_alias_target_missing",
            f"source {source_id} -> {alias.canonical_id}; neither target nor current-element "
            f"variant {variant_id or '<unavailable>'} exists in Character Master",
        )
    _pending_missing_aliases(report, "character", missing, len(rows))
    report.counts["character_fixture"] = len(rows)
    report.counts["character_resolved"] = resolved
    report.counts["character_variant_resolved"] = variant_resolved


def _validate_weapon(
    fixture: dict[str, Any],
    aliases: dict[tuple[str, str, str], AliasRow],
    masters: Masters,
    report: ValidationReport,
) -> None:
    rows = _fixture_rows_with_ids(fixture["weapon"], section="weapon", report=report)
    missing: list[str] = []
    resolved = 0
    unverifiable = 0
    for _row, source_id in rows:
        alias = _alias(aliases, "weapon", source_id)
        if alias is None:
            missing.append(source_id)
            continue
        if not masters.weapon_ids:
            unverifiable += 1
            continue
        if alias.canonical_id not in masters.weapon_ids:
            report.error(
                "weapon_alias_target_missing",
                f"source {source_id} -> unknown canonical weapon_id {alias.canonical_id}",
            )
            continue
        resolved += 1
    _pending_missing_aliases(report, "weapon", missing, len(rows))
    if unverifiable:
        report.pending(
            "weapon_targets_unverifiable",
            f"{unverifiable} weapon aliases cannot be target-validated because Weapon Master is empty",
        )
    report.counts["weapon_fixture"] = len(rows)
    report.counts["weapon_resolved"] = resolved


def _validate_artifacts(
    fixture: dict[str, Any],
    aliases: dict[tuple[str, str, str], AliasRow],
    masters: Masters,
    report: ValidationReport,
) -> None:
    set_rows = _fixture_rows_with_ids(fixture["artifact_set"], section="artifact_set", report=report)
    set_source_id_set = {source_id for _row, source_id in set_rows}
    missing_sets: list[str] = []
    resolved_sets: dict[str, str] = {}
    for _row, source_id in set_rows:
        alias = _alias(aliases, "artifact_set", source_id)
        if alias is None:
            missing_sets.append(source_id)
            continue
        if alias.canonical_id not in masters.artifact_set_ids:
            report.error(
                "artifact_set_alias_target_missing",
                f"source {source_id} -> unknown canonical set_id {alias.canonical_id}",
            )
            continue
        resolved_sets[source_id] = alias.canonical_id
    _pending_missing_aliases(report, "artifact_set", missing_sets, len(set_rows))

    raw_piece_rows = _fixture_rows_with_ids(
        fixture["artifact_piece"], section="artifact_piece", report=report
    )
    valid_piece_rows: list[tuple[str, str, str]] = []
    slot_source_ids: set[str] = set()
    for index, (row, piece_source_id) in enumerate(raw_piece_rows):
        try:
            set_source_id = _stringify(
                row.get("set_source_id"),
                field_name="set_source_id",
                origin=f"artifact_piece[{index}]",
            )
            slot_source_id = _stringify(
                row.get("slot"),
                field_name="slot",
                origin=f"artifact_piece[{index}]",
            )
        except ValueError as exc:
            report.error("artifact_fixture_invalid_relation", str(exc))
            continue
        if set_source_id not in set_source_id_set:
            report.error(
                "artifact_piece_unknown_fixture_set",
                f"piece source {piece_source_id} references absent fixture set {set_source_id}",
            )
        slot_source_ids.add(slot_source_id)
        valid_piece_rows.append((piece_source_id, set_source_id, slot_source_id))

    missing_slots: list[str] = []
    resolved_slots: dict[str, str] = {}
    for source_id in sorted(slot_source_ids):
        alias = _alias(aliases, "artifact_slot", source_id)
        if alias is None:
            missing_slots.append(source_id)
            continue
        if alias.canonical_id not in masters.artifact_slots:
            report.error(
                "artifact_slot_alias_target_missing",
                f"source {source_id} -> unknown canonical slot {alias.canonical_id}",
            )
            continue
        resolved_slots[source_id] = alias.canonical_id
    _pending_missing_aliases(report, "artifact_slot", missing_slots, len(slot_source_ids))

    primary_resolved = 0
    secondary_checked = 0
    for piece_source_id, set_source_id, slot_source_id in valid_piece_rows:
        canonical_set = resolved_sets.get(set_source_id)
        canonical_slot = resolved_slots.get(slot_source_id)
        if canonical_set is None or canonical_slot is None:
            continue
        canonical_piece = masters.artifact_piece_by_set_slot.get((canonical_set, canonical_slot))
        if canonical_piece is None:
            report.error(
                "artifact_primary_piece_missing",
                f"({canonical_set}, {canonical_slot}) has no canonical piece",
            )
            continue
        primary_resolved += 1
        secondary = _alias(aliases, "artifact_piece", piece_source_id)
        if secondary is None:
            continue
        secondary_checked += 1
        if secondary.canonical_id not in masters.artifact_piece_ids:
            report.error(
                "artifact_piece_secondary_target_missing",
                f"source {piece_source_id} -> unknown secondary piece_id {secondary.canonical_id}",
            )
            continue
        if secondary.canonical_id != canonical_piece:
            report.error(
                "artifact_piece_secondary_conflict",
                f"source {piece_source_id}: primary -> {canonical_piece}, secondary -> "
                f"{secondary.canonical_id}",
            )

    if primary_resolved < len(valid_piece_rows) and valid_piece_rows:
        report.pending(
            "artifact_piece_primary_incomplete",
            f"primary set+slot resolution complete for {primary_resolved}/{len(valid_piece_rows)} pieces",
        )

    report.counts["artifact_set_fixture"] = len(set_rows)
    report.counts["artifact_set_resolved"] = len(resolved_sets)
    report.counts["artifact_slot_fixture"] = len(slot_source_ids)
    report.counts["artifact_slot_resolved"] = len(resolved_slots)
    report.counts["artifact_piece_fixture"] = len(raw_piece_rows)
    report.counts["artifact_piece_primary_resolved"] = primary_resolved
    report.counts["artifact_piece_secondary_checked"] = secondary_checked


def _validate_all_alias_targets(
    aliases: dict[tuple[str, str, str], AliasRow], masters: Masters, report: ValidationReport
) -> None:
    for (_provider, entity_kind, _source_id), alias in aliases.items():
        if entity_kind == "weapon":
            if masters.weapon_ids and alias.canonical_id not in masters.weapon_ids:
                report.error(
                    "alias_projection_unknown_weapon_target",
                    f"{alias.origin}: unknown weapon target {alias.canonical_id}",
                )
        elif entity_kind == "artifact_set":
            if alias.canonical_id not in masters.artifact_set_ids:
                report.error(
                    "alias_projection_unknown_artifact_set_target",
                    f"{alias.origin}: unknown artifact set target {alias.canonical_id}",
                )
        elif entity_kind == "artifact_slot":
            if alias.canonical_id not in masters.artifact_slots:
                report.error(
                    "alias_projection_unknown_artifact_slot_target",
                    f"{alias.origin}: unknown artifact slot target {alias.canonical_id}",
                )
        elif entity_kind == "artifact_piece":
            if alias.canonical_id not in masters.artifact_piece_ids:
                report.error(
                    "alias_projection_unknown_artifact_piece_target",
                    f"{alias.origin}: unknown artifact piece target {alias.canonical_id}",
                )
        elif entity_kind == "character":
            if alias.canonical_id in masters.character_ids:
                continue
            prefix = f"{alias.canonical_id}_"
            if not any(character_id.startswith(prefix) for character_id in masters.character_ids):
                report.error(
                    "alias_projection_unknown_character_target",
                    f"{alias.origin}: unknown character/base target {alias.canonical_id}",
                )


def run_validation(paths: Paths, *, mode: str) -> ValidationReport:
    if mode not in {"readiness", "strict"}:
        raise ValueError(f"unsupported mode: {mode}")
    report = ValidationReport(mode=mode)
    try:
        fixture = _load_fixture(paths.fixture)
        masters = _load_masters(paths, report)
        aliases = _load_aliases(paths.alias_files, report)
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as exc:
        report.error("input_error", str(exc))
        return report

    report.counts["alias_rows_loaded"] = len(aliases)
    if not paths.alias_files:
        report.pending(
            "alias_projection_not_supplied",
            "no owner-provided alias projection supplied; identity integration is not ready",
        )

    _validate_all_alias_targets(aliases, masters, report)
    _validate_character(fixture, aliases, masters, report)
    _validate_weapon(fixture, aliases, masters, report)
    _validate_artifacts(fixture, aliases, masters, report)
    return report


def _default_paths() -> tuple[Path, Path, Path, Path, Path]:
    repo_root = Path(__file__).resolve().parents[2]
    base = Path(__file__).resolve().parent
    return (
        base / "testdata" / "en_us_identity_inventory.json",
        repo_root / "data" / "official" / "characters",
        repo_root / "data" / "official" / "weapons" / "weapons.csv",
        repo_root / "data" / "official" / "artifacts" / "artifact_sets.csv",
        repo_root / "data" / "official" / "artifacts" / "artifact_pieces.csv",
    )


def _build_parser() -> argparse.ArgumentParser:
    fixture, chars, weapons, sets, pieces = _default_paths()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("readiness", "strict"), default="readiness")
    parser.add_argument("--fixture", type=Path, default=fixture)
    parser.add_argument("--character-master-dir", type=Path, default=chars)
    parser.add_argument("--weapon-master", type=Path, default=weapons)
    parser.add_argument("--artifact-set-master", type=Path, default=sets)
    parser.add_argument("--artifact-piece-master", type=Path, default=pieces)
    parser.add_argument(
        "--alias-file",
        type=Path,
        action="append",
        default=[],
        help="normalized integration alias projection (.json/.csv); may be repeated",
    )
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def _as_dict(report: ValidationReport) -> dict[str, Any]:
    return {
        "mode": report.mode,
        "overall": report.overall,
        "counts": report.counts,
        "findings": [
            {"level": item.level, "code": item.code, "message": item.message}
            for item in report.findings
        ],
    }


def _print_text(report: ValidationReport) -> None:
    print("Identity Integration Validator")
    print(f"mode: {report.mode}")
    print(f"overall: {report.overall}")
    for key in sorted(report.counts):
        print(f"{key}: {report.counts[key]}")
    for item in report.findings:
        print(f"[{item.level}] {item.code}: {item.message}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    paths = Paths(
        fixture=args.fixture,
        character_master_dir=args.character_master_dir,
        weapon_master=args.weapon_master,
        artifact_set_master=args.artifact_set_master,
        artifact_piece_master=args.artifact_piece_master,
        alias_files=tuple(args.alias_file),
    )
    report = run_validation(paths, mode=args.mode)
    if args.json_output:
        print(json.dumps(_as_dict(report), ensure_ascii=False, indent=2))
    else:
        _print_text(report)
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
