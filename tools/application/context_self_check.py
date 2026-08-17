#!/usr/bin/env python3
"""Public Context Repository manifest self-check.

This Application-owned tool is intentionally narrow:
- reads only the fixed root context-manifest.json from its own repository
- verifies that this exact tool path is registered as TRUSTED_EXECUTABLE
- verifies basic role separation for its own path
- emits structured JSON

It does not execute other repository code, read USER_DATA, access the network,
spawn processes, or validate Domain-owned Recommendation/Search/Damage semantics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SELF_PATH = "tools/application/context_self_check.py"


class SelfCheckError(RuntimeError):
    pass


def bind_repository_root(root: Path) -> Path:
    """Require --root to identify the repository containing this exact tool.

    This prevents a caller from repurposing the trusted executable as a generic
    local-file reader by supplying an unrelated filesystem root.
    """

    try:
        resolved_root = root.resolve(strict=True)
    except OSError as exc:
        raise SelfCheckError(f"repository root is unavailable: {exc}") from exc

    if not resolved_root.is_dir():
        raise SelfCheckError("repository root must be a directory")

    self_file = Path(__file__).resolve()
    expected_self = resolved_root / SELF_PATH

    if expected_self.is_symlink() or not expected_self.is_file():
        raise SelfCheckError("repository root does not contain the registered self-check file")

    try:
        expected_resolved = expected_self.resolve(strict=True)
    except OSError as exc:
        raise SelfCheckError(f"failed to resolve registered self-check file: {exc}") from exc

    if expected_resolved != self_file:
        raise SelfCheckError("repository root is not the root containing this executing tool")

    return resolved_root


def load_manifest(root: Path) -> dict[str, Any]:
    path = root / "context-manifest.json"
    if path.is_symlink() or not path.is_file():
        raise SelfCheckError("context-manifest.json must be a regular file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SelfCheckError(f"failed to read manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise SelfCheckError("manifest root must be an object")
    return value


def inspect(root: Path) -> dict[str, Any]:
    root = bind_repository_root(root)
    manifest = load_manifest(root)
    registry = manifest.get("registry")
    if not isinstance(registry, dict):
        raise SelfCheckError("manifest.registry must be an object")

    trusted_instruction = registry.get("trusted_instruction")
    trusted_contract = registry.get("trusted_contract")
    trusted_executable = registry.get("trusted_executable")
    data_roots = registry.get("data_reference_roots")

    for name, value in {
        "trusted_instruction": trusted_instruction,
        "trusted_contract": trusted_contract,
        "trusted_executable": trusted_executable,
        "data_reference_roots": data_roots,
    }.items():
        if not isinstance(value, list):
            raise SelfCheckError(f"registry.{name} must be an array")

    if SELF_PATH not in trusted_executable:
        raise SelfCheckError("self-check tool is not registered as TRUSTED_EXECUTABLE")
    if SELF_PATH in trusted_instruction or SELF_PATH in trusted_contract:
        raise SelfCheckError("self-check tool has a privileged role collision")
    if any(SELF_PATH.startswith(root_path) for root_path in data_roots):
        raise SelfCheckError("self-check tool overlaps DATA_REFERENCE root")

    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, dict):
        raise SelfCheckError("manifest.capabilities must be an object")

    return {
        "ok": True,
        "tool": SELF_PATH,
        "role": "TRUSTED_EXECUTABLE",
        "root_binding": "self_repository_only",
        "manifest_version": manifest.get("manifest_version"),
        "repository_role": manifest.get("repository_role"),
        "release_status": manifest.get("release_status"),
        "registry_counts": {
            "trusted_instruction": len(trusted_instruction),
            "trusted_contract": len(trusted_contract),
            "trusted_executable": len(trusted_executable),
            "data_reference_roots": len(data_roots),
        },
        "capabilities": capabilities,
    }


def main() -> int:
    default_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=default_root)
    args = parser.parse_args()

    try:
        result = inspect(args.root)
    except SelfCheckError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
