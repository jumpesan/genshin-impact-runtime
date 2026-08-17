#!/usr/bin/env python3
"""Deterministic validator candidate for genshin_portable_user_context 0.1-draft."""

from __future__ import annotations

import json
import sys
from typing import Any

CONTRACT_VERSION = "1"
SUPPORTED_FORMAT = "genshin_portable_user_context"
SUPPORTED_VERSION = "0.1-draft"
SUPPORTED_RAW_FORMAT = "genshin_hoyolab_raw_snapshot"
SUPPORTED_RAW_VERSION = "0.1-poc"
EXPECTED_COVERAGE = {
    "characters": "complete",
    "character_details": "complete",
    "equipped_weapons": "equipped_only",
    "equipped_artifacts": "equipped_only",
    "weapon_inventory": "unavailable",
    "artifact_inventory": "unavailable",
    "character_ascension": "not_explicit_in_source",
}
FORBIDDEN_EXACT_KEYS = {
    "role_id", "game_role_id", "cookie", "authorization", "auth_token",
    "access_token", "refresh_token", "token", "device_id", "device_fp", "devicefp",
}


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _normalized_key(key: str) -> str:
    return key.strip().lower().replace("-", "_")


def _is_forbidden_key(key: str) -> bool:
    lowered = key.strip().lower()
    normalized = _normalized_key(key)
    return normalized in FORBIDDEN_EXACT_KEYS or lowered.startswith("x-rpc-") or normalized.startswith("x_rpc_")


def _scan_forbidden(value: Any, path: str = "$") -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if _is_forbidden_key(str(key)):
                errors.append(_issue("FORBIDDEN_FIELD", child_path, "authority/privacy-bearing field is forbidden in Portable User Context"))
            errors.extend(_scan_forbidden(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_scan_forbidden(child, f"{path}[{index}]"))
    return errors


def _check_keys(obj: Any, required: set[str], optional: set[str], path: str, errors: list[dict[str, str]]) -> bool:
    if not isinstance(obj, dict):
        errors.append(_issue("INVALID_TYPE", path, "must be an object"))
        return False
    keys = set(obj)
    for key in sorted(required - keys):
        errors.append(_issue("MISSING_FIELD", f"{path}.{key}", "required field is missing"))
    for key in sorted(keys - required - optional):
        errors.append(_issue("UNKNOWN_FIELD", f"{path}.{key}", "field is not allowed by contract v1"))
    return True


def _check_nullable_int(value: Any, path: str, errors: list[dict[str, str]], minimum: int = 0) -> None:
    if value is not None and (not _is_int(value) or value < minimum):
        errors.append(_issue("INVALID_VALUE", path, f"must be null or integer >= {minimum}"))


def _check_nullable_string(value: Any, path: str, errors: list[dict[str, str]]) -> None:
    if value is not None and not isinstance(value, str):
        errors.append(_issue("INVALID_TYPE", path, "must be string or null"))


def _validate_artifact_stat(value: Any, path: str, errors: list[dict[str, str]]) -> None:
    if not _check_keys(value, {"property_type", "value"}, {"source_times"}, path, errors):
        return
    if not _is_int(value.get("property_type")):
        errors.append(_issue("INVALID_TYPE", f"{path}.property_type", "must be integer"))
    stat_value = value.get("value")
    if isinstance(stat_value, bool) or not isinstance(stat_value, (str, int, float)):
        errors.append(_issue("INVALID_TYPE", f"{path}.value", "must be string or number"))
    if "source_times" in value and (not _is_int(value.get("source_times")) or value.get("source_times") < 0):
        errors.append(_issue("INVALID_VALUE", f"{path}.source_times", "must be integer >= 0"))


def _validate_verification_property(value: Any, path: str, errors: list[dict[str, str]]) -> None:
    if not _check_keys(value, {"property_type", "base", "add", "final"}, set(), path, errors):
        return
    if not _is_int(value.get("property_type")):
        errors.append(_issue("INVALID_TYPE", f"{path}.property_type", "must be integer"))
    for field in ("base", "add", "final"):
        item = value.get(field)
        if isinstance(item, bool) or not isinstance(item, (str, int, float)):
            errors.append(_issue("INVALID_TYPE", f"{path}.{field}", "must be string or number"))


def _validate_character(value: Any, index: int, errors: list[dict[str, str]]) -> int | None:
    path = f"$.characters[{index}]"
    required = {"character_id", "level", "friendship_level", "current_element", "constellations", "skills", "equipped_weapon", "equipped_artifacts", "verification"}
    if not _check_keys(value, required, set(), path, errors):
        return None
    character_id = value.get("character_id")
    if not _is_int(character_id) or character_id < 1:
        errors.append(_issue("INVALID_VALUE", f"{path}.character_id", "must be integer >= 1"))
        character_id = None
    _check_nullable_int(value.get("level"), f"{path}.level", errors)
    _check_nullable_int(value.get("friendship_level"), f"{path}.friendship_level", errors)
    _check_nullable_string(value.get("current_element"), f"{path}.current_element", errors)

    constellations = value.get("constellations")
    constellation_ids: set[int] = set()
    active_count = 0
    if not isinstance(constellations, list):
        errors.append(_issue("INVALID_TYPE", f"{path}.constellations", "must be an array"))
        constellations = []
    for c_index, constellation in enumerate(constellations):
        c_path = f"{path}.constellations[{c_index}]"
        if not _check_keys(constellation, {"constellation_id", "position", "active", "enhanced"}, set(), c_path, errors):
            continue
        c_id = constellation.get("constellation_id")
        if not _is_int(c_id) or c_id < 1:
            errors.append(_issue("INVALID_VALUE", f"{c_path}.constellation_id", "must be integer >= 1"))
        elif c_id in constellation_ids:
            errors.append(_issue("DUPLICATE_CONSTELLATION_ID", f"{c_path}.constellation_id", "duplicate constellation_id"))
        else:
            constellation_ids.add(c_id)
        _check_nullable_int(constellation.get("position"), f"{c_path}.position", errors)
        if not isinstance(constellation.get("active"), bool):
            errors.append(_issue("INVALID_TYPE", f"{c_path}.active", "must be boolean"))
        elif constellation.get("active"):
            active_count += 1
        if not isinstance(constellation.get("enhanced"), bool):
            errors.append(_issue("INVALID_TYPE", f"{c_path}.enhanced", "must be boolean"))

    skills = value.get("skills")
    skill_ids: set[int] = set()
    if not isinstance(skills, list):
        errors.append(_issue("INVALID_TYPE", f"{path}.skills", "must be an array"))
        skills = []
    for s_index, skill in enumerate(skills):
        s_path = f"{path}.skills[{s_index}]"
        if not _check_keys(skill, {"skill_id", "level", "unlocked", "enhanced"}, set(), s_path, errors):
            continue
        s_id = skill.get("skill_id")
        if not _is_int(s_id) or s_id < 1:
            errors.append(_issue("INVALID_VALUE", f"{s_path}.skill_id", "must be integer >= 1"))
        elif s_id in skill_ids:
            errors.append(_issue("DUPLICATE_SKILL_ID", f"{s_path}.skill_id", "duplicate skill_id"))
        else:
            skill_ids.add(s_id)
        _check_nullable_int(skill.get("level"), f"{s_path}.level", errors)
        if not isinstance(skill.get("unlocked"), bool):
            errors.append(_issue("INVALID_TYPE", f"{s_path}.unlocked", "must be boolean"))
        if not isinstance(skill.get("enhanced"), bool):
            errors.append(_issue("INVALID_TYPE", f"{s_path}.enhanced", "must be boolean"))

    weapon = value.get("equipped_weapon")
    w_path = f"{path}.equipped_weapon"
    if _check_keys(weapon, {"weapon_id", "level", "ascension_level", "refinement"}, set(), w_path, errors):
        if not _is_int(weapon.get("weapon_id")) or weapon.get("weapon_id") < 1:
            errors.append(_issue("INVALID_VALUE", f"{w_path}.weapon_id", "must be integer >= 1"))
        for field in ("level", "ascension_level", "refinement"):
            _check_nullable_int(weapon.get(field), f"{w_path}.{field}", errors)

    artifacts = value.get("equipped_artifacts")
    artifact_slots: set[int] = set()
    if not isinstance(artifacts, list):
        errors.append(_issue("INVALID_TYPE", f"{path}.equipped_artifacts", "must be an array"))
        artifacts = []
    elif len(artifacts) > 5:
        errors.append(_issue("INVALID_VALUE", f"{path}.equipped_artifacts", "must contain at most 5 artifacts"))
    for a_index, artifact in enumerate(artifacts):
        a_path = f"{path}.equipped_artifacts[{a_index}]"
        required_artifact = {"slot", "piece_id", "set_id", "rarity", "level", "main_stat", "substats"}
        if not _check_keys(artifact, required_artifact, set(), a_path, errors):
            continue
        slot = artifact.get("slot")
        if not _is_int(slot) or not 1 <= slot <= 5:
            errors.append(_issue("INVALID_VALUE", f"{a_path}.slot", "must be integer in range 1..5"))
        elif slot in artifact_slots:
            errors.append(_issue("DUPLICATE_ARTIFACT_SLOT", f"{a_path}.slot", "duplicate equipped artifact slot"))
        else:
            artifact_slots.add(slot)
        if not _is_int(artifact.get("piece_id")) or artifact.get("piece_id") < 1:
            errors.append(_issue("INVALID_VALUE", f"{a_path}.piece_id", "must be integer >= 1"))
        set_id = artifact.get("set_id")
        if set_id is not None and (not _is_int(set_id) or set_id < 1):
            errors.append(_issue("INVALID_VALUE", f"{a_path}.set_id", "must be null or integer >= 1"))
        _check_nullable_int(artifact.get("rarity"), f"{a_path}.rarity", errors)
        _check_nullable_int(artifact.get("level"), f"{a_path}.level", errors)
        _validate_artifact_stat(artifact.get("main_stat"), f"{a_path}.main_stat", errors)
        substats = artifact.get("substats")
        if not isinstance(substats, list):
            errors.append(_issue("INVALID_TYPE", f"{a_path}.substats", "must be an array"))
        else:
            for sub_index, substat in enumerate(substats):
                _validate_artifact_stat(substat, f"{a_path}.substats[{sub_index}]", errors)

    verification = value.get("verification")
    v_path = f"{path}.verification"
    v_required = {"hoyolab_actived_constellation_num", "hoyolab_constellation_can_enhanced", "hoyolab_skill_can_enhanced", "hoyolab_selected_properties", "hoyolab_base_properties", "hoyolab_extra_properties", "hoyolab_element_properties"}
    if _check_keys(verification, v_required, set(), v_path, errors):
        observed_count = verification.get("hoyolab_actived_constellation_num")
        _check_nullable_int(observed_count, f"{v_path}.hoyolab_actived_constellation_num", errors)
        if _is_int(observed_count) and observed_count != active_count:
            errors.append(_issue("CONSTELLATION_COUNT_MISMATCH", f"{v_path}.hoyolab_actived_constellation_num", f"source verification count {observed_count} != active constellation count {active_count}"))

        c_verify = verification.get("hoyolab_constellation_can_enhanced")
        seen_c_verify: set[int] = set()
        if not isinstance(c_verify, list):
            errors.append(_issue("INVALID_TYPE", f"{v_path}.hoyolab_constellation_can_enhanced", "must be an array"))
        else:
            for cv_index, entry in enumerate(c_verify):
                cv_path = f"{v_path}.hoyolab_constellation_can_enhanced[{cv_index}]"
                if not _check_keys(entry, {"constellation_id", "can_enhanced"}, set(), cv_path, errors):
                    continue
                c_id = entry.get("constellation_id")
                if not _is_int(c_id) or c_id < 1:
                    errors.append(_issue("INVALID_VALUE", f"{cv_path}.constellation_id", "must be integer >= 1"))
                else:
                    if c_id in seen_c_verify:
                        errors.append(_issue("DUPLICATE_VERIFICATION_REFERENCE", f"{cv_path}.constellation_id", "duplicate verification constellation reference"))
                    seen_c_verify.add(c_id)
                    if c_id not in constellation_ids:
                        errors.append(_issue("VERIFICATION_REFERENCE_MISMATCH", f"{cv_path}.constellation_id", "constellation verification reference not present in canonical state"))
                if not isinstance(entry.get("can_enhanced"), bool):
                    errors.append(_issue("INVALID_TYPE", f"{cv_path}.can_enhanced", "must be boolean"))

        s_verify = verification.get("hoyolab_skill_can_enhanced")
        seen_s_verify: set[int] = set()
        if not isinstance(s_verify, list):
            errors.append(_issue("INVALID_TYPE", f"{v_path}.hoyolab_skill_can_enhanced", "must be an array"))
        else:
            for sv_index, entry in enumerate(s_verify):
                sv_path = f"{v_path}.hoyolab_skill_can_enhanced[{sv_index}]"
                if not _check_keys(entry, {"skill_id", "can_enhanced"}, set(), sv_path, errors):
                    continue
                s_id = entry.get("skill_id")
                if not _is_int(s_id) or s_id < 1:
                    errors.append(_issue("INVALID_VALUE", f"{sv_path}.skill_id", "must be integer >= 1"))
                else:
                    if s_id in seen_s_verify:
                        errors.append(_issue("DUPLICATE_VERIFICATION_REFERENCE", f"{sv_path}.skill_id", "duplicate verification skill reference"))
                    seen_s_verify.add(s_id)
                    if s_id not in skill_ids:
                        errors.append(_issue("VERIFICATION_REFERENCE_MISMATCH", f"{sv_path}.skill_id", "skill verification reference not present in canonical state"))
                if not isinstance(entry.get("can_enhanced"), bool):
                    errors.append(_issue("INVALID_TYPE", f"{sv_path}.can_enhanced", "must be boolean"))

        for field in ("hoyolab_selected_properties", "hoyolab_base_properties", "hoyolab_extra_properties", "hoyolab_element_properties"):
            entries = verification.get(field)
            field_path = f"{v_path}.{field}"
            if not isinstance(entries, list):
                errors.append(_issue("INVALID_TYPE", field_path, "must be an array"))
            else:
                for p_index, entry in enumerate(entries):
                    _validate_verification_property(entry, f"{field_path}[{p_index}]", errors)
    return character_id


def validate_portable_context(data: Any) -> dict[str, Any]:
    warnings: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    format_value = data.get("format") if isinstance(data, dict) else None
    version_value = data.get("format_version") if isinstance(data, dict) else None
    coverage_value = data.get("coverage") if isinstance(data, dict) and isinstance(data.get("coverage"), dict) else {}

    def result(status: str) -> dict[str, Any]:
        return {"contract_version": CONTRACT_VERSION, "status": status, "portable_context_valid": status == "valid", "format": format_value, "format_version": version_value, "coverage": coverage_value, "warnings": warnings, "errors": errors}

    if not isinstance(data, dict):
        errors.append(_issue("INVALID_TYPE", "$", "Portable User Context must be an object"))
        return result("invalid")
    forbidden = _scan_forbidden(data)
    if forbidden:
        errors.extend(forbidden)
        return result("invalid")
    if data.get("format") != SUPPORTED_FORMAT:
        errors.append(_issue("FORMAT_MISMATCH", "$.format", f"expected {SUPPORTED_FORMAT}"))
        return result("invalid")
    if "format_version" not in data:
        errors.append(_issue("MISSING_FIELD", "$.format_version", "required field is missing"))
        return result("invalid")
    if data.get("format_version") != SUPPORTED_VERSION:
        errors.append(_issue("UNSUPPORTED_VERSION", "$.format_version", f"supported exact version is {SUPPORTED_VERSION}"))
        return result("unsupported_version")

    coverage = data.get("coverage")
    if isinstance(coverage, dict):
        missing = sorted(set(EXPECTED_COVERAGE) - set(coverage))
        if missing:
            for key in missing:
                errors.append(_issue("MISSING_FIELD", f"$.coverage.{key}", "required coverage field is missing"))
            return result("invalid")
        unknown = sorted(set(coverage) - set(EXPECTED_COVERAGE))
        if unknown:
            for key in unknown:
                errors.append(_issue("UNSUPPORTED_COVERAGE_FIELD", f"$.coverage.{key}", "coverage field is not understood by contract v1"))
            return result("unsupported_semantics")
        bad_values = [key for key, expected in EXPECTED_COVERAGE.items() if coverage.get(key) != expected]
        if bad_values:
            for key in bad_values:
                errors.append(_issue("UNSUPPORTED_COVERAGE_VALUE", f"$.coverage.{key}", f"expected {EXPECTED_COVERAGE[key]!r} for Portable 0.1-draft"))
            return result("unsupported_semantics")

    _check_keys(data, {"format", "format_version", "generated_at", "source", "coverage", "characters"}, set(), "$", errors)
    _check_nullable_string(data.get("generated_at"), "$.generated_at", errors)
    if data.get("generated_at") is None:
        warnings.append(_issue("PROVENANCE_GENERATED_AT_MISSING", "$.generated_at", "generated_at is null; do not infer a timestamp"))

    source = data.get("source")
    if _check_keys(source, {"provider", "server", "raw_format", "raw_format_version"}, set(), "$.source", errors):
        if source.get("provider") != "HoYoLAB":
            errors.append(_issue("INVALID_VALUE", "$.source.provider", "must equal HoYoLAB"))
        _check_nullable_string(source.get("server"), "$.source.server", errors)
        if source.get("server") is None:
            warnings.append(_issue("SOURCE_SERVER_MISSING", "$.source.server", "source server is null; do not infer a server"))
        if source.get("raw_format") != SUPPORTED_RAW_FORMAT:
            errors.append(_issue("INVALID_VALUE", "$.source.raw_format", f"must equal {SUPPORTED_RAW_FORMAT}"))
        raw_version = source.get("raw_format_version")
        if raw_version is not None and raw_version != SUPPORTED_RAW_VERSION:
            errors.append(_issue("INVALID_VALUE", "$.source.raw_format_version", f"must be null or {SUPPORTED_RAW_VERSION}"))
        if raw_version is None:
            warnings.append(_issue("SOURCE_RAW_FORMAT_VERSION_MISSING", "$.source.raw_format_version", "raw source format version is null; do not infer it"))
    if not isinstance(coverage, dict):
        errors.append(_issue("INVALID_TYPE", "$.coverage", "must be an object"))

    characters = data.get("characters")
    seen_character_ids: set[int] = set()
    if not isinstance(characters, list):
        errors.append(_issue("INVALID_TYPE", "$.characters", "must be an array"))
    else:
        for index, character in enumerate(characters):
            character_id = _validate_character(character, index, errors)
            if character_id is None:
                continue
            if character_id in seen_character_ids:
                errors.append(_issue("DUPLICATE_CHARACTER_ID", f"$.characters[{index}].character_id", "duplicate character_id"))
            seen_character_ids.add(character_id)
    return result("invalid" if errors else "valid")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_portable_context.py <portable.json>", file=sys.stderr)
        return 2
    try:
        with open(argv[1], "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        output = {"contract_version": CONTRACT_VERSION, "status": "invalid", "portable_context_valid": False, "format": None, "format_version": None, "coverage": {}, "warnings": [], "errors": [_issue("INVALID_JSON", "$", str(exc))]}
        print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
        return 1
    output = validate_portable_context(data)
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
