# Party Candidate Validity Contract v1

## Status

```text
owner                     = optimization
workspace                 = optimization/party/
contract_version          = 1.0.1
validator_version         = 1.0.1
search_semantics_version  = party-validator-only-v1
phase                     = Phase 1B / B1
implementation_scope      = validator-only
review_state              = proposed / focused re-review required
```

This contract defines the minimum deterministic Party candidate validity capability for Context App Phase 1B B1.

Formal boundaries:

- `architecture/optimization_owner_activation.md`
- `architecture/context_app_phase1b_b1_owner_interfaces.md`
- `architecture/context_app_phase1b_recommendation_boundary.md`
- `optimization/README.md`
- `optimization/party/README.md`
- `share/20260816_1753_application_to_optimization_phase1b_b1_party_validation_interface.md`

Mandatory invariant:

```text
candidate_proposed != candidate_validated != search_complete
```

v1 is validator-only, therefore every result uses:

```text
search_completeness = not_searched
```

`validated` never means exhaustive Party search, enumeration, optimality, or complete coverage.

---

## 1. Ownership

Owned here:

```text
Party candidate input shape
registered mode hard-rule validation
request hard-constraint validation
canonical identity coverage gate for all IDs used by validation
owned-roster constraint validation
candidate validity status
reason / diagnostic propagation
validator-only search completeness semantics
```

Not owned here:

```text
Damage Formula / DamageEvent
Rotation / exact DPS
Recommendation utility / ranking policy
natural-language interpretation
canonical identity creation or alias inference
Account acquisition
Party enumeration / pruning / best-candidate claims
```

---

## 2. Supported mode

Initial mode:

```text
spiral_abyss_single_team_v1
```

Hard rules:

```text
minimum members = 1
maximum members = 4
candidate member Canonical Character IDs must be unique
```

This is only a single-team candidate validator. It does not validate two-half/two-team completeness, chamber-specific eligibility, current Abyss conditions, combat viability, DPS, Rotation, Recommendation ranking, enumeration, or pruning.

Unknown `mode_id` is `unsupported` and is never mapped to a known mode.

---

## 3. Canonical identity gate

Every Character ID that participates in validation must be supplied as an exact Canonical Character ID and must be resolved by `validation_context.identity` before the candidate may become `validated`.

Identity-gated fields are:

```text
candidate.members[].canonical_character_id
request_constraints.required_character_ids[]
request_constraints.forbidden_character_ids[]
```

Forbidden:

```text
localized name -> canonical ID inference
source numeric ID -> canonical ID inference
slot/order inference
unresolved identity -> validated
unresolved hard-constraint operand -> pass/fail as if resolved
```

The validator does not define Canonical Character ID lexical syntax beyond a non-empty exact string. Identity semantics remain owned upstream.

Coverage meaning:

```text
complete
  listed IDs are resolved; absence is authoritative unresolved/absent evidence

partial
  listed IDs are resolved; absence is unknown

unavailable
  no usable identity evidence; canonical_character_ids must be []
```

For every identity-gated field:

```text
ID present in identity coverage
  -> resolved

ID absent from complete coverage
  -> unresolved -> unsupported

ID absent from partial coverage
  -> unresolved/unknown -> unsupported

identity unavailable
  -> unresolved -> unsupported
```

v1.0.1 explicitly closes Independent Review F1: unresolved `required_character_ids` or `forbidden_character_ids` can never be treated as ordinary hard-constraint operands.

---

## 4. Input

```yaml
candidate:
  candidate_id: proposal_001
  mode_id: spiral_abyss_single_team_v1
  members:
    - canonical_character_id: aether

request_constraints:
  required_character_ids: []
  forbidden_character_ids: []
  min_member_count: null
  max_member_count: null
  require_owned_roster: false

validation_context:
  identity:
    status: complete | partial | unavailable
    canonical_character_ids: []
  owned_roster:
    status: complete | partial | unavailable
    canonical_character_ids: []
```

All three top-level objects are required. Unknown fields are `invalid` rather than ignored.

### Candidate

```text
candidate_id  non-empty string
mode_id       non-empty string
members       array of {canonical_character_id}
```

Duplicate candidate members are a supported Party-rule failure and produce `rejected`.

### Request constraints

```text
required_character_ids   unique canonical ID array, default []
forbidden_character_ids  unique canonical ID array, default []
min_member_count         null or non-negative integer
max_member_count         null or non-negative integer
require_owned_roster     boolean, default false
```

Contradictory input is `invalid`, including:

```text
same ID in required and forbidden
min_member_count > max_member_count
registered-mode min/max contradiction
```

### Owned roster

When `require_owned_roster = true`:

```text
member present in roster coverage
  -> pass

member absent from complete roster coverage
  -> fail -> rejected

member absent from partial roster coverage
  -> unknown -> unsupported

roster unavailable
  -> unsupported
```

If identity coverage is `complete`, every supplied owned-roster ID must also exist in that complete identity set; otherwise the validation context is contradictory and `invalid`.

---

## 5. Output

```yaml
contract_version: 1.0.1
validator_version: 1.0.1
candidate_id: proposal_001
status: validated | rejected | unsupported | invalid
hard_constraints:
  status: pass | fail | unsupported
  results: []
reasons: []
search_completeness: not_searched
search_semantics_version: party-validator-only-v1
```

Candidate status:

```text
validated
  every required v1 rule is supported and passes

rejected
  at least one supported hard rule definitively fails

unsupported
  no supported hard rule fails, but at least one required identity/rule/capability is unresolved

invalid
  malformed or contradictory contract input
```

Aggregate precedence:

```text
known hard-rule fail > unsupported > pass
```

`unsupported` is never coerced to `pass`.

For unresolved request-constraint IDs specifically:

```text
identity.constraint_ids_resolved = unsupported
request.required_members          = unsupported if any required ID unresolved
request.forbidden_members         = unsupported if any forbidden ID unresolved
```

A resolved required/forbidden ID retains normal pass/fail semantics.

---

## 6. Stable rule order

```text
1. mode.registered
2. mode.member_count
3. party.unique_members
4. identity.members_resolved
5. identity.constraint_ids_resolved
6. request.required_members
7. request.forbidden_members
8. request.min_member_count
9. request.max_member_count
10. request.owned_roster
```

Stable rule and reason order is part of deterministic behavior.

---

## 7. Reason codes

```text
invalid_contract_input
mode_not_supported
mode_rule_unavailable
mode_member_count_out_of_range
duplicate_party_member
canonical_identity_unresolved
canonical_constraint_identity_unresolved
required_character_identity_unresolved
forbidden_character_identity_unresolved
required_character_missing
forbidden_character_present
request_min_member_count_not_met
request_max_member_count_exceeded
candidate_contains_unowned_character
owned_roster_membership_unknown
```

Reason codes are diagnostics, not Recommendation ranking features.

---

## 8. Search completeness

No candidate enumeration or Party search is performed.

```text
search_completeness = not_searched
search_semantics_version = party-validator-only-v1
```

Forbidden claims:

```text
validated -> complete
accepted candidate -> best candidate
LLM proposals exhausted -> complete
unknown coverage -> complete
```

Future enumeration/search requires a separately reviewed contract defining finite search space, pruning, approximation, and completeness semantics.

---

## 9. Determinism and side effects

The reference validator:

```text
is deterministic
has no network access
has no master/account mutation
does not mutate input objects
uses no randomness
uses no LLM call
```

Same request + same validator version + same owner-supplied context produces the same structured result.

---

## 10. Reference implementation and tests

```text
optimization/party/tools/party_candidate_validator.py
optimization/party/tests/test_party_candidate_validator.py
optimization/party/tests/test_party_candidate_validator_review_fix_f1.py
```

CLI:

```bash
python optimization/party/tools/party_candidate_validator.py request.json
```

Exit codes:

```text
0  parsed domain result: validated/rejected/unsupported
2  malformed JSON or status=invalid
```

---

## 11. Review / Public Context gate

Independent Review 01 returned `NEEDS_FIX` for F1 only. v1.0.1 is the Producer correction and requires focused re-review.

Public Context candidate paths remain:

```text
contracts/optimization/party-candidate-validity-v1.md
tools/optimization/party_candidate_validator.py
```

Required before trusted Public Context use:

```text
Focused Independent Review PASS
Context Review
Sandbox Review
Public Candidate export / integrity checks
```

Until those gates pass:

```text
public_context_readiness = not_ready
```
