---
document_role: runtime_distribution_entry
audience: conversational_llm
application_id: genshin-context-app
repository_role: runtime_distribution
---

# Genshin Context App Runtime

> **EXPERIMENTAL / UNREVIEWED**

This repository is the public distribution entry for Genshin Context App.

Canonical start:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

The repository root is only the current application-entry selector.

```text
repository root
-> context-entry.json
-> current immutable bootstrap entrypoint
-> Genshin Context App
```

`context-entry.json` identifies one immutable application bootstrap entrypoint.

After that entrypoint is selected, the selected bootstrap contract is the semantic owner of the application start state for the conversation.

The ordinary user does not need to manage internal runtime identity.

This default-branch entry does not duplicate the selected runtime's bootstrap, delivery, capability, or conversational semantics.
