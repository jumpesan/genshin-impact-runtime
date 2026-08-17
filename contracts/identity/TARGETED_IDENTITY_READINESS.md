# Targeted Identity Readiness v1

## Purpose

`integration/identity/targeted_identity_readiness.py` is the Identity Integration-owned
targeted readiness interface for validating one Source Character identity against
Domain-owned Production alias + Character Identity Registry data.

It is **not** a Production runtime resolver and does not claim full Account-roster
readiness.

Formal upstream contracts:

```text
architecture/identity_integration.md
architecture/character_identity_form.md
```

Current downstream consumer request:

```text
application/context_app/IDENTITY_CONTEXT_REQUIREMENTS.md
share/20260816_1752_application_to_identity_integration_phase1b_identity_readiness.md
```

## Scope

v1 supports:

```text
entity_kind = character
coverage    = one provider + source_id
canonical target class = Character base identity
```

Input identity is only:

```text
provider
source_id
```

Portable state is intentionally not an identity input.

Forbidden:

```text
current_element -> canonical form synthesis
name -> canonical ID guessing
slug -> canonical ID guessing
profile.json existence -> targeted base identity acceptance
review-work candidate -> Production identity
```

Therefore the current Traveler invariant is:

```text
(hoyolab, character, 10000005)
  -> aether

current Account element may be Cryo
  -> no aether_cryo synthesis
```

## Production inputs

The targeted validator consumes:

```text
Domain-owned normalized Source Alias projection
  provider,entity_kind,source_id,canonical_id

Character-owned Production Registry
  data/official/characters/identity_registry.json
```

Current Character Registry v1 is intentionally partial. A targeted PASS does not
authorize global Registry cutover.

## Result contract

Interface identifier:

```text
identity_targeted_readiness_v1
```

Machine-readable JSON fields:

```text
interface_version
coverage_scope
coverage.requested
coverage.resolved
full_fixture_claim
entity_kind
provider
source_id
canonical_id
canonical_kind
owner_readiness
diagnostics[]
trace.projection_contract
trace.alias_origin
trace.character_identity_registry
trace.character_identity_registry_schema_version
trace.owner_contracts[]
```

Semantics:

```text
owner alias missing
  -> owner_readiness = PENDING
  -> canonical_id = null
  -> process exit 0

owner alias exists but canonical base target is absent from Production Registry
  -> owner_readiness = FAIL
  -> canonical_id = null
  -> process exit 1

owner alias exists and canonical base target exists in Production Registry
  -> owner_readiness = PASS
  -> canonical_id = accepted stable base identity
  -> process exit 0
```

`canonical_id` is intentionally emitted only for PASS.

Coverage fields:

```text
coverage_scope    = targeted_single_source
full_fixture_claim = NOT_MADE
```

This prevents a targeted PASS from being interpreted as full fixture or full
roster readiness.

## CLI

From repository root:

```bash
python3 integration/identity/targeted_identity_readiness.py \
  --provider hoyolab \
  --source-id 10000005 \
  --character-identity-registry data/official/characters/identity_registry.json \
  --alias-file data/official/characters/source_aliases/hoyolab_character_aliases.csv \
  --json
```

Current expected targeted result:

```text
provider         = hoyolab
entity_kind      = character
source_id        = 10000005
canonical_id     = aether
canonical_kind   = traveler_base
owner_readiness  = PASS
coverage_scope   = targeted_single_source
full_fixture_claim = NOT_MADE
```

## Full-readiness separation

The existing cross-domain full validator remains a separate gate:

```text
integration/identity/identity_integration_validator.py
```

Until Character Collection authorizes and materializes sufficient Registry
coverage for global cutover, the targeted interface does not upgrade or replace
full Account-roster readiness.

In particular:

```text
targeted Aether PASS
  != full Character roster PASS
  != full Account identity PASS
  != form resolution PASS
  != executable capability PASS
```

Unresolved Character / Weapon / Artifact rows remain governed by their existing
PENDING / FAIL gates.

## Character Registry schema boundary

The current targeted implementation accepts Production Character Identity
Registry schema v1 only.

Unknown Registry schema versions fail closed:

```text
input_error / FAIL
```

A reviewed future Registry version must be explicitly added to this interface
after Character Production materialization; review-work rows are not consumed
early.

## Tests / CI

Synthetic regression:

```text
integration/identity/targeted_identity_readiness_test.py
```

Required cases include:

```text
Aether base target resolves without profile/form dependency
missing owner alias -> PENDING
missing canonical base target -> FAIL
form identity cannot satisfy a base alias target
duplicate base identity -> FAIL
unknown Registry schema -> FAIL
```

The Identity Integration workflow also runs the real Production Aether targeted
validation separately from full-fixture readiness.
