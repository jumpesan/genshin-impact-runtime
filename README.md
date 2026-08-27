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

`context-entry.json` identifies the immutable runtime snapshot and the primary application entrypoint inside that snapshot.

The primary application entrypoint is the selected runtime's `bootstrap/BOOTSTRAP.md`. It owns the current bootstrap state and user-flow interpretation.

The selected runtime's other surfaces support that application state:

```text
README.md = entry semantics
AGENTS.md = conversational interpretation
context-manifest.json = exact runtime facts/capabilities
```

The ordinary user does not need to manage internal runtime identity in order to use the app.

This default-branch entry is experimental discovery context only. The selected immutable snapshot is the runtime context for the conversation.
