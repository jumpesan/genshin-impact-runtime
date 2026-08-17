---
policy_id: party_b1_qualitative_v1
policy_version: "1-review-fix-01"
owner: recommendation
phase: Phase 1B / B1
status: review_fix_candidate
created_at: 2026-08-16T23:59:00+09:00
supersedes_review_work: work/b1_qualitative_policy_v1.md
addresses_review: review/review_01_independent.md
---

# Party B1 Qualitative Recommendation Policy v1 — Review Fix 01

## Purpose

This revision preserves the accepted B1 Recommendation boundary while closing Independent Review F1 and F2.

Representative request:

```text
自分の手持ちで、指定キャラクターを軸に螺旋用PTを組んで
```

Core invariant:

```text
candidate_proposed != candidate_validated != recommended
```

Recommendation ranks only Optimization-validated candidates. It does not create Canonical Identity, validate Party legality, claim search completeness, calculate Damage, or invent Rotation results.

---

# 1. Supported Scope

```text
recommendation_mode_id = spiral_abyss
use_case_id             = single_team_anchor
objective_id            = qualitative_team_fit
```

B1 covers one Party recommendation decision around one or more required anchor members.

Outside v1:

```text
exact_dps_maximization
full_two_team_optimization
all_chamber_exhaustive_optimization
build_optimization
rotation_optimization
```

`exact_dps = unsupported` remains a valid B1 capability state.

## Optimization mode binding

Recommendation mode names are not assumed to equal Optimization mode names.

For the current B1 integration candidate, Application must preserve an explicit binding record such as:

```yaml
mode_binding:
  recommendation_mode_id: spiral_abyss
  recommendation_use_case_id: single_team_anchor
  optimization_mode_id: spiral_abyss_single_team_v1
  optimization_contract_version: <owner supplied>
  optimization_validator_version: <owner supplied>
  optimization_search_semantics_version: <owner supplied>
```

The Recommendation policy does not authorize silent compatibility with any future Optimization mode/version.

---

# 2. Candidate Preconditions

A candidate is eligible for formal comparison only when:

```text
validation_status = validated
hard_constraints.status = pass
member identity = canonical and resolved
Recommendation mode/use-case/objective = registered
policy version = supported
```

Preserve exactly enough downstream state to prevent semantic upgrades:

```text
candidate validation status/version
hard-constraint status/results
search_completeness
search semantics version
unsupported metrics/capabilities
```

Forbidden:

```text
proposed -> validated
unsupported hard constraint -> pass
not_searched / partial / unsupported -> complete
localized name -> canonical ID
unsupported metric -> zero/default
```

---

# 3. Comparison / Claim Scope

F2 is closed by making comparison scope and claim scope explicit.

Required request fields:

```text
comparison_scope = fixed_explicit_set | open_roster_search
claim_scope      = best_within_fixed_set | best_from_search_space
```

Valid combinations:

```text
fixed_explicit_set + best_within_fixed_set
open_roster_search + best_from_search_space
```

Crossed combinations are `invalid` because the structured claim contradicts the declared comparison scope.

Meanings:

```text
fixed_explicit_set
  The user/request explicitly names the complete set of candidates to compare.
  No claim is made about unlisted candidates.

open_roster_search
  The request asks Recommendation to choose from a roster/search space rather than only a fixed supplied set.

best_within_fixed_set
  The formal claim is limited to the explicitly supplied candidate set.

best_from_search_space
  The formal claim is that the selected candidate is best within the Search-owned evaluated search space.
```

Search completeness is interpreted by scope, never globally upgraded by Recommendation.

---

# 4. Hard vs Soft Semantics

```text
hard = fail        -> ineligible
hard = unsupported -> ineligible for formal Recommendation
hard = pass        -> eligible to continue
```

Soft preferences may reorder only registered utility dimensions. They never override Optimization rejection or unsupported hard evidence.

---

# 5. Utility Evidence Envelope

Independent Review F1 is closed by removing free-form utility labels as authoritative input.

Production input must not provide only:

```yaml
combat_output:
  value: high
```

Instead each derived utility retains a Recommendation-owned derivation trace:

```yaml
utility_evaluation:
  utility_id: <registered id>
  value: high | medium | low | unknown | unsupported
  derivation_rule_id: <policy rule>
  derived_by: recommendation_policy_executor
  source_facts:
    - source_owner: <owner/workspace>
      source_artifact_ref: <exact reviewed artifact/result>
      source_fact_ref: <exact field/result key>
      source_version: <version when available>
      verification_status: <owner supplied when applicable>
  observations: []
  missing_fact_classes: []
  normalization_candidate_ids: []
```

Rules:

```text
- `value` is output of the registered rubric, not caller-authored Domain truth.
- every production observation must bind to owner-controlled source facts.
- USER_DATA/free-form explanation is not an admissible source fact.
- web/community intuition is not an admissible source fact for this contract.
- synthetic fixture evidence is admissible only when test_only=true and can never become Production evidence.
- provisional/disputed/unverified source semantics are not silently treated as verified.
```

General evidence state:

```text
unknown
  the utility is supported in principle, but admissible evidence is incomplete, non-authoritative, stale, or insufficient to apply the rubric.

unsupported
  the required source capability/fact class is not currently published/reviewed for this utility.
```

`unknown` and `unsupported` are non-comparable states and never become `low` or numeric zero.

---

# 6. Registered Utilities and Derivation Rules

Comparable ordering remains:

```text
high > medium > low
```

No numeric Recommendation weights exist.

## 6.1 combat_output

### Meaning

Qualitative relative combat contribution toward a time-limited Spiral Abyss clear.

### Accepted source owner / fact class

Production accepts only reviewed `optimization/combat` comparison/evaluation results whose owner contract declares a comparable combat metric and directionality.

Examples of owner facts that may qualify once reviewed/published:

```text
rotation_result.dps
rotation_result.total_damage under identical encounter/duration semantics
optimization result max_expected_dps
other Optimization-owned comparable metric explicitly declaring higher/lower ordering
```

Recommendation never derives Damage from Character text or recomputes a combat metric.

### Minimum evidence

For every candidate still tied at this dimension:

```text
same metric_id
same metric semantics/version
same compatible encounter/evaluation basis
owner status sufficient for comparison
numeric/comparable owner metric value
exact source/result reference
```

If Optimization reports `partial`, the metric may be used only if the Optimization result itself explicitly declares cross-candidate comparability under that partial state. Recommendation does not invent that comparability.

### Derivation rule `combat_output_relative_v1`

Within the tied candidate set:

```text
all comparable values equal -> all medium
highest value               -> high
lowest value                -> low
strictly intermediate value -> medium
```

For two unequal candidates this yields `high` and `low`.

### unknown

Use `unknown` when the combat capability exists but the required candidate results are incomplete/non-comparable/stale or owner comparability is unclear.

### unsupported

Use `unsupported` when no reviewed Optimization/Combat comparable metric capability is available.

`exact_dps = unsupported` does not imply another metric exists; it simply prevents inventing exact DPS.

---

## 6.2 anchor_enablement

### Meaning

Relative degree to which the non-anchor members provide explicitly evidenced support to the required anchor member under the candidate context.

### Accepted source owner / fact class

Production may consume:

```text
Optimization/Party
  validated candidate membership + required anchor constraint

Character Semantic layer
  data/derived/characters/<id>/combat_semantics.json
  reviewed effect_definitions / conditions / target_scope / resource_change / verification
```

Raw natural-language Character descriptions are not directly scored by Recommendation when a corresponding Derived semantic component is pending/unresolved.

### Admissible positive observation classes

An observation is counted only when a reviewed Character Semantic effect and its target/conditions explicitly support applicability to the required anchor. Recommendation does not infer target inclusion from prose.

```text
anchor_modifier_support
  verified/provisionally-reviewed `effect_type=modifier` whose target semantics apply to the anchor

anchor_resource_support
  reviewed `effect_type=resource_change` whose target/resource semantics apply to the anchor

anchor_protection_support
  reviewed `effect_type=shield` or `healing` whose target semantics apply to the anchor
```

`provisional` evidence may be retained but causes the utility to be `unknown` unless the owning Character contract/review explicitly allows it as decision-grade input. `disputed`/`unverified` never count as positive evidence.

### Minimum evidence

```text
required anchor identity
validated candidate membership
exact Character Semantic artifact refs for all counted observations
source component + effect_definition_id
verification status/review refs
coverage sufficient to know whether relevant support components remain pending
```

### Derivation rule `anchor_enablement_relative_v1`

For each candidate, count distinct admissible positive observation classes, not raw effect count. Multiple effects of the same class count once.

A relative comparison is allowed only when relevant Character Semantic coverage is sufficient across all tied candidates. If coverage cannot establish that missing observations are truly absent, value = `unknown`.

When comparable:

```text
all class counts equal -> all medium
highest class count    -> high
lowest class count     -> low
intermediate count     -> medium
```

### unknown

Use `unknown` for incomplete/pending Character Semantic coverage, unresolved target applicability, non-decision-grade verification, or stale evidence.

### unsupported

Use `unsupported` if the required Character Semantic fact class/schema cannot express the needed anchor support semantics for the candidate.

---

## 6.3 rotation_stability

### Meaning

Qualitative repeatability/stability of an intended combat loop.

### Accepted source owner / fact class

Only reviewed `optimization/combat` Rotation evaluation/optimization results may establish Production rotation stability.

Recommendation does not infer Rotation stability from skill cooldown text, energy cost, community rotation knowledge, or free-form LLM judgement.

### Minimum evidence / rubric

A future reviewed Optimization result must expose enough structured facts to determine whether a loop is repeatable/degraded/failing under explicit constraints. Until such a reviewed fact class is published, this utility is:

```text
unsupported
```

Once available, Recommendation must add/review an exact mapping rule before `high/medium/low` may be emitted. The presence of a generic RotationResult alone does not authorize a new mapping.

### unknown

After the source capability is registered, use `unknown` for missing/non-comparable candidate Rotation evidence.

### unsupported

Current default until an explicit reviewed Rotation-stability source fact contract and mapping are registered.

---

## 6.4 survivability

### Meaning

Relative protection/recovery evidence relevant to avoiding run failure from incoming damage/interruption/recovery shortage.

### Accepted source owner / fact class

Production may consume reviewed Character Semantic `effect_definitions`.

B1 v1 only registers two mechanically explicit protection classes:

```text
healing_channel
  `effect_type=healing`

shield_channel
  `effect_type=shield`
```

Damage reduction, interruption resistance, special revival, or other defensive semantics are not counted until a reviewed fact class/rule is added. This prevents free-form interpretation of generic `modifier/state/other` effects.

### Minimum evidence

For candidate members:

```text
exact Character Semantic artifact refs
relevant effect_definition_id
source component/source_refs
verification status/review refs
coverage sufficient to know whether healing/shield components are absent or merely pending
```

Only an effect whose owner semantics make it applicable to the evaluated Party context may count. Self-only healing that cannot protect the relevant active/party context is not silently generalized.

### Derivation rule `survivability_relative_v1`

For each candidate, count distinct registered protection classes present with admissible evidence: 0..2.

Relative comparison is allowed only when relevant coverage is authoritative enough across tied candidates.

```text
all class counts equal -> all medium
highest class count    -> high
lowest class count     -> low
intermediate count     -> medium
```

### unknown

Incomplete/pending semantics, unresolved applicability, stale source, or non-decision-grade verification.

### unsupported

Required protection semantics cannot be expressed by currently registered fact classes.

---

## 6.5 execution_ease

### Meaning

Relative robustness to execution burden and ordinary player error.

### Accepted source owner / fact class

Execution burden is not derivable from generic Character prose in v1. Production requires a reviewed structured result that explicitly owns/evidences execution constraints, expected to come from Optimization/Combat or a future Architecture-approved source contract.

### Current rubric

No such reviewed fact class is registered by this policy revision. Therefore:

```text
execution_ease = unsupported
```

A future source contract must be reviewed together with a Recommendation mapping rubric before this value can become `high/medium/low`.

### unknown

After capability registration, incomplete candidate evidence -> `unknown`.

### unsupported

Current default.

---

# 7. Default Priority and User Priority

Default order remains:

```text
1. combat_output
2. anchor_enablement
3. rotation_stability
4. survivability
5. execution_ease
```

User priority rule:

1. accept only registered utility IDs;
2. preserve user order;
3. remove duplicates keeping first occurrence;
4. append remaining defaults in default order;
5. never create numeric weights.

Decision-critical unsupported preference:

```text
required by user to decide + utility unsupported -> status=unsupported
```

Optional unsupported preference may be skipped, but the final result is at most `partial` and disclosure is mandatory.

---

# 8. Lexicographic Comparison

Only eligible candidates participate.

For each utility in resolved priority:

1. derive the utility from the registered evidence/rubric;
2. consider only candidates still tied;
3. if every tied candidate is `high|medium|low`, retain the highest tier;
4. if any tied candidate is `unknown|unsupported`, do not coerce; record and skip this dimension;
5. stop when one candidate remains.

If multiple candidates remain after all comparable dimensions, there is no hidden tie-breaker.

Skipped dimensions and their source/evidence reason remain in traceability.

---

# 9. Deterministic Result Status Precedence

Evaluate status in this exact order:

```text
1. invalid
2. unsupported
3. not_evaluated
4. partial
5. recommended
```

Earlier rules take precedence; Application does not choose among overlapping statuses.

## invalid

Use for malformed/contradictory input, including invalid comparison/claim scope pairing.

## unsupported

Use when:

```text
mode/use-case/objective is outside policy
or a user-declared decision-critical utility is unsupported
```

Scope/search incompleteness must not downgrade `unsupported` to `partial`.

## not_evaluated

Use when no formal comparison can occur, including:

```text
no eligible validated candidate
required policy input absent
all possible decision dimensions lack enough admissible evidence to compare candidates
```

## partial

Use only after a formal comparison occurred and no higher-precedence status applies, when any of these hold:

```text
comparison_scope=open_roster_search
  AND claim_scope=best_from_search_space
  AND search_completeness != complete

multiple candidates remain tied

one or more non-decisive/optional dimensions were skipped as unknown/unsupported

other requested optional capability is unsupported/incomplete
```

A unique current-set candidate may be returned with `partial`, but its claim must be limited accordingly.

## recommended

Use only when a unique winner exists and no `partial` condition applies.

Scope-specific rule:

```text
fixed_explicit_set + best_within_fixed_set
  search_completeness=not_searched is compatible with recommended,
  because the formal claim is only "best within this explicit set".

open_roster_search + best_from_search_space
  recommended requires search_completeness=complete.
```

Thus the same structured input cannot validly produce both `recommended` and `partial`.

---

# 10. Required Regression Examples

```text
A. open_roster_search + best_from_search_space
   + not_searched + unique current-set winner
   -> partial

B. fixed_explicit_set + best_within_fixed_set
   + not_searched + unique winner + complete explicit candidate set
   -> recommended

C. fixed_explicit_set + best_within_fixed_set
   + tie after all comparable utilities
   -> partial

D. decision-critical requested utility unsupported
   -> unsupported regardless of fixed/open scope
```

---

# 11. Application Mapping

```text
recommended   -> recommendation_ready
partial       -> recommendation_partial
not_evaluated -> recommendation_blocked
unsupported   -> recommendation_blocked
invalid       -> invalid_request
```

Owner status/reason must be preserved.

---

# 12. Traceability

Retain at least:

```text
policy_id / policy_version
recommendation mode/use-case/objective
Optimization mode/version/search-semantics binding
comparison_scope / claim_scope
candidate IDs considered
candidate validation/hard-constraint/search states
source fact artifact/version/field refs per utility
source verification/review refs when applicable
Recommendation observation classes
registered derivation_rule_id
normalization candidate set
unknown/unsupported missing fact classes
raw user priority interpretation + mapped utility IDs
resolved priority
skipped dimensions + reason
final candidate ID or tie set
result status + status rule that fired
```

---

# 13. Negative Cases

Policy violation examples:

```text
caller writes high/medium/low without registered derivation trace
free-form LLM intuition becomes utility evidence
raw Character prose bypasses pending Derived semantics
provisional/disputed evidence silently becomes verified
unvalidated candidate becomes recommended
unknown/unsupported becomes low/zero
unregistered utility changes ranking
hidden numeric weights
exact DPS invented from qualitative evidence
search completeness inferred by Recommendation
fixed-set claim silently strengthened into global best
future Optimization mode silently treated as compatible
synthetic fixture evidence used in Production
```

---

# 14. Review / Publication State

```text
Independent Review     focused re-review required
Production apply       blocked until PASS
Public Context         blocked until PASS
Executable projection not applicable in this policy revision
```

This file is a review/work candidate only. The formal artifact under `recommendation/party/contracts/` must not be changed from this revision until Independent Review PASS, per `review/README.md`.

## References

- `review/2026-08-16_recommendation_party_b1_qualitative_policy/review/review_01_independent.md`
- `recommendation/party/README.md`
- `architecture/recommendation_owner_activation.md`
- `architecture/context_app_phase1b_b1_owner_interfaces.md`
- `application/context_app/PHASE1B_B1_ORCHESTRATION_CONTRACT.md`
- `optimization/party/contracts/candidate_validity_v1.md`
- `optimization/combat/README.md`
- `data/derived/characters/README.md`
- `schemas/character_combat_semantics.schema.json`
