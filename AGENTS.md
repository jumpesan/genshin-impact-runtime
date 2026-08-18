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
-> acquire exact executable resource through a host retrieval capability
-> materialize exact executable + required inputs into a compatible execution environment
-> execute registered implementation
-> consume its structured output
-> preserve its result/status semantics
```

The authoritative deterministic result is the execution output, not a reimplementation of the algorithm in conversational reasoning.

### Acquisition plane and execution plane

Resource acquisition and deterministic execution are separate capabilities.

```text
HOST RETRIEVAL PLANE
selected immutable runtime locator
+ registered executable path
-> exact runtime resource identity
-> obtain exact resource through an available host retrieval mechanism
-> materialize resource bytes/content

OFFLINE EXECUTION PLANE
materialized registered executable
+ materialized required input
+ compatible sandbox/runtime
-> execute
-> structured result
```

Do not infer that a code-execution sandbox has outbound network capability merely because it can run Python or shell commands. Network retrieval from inside the execution sandbox is only an applicable acquisition path when that environment explicitly provides such access.

For a sandbox without outbound network access, shell/Python network clients such as `curl`, `wget`, or `requests` are not the normal resource-acquisition mechanism. Resolve an external host retrieval capability first, then materialize the exact resource into the sandbox for execution.

### Exact-resource acquisition

For a manifest-registered executable, resolve:

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

Only after exact resource acquisition, materialization, and execution capabilities have been resolved may the deterministic operation be classified as unavailable. Preserve the concrete blocker, distinguishing at least:

```text
resource identity unresolved
host exact-resource retrieval unavailable
materialization failure
incompatible execution runtime
missing required input
execution error
```

A conversational reimplementation or ad-hoc structural check may provide diagnostic observations, but it cannot substitute for the registered executable, cannot establish its authoritative result, and cannot upgrade a repository-owned deterministic status.

This applies to exact DPS, deterministic reaction/runtime numbers, validators, and other registered deterministic functions.

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
host retrieval mechanism used / blocking condition
whether materialization occurred
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
-> equivalent exact-resource acquisition resolution
-> equivalent materialization/execution resolution
-> equivalent result/status semantics
```

Natural prose may differ while this interpretation remains stable.
