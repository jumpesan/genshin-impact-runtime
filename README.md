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
-> Genshin Context App
```

`context-entry.json` identifies the immutable runtime snapshot that carries the current app semantics and capabilities.

After that snapshot is selected, continue from its `README.md`, `bootstrap/BOOTSTRAP.md`, `AGENTS.md`, and `context-manifest.json` as the application runtime.

The ordinary user does not need to manage internal runtime identity in order to use the app.

This default-branch entry is experimental discovery context only. The selected immutable snapshot is the runtime context for the conversation.
