#!/usr/bin/env python3
"""Validate one source Character identity against the Production Character Identity Registry.

This is a targeted integration-readiness interface, not a Production runtime
resolver and not a full-roster completeness claim.

The interface intentionally accepts only Source Identity inputs. Portable state
such as current element/form selectors is out of scope, so callers cannot turn
`current_element=cryo` into an inferred `aether_cryo` canonical identity here.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import identity_integration_validator as shared

INTERFACE_VERSION = "identity_targeted_readiness_v1"
COVERAGE_SCOPE = "targeted_single_source"
ENTITY_KIND = "character"


@dataclass(frozen=True)
class CharacterRegistrySnapshot:
    schema_version: int
    base_identity_kinds: dict[str, str]


@dataclass
class TargetedIdentityResult:
    provider: str
    source_id: str
    status: str
    canonical_id: str | None
    canonical_kind: str | None
    alias_origin: str | None
    registry_path: str
    registry_schema_version: int | None
    findings: list[shared.Finding]

    @property
    def exit_code(self) -> int:
        return 1 if self.status == "FAIL" else 0


def _load_character_registry(path: Path) -> CharacterRegistrySnapshot:
    if not path.is_file():
        raise ValueError(f"{path}: character identity registry not found")

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError(f"{path}: registry must be a JSON object")

    schema_version = payload.get("schema_version")
    if schema_version != 1:
        raise ValueError(
            f"{path}: unsupported Character Identity Registry schema_version "
            f"{schema_version!r}; targeted interface currently supports v1"
        )

    base_rows = payload.get("base_identities")
    form_rows = payload.get("form_identities")
    if not isinstance(base_rows, list):
        raise ValueError(f"{path}: base_identities must be an array")
    if not isinstance(form_rows, list):
        raise ValueError(f"{path}: form_identities must be an array")

    base_identity_kinds: dict[str, str] = {}
    for index, raw in enumerate(base_rows):
        origin = f"{path}:base_identities[{index}]"
        if not isinstance(raw, dict):
            raise ValueError(f"{origin}: expected object")
        canonical_id = shared._stringify(
            raw.get("canonical_character_id"),
            field_name="canonical_character_id",
            origin=origin,
        )
        identity_kind = shared._stringify(
            raw.get("identity_kind"),
            field_name="identity_kind",
            origin=origin,
        )
        if canonical_id in base_identity_kinds:
            raise ValueError(f"{origin}: duplicate canonical_character_id {canonical_id}")
        base_identity_kinds[canonical_id] = identity_kind

    return CharacterRegistrySnapshot(
        schema_version=schema_version,
        base_identity_kinds=base_identity_kinds,
    )


def run_targeted_character_readiness(
    *,
    provider: str,
    source_id: str | int,
    alias_files: Sequence[Path],
    character_identity_registry: Path,
) -> TargetedIdentityResult:
    normalized_provider = str(provider).strip().lower()
    normalized_source_id = shared._stringify(
        source_id,
        field_name="source_id",
        origin="target",
    )
    report = shared.ValidationReport(mode="readiness")
    registry: CharacterRegistrySnapshot | None = None
    aliases: dict[tuple[str, str, str], shared.AliasRow] = {}

    try:
        if not normalized_provider:
            raise ValueError("target: provider must be non-empty")
        registry = _load_character_registry(character_identity_registry)
        aliases = shared._load_aliases(alias_files, report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report.error("input_error", str(exc))

    if not alias_files and not report.error_count:
        report.pending(
            "alias_projection_not_supplied",
            "no owner-provided alias projection supplied for targeted identity readiness",
        )

    canonical_id: str | None = None
    canonical_kind: str | None = None
    alias_origin: str | None = None

    if not report.error_count and registry is not None:
        alias = aliases.get((normalized_provider, ENTITY_KIND, normalized_source_id))
        if alias is None:
            report.pending(
                "character_alias_missing",
                f"{normalized_provider}/character/{normalized_source_id} has no owner-provided alias",
            )
        else:
            alias_origin = alias.origin
            canonical_id = alias.canonical_id
            canonical_kind = registry.base_identity_kinds.get(canonical_id)
            if canonical_kind is None:
                report.error(
                    "character_registry_target_missing",
                    f"source {normalized_source_id} -> {canonical_id}; "
                    "target is not a Production base identity in Character Identity Registry",
                )
            else:
                report.info(
                    "character_identity_resolved",
                    f"source {normalized_source_id} -> canonical base {canonical_id}",
                )

    return TargetedIdentityResult(
        provider=normalized_provider,
        source_id=normalized_source_id,
        status=report.overall,
        canonical_id=canonical_id if report.overall == "PASS" else None,
        canonical_kind=canonical_kind if report.overall == "PASS" else None,
        alias_origin=alias_origin,
        registry_path=str(character_identity_registry),
        registry_schema_version=registry.schema_version if registry is not None else None,
        findings=report.findings,
    )


def as_dict(result: TargetedIdentityResult) -> dict[str, Any]:
    return {
        "interface_version": INTERFACE_VERSION,
        "coverage_scope": COVERAGE_SCOPE,
        "coverage": {
            "requested": 1,
            "resolved": 1 if result.status == "PASS" else 0,
        },
        "full_fixture_claim": "NOT_MADE",
        "entity_kind": ENTITY_KIND,
        "provider": result.provider,
        "source_id": result.source_id,
        "canonical_id": result.canonical_id,
        "canonical_kind": result.canonical_kind,
        "owner_readiness": result.status,
        "diagnostics": [
            {"level": item.level, "code": item.code, "message": item.message}
            for item in result.findings
        ],
        "trace": {
            "projection_contract": "provider,entity_kind,source_id,canonical_id",
            "alias_origin": result.alias_origin,
            "character_identity_registry": result.registry_path,
            "character_identity_registry_schema_version": result.registry_schema_version,
            "owner_contracts": [
                "architecture/identity_integration.md",
                "architecture/character_identity_form.md",
            ],
        },
    }


def _default_registry() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "data"
        / "official"
        / "characters"
        / "identity_registry.json"
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", default=shared.PROVIDER)
    parser.add_argument("--source-id", required=True)
    parser.add_argument(
        "--character-identity-registry",
        type=Path,
        default=_default_registry(),
    )
    parser.add_argument(
        "--alias-file",
        type=Path,
        action="append",
        default=[],
        help="owner-provided normalized alias projection (.json/.csv); may be repeated",
    )
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def _print_text(result: TargetedIdentityResult) -> None:
    print("Identity Targeted Readiness")
    print(f"interface_version: {INTERFACE_VERSION}")
    print(f"coverage_scope: {COVERAGE_SCOPE}")
    print(f"provider: {result.provider}")
    print(f"entity_kind: {ENTITY_KIND}")
    print(f"source_id: {result.source_id}")
    print(f"owner_readiness: {result.status}")
    print(f"canonical_id: {result.canonical_id or '<unresolved>'}")
    print(f"canonical_kind: {result.canonical_kind or '<unresolved>'}")
    print("full_fixture_claim: NOT_MADE")
    for item in result.findings:
        print(f"[{item.level}] {item.code}: {item.message}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    result = run_targeted_character_readiness(
        provider=args.provider,
        source_id=args.source_id,
        alias_files=tuple(args.alias_file),
        character_identity_registry=args.character_identity_registry,
    )
    if args.json_output:
        print(json.dumps(as_dict(result), ensure_ascii=False, indent=2))
    else:
        _print_text(result)
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
