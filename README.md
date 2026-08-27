---
document_role: runtime_distribution_entry
audience: conversational_llm
application_id: genshin-context-app
repository_role: runtime_distribution
---

# Genshin Context App Runtime

> **EXPERIMENTAL / UNREVIEWED**

This repository is the public distribution entry for Genshin Context App, a chat-native application.

Canonical start:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

The repository root is a small current-runtime entry surface.

```text
repository root
-> context-entry.json
-> current immutable runtime
-> bootstrap/BOOTSTRAP.md
-> APP_SESSION_STARTED
-> Genshin Context App
```

`context-entry.json` identifies the immutable runtime snapshot and the application composition inside that snapshot.

The primary application entrypoint is the selected runtime's `bootstrap/BOOTSTRAP.md`. It owns current bootstrap state and user-flow interpretation.

When Account acquisition guidance is needed, the selected runtime's `bootstrap/ARTIFACT_DELIVERY_SECURITY.md` supplies the delivery and user-device guidance semantics that complete the bootstrap flow.

The selected runtime's supporting surfaces are:

```text
bootstrap/ARTIFACT_DELIVERY_SECURITY.md = USER_DISTRIBUTABLE delivery/guidance semantics
bootstrap/BOOTSTRAP.md                  = primary application bootstrap semantics
AGENTS.md                               = conversational interpretation
README.md                               = entry semantics
context-manifest.json                   = exact runtime facts/capabilities
```

The ordinary user does not need to manage internal runtime identity in order to use the app.

This default-branch entry is experimental discovery context only. The selected immutable snapshot is the runtime context for the conversation.
