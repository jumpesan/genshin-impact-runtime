# Genshin Context App Runtime — Experimental Entry

> **EXPERIMENTAL / UNREVIEWED**

This repository is the public runtime entry for the conversational Genshin Context App.

The repository root identifies the current app runtime. `context-entry.json` points to the immutable snapshot that describes the current application behavior.

## Start

The ordinary user starts with:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

Interpret this as starting the Context App, then continue from the current immutable runtime selected by `context-entry.json`.

The user-facing application flow is:

```text
Context App start
-> choose platform
-> prepare Account Context
-> return Portable User Context
-> continue into normal app use
```

Internal repository identities support that flow in the background. They are not normal setup choices for the user.

## Current experimental stage

CNB-1 established the first transition on ChatGPT Free:

```text
repository root
-> current immutable runtime
-> PLATFORM_REQUIRED
```

CNB-002 continues the PC / Chromium path:

```text
PLATFORM_REQUIRED
-> PC / Chromium selected
-> Account setup resource and guidance
-> PORTABLE_USER_CONTEXT_REQUIRED
```

The selected immutable runtime contains the exact metadata needed for that setup. The conversation should feel like continuation of the app rather than repository inspection.

## Runtime context

The selected snapshot contains supporting application context such as:

```text
README.md
bootstrap/BOOTSTRAP.md
AGENTS.md
context-manifest.json
bootstrap/ARTIFACT_DELIVERY_SECURITY.md
```

These files describe current state, capabilities, artifact facts, and detailed delivery semantics.

## Boundary

This is a manual context-interpretation experiment. Success here is experimental evidence only and does not itself mean Production, release, Account validation PASS, or EC-C PASS.
