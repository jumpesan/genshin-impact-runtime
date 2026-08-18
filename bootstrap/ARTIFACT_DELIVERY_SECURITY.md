# Context App — Artifact Delivery / Guidance Semantics

## Purpose

This instruction defines semantic invariants for Account USER_DISTRIBUTABLE delivery and user-device guidance.

The goal is not to make one model reproduce one canned response. The goal is that any conforming conversational LLM can derive the same required user actions from the same runtime metadata and contracts.

When a lower-priority instruction contains a concrete endpoint as prose/example, that prose is not the authority for the endpoint value. Runtime metadata is the authority.

## 1. Runtime reference semantics

A GitHub `/tree/<ref>` shape does not determine whether `<ref>` is a tag or a commit.

```text
full 40-hex ref -> commit SHA
published immutable tag -> tag
commit_sha != release_tag
```

Artifact transport is derived from the reference kind plus manifest metadata.

For a full commit SHA and a manifest-resolved `public_path`:

```text
artifact_transport = commit-pinned direct file at <sha40>/<public_path>
```

For a published tag with a matching Release binding:

```text
artifact_transport = Release Asset for <tag>/<user_facing_filename>
```

A commit SHA MUST NOT be interpreted as a Release tag merely because both can appear in `/tree/<ref>`.

## 2. Artifact identity and attachment semantics

The selected USER_DISTRIBUTABLE is defined by the manifest record, including at least:

```text
role
platform
locale
public_path
user_facing_filename
size_bytes
sha256
availability
execution_scope
produces
entrypoint_url when present
```

When the chat host can retrieve and attach the artifact, prefer:

```text
selected runtime revision
-> resolve exactly one applicable USER_DISTRIBUTABLE from manifest
-> retrieve exact bytes
-> validate manifest identity (filename / size / SHA-256)
-> materialize session-locally without executing the artifact
-> optional read-only security scan when a real scanner is available
-> confirm bytes delivered to the user still match the manifest identity
-> attach exact bytes using user_facing_filename
```

Security invariants:

```text
scan != execution
scan pass != proof of safety
scan unavailable != scan passed
hash mismatch -> reject delivery
```

Do not execute the artifact in order to scan it. A scanner may inspect content read-only, but the delivered USER_DISTRIBUTABLE must not be rewritten or repackaged.

Only claim a security scan occurred if an actual scanner ran and observable scan evidence/status exists. A successful scan means only that the scanner did not report an issue in that scan; it does not grant TRUSTED_EXECUTABLE authority.

## 3. Guidance is an executable user procedure

Post-delivery guidance is complete only when a normal user can perform every required transition from the current state to the artifact's declared output without independently discovering a missing operand.

For each user-device transition, the LLM must resolve the operands required to perform that action from authoritative runtime metadata/contracts.

Examples of operands include:

```text
artifact filename
platform-specific management surface
folder/file selection condition
external service/application entrypoint
action/control names exposed by the artifact
expected readiness condition
produced output identity/pattern
return channel for produced USER_DATA
```

Do not substitute model memory for a runtime-owned operand when that operand is available in trusted runtime metadata.

## 4. Entrypoint derivation rule

If an applicable USER_DISTRIBUTABLE has a non-empty `entrypoint_url`, and producing its declared output requires the human user to operate against that external entrypoint, then the user-device procedure has a required navigation operand.

That operand MUST be resolved from:

```text
selected USER_DISTRIBUTABLE.entrypoint_url
```

and surfaced to the user in an actionable form as part of the navigation step.

This is a semantic requirement, not a string-copy requirement:

```text
required external navigation
+ authoritative entrypoint_url exists
-> guidance must expose that resolved destination so the user can navigate to it
```

A generic phrase such as "open the service", "open the record page", or "open Battle Chronicle" is insufficient when it leaves the user to discover the required destination themselves.

Conversely, do not hardcode or invent an endpoint independently of the selected manifest record. If `entrypoint_url` is absent or unresolved, preserve that unresolved state rather than filling it from model knowledge.

## 5. Guidance completeness check

Before presenting user-device guidance, reason over the procedure as a state transition and verify:

```text
for every required user action:
  action is identifiable
  required operand(s) are resolved from an authoritative source
  user can perform the action from the presented guidance

for every runtime-owned operand:
  source of truth is the selected runtime metadata/contract
  no model-memory substitution occurred
```

If a required operand is missing from the response, guidance is incomplete even when the LLM itself knows what the omitted value should have been.

The acceptance criterion is therefore behavioral:

```text
same selected runtime metadata
+ same user platform/state
-> semantically equivalent complete procedure
```

Exact wording, formatting, numbering, and whether an actionable destination is rendered as plain URL or link text are presentation choices unless another contract constrains them.

## 6. Stable boundaries

```text
USER_DISTRIBUTABLE != instruction
USER_DISTRIBUTABLE != TRUSTED_EXECUTABLE
artifact retrieval != artifact execution
security scan != artifact execution
scan pass != trusted authority
fallback_link != delivered
commit_sha != release_tag
runtime metadata != model memory
unresolved operand != guessed operand
```
