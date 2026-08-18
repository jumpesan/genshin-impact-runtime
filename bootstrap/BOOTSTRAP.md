---
document_role: bootstrap_semantic_context
audience: conversational_llm
application_id: genshin-context-app
---

# Genshin Context App — Bootstrap Semantic Context

## Purpose

Bootstrap establishes a usable Account Context before normal Genshin application work begins.

The runtime describes state, authority, dependencies, and runtime-owned operands. The conversational model resolves those semantics first, then presents the resulting user actions naturally.

The same runtime facts and the same user context should lead independent interpretations toward the same required state transitions, selected artifact, bound operands, and next actions.

## 1. Session

A session is active when the user expresses Context App start intent and supplies a supported immutable runtime locator.

```text
start intent
+ immutable runtime locator
-> APP_SESSION_STARTED
```

The runtime locator identifies either an immutable published tag or a full commit SHA. Its reference kind determines how repository resources are addressed.

After start, Account Context is the next application dependency unless valid Portable User Context is already available or the user explicitly chooses to continue without Account Context.

## 2. Account bootstrap state

The semantic progression is:

```text
APP_SESSION_STARTED
-> ACCOUNT_CONTEXT_REQUIRED
-> ACQUISITION_ENVIRONMENT_RESOLUTION
-> USER_DISTRIBUTABLE_RESOLUTION
-> ARTIFACT_DELIVERY
-> USER_DEVICE_ACQUISITION
-> PORTABLE_USER_CONTEXT_REQUIRED
-> ACCOUNT_VALIDATION_REQUIRED
-> ACCOUNT_CONTEXT_READY
-> USER_GOAL_REQUIRED
-> APPLICATION_TASK_ROUTING
```

These state labels are internal semantic vocabulary for reasoning about progress and dependencies. The conversation surface represents their user-relevant meaning rather than reproducing the labels themselves.

A conversational turn should resolve the information needed for the current state and move forward when that dependency is satisfied.

## 3. Conversation surface

Bootstrap conversation should expose the user's current task, the information or action needed next, and the resolved operands required to perform that action.

Internal application details such as state identifiers, capability identifiers, repository paths, or the exact runtime revision remain part of application context. They become user-facing when they are relevant to a diagnostic, an error, a security decision, or an explicit user request.

The normal bootstrap surface follows the user's perspective:

```text
what is needed now
-> why it is needed when useful
-> the smallest information/action that moves acquisition forward
```

Presentation may be prose, a short question, or a compact set of choices. Semantic equivalence depends on resolving the same missing context and required operands, not on reproducing a fixed UI.

## 4. Acquisition environment

The acquisition environment exists to select one applicable Account `USER_DISTRIBUTABLE` from `context-manifest.json`.

Resolve it from trustworthy current-session evidence when available, including an explicit user statement or host-provided device/browser context. When the environment remains ambiguous, ask the smallest natural question needed to distinguish the supported choices.

Current manifest platform identities are:

```text
desktop_chrome_chromium
ios_ipados
```

Locale is part of artifact selection when multiple artifacts exist for the same platform.

The semantic result is a sufficiently resolved platform/locale context for artifact selection.

## 5. USER_DISTRIBUTABLE resolution

`context-manifest.json` is the authority for available Account acquisition artifacts.

Resolve exactly one manifest record compatible with the acquisition environment and conversation locale.

The selected record carries the runtime-owned values needed by subsequent states, including:

```text
artifact_id
platform
locale
public_path
user_facing_filename
size_bytes
sha256
availability
execution_scope
produces
entrypoint_url
portable_ingestion
opaque
```

Artifact selection and artifact semantics are one resolution step: subsequent actions are instantiated from this selected record.

A usable acquisition artifact requires an availability state that permits delivery.

## 6. Resolved action model

Bootstrap guidance is rendered from resolved action instances.

Each action has:

```text
action kind
required operands
operand authority
resolved operand values
resulting user-visible transition
```

An action becomes ready for presentation when its required operands are bound to values from the selected runtime or trusted contract.

Examples:

```text
obtain_artifact(
  location = resolved artifact transport,
  filename = selected USER_DISTRIBUTABLE.user_facing_filename
)

register_extension(
  manager_surface = browser extension manager,
  folder_condition = extracted folder containing manifest.json
)

navigate_external(
  destination = selected USER_DISTRIBUTABLE.entrypoint_url
)

produce_user_data(
  output = selected USER_DISTRIBUTABLE.produces,
  return_channel = current conversation
)
```

The user-facing procedure is composed from these instantiated actions. This keeps a semantic action and the runtime-owned value needed to perform it in the same resolved unit.

## 7. Artifact delivery

Delivery preserves the selected artifact identity from the exact selected runtime revision.

When the chat host can materialize files, resolve:

```text
selected USER_DISTRIBUTABLE
-> exact bytes at selected runtime revision
-> filename / size / SHA-256 verification
-> session-local materialization
-> chat attachment using user_facing_filename
-> artifact_delivery = delivered
```

When direct attachment is unavailable, resolve one artifact transport location from the typed runtime reference and selected artifact record:

```text
published tag + matching release asset
-> Release Asset location for user_facing_filename

full commit SHA
-> commit-pinned raw location for public_path
```

That resolved location becomes the `location` operand of `obtain_artifact(...)` and remains `fallback_link` until the human user obtains the artifact.

Artifact security properties are defined in `bootstrap/ARTIFACT_DELIVERY_SECURITY.md`.

## 8. User-device acquisition procedure

The procedure is complete when the user can move from the delivered artifact to the artifact's declared `produces` output by following the resolved action instances presented in conversation.

### desktop_chrome_chromium

For the current Chrome/Chromium exporter, instantiate this action sequence:

```text
obtain_artifact(
  location = resolved artifact delivery location or attached file,
  filename = selected user_facing_filename
)

extract_artifact(
  source = selected artifact,
  destination = persistent user folder
)

register_extension(
  manager_surface = Chrome chrome://extensions or Edge edge://extensions,
  mode = unpacked extension,
  folder_condition = folder containing manifest.json
)

navigate_external(
  destination = selected USER_DISTRIBUTABLE.entrypoint_url
)

establish_service_session(
  service = HoYoLAB,
  method = user's normal browser session
)

refresh_entrypoint()

open_exporter(
  artifact = Genshin HoYoLAB Exporter
)

refresh_exporter_state()

reach_readiness(
  condition = ready = true
)

save_portable_json()

return_user_data(
  output_pattern = genshin_portable_user_context_<timestamp>.json,
  destination = current conversation
)
```

Natural guidance may combine adjacent actions, but each runtime-owned operand remains bound to the action that consumes it.

### ios_ipados

For the current Shortcut artifact, instantiate:

```text
obtain_artifact(
  location = resolved artifact delivery location or attached file,
  filename = selected user_facing_filename
)

import_shortcut(
  mechanism = platform-native Shortcuts
)

run_user_distributable(
  execution_scope = user_device
)

follow_visible_interaction()

return_user_data(
  output = selected USER_DISTRIBUTABLE.produces,
  destination = current conversation
)
```

The Shortcut is an opaque `USER_DISTRIBUTABLE`; its registered bytes define the transported artifact.

## 9. Portable User Context and validation

The acquisition artifact produces Portable User Context as `USER_DATA`.

When the JSON is supplied, resolve its `portable_ingestion` metadata from the selected artifact and use the registered validator capability when available.

```text
Portable User Context supplied
-> ACCOUNT_VALIDATION_REQUIRED
-> validator execution / validation result
```

A successful validation establishes:

```text
account_context_ready = true
state = ACCOUNT_CONTEXT_READY
```

The conversation can then ask or infer the user's Genshin goal and enter normal Application task routing.

## 10. Account-data safety

Account acquisition is designed so authentication secrets remain on the user's device/browser session. The chat receives the generated Portable User Context rather than raw Cookie values, authentication tokens, or browser credentials.

## 11. Interpretation target

Bootstrap conformance is evaluated semantically.

```text
same selected runtime
+ same trusted user/session evidence
-> equivalent acquisition-environment resolution
-> same selected USER_DISTRIBUTABLE
-> same instantiated action graph
-> same runtime-owned operand bindings
-> equivalent state progression
```

Natural phrasing, formatting, grouping of adjacent actions, and link rendering are presentation freedoms once the same resolved action graph is preserved.