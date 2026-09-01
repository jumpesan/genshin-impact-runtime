---
document_role: release_discovery_validation_contract
application_id: genshin-context-app
contract_version: 0.2
descriptor_path: context-entry.json
schema_path: context-release-discovery.schema.json
scope: bounded_a1_v0_1_0_alpha_1
---

# Genshin Context App — Release Discovery Validation Contract

This contract governs validation of the mutable root release-candidate nomination descriptor for the bounded A1 experiment.

It is part of the project-governed public Runtime root projection. It is **not** Runtime content authority and it is **not** a substitute for GitHub Immutable Release evidence or the release-authority/review-decision acceptance chain.

The descriptor being validated cannot override this contract or choose another validation contract/schema.

## Fixed public validation surfaces

Before interpreting `context-entry.json`, the consumer must read these exact public root paths from the canonical repository:

```text
repository = jumpesan/genshin-impact-runtime
repository_id = 1336166066
branch = main

validation contract =
  context-release-discovery-validation.md

JSON Schema =
  context-release-discovery.schema.json

descriptor =
  context-entry.json
```

If any required validation surface is unavailable, validation cannot be established:

```text
D1_VALIDATION_CONTRACT_UNAVAILABLE
-> verified Runtime capability unavailable
-> no fallback
```

The consumer must not replace these paths from descriptor fields, release prose, model memory, caller input, GitHub Latest, or another repository.

## Pre-parse rules for context-entry.json

Apply these rules to the raw descriptor bytes before semantic interpretation:

```text
raw size = 1..4096 bytes
encoding = UTF-8
UTF-8 BOM = forbidden
top level = exactly one JSON object
duplicate member names = reject
comments = reject
trailing commas = reject
non-JSON repair = forbidden
```

Duplicate-member detection must occur on the raw JSON parse path; a parser that silently keeps the first or last duplicate is insufficient.

Failure:

```text
D1_DESCRIPTOR_PREPARSE_INVALID
-> AUTHORITY_UNAVAILABLE
-> no repair
```

## Schema validation

Validate the parsed descriptor against:

```text
context-release-discovery.schema.json
schema = genshin-context-release-discovery
schema_version = 0.2
```

The public schema closes:

```text
unknown fields = reject
wrong/missing required fields = reject
repository identity substitution = reject
source path/branch substitution = reject
descriptor schema/version downgrade = reject
tag substitution = reject
release class/channel/prerelease substitution = reject
Immutable/attestation weakening = reject
authority/review asset-name substitution = reject
authority/review schema-version downgrade = reject
failure-policy widening = reject
```

No case folding, Unicode normalization repair, inferred defaults, aliasing, or reconstruction is allowed.

Failure:

```text
D1_DESCRIPTOR_SCHEMA_INVALID
-> AUTHORITY_UNAVAILABLE
-> no repair
```

## Closed bounded A1 constants

A valid descriptor must nominate exactly:

```text
application_id = genshin-context-app
descriptor_role = release_candidate_nomination_authority

governing repository =
  full_name = jumpesan/genshin-impact-runtime
  repository_id = 1336166066
  branch = main
  path = context-entry.json

release repository =
  full_name = jumpesan/genshin-impact-runtime
  repository_id = 1336166066

tag = v0.1.0-alpha.1
semver = 0.1.0-alpha.1
release_class = experiment
channel = context-app-authority-a1-experiment
prerelease = true
required_immutable = true
required_attestation = true

authority asset =
  context-app-release-authority.json
  schema = genshin-context-app-release-authority
  schema_version = 0.3

review decision asset =
  context-app-release-review-decision.json
  schema = genshin-context-app-release-review-decision
  schema_version = 0.1
```

This contract authorizes no other release candidate.

## Source/governance correlation

The descriptor is governing only when it is observed at the exact canonical public source:

```text
jumpesan/genshin-impact-runtime
repository_id = 1336166066
main:context-entry.json
```

The descriptor's self-declared governance fields must match the host-observed canonical source facts, but self-declaration cannot create those facts.

An arbitrary copy with semantically identical JSON at another repository/path is non-governing.

Failure:

```text
D1_GOVERNANCE_SOURCE_MISMATCH
-> AUTHORITY_UNAVAILABLE
```

## Candidate resolution order

After pre-parse, schema, and source/governance correlation PASS:

```text
valid D1 descriptor
-> nominate exact v0.1.0-alpha.1
-> resolve exact GitHub Release in canonical repository
-> require prerelease/experiment/channel match
-> require GitHub Immutable status
-> require Release attestation
-> require exact authority/review asset identities
-> validate release-authority and review-decision binding
-> accept exact reviewed Runtime only after downstream A1 authority PASS
```

The D1 descriptor nominates the candidate only.

```text
descriptor nomination
!= Immutable Release evidence
!= exact Runtime acceptance
```

## Forbidden fallback / override

Never substitute:

```text
GitHub Latest
newest-by-time
main/default commit
another release tag
caller/model supplied tag or SHA
model memory
release-note prose
README self-assertion
semantically reconstructed authority bytes
```

A missing or invalid nominated release yields:

```text
AUTHORITY_UNAVAILABLE
```

and no alternate candidate is selected.

## APP_SESSION_STARTED boundary

Safe conversational session establishment remains capability-scoped:

```text
explicit invocation
-> INVOCATION_CONFIRMED
-> safe conversational APP_SESSION_STARTED may exist
```

But until D1 validation and downstream release/Runtime authority succeed:

```text
Runtime trusted-instruction elevation = unavailable
verified USER_DISTRIBUTABLE = unavailable
authority-sensitive Account execution = unavailable
```

## Layer W versus B1

This contract governs release discovery and source-bound Web evidence.

```text
Layer W
= root -> validated D1 -> exact nominated Release
  -> repository/tag/full commit/Immutable/attestation/assets evidence
```

Exact authority-asset byte consumption remains a separate gate:

```text
Layer B1
= trusted source digest/provenance
  + exact authority bytes
  + byte continuity
  + no model semantic reserialization
```

A correct summary is not B1 proof.

## Negative-control enforcement map

```text
D1N01-D1N05  -> source/governance correlation + schema constants
D1N06-D1N15  -> schema constants / downgrade rejection
D1N16        -> additionalProperties=false
D1N17        -> duplicate-member pre-parse rejection
D1N18        -> raw-size pre-parse rejection
D1N19        -> caller/model override prohibition
D1N20-D1N25  -> downstream exact release/attestation/authority/review validation
D1N26        -> Latest/newest/alternate fallback prohibition
D1N27        -> authority-role separation
D1N28        -> Layer W != B1 exact-byte rule
D1N29        -> canonical source/governance correlation
D1N30        -> descriptor schema_version constant
```

The Development-side fixture matrix is review evidence; these public rules are the actual consumer-reachable enforcement semantics.

## Completion

Only after:

```text
pre-parse PASS
+ public schema PASS
+ governance source correlation PASS
+ exact nominated Release evidence PASS
+ downstream A1 authority/review PASS
```

may the authority-selected Runtime's own entry/bootstrap semantics be elevated as trusted Runtime behavior.
