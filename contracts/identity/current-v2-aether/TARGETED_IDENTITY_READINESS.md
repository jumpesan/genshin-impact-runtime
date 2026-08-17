# Targeted Identity Readiness v1

## Purpose

`integration/identity/targeted_identity_readiness.py` is the Identity Integration-owned targeted readiness interface for validating one Source Character identity against Domain-owned Production alias + Character Identity Registry data.

It is **not** a Production runtime resolver and does not claim full Account-roster readiness.

Formal upstream contracts:

```text
architecture/identity_integration.md
architecture/character_identity_form.md
```

Current downstream consumer:

```text
application/context_app/IDENTITY_CONTEXT_REQUIREMENTS.md
share/20260817_0106_application_to_identity_integration_registry_v2_loader_blocker_ack.md
```

## Scope

Interface v1 supports:

```text
entity_kind = character
coverage    = one provider + source_id
canonical target class = accepted Character base identity
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

Traveler invariant:

```text
(hoyolab, character, 10000005) -> aether
current Account element may vary -> no aether_<element> synthesis
```

## Production inputs

```text
Domain-owned normalized Source Alias projection
  provider,entity_kind,source_id,canonical_id

Character-owned Production Registry
  data/official/characters/identity_registry.json
```

Current Production Character Registry:

```text
schema_version = 2
base identities = 3
form identities = 0
```

A targeted PASS does not authorize full Character or full Account cutover.

## Result contract

Interface identifier remains:

```text
identity_targeted_readiness_v1
```

Registry schema support is an input-loader compatibility extension; the published targeted result semantics and fields remain unchanged.

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

owner alias exists but canonical base target is absent from accepted Production base identities
  -> owner_readiness = FAIL
  -> canonical_id = null
  -> process exit 1

owner alias exists and canonical target is an accepted Production base identity
  -> owner_readiness = PASS
  -> canonical_id = accepted stable base identity
  -> process exit 0
```

`canonical_id` is emitted only for PASS.

For Registry v2:

```text
base_identity_status = accepted
  -> eligible base identity

relationship.status = resolved
  -> canonical_kind = relationship.kind

relationship.status = pending
  -> base identity is still accepted
  -> canonical_kind = null
  -> no fake/default relationship kind is synthesized
```

This separation is required:

```text
accepted base identity
  != relationship classification complete
  != form identity
  != executable capability
```

Coverage remains:

```text
coverage_scope     = targeted_single_source
full_fixture_claim = NOT_MADE
```

## Character Registry schema boundary

Supported Production schemas:

```text
schema_version = 1
schema_version = 2
```

Registry v1 remains readable for backward compatibility with immutable historical reviewed pins.

Registry v2 is consumed only from the Character-owned Production Registry. Review-work candidates are not valid inputs.

Unknown versions fail closed:

```text
input_error / FAIL
```

Registry v2 validation requires:

```text
canonical_character_id present
base_identity_status == accepted
relationship.status in {resolved, pending}
resolved relationship -> non-empty relationship.kind
no duplicate canonical_character_id
```

Form rows never satisfy a base Source Alias target.

## Current Production Aether result

CLI:

```bash
python3 integration/identity/targeted_identity_readiness.py \
  --provider hoyolab \
  --source-id 10000005 \
  --character-identity-registry data/official/characters/identity_registry.json \
  --alias-file data/official/characters/source_aliases/hoyolab_character_aliases.csv \
  --json
```

Current-main validated result against Registry v2:

```text
provider         = hoyolab
entity_kind      = character
source_id        = 10000005
canonical_id     = aether
canonical_kind   = traveler_base
owner_readiness  = PASS
coverage_scope   = targeted_single_source
full_fixture_claim = NOT_MADE
registry schema  = 2
```

## Full-readiness separation

The full cross-domain validator remains a separate fail-closed gate:

```text
integration/identity/identity_integration_validator.py
```

Therefore:

```text
targeted Aether PASS
  != full Character roster PASS
  != full Account identity PASS
  != form resolution PASS
  != executable capability PASS
```

Current global full-fixture failures must not be suppressed to make the workflow green.

## Tests / CI

Synthetic regression:

```text
integration/identity/targeted_identity_readiness_test.py
```

Current required cases include:

```text
Registry v1 Aether base target resolves
Registry v2 Aether accepted/resolved base resolves
Registry v2 relationship.status=pending still accepts the base without canonical_kind synthesis
Registry v2 non-accepted base status fails closed
missing owner alias -> PENDING
missing canonical base target -> FAIL
form identity cannot satisfy a base alias target
duplicate base identity -> FAIL
unknown Registry schema -> FAIL
```

Current-main CI evidence:

```text
run_id = 31957971144
job_id = 95191450224
head    = e7c37a2b33ed6107087be1b5767cfc883b1bd516

full synthetic regression      PASS / 9
targeted synthetic regression  PASS / 9
real targeted Aether readiness PASS / Registry v2
real full-fixture readiness    FAIL / existing global fail-closed diagnostics
```

The workflow-level result remains failure because the global full-fixture gate is intentionally still red. That does not invalidate the independently proven targeted Production-v2 PASS.
