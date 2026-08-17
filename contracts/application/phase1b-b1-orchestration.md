# Phase 1B B1 Orchestration Contract Projection

Status:

```text
owner = application
publication = candidate
recommendation capability = not_evaluated
release_status = candidate
```

This contract defines Application/LLM execution lifecycle only. It does not own Recommendation, Search, Optimization, Identity, Damage, or Runtime semantics. The current Public Candidate separately publishes reviewed owner artifacts under their existing authority boundaries; their presence does not widen Application authority.

## Goal

```text
User request
  -> LLM intent / constraints
  -> LLM candidate proposal OR owner-approved enumeration
  -> deterministic Party candidate validation
  -> registered Recommendation policy comparison when reviewed execution/evidence authority exists
  -> final recommendation / alternatives / limitations only when formally available
```

B1 permits:

```text
exact_dps = unsupported
```

and forbids replacing it with inferred DPS.

## Invariant

```text
candidate_proposed != candidate_validated != search_complete
candidate_validated != recommended
not_searched != search_complete=true
unsupported != zero
```

## Required dependencies for validated qualitative recommendation

```text
usable Account/User Context
canonical member identity
Search/Optimization candidate-validity contract + deterministic capability
Recommendation mode/constraint/utility/trade-off policy required by the request
```

Combat/Runtime/Damage are optional in B1 unless the selected Recommendation policy requires their metrics.

## No fallback

```text
Party/Search validation absent
  -> candidate stays candidate_proposed

Recommendation policy/execution authority absent
  -> no formal final ranking

Identity unresolved
  -> identity_pending

exact DPS absent
  -> unsupported
```

Application does not invent owner semantics to continue.

## Candidate lifecycle

```text
CANDIDATE_PLANNED
  -> CANDIDATE_PROPOSED
  -> CANDIDATE_VALIDATED | CANDIDATE_REJECTED | VALIDATION_UNAVAILABLE
  -> QUALITATIVE_COMPARISON_READY
  -> RECOMMENDATION_READY | RECOMMENDATION_PARTIAL | RECOMMENDATION_BLOCKED
```

## Final LLM recommendation requirements

```text
candidate validated
hard constraints PASS
required Recommendation policy available
registered utility dimensions only
owner metrics/status preserved
user priorities preserved
partial/unsupported preserved
```

If combat rank and final recommendation differ, preserve both and record the policy/user-priority reason.

## Search completeness

Only Search/Optimization owner result semantics may establish:

```text
search_complete
search_partial
search_unknown
```

The reviewed Optimization Party validator currently reports:

```text
search_completeness = not_searched
```

A small LLM proposal set or a validated Party candidate is never proof of exhaustive search.

## Executable boundary

Application may invoke only manifest-registered reviewed `TRUSTED_EXECUTABLE` paths.

The current candidate publishes the reviewed Optimization Party candidate validator as a `TRUSTED_EXECUTABLE`, but that executable is validator-only and does not provide exhaustive Search semantics. No Recommendation executable/scorer is registered. The Application self-check tool does not validate Party candidates and must not be used as a substitute.

## Current availability

This projection is a candidate-stage Application orchestration contract. Current Public Candidate availability is:

```text
Recommendation B1 contract projection = published / TRUSTED_CONTRACT
Recommendation executable             = absent
Recommendation capability             = not_evaluated
formal final ranking                   = unavailable

Party candidate validator              = published / TRUSTED_EXECUTABLE / validator-only
Party candidate validation capability  = review_pending
Party search_completeness              = not_searched
exhaustive Search capability           = unavailable

release_status                         = candidate
```

Therefore contract presence does not create Recommendation executable/scorer authority, `candidate_validated` does not become `recommended`, and validator-only `not_searched` does not become `search_complete=true`. The current Public Context candidate must not claim positive B1 Recommendation availability.
