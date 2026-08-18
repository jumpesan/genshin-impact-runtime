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
postcondition
```

An action becomes ready for presentation when its required operands are bound to values from the selected runtime or trusted contract and its postcondition is achievable from the presented action.

Examples:

```text
obtain_artifact(
  location = resolved artifact transport,
  filename = selected USER_DISTRIBUTABLE.user_facing_filename,
  postcondition = user obtains the selected artifact bytes
)

register_extension(
  manager_surface = browser extension manager,
  folder_condition = extracted folder containing manifest.json
)

navigate_external(
  destination = selected USER_DISTRIBUTABLE.entrypoint_url,
  postcondition = external entrypoint is open in the user's browser
)

produce_user_data(
  output = selected USER_DISTRIBUTABLE.produces,
  return_channel = current conversation
)
```

The user-facing procedure is composed from these instantiated actions. This keeps a semantic action, the runtime-owned value needed to perform it, and the state it must establish in the same resolved unit.

## 7. Actionable presentation

A resolved action is not complete at the conversation surface merely because its operand value is visible. The presentation must preserve the interaction needed to establish the action postcondition.

For an action whose required operand is a navigable URI and whose postcondition is reached by the human user opening or retrieving that URI, interpret presentation as:

```text
resolved URI operand
+ user activation required
+ conversation host supports navigable hyperlinks
-> render a directly actionable hyperlink bound to that exact resolved URI
```

Examples include:

```text
obtain_artifact.location
navigate_external.destination
```

The visible label is presentation text; the hyperlink target is the resolved operand. The label may describe the user action naturally, while the target preserves the authoritative runtime value.

If the conversation host cannot provide a navigable hyperlink, preserve the URI as an explicit copyable operand together with the action needed to use it. A presentation that places a URI in a non-interactive representation establishes only that the value was shown; it does not by itself establish an action postcondition that depends on user navigation.

This distinction is part of semantic completeness:

```text
operand resolved
-> operand exposed
-> required interaction available
-> action postcondition reachable
```

## 8. Artifact transport and delivery

Delivery preserves the selected artifact identity from the exact selected runtime revision.

An artifact transport is the terminal resource operand consumed by `obtain_artifact(...)`.

Its semantics are:

```text
retrieve artifact_transport
-> artifact bytes are returned
-> bytes can be checked against selected USER_DISTRIBUTABLE identity
```

The transport therefore resolves to the artifact resource itself, not merely to a navigation surface that requires another unresolved user action before the artifact bytes can be obtained.

For supported GitHub runtime locators, transport derivation is deterministic:

```text
published tag + matching release asset
-> https://github.com/<owner>/<repository>/releases/download/<tag>/<user_facing_filename>

full commit SHA
-> https://raw.githubusercontent.com/<owner>/<repository>/<sha40>/<public_path>
```

The exact owner, repository, reference, filename, and public path come from the selected runtime locator and selected `USER_DISTRIBUTABLE` record.

When the chat host can materialize files, resolve:

```text
selected USER_DISTRIBUTABLE
-> exact bytes at selected runtime revision
-> filename / size / SHA-256 verification
-> session-local materialization
-> chat attachment using user_facing_filename
-> artifact_delivery = delivered
```

When direct attachment is unavailable, the derived terminal artifact transport becomes the `location` operand of `obtain_artifact(...)` and remains `fallback_link` until the human user obtains the artifact bytes.

If a proposed presentation introduces an intermediate page or interaction before bytes are obtained, that interaction is an additional action in the graph. The artifact acquisition graph is complete only when all actions and operands needed to reach the artifact bytes are resolved.

Artifact security properties are defined in `bootstrap/ARTIFACT_DELIVERY_SECURITY.md`.

## 9. User-device acquisition procedure

The procedure is complete when the user can move from the delivered artifact to the artifact's declared `produces` output by following the resolved action instances presented in conversation.

### desktop_chrome_chromium

For the current Chrome/Chromium exporter, instantiate this action sequence:

```text
obtain_artifact(
  location = resolved terminal artifact transport or attached file,
  filename = selected user_facing_filename,
  postcondition = selected ZIP bytes obtained
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
  destination = selected USER_DISTRIBUTABLE.entrypoint_url,
  postcondition = HoYoLAB entrypoint open in the user's browser
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

Natural guidance may combine adjacent actions, but each runtime-owned operand remains bound to the action that consumes it and the combined guidance must still establish the same postconditions.

### ios_ipados

For the current Shortcut artifact, instantiate:

```text
obtain_artifact(
  location = resolved terminal artifact transport or attached file,
  filename = selected user_facing_filename,
  postcondition = selected Shortcut bytes obtained
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

## 10. Portable User Context and validation

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

## 11. Account-data safety

Account acquisition is designed so authentication secrets remain on the user's device/browser session. The chat receives the generated Portable User Context rather than raw Cookie values, authentication tokens, or browser credentials.

## 12. Interpretation target

Bootstrap conformance is evaluated semantically.

```text
same selected runtime
+ same trusted user/session evidence
-> equivalent acquisition-environment resolution
-> same selected USER_DISTRIBUTABLE
-> same instantiated action graph
-> same runtime-owned operand bindings
-> same required interaction affordances
-> same action postconditions
-> equivalent state progression
```

Natural phrasing, formatting, grouping of adjacent actions, and link labels are presentation freedoms once the same resolved action graph, operand targets, interaction affordances, and postconditions are preserved.
