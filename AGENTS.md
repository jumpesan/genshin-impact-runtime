---
document_role: application_semantic_context
audience: conversational_llm
application_id: genshin-context-app
---

# Genshin Context App — Application Semantic Context

## Purpose

This document defines how normal Context App conversation resolves repository-owned Genshin tasks after bootstrap.

The objective is reproducible interpretation: the same user state, runtime authority, and task should converge on equivalent capability resolution and result semantics even when natural-language presentation differs.

Bootstrap semantics live in `bootstrap/BOOTSTRAP.md`. Artifact security boundaries live in `bootstrap/ARTIFACT_DELIVERY_SECURITY.md`.

## 1. Application state continuity

The normal progression is:

```text
APP_SESSION_STARTED
-> Account bootstrap
-> ACCOUNT_CONTEXT_READY
-> USER_GOAL_REQUIRED
-> APPLICATION_TASK_ROUTING
```

A user may explicitly choose to work without Account Context. Features whose inputs depend on Account Context then retain that missing-input state.

Once `ACCOUNT_CONTEXT_READY` is established, the supplied Portable User Context represents current user state as `USER_DATA`.

## 2. Runtime authority model

Interpret repository resources by manifest role:

```text
USER_DATA          = current user/account state supplied by the user
TRUSTED_CONTRACT   = owner semantics, schemas, interfaces, capability meaning
DATA_REFERENCE     = repository-projected game/mechanics facts
TRUSTED_EXECUTABLE = registered deterministic implementation
USER_DISTRIBUTABLE = artifact handed to the human user for user-device execution
```

`context-manifest.json` is the registry for runtime roles and capability states.

A repository-owned result is grounded in the authority that owns that result. Natural-language presentation may be composed freely after the authoritative result or status has been resolved.

An embedded executable payload in this document is a delivery transport only. It does not grant executable authority. Executable authority still requires the exact path to be registered in `context-manifest.json` as `TRUSTED_EXECUTABLE` and the materialized bytes to match the embedded content identity.

## 3. Task interpretation

For each in-app Genshin request, infer the user's goal and the capabilities needed to answer it.

Typical capability classes include:

```text
account_state
identity_resolution
static_game_data
party_candidate_validation
recommendation
exact_damage_or_dps
reaction_or_runtime_numeric
```

A request may need more than one capability. Resolve them independently and preserve each status.

Semantic flow:

```text
USER_QUERY
-> USER_GOAL
-> REQUIRED_CAPABILITIES
-> AUTHORITY_RESOLUTION
-> REQUIRED_EXECUTION / DATA RESOLUTION
-> STRUCTURED_RESULT OR STATUS
-> USER_PRESENTATION
```

The user is expected to speak in ordinary Genshin terms. Internal capability names, repository paths, source IDs, or schema terminology are implementation details resolved by the Application when possible.

## 4. Capability state

Capability state is part of the result semantics.

Representative states include:

```text
available
partial
unsupported
invalid
identity_pending
source_pending
review_pending
not_evaluated
```

Use the state declared by the current runtime and the owner contract. A result remains unavailable or partial until the capability and its required inputs support a stronger result.

## 5. Deterministic execution

When a requested repository-owned result is defined by a deterministic implementation, resolve execution through the runtime registry.

```text
required deterministic capability
+ capability state permits execution
+ required inputs resolved
+ manifest-registered TRUSTED_EXECUTABLE resolved
-> resolve exact executable delivery transport
-> materialize exact executable + required inputs into a compatible execution environment
-> verify materialized executable identity when an identity record is supplied
-> execute registered implementation
-> consume its structured output
-> preserve its result/status semantics
```

The authoritative deterministic result is the execution output, not a reimplementation of the algorithm in conversational reasoning.

### Acquisition plane and execution plane

Resource acquisition and deterministic execution are separate capabilities.

```text
DELIVERY PLANE
selected immutable runtime
+ registered executable path
-> exact runtime resource identity
-> embedded exact payload when one is registered for that path
   OR host exact-resource retrieval when no embedded payload is available
-> materialize resource bytes/content

OFFLINE EXECUTION PLANE
materialized registered executable
+ materialized required input
+ compatible sandbox/runtime
-> verify executable identity
-> execute
-> structured result
```

Do not infer that a code-execution sandbox has outbound network capability merely because it can run Python or shell commands. Network retrieval from inside the execution sandbox is only an applicable acquisition path when that environment explicitly provides such access.

For a sandbox without outbound network access, shell/Python network clients such as `curl`, `wget`, `urllib`, or `requests` are not the normal resource-acquisition mechanism.

### Embedded exact-payload transport

An embedded payload record is applicable only when all of the following resolve:

```text
record.path == required registered executable path
record.path is present in manifest registry.trusted_executable
record encoding is supported by the execution environment
payload decodes successfully
materialized byte length == decoded_size_bytes
SHA-256(materialized bytes) == record.sha256
Git blob identity(materialized bytes) == record.git_blob_sha
```

Git blob identity is computed as SHA-1 over:

```text
b"blob " + decimal_byte_length + b"\0" + materialized_bytes
```

When an applicable embedded payload exists, use it as the executable delivery transport before attempting external network retrieval. This removes dependence on fresh GitHub page/search/cache availability while retaining the registered path as executable authority.

If payload decoding or either identity check fails:

```text
materialization = invalid
execution = not performed
result = fail closed with concrete payload identity blocker
```

Do not repair, reconstruct, or conversationally rewrite a failed embedded payload.

### Exact-resource acquisition fallback

When no applicable embedded payload exists, resolve:

```text
selected immutable runtime locator
+ registered executable path
-> exact runtime resource identity
```

Resource identity remains fixed across acquisition mechanisms. Any acquisition fallback must preserve:

```text
same repository
same immutable runtime revision
same registered path
same resource content identity
```

A discovery/search result does not substitute for the registered executable. Unrelated search matches, reconstructed source, or conversational reimplementation are not equivalent resources.

The following do not by themselves establish execution unavailability:

```text
registered executable is not preloaded in the sandbox
registered executable has not yet been materialized
sandbox networking is unavailable
one acquisition mechanism fails
source-specific repository connector is unavailable or intentionally unused
```

When the host has an exact-resource retrieval capability separate from the execution sandbox, use that retrieval plane before classifying the executable as unobtainable.

Only after exact resource delivery, materialization, identity verification when applicable, and execution capabilities have been resolved may the deterministic operation be classified as unavailable. Preserve the concrete blocker, distinguishing at least:

```text
resource identity unresolved
embedded payload identity mismatch
host exact-resource retrieval unavailable
materialization failure
incompatible execution runtime
missing required input
execution error
```

A conversational reimplementation or ad-hoc structural check may provide diagnostic observations, but it cannot substitute for the registered executable, cannot establish its authoritative result, and cannot upgrade a repository-owned deterministic status.

This applies to exact DPS, deterministic reaction/runtime numbers, validators, and other registered deterministic functions.

### Embedded payload record — Account Portable User Context validator

This record transports the exact bytes for the registered path `tools/account/validate_portable_context.py`.

```text
path               = tools/account/validate_portable_context.py
encoding           = gzip+base64
decoded_size_bytes = 20541
sha256             = 0a363c3f88c9b5585567a846384984bbbd81bf2cf314f8e21a08d89c05cd2331
git_blob_sha       = 4b62d77aa480f1d1fd0f790f3142e4b09cb22aab
```

Payload (`gzip+base64`, one continuous value):

```text
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
```

## 6. Identity resolution

Identity is repository-owned whenever Account/source identity must be converted into a canonical or user-facing character identity.

Interpret natural questions such as character identification through the same authority model:

```text
natural target description
-> resolve target from USER_DATA when needed
-> obtain source identity
-> resolve Identity capability and owner contract
-> resolve registered Identity implementation when the capability is executable
-> execute with resolved inputs
-> consume canonical identity/status
-> present a natural character identity to the user
```

When Identity authority is unresolved, preserve an Identity status rather than converting source IDs through unrelated knowledge.

## 7. Static data and qualitative reasoning

Static repository-owned facts resolve through accepted `DATA_REFERENCE` and owner contracts.

Qualitative reasoning may combine multiple resolved repository facts and user state. The resulting explanation should distinguish repository-supported facts from ordinary conversational interpretation when that distinction matters to the user's decision.

## 8. Presentation semantics

User-facing responses are conversational application output rather than a rendering of internal state names.

Presentation may vary in:

```text
wording
ordering
amount of explanation
use of prose vs concise lists
link rendering
```

Semantic acceptance focuses on whether the response uses the resolved authority, preserves capability/result status, and gives the user the information needed for the next action.

## 9. Diagnostics

When the user asks how a repository-owned result was obtained, report the session facts available for that result, such as:

```text
selected runtime revision
resolved capability
owner contract/data authority
registered executable when applicable
exact resource identity
delivery transport used / blocking condition
whether materialization occurred
whether identity verification succeeded
execution environment
whether execution occurred
result status
```

Diagnostics describe what actually happened in the session; they are not required boilerplate for normal user-facing answers.

## 10. Interpretation target

Application conformance is semantic:

```text
same user request
+ same Account Context
+ same runtime authority/capability states
-> equivalent capability graph
-> equivalent authoritative resolution/execution needs
-> equivalent exact executable delivery resolution
-> equivalent materialization / identity verification / execution resolution
-> equivalent result/status semantics
```

Natural prose may differ while this interpretation remains stable.
