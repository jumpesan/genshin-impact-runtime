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

## 2. Artifact candidate vs resolved artifact semantics

A platform/locale mapping may identify an artifact candidate without resolving the selected artifact's full runtime semantics.

Preserve:

```text
artifact_candidate_resolved
!= selected_USER_DISTRIBUTABLE_resolved
!= user_device_procedure_ready
```

The candidate mapping may be sufficient to know a filename or public path, but a user-device procedure depends on the selected manifest-declared `USER_DISTRIBUTABLE` record.

Before procedure generation can be complete, resolve exactly one applicable `USER_DISTRIBUTABLE` from the selected runtime revision.

That resolved record supplies runtime-owned semantics including at least:

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
portable_ingestion
```

If the candidate is known but the matching record is unresolved, preserve that distinction. Do not allow model memory or generic platform knowledge to silently stand in for unresolved runtime-owned operands.

## 3. Artifact identity and attachment semantics

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

## 4. Guidance is an executable user procedure

Post-delivery guidance is complete only when a normal user can perform every required transition from the current state to the artifact's declared output without independently discovering a missing operand.

Interpret procedure construction as dependency resolution:

```text
required user transition
-> required action
-> operands required by that action
-> authority that owns each runtime operand
-> resolved operand value
-> user-presentable action
```

For each user-device transition, resolve the operands required to perform that action from authoritative runtime metadata/contracts before considering the procedure ready.

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

A generic semantic label is not the resolved value of an operand. For example, identifying that an action is "navigate to the record page" does not by itself resolve the destination required to perform that navigation.

## 5. Entrypoint derivation rule

If an applicable USER_DISTRIBUTABLE has a non-empty `entrypoint_url`, and producing its declared output requires the human user to operate against that external entrypoint, then the user-device procedure has a required navigation operand.

Its authority is:

```text
selected USER_DISTRIBUTABLE.entrypoint_url
```

Interpret the dependency as:

```text
external navigation required
+ selected USER_DISTRIBUTABLE resolved
+ authoritative entrypoint_url exists
-> navigation operand is resolved from that field
-> procedure can expose the resolved destination in an actionable form
```

This is a semantic requirement, not a string-copy requirement.

A generic phrase such as "open the service", "open the record page", or "open Battle Chronicle" represents the action class but leaves the destination operand unresolved from the user's point of view.

Conversely, do not hardcode or invent an endpoint independently of the selected manifest record. If `entrypoint_url` is absent or unresolved, preserve that unresolved state rather than filling it from model knowledge.

## 6. Guidance completeness check

Before presenting user-device guidance, reason over the procedure as a dependency graph and verify:

```text
selected USER_DISTRIBUTABLE is resolved

for every required user action:
  action is identifiable
  required operand(s) are resolved
  each runtime-owned operand has an authoritative source
  user can perform the action from the presented guidance

for every runtime-owned operand:
  source of truth is the selected runtime metadata/contract
  no model-memory substitution occurred
```

If a required operand is missing from the response, guidance is incomplete even when the LLM itself knows what the omitted value should have been.

The acceptance criterion is behavioral:

```text
same selected runtime metadata
+ same user platform/state
-> semantically equivalent complete procedure
```

Exact wording, formatting, numbering, and whether an actionable destination is rendered as plain URL or link text are presentation choices unless another contract constrains them.

## 7. Stable boundaries

```text
USER_DISTRIBUTABLE != instruction
USER_DISTRIBUTABLE != TRUSTED_EXECUTABLE
artifact_candidate_resolved != selected_USER_DISTRIBUTABLE_resolved
selected_USER_DISTRIBUTABLE_resolved != user_device_procedure_ready
artifact retrieval != artifact execution
security scan != artifact execution
scan pass != trusted authority
fallback_link != delivered
commit_sha != release_tag
runtime metadata != model memory
generic action label != resolved operand
unresolved operand != guessed operand
```
