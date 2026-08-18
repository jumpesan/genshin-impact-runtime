---
document_role: bootstrap_semantic_context
audience: conversational_llm
application_id: genshin-context-app
---

# Genshin Context App — Bootstrap Semantic Context

## Purpose

Bootstrap establishes a usable Account Context before normal Genshin application work begins.

The runtime describes state, authority, dependencies, runtime-owned operands, required user interactions, and the bindings that make those actions usable on the conversation surface. The conversational model resolves those semantics first, then presents the resulting user actions naturally.

The same runtime facts and the same user context should lead independent interpretations toward the same required state transitions, selected artifact, bound operands, required interactions, usable surface bindings, and next actions.

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

Bootstrap conversation should expose the user's current task and every user-consumed value or interaction needed to perform the next actions.

Internal application details such as state identifiers, capability identifiers, repository paths, or the exact runtime revision remain part of application context. They become user-facing when they are relevant to a diagnostic, an error, a security decision, or an explicit user request.

The normal bootstrap surface follows the user's perspective:

```text
what is needed now
-> the usable action that moves the task forward
-> enough artifact/destination identity to recognize that action
-> what to do after the action succeeds
```

Presentation may be prose, a short question, a compact set of choices, host-native references, or attachments. Semantic equivalence depends on resolving and surfacing the same user-consumed operands, required interactions, and postconditions, not on reproducing a fixed UI or wording.

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
user-consumed operands
required interaction
interaction capability
surface binding
resulting user-visible transition
postcondition
```

A resolved internal action is not yet a presented user action.

For each operand the human user must consume directly, the conversation surface must bind that exact resolved operand to the interaction or object the user will act on. The user should not need to reconstruct, infer, search for, or request a missing runtime-owned value that is already resolved internally.

An action becomes complete for the current turn when:

```text
required operands resolved
-> human-consumed operands bound to the conversation surface
-> required interaction bound to the same operand/object
-> user can recognize the action target sufficiently for the task
-> postcondition reachable from the presented action
```

Examples:

```text
obtain_artifact(
  location = resolved artifact transport,
  filename = selected USER_DISTRIBUTABLE.user_facing_filename,
  user_consumes = location,
  interaction = user_activate_uri(target = location),
  surface_binding = actionable_reference(target = location, identity = filename),
  postcondition = user obtains the selected artifact bytes
)

register_extension(
  manager_surface = browser extension manager,
  folder_condition = extracted folder containing manifest.json
)

navigate_external(
  destination = selected USER_DISTRIBUTABLE.entrypoint_url,
  user_consumes = destination,
  interaction = user_activate_uri(target = destination),
  surface_binding = actionable_reference(target = destination, identity = service/entrypoint meaning),
  postcondition = external entrypoint is open in the user's browser
)

produce_user_data(
  output = selected USER_DISTRIBUTABLE.produces,
  return_channel = current conversation
)
```

The user-facing procedure is composed from these instantiated actions. This keeps a semantic action, the runtime-owned value needed to perform it, the interaction that consumes that value, the visible/actionable surface object, and the state it must establish in the same resolved unit.

## 7. Surface binding and interaction resolution

Surface binding is part of action completion rather than a formatting afterthought.

A human-consumed operand can be internally resolved without being usable. It becomes usable only when the current conversation surface exposes a concrete object or control bound to that operand.

For a URI-backed action that requires the human user to open or retrieve a destination:

```text
resolved URI operand
+ user_activate_uri(target = operand)
+ conversation host supports navigable URI activation
-> actionable_reference(target = exact operand)
```

For the current ChatGPT conversation surface:

```text
navigable URI activation = available
```

Therefore the URI-consuming action should surface a host-native actionable reference whose target is the exact runtime-owned URI. Its visible identity may be a natural action label, filename, or destination meaning; literal URI text is not required when the target is correctly bound and the user can recognize what the action does.

### User-distributable delivery UX contract

`USER_DISTRIBUTABLE` acquisition is a user-entry boundary where interaction friction is part of application correctness rather than optional presentation polish.

When the selected artifact is delivered by URI and the conversation host supports navigable URI activation:

```text
selected USER_DISTRIBUTABLE
+ terminal artifact URI resolved
+ navigable URI activation available
-> expose one directly actionable download reference bound to the exact terminal artifact URI
-> user can initiate artifact retrieval without copying, reconstructing, or manually re-entering the URI
```

For a Markdown-capable conversation surface, an ordinary rendered hyperlink bound to the exact URI satisfies this contract. An equivalent host-native link/file control also satisfies it.

The following do **not** satisfy the delivery contract when direct activation is available:

```text
URI inside a fenced code block
URI presented only as inline code
plain instructions telling the user to copy/paste the URI into an address bar
prose that names the artifact without a bound download control
an intermediate repository page when the terminal artifact resource is already resolved
```

The same interaction requirement applies to a resolved external service entrypoint such as `navigate_external.destination`: when the host can render a navigable reference, the user should be able to open the selected destination directly from the response.

Visible labels and surrounding explanatory prose remain presentation freedoms. Whether the user receives an actionable control for an already-resolved human-consumed URI is not a presentation freedom.

A copyable URI is a fallback only on a host where direct URI activation is genuinely unavailable.

The same principle generalizes beyond links:

```text
artifact bytes -> attachment/file object
choice operand -> selectable control when available
URI operand -> actionable reference
```

Surface completeness is:

```text
operand resolved
-> operand surface-bound
-> required interaction surface-bound
-> target recognizable to the user
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

For supported GitHub runtime locators, transport derivation is deterministic.

For a published tag with a matching release asset, resolve a GitHub release-download terminal URI from the runtime owner, repository, tag, and selected `user_facing_filename`.

For a full commit SHA, resolve a `raw.githubusercontent.com` terminal URI from the runtime owner, repository, full SHA, and selected `public_path`.

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

When direct attachment is unavailable, the derived terminal artifact transport becomes the `location` operand of `obtain_artifact(...)` and remains `fallback_link` until the human user obtains the artifact bytes. On a host with navigable URI activation, that fallback link is still an actionable download reference; it is not inert URI text.

Artifact identity cues such as the user-facing filename belong with the acquisition action when they help the user recognize what they are obtaining. Integrity metadata such as size/SHA remains available for verification and diagnostics and may be surfaced when useful without becoming mandatory prose.

If a proposed presentation introduces an intermediate page or interaction before bytes are obtained, that interaction is an additional action in the graph. The artifact acquisition graph is complete only when all actions, operands, surface bindings, and interactions needed to reach the artifact bytes are resolved.

Artifact security properties are defined in `bootstrap/ARTIFACT_DELIVERY_SECURITY.md`.

## 9. User-device acquisition procedure

The procedure is complete when the user can move from the delivered artifact to the artifact's declared `produces` output by following the resolved action instances presented in conversation.

### desktop_chrome_chromium

For the current Chrome/Chromium exporter, instantiate this action sequence:

```text
obtain_artifact(
  location = resolved terminal artifact transport or attached file,
  filename = selected user_facing_filename,
  user_consumes = location or attached file,
  interaction = user_activate_uri(target = location) when location is a URI,
  surface_binding = actionable_reference(target = location, identity = filename) when location is a URI,
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
  user_consumes = destination,
  interaction = user_activate_uri(target = destination),
  surface_binding = actionable_reference(target = destination, identity = HoYoLAB Genshin records entrypoint),
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

Natural guidance may combine adjacent actions, but every human-consumed runtime operand and its required interaction remains surface-bound to the action that consumes it. Combined guidance must still let the user perform the next action directly without recovering omitted runtime-owned values.

### ios_ipados

For the current Shortcut artifact, instantiate:

```text
obtain_artifact(
  location = resolved terminal artifact transport or attached file,
  filename = selected user_facing_filename,
  user_consumes = location or attached file,
  interaction = user_activate_uri(target = location) when location is a URI,
  surface_binding = actionable_reference(target = location, identity = filename) when location is a URI,
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
-> same human-consumed operand surface bindings
-> same required interaction resolution
-> same action postconditions
-> equivalent state progression
```

Natural phrasing, grouping of adjacent actions, link labels, and verification-detail density are presentation freedoms once the same resolved action graph, operand targets, surface bindings, required interactions, and postconditions are preserved. For a human-consumed URI on a host with navigable URI activation, actionable versus inert presentation is part of semantic conformance, not a formatting preference.
