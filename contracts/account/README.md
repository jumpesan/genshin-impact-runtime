# Portable User Context Ingestion Contract

This Account-owned contract validates a user-attached `genshin_portable_user_context` before Application uses it as `USER_DATA`.

It is **not** the formal Runtime Account Schema. It does not perform Canonical Identity mapping, Game Master lookup, Recommendation evaluation or Runtime Resolution.

## Contract version

```text
contract_version = 1
supported format = genshin_portable_user_context
supported Portable version = 0.1-draft exactly
```

Version compatibility is exact. Application must not infer compatibility from version prefixes.

## Required envelope

```text
format
format_version
generated_at
source
coverage
characters
```

The contract is strict: unknown fields at contracted object boundaries are invalid. Unknown coverage keys/values are `unsupported_semantics` and fail closed.

## Coverage

For Portable `0.1-draft`:

```text
characters            complete
character_details     complete
equipped_weapons      equipped_only
equipped_artifacts    equipped_only
weapon_inventory      unavailable
artifact_inventory    unavailable
character_ascension   not_explicit_in_source
```

Meanings:

- `complete`: complete for the named capability under this acquisition contract.
- `equipped_only`: only currently equipped state is represented; not full inventory.
- `unavailable`: capability is unavailable; not an empty inventory.
- `not_explicit_in_source`: Source does not expose the state explicitly; do not infer or treat as zero.

A valid Portable may intentionally contain limited coverage. Therefore Account contract v1 uses `valid`, not `valid_partial`; completeness remains explicit in `coverage`.

## Validation result

```json
{
  "contract_version": "1",
  "status": "valid",
  "portable_context_valid": true,
  "format": "genshin_portable_user_context",
  "format_version": "0.1-draft",
  "coverage": {},
  "warnings": [],
  "errors": []
}
```

Stable statuses:

```text
valid
unsupported_version
unsupported_semantics
invalid
```

Only `valid` sets `portable_context_valid=true`.

## Privacy / security

Portable User Context must not carry authentication or device authority. The deterministic validator rejects forbidden field classes before ordinary structural validation, including:

```text
role_id / game_role_id
Cookie / Authorization
auth/access/refresh/generic token fields
X-Rpc-* / x_rpc_* request-header fields
device identifier / fingerprint fields
```

Unknown fields are also rejected, so uncontracted credential-like fields are never silently ignored.

The validator does not attempt heuristic secret detection inside arbitrary allowed string values. Application must never ask the user to add Raw authentication material to satisfy this contract.

## Provenance nullability

The current `0.1-draft` producer can emit null for:

```text
generated_at
source.server
source.raw_format_version
```

These keys remain required. Null is preserved as unknown and produces a warning; the validator does not infer a replacement.

## Semantic checks beyond JSON Schema

`validate_portable_context.py` additionally verifies:

```text
unique character_id
unique constellation_id per character
unique skill_id per character
unique equipped artifact slot per character
active constellation count == HoYoLAB verification count when non-null
verification constellation/skill references exist in the corresponding state arrays
```

No Source ID is converted into a Canonical ID here.

## Application readiness boundary

```text
validator status == valid
  -> Account Portable ingestion is valid
```

This does not imply:

```text
identity_ready
recommendation_ready
runtime_ready
```

Application must retain those downstream readiness states separately and must not upgrade `equipped_only`, `unavailable`, or `not_explicit_in_source` semantics.

## Files

```text
portable_context.schema.json      structural contract
validate_portable_context.py      deterministic validation + structured result
```

The validator is Python stdlib-only and requires no private Account fixture or HoYoLAB Raw Snapshot.
