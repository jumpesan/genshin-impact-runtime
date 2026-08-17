#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any, Iterable

CONTRACT_VERSION = "1.0.1"
VALIDATOR_VERSION = "1.0.1"
SEARCH_SEMANTICS_VERSION = "party-validator-only-v1"

SUPPORTED_MODES: dict[str, dict[str, int]] = {
    "spiral_abyss_single_team_v1": {"min_members": 1, "max_members": 4}
}

_TOP_LEVEL_KEYS = {"candidate", "request_constraints", "validation_context"}
_CANDIDATE_KEYS = {"candidate_id", "mode_id", "members"}
_MEMBER_KEYS = {"canonical_character_id"}
_CONSTRAINT_KEYS = {
    "required_character_ids",
    "forbidden_character_ids",
    "min_member_count",
    "max_member_count",
    "require_owned_roster",
}
_VALIDATION_CONTEXT_KEYS = {"identity", "owned_roster"}
_COVERAGE_KEYS = {"status", "canonical_character_ids"}
_COVERAGE_STATUSES = {"complete", "partial", "unavailable"}


class ContractInputError(ValueError):
    """Raised when the request is malformed or contradictory."""


@dataclass(frozen=True)
class RuleResult:
    rule_id: str
    status: str
    reason_code: str | None = None
    details: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"rule_id": self.rule_id, "status": self.status}
        if self.reason_code is not None:
            result["reason_code"] = self.reason_code
        if self.details is not None:
            result["details"] = self.details
        return result


def _require_exact_keys(value: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ContractInputError(f"{path}: unknown fields: {', '.join(unknown)}")


def _require_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractInputError(f"{path}: expected object")
    return value


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ContractInputError(
            f"{path}: expected non-empty canonical string without surrounding whitespace"
        )
    return value


def _require_bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise ContractInputError(f"{path}: expected boolean")
    return value


def _require_optional_nonnegative_int(value: Any, path: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractInputError(f"{path}: expected null or non-negative integer")
    return value


def _require_unique_id_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        raise ContractInputError(f"{path}: expected array")
    ids = [_require_string(item, f"{path}[{index}]") for index, item in enumerate(value)]
    if len(ids) != len(set(ids)):
        raise ContractInputError(f"{path}: duplicate canonical IDs are not allowed")
    return ids


def _parse_coverage(value: Any, path: str) -> tuple[str, list[str]]:
    obj = _require_object(value, path)
    _require_exact_keys(obj, _COVERAGE_KEYS, path)
    if set(obj) != _COVERAGE_KEYS:
        missing = sorted(_COVERAGE_KEYS - set(obj))
        raise ContractInputError(f"{path}: missing required fields: {', '.join(missing)}")
    status = _require_string(obj["status"], f"{path}.status")
    if status not in _COVERAGE_STATUSES:
        raise ContractInputError(
            f"{path}.status: expected one of {', '.join(sorted(_COVERAGE_STATUSES))}"
        )
    ids = _require_unique_id_list(obj["canonical_character_ids"], f"{path}.canonical_character_ids")
    if status == "unavailable" and ids:
        raise ContractInputError(f"{path}: unavailable coverage must not carry canonical IDs")
    return status, ids


def _invalid_result(candidate_id: str | None, message: str) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "candidate_id": candidate_id,
        "status": "invalid",
        "hard_constraints": {"status": "unsupported", "results": []},
        "reasons": [{"code": "invalid_contract_input", "message": message}],
        "search_completeness": "not_searched",
        "search_semantics_version": SEARCH_SEMANTICS_VERSION,
    }


def _coverage_contains(canonical_id: str, coverage_status: str, ids: set[str]) -> str:
    if canonical_id in ids:
        return "present"
    if coverage_status == "complete":
        return "absent"
    return "unknown"


def _identity_rule(
    rule_id: str,
    canonical_ids: list[str],
    identity_status: str,
    identity_ids: set[str],
    reason_code: str,
) -> RuleResult:
    unresolved = [
        canonical_id
        for canonical_id in canonical_ids
        if _coverage_contains(canonical_id, identity_status, identity_ids) != "present"
    ]
    if not unresolved:
        return RuleResult(rule_id, "pass")
    return RuleResult(
        rule_id,
        "unsupported",
        reason_code,
        {
            "unresolved_character_ids": unresolved,
            "identity_coverage_status": identity_status,
        },
    )


def _evaluate_owned_roster(
    member_ids: list[str],
    require_owned_roster: bool,
    roster_status: str,
    roster_ids: set[str],
) -> RuleResult:
    if not require_owned_roster:
        return RuleResult("request.owned_roster", "pass", details={"required": False})
    absent: list[str] = []
    unknown: list[str] = []
    for member_id in member_ids:
        membership = _coverage_contains(member_id, roster_status, roster_ids)
        if membership == "absent":
            absent.append(member_id)
        elif membership == "unknown":
            unknown.append(member_id)
    if absent:
        return RuleResult(
            "request.owned_roster",
            "fail",
            "candidate_contains_unowned_character",
            {"character_ids": absent, "owned_roster_coverage_status": roster_status},
        )
    if unknown:
        return RuleResult(
            "request.owned_roster",
            "unsupported",
            "owned_roster_membership_unknown",
            {"character_ids": unknown, "owned_roster_coverage_status": roster_status},
        )
    return RuleResult("request.owned_roster", "pass", details={"required": True})


def _aggregate_hard_status(results: Iterable[RuleResult]) -> str:
    statuses = [result.status for result in results]
    if "fail" in statuses:
        return "fail"
    if "unsupported" in statuses:
        return "unsupported"
    return "pass"


def _append_reason(reasons: list[dict[str, Any]], result: RuleResult) -> None:
    if result.status == "pass":
        return
    reason: dict[str, Any] = {
        "code": result.reason_code or "rule_not_passed",
        "rule_id": result.rule_id,
    }
    if result.details is not None:
        reason["details"] = result.details
    reasons.append(reason)


def validate_candidate(request: Any) -> dict[str, Any]:
    candidate_id: str | None = None
    try:
        root = _require_object(request, "request")
        _require_exact_keys(root, _TOP_LEVEL_KEYS, "request")
        missing_top = sorted(_TOP_LEVEL_KEYS - set(root))
        if missing_top:
            raise ContractInputError(f"request: missing required fields: {', '.join(missing_top)}")

        candidate = _require_object(root["candidate"], "candidate")
        _require_exact_keys(candidate, _CANDIDATE_KEYS, "candidate")
        missing_candidate = sorted(_CANDIDATE_KEYS - set(candidate))
        if missing_candidate:
            raise ContractInputError(
                f"candidate: missing required fields: {', '.join(missing_candidate)}"
            )
        candidate_id = _require_string(candidate["candidate_id"], "candidate.candidate_id")
        mode_id = _require_string(candidate["mode_id"], "candidate.mode_id")

        members_raw = candidate["members"]
        if not isinstance(members_raw, list):
            raise ContractInputError("candidate.members: expected array")
        member_ids: list[str] = []
        for index, member in enumerate(members_raw):
            member_obj = _require_object(member, f"candidate.members[{index}]")
            _require_exact_keys(member_obj, _MEMBER_KEYS, f"candidate.members[{index}]")
            if "canonical_character_id" not in member_obj:
                raise ContractInputError(
                    f"candidate.members[{index}]: canonical_character_id is required"
                )
            member_ids.append(
                _require_string(
                    member_obj["canonical_character_id"],
                    f"candidate.members[{index}].canonical_character_id",
                )
            )

        constraints = _require_object(root["request_constraints"], "request_constraints")
        _require_exact_keys(constraints, _CONSTRAINT_KEYS, "request_constraints")
        required_ids = _require_unique_id_list(
            constraints.get("required_character_ids", []),
            "request_constraints.required_character_ids",
        )
        forbidden_ids = _require_unique_id_list(
            constraints.get("forbidden_character_ids", []),
            "request_constraints.forbidden_character_ids",
        )
        overlap = sorted(set(required_ids) & set(forbidden_ids))
        if overlap:
            raise ContractInputError(
                "request_constraints: required_character_ids and forbidden_character_ids overlap: "
                + ", ".join(overlap)
            )
        min_member_count = _require_optional_nonnegative_int(
            constraints.get("min_member_count"), "request_constraints.min_member_count"
        )
        max_member_count = _require_optional_nonnegative_int(
            constraints.get("max_member_count"), "request_constraints.max_member_count"
        )
        if min_member_count is not None and max_member_count is not None and min_member_count > max_member_count:
            raise ContractInputError(
                "request_constraints: min_member_count must be <= max_member_count"
            )
        require_owned_roster = _require_bool(
            constraints.get("require_owned_roster", False),
            "request_constraints.require_owned_roster",
        )

        validation_context = _require_object(root["validation_context"], "validation_context")
        _require_exact_keys(validation_context, _VALIDATION_CONTEXT_KEYS, "validation_context")
        missing_context = sorted(_VALIDATION_CONTEXT_KEYS - set(validation_context))
        if missing_context:
            raise ContractInputError(
                f"validation_context: missing required fields: {', '.join(missing_context)}"
            )
        identity_status, identity_ids_list = _parse_coverage(
            validation_context["identity"], "validation_context.identity"
        )
        roster_status, roster_ids_list = _parse_coverage(
            validation_context["owned_roster"], "validation_context.owned_roster"
        )
        identity_ids = set(identity_ids_list)
        roster_ids = set(roster_ids_list)

        if identity_status == "complete":
            contradictory_roster_ids = sorted(roster_ids - identity_ids)
            if contradictory_roster_ids:
                raise ContractInputError(
                    "validation_context: complete identity coverage does not contain owned roster IDs: "
                    + ", ".join(contradictory_roster_ids)
                )

        mode_rule = SUPPORTED_MODES.get(mode_id)
        if mode_rule is not None:
            if min_member_count is not None and min_member_count > mode_rule["max_members"]:
                raise ContractInputError(
                    "request_constraints.min_member_count exceeds the registered mode maximum"
                )
            if max_member_count is not None and max_member_count < mode_rule["min_members"]:
                raise ContractInputError(
                    "request_constraints.max_member_count is below the registered mode minimum"
                )
    except ContractInputError as exc:
        return _invalid_result(candidate_id, str(exc))

    results: list[RuleResult] = []
    if mode_rule is None:
        results.extend(
            [
                RuleResult(
                    "mode.registered",
                    "unsupported",
                    "mode_not_supported",
                    {"mode_id": mode_id, "supported_mode_ids": sorted(SUPPORTED_MODES)},
                ),
                RuleResult(
                    "mode.member_count",
                    "unsupported",
                    "mode_rule_unavailable",
                    {"mode_id": mode_id, "member_count": len(member_ids)},
                ),
            ]
        )
    else:
        results.append(RuleResult("mode.registered", "pass", details={"mode_id": mode_id}))
        member_count = len(member_ids)
        if mode_rule["min_members"] <= member_count <= mode_rule["max_members"]:
            results.append(
                RuleResult(
                    "mode.member_count",
                    "pass",
                    details={
                        "member_count": member_count,
                        "minimum": mode_rule["min_members"],
                        "maximum": mode_rule["max_members"],
                    },
                )
            )
        else:
            results.append(
                RuleResult(
                    "mode.member_count",
                    "fail",
                    "mode_member_count_out_of_range",
                    {
                        "member_count": member_count,
                        "minimum": mode_rule["min_members"],
                        "maximum": mode_rule["max_members"],
                    },
                )
            )

    duplicate_ids = sorted({member_id for member_id in member_ids if member_ids.count(member_id) > 1})
    if duplicate_ids:
        results.append(
            RuleResult(
                "party.unique_members",
                "fail",
                "duplicate_party_member",
                {"character_ids": duplicate_ids},
            )
        )
    else:
        results.append(RuleResult("party.unique_members", "pass"))

    results.append(
        _identity_rule(
            "identity.members_resolved",
            member_ids,
            identity_status,
            identity_ids,
            "canonical_identity_unresolved",
        )
    )

    constraint_ids = list(dict.fromkeys(required_ids + forbidden_ids))
    results.append(
        _identity_rule(
            "identity.constraint_ids_resolved",
            constraint_ids,
            identity_status,
            identity_ids,
            "canonical_constraint_identity_unresolved",
        )
    )

    unresolved_required = [item for item in required_ids if item not in identity_ids]
    if unresolved_required:
        results.append(
            RuleResult(
                "request.required_members",
                "unsupported",
                "required_character_identity_unresolved",
                {
                    "unresolved_character_ids": unresolved_required,
                    "identity_coverage_status": identity_status,
                },
            )
        )
    else:
        missing_required = [item for item in required_ids if item not in set(member_ids)]
        if missing_required:
            results.append(
                RuleResult(
                    "request.required_members",
                    "fail",
                    "required_character_missing",
                    {"character_ids": missing_required},
                )
            )
        else:
            results.append(RuleResult("request.required_members", "pass"))

    unresolved_forbidden = [item for item in forbidden_ids if item not in identity_ids]
    if unresolved_forbidden:
        results.append(
            RuleResult(
                "request.forbidden_members",
                "unsupported",
                "forbidden_character_identity_unresolved",
                {
                    "unresolved_character_ids": unresolved_forbidden,
                    "identity_coverage_status": identity_status,
                },
            )
        )
    else:
        present_forbidden = [item for item in forbidden_ids if item in set(member_ids)]
        if present_forbidden:
            results.append(
                RuleResult(
                    "request.forbidden_members",
                    "fail",
                    "forbidden_character_present",
                    {"character_ids": present_forbidden},
                )
            )
        else:
            results.append(RuleResult("request.forbidden_members", "pass"))

    if min_member_count is None or len(member_ids) >= min_member_count:
        results.append(RuleResult("request.min_member_count", "pass", details={"minimum": min_member_count}))
    else:
        results.append(
            RuleResult(
                "request.min_member_count",
                "fail",
                "request_min_member_count_not_met",
                {"member_count": len(member_ids), "minimum": min_member_count},
            )
        )

    if max_member_count is None or len(member_ids) <= max_member_count:
        results.append(RuleResult("request.max_member_count", "pass", details={"maximum": max_member_count}))
    else:
        results.append(
            RuleResult(
                "request.max_member_count",
                "fail",
                "request_max_member_count_exceeded",
                {"member_count": len(member_ids), "maximum": max_member_count},
            )
        )

    results.append(
        _evaluate_owned_roster(member_ids, require_owned_roster, roster_status, roster_ids)
    )

    hard_status = _aggregate_hard_status(results)
    candidate_status = (
        "rejected" if hard_status == "fail" else "unsupported" if hard_status == "unsupported" else "validated"
    )
    reasons: list[dict[str, Any]] = []
    for result in results:
        _append_reason(reasons, result)
    return {
        "contract_version": CONTRACT_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "candidate_id": candidate_id,
        "status": candidate_status,
        "hard_constraints": {
            "status": hard_status,
            "results": [result.as_dict() for result in results],
        },
        "reasons": reasons,
        "search_completeness": "not_searched",
        "search_semantics_version": SEARCH_SEMANTICS_VERSION,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a B1 Party candidate deterministically.")
    parser.add_argument("input", nargs="?", default="-", help="JSON request file path, or '-' for stdin")
    args = parser.parse_args(argv)
    try:
        if args.input == "-":
            request = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as handle:
                request = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps(_invalid_result(None, f"input_json: {exc}"), ensure_ascii=False, indent=2))
        return 2
    result = validate_candidate(request)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] != "invalid" else 2


if __name__ == "__main__":
    raise SystemExit(main())
