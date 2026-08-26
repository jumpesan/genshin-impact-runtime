# Genshin Context App — CNB-002 Semantic Interpretation Experiment

> **EXPERIMENTAL / UNREVIEWED**

This repository is the runtime context for a conversational Genshin Context App.

The important interpretation is the **application state**, not repository administration.
Repository files provide the app's current facts, capabilities, and user-flow context in the background.

## Start

The ordinary user starts with:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

The repository root identifies the current Context App distribution. Its small current-runtime index leads to one immutable runtime snapshot, and the conversation then continues as the application described by that snapshot.

For the user, the flow is simply:

```text
Context App start
-> choose platform
-> prepare Account Context
-> return Portable User Context
-> continue into normal app use
```

Internal revision and manifest details support this flow but are not normal user-facing setup choices.

## Current experiment state

CNB-1 has already shown that ChatGPT Free can interpret the repository root as the Context App entry and reach platform selection with both thinking modes.

CNB-002 continues from that application state.

```text
PLATFORM_REQUIRED
```

Supported choices presented to the user are:

```text
PC / Chromium系ブラウザ
Android
iPhone / iPad
```

This experiment follows the PC / Chromium path.

## PC / Chromium path

When the user chooses PC / Chrome / Chromium, interpret that as:

```text
platform = PC / Chromium
-> Account setup is needed
-> use the PC Account acquisition resource defined by this runtime
-> guide the user through setup
-> user generates Portable User Context
-> PORTABLE_USER_CONTEXT_REQUIRED
```

The runtime already contains the information needed to identify the applicable PC acquisition package, its public location, the HoYoLAB entrypoint it works with, and the Portable User Context it produces.

Use those runtime facts to give the user a concise, actionable setup flow. The user should experience this as continuing the Context App, not as inspecting or managing a GitHub repository.

## Supporting runtime context

The following are backing context for the application:

```text
context-manifest.json
bootstrap/BOOTSTRAP.md
bootstrap/ARTIFACT_DELIVERY_SECURITY.md
AGENTS.md
```

They provide precise artifact identity, platform mapping, entrypoint, and delivery semantics when those details are needed.

They are supporting evidence for the current application state; they are not the application experience itself.

## CNB-002 boundary

CNB-002 ends after the PC setup resource and procedure have been presented and the conversation is waiting for the generated Portable User Context.

```text
PORTABLE_USER_CONTEXT_REQUIRED
```

Portable User Context validation and repository executable execution belong to later experiments.

A successful CNB-002 conversation remains experimental evidence only; it is not Production, release authority, Account validation PASS, or EC-C PASS.
