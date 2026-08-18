---
document_role: bootstrap_semantic_context
audience: conversational_llm
application_id: genshin-context-app
---

# Genshin Context App — Bootstrap Semantic Context

## Purpose

Bootstrap establishes a usable Account Context before normal Genshin application work begins.

The runtime describes state, authority, and dependencies. The conversational model chooses natural wording and presentation while preserving those semantics.

The same runtime facts and the same user context should lead independent interpretations toward the same required state transitions and runtime-owned values.

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

These are application states, not prescribed UI screens.

A conversational turn should resolve the information needed for the current state and move forward when that dependency is satisfied.

## 3. Acquisition environment

The acquisition environment exists to select one applicable Account `USER_DISTRIBUTABLE` from `context-manifest.json`.

Use explicit evidence already present in the current conversation when it resolves the environment. When the environment remains ambiguous, ask the smallest natural question needed to distinguish the supported choices.

Current manifest platform identities are:

```text
desktop_chrome_chromium
ios_ipados
```

Locale is part of artifact selection when multiple artifacts exist for the same platform.

The user-facing wording for environment resolution is a presentation choice. The semantic result is a sufficiently resolved platform/locale context for artifact selection.

## 4. USER_DISTRIBUTABLE resolution

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

Artifact selection and artifact semantics are one resolution step: user-device guidance is built from the selected record rather than from a separately duplicated filename or endpoint table.

A usable acquisition artifact requires an availability state that permits delivery.

## 5. Artifact delivery

Delivery preserves the selected artifact identity from the exact selected runtime revision.

When the chat host can materialize files, the preferred path is:

```text
selected USER_DISTRIBUTABLE
-> retrieve exact bytes from selected runtime revision
-> verify filename / size / SHA-256
-> session-local materialization
-> attach exact bytes using user_facing_filename
-> artifact_delivery = delivered
```

When direct attachment is unavailable, derive an actionable direct-file location from the typed runtime reference and the selected artifact record:

```text
published tag + matching release asset
-> Release Asset location for user_facing_filename

full commit SHA
-> commit-pinned raw location for public_path
```

The result is `fallback_link` until the human user actually obtains the artifact.

Artifact security properties are defined in `bootstrap/ARTIFACT_DELIVERY_SECURITY.md`.

## 6. User-device acquisition procedure

The procedure is complete when the user can move from the delivered artifact to the artifact's declared `produces` output using the presented guidance alone.

Construct the procedure as dependency resolution:

```text
required transition
-> user action
-> operands needed by the action
-> runtime/contract authority for each operand
-> resolved operand
-> natural user-facing guidance
```

Runtime-owned operands come from the selected `USER_DISTRIBUTABLE` or its trusted contracts.

### desktop_chrome_chromium

For the current Chrome/Chromium exporter, the semantic action sequence is:

```text
obtain selected ZIP
-> extract it to a persistent folder
-> register that folder as an unpacked Chromium extension; the selected folder contains manifest.json
-> navigate in the same browser to the external entrypoint owned by the selected USER_DISTRIBUTABLE
-> establish the user's normal HoYoLAB session when needed
-> reload the entrypoint page so the extension observes the active page state
-> open Genshin HoYoLAB Exporter
-> refresh exporter state
-> reach ready = true
-> save Portable JSON
-> obtain genshin_portable_user_context_<timestamp>.json
-> return that JSON to this conversation
```

The Chromium extension-management surface is the browser's standard extension manager (`chrome://extensions` for Chrome and `edge://extensions` for Edge).

When external navigation is part of this action sequence, the destination operand is the selected record's `entrypoint_url`; present that resolved destination in a form the user can act on directly.

### ios_ipados

For the current Shortcut artifact, the semantic action sequence is:

```text
obtain selected .shortcut
-> import/open it through the platform-native Shortcuts mechanism
-> run it on the user device
-> follow its visible interaction
-> return the generated Portable User Context to this conversation
```

The Shortcut is an opaque `USER_DISTRIBUTABLE`; its binary contents are transported as registered bytes.

## 7. Portable User Context and validation

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

## 8. Account-data safety

Account acquisition is designed so authentication secrets remain on the user's device/browser session. The chat receives the generated Portable User Context rather than raw Cookie values, authentication tokens, or browser credentials.

## 9. Interpretation target

Bootstrap conformance is evaluated semantically.

```text
same selected runtime
+ same user evidence
-> equivalent acquisition-environment resolution
-> same selected USER_DISTRIBUTABLE
-> same runtime-owned operands
-> equivalent state progression
```

Natural phrasing, formatting, whether a choice is expressed as prose or a list, and link rendering are presentation freedoms so long as the required context and operands are actually resolved.