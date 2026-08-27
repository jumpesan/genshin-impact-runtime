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

The repository root is only the current-runtime selector.

```text
repository root
-> context-entry.json
-> current immutable runtime
-> Genshin Context App
```

`context-entry.json` identifies one immutable runtime tree. After that tree is selected, that immutable tree is the application runtime for the conversation.

The ordinary user does not need to manage internal runtime identity.

This default-branch entry does not duplicate the selected runtime's bootstrap, delivery, capability, or conversational semantics.
