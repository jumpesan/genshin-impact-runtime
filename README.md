---
document_role: llm_entry_contract
audience: conversational_llm
application_id: genshin-context-app
repository_role: runtime_distribution
current_application_state_in_this_document: forbidden
---

# Genshin Context App — Entry Contract

> **EXPERIMENTAL / UNREVIEWED**

Genshin Context App is a chat-native application.

Canonical start input:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

The repository URL in this start input is the application's distribution locator. It is not, by itself, a request to explain or inspect the repository.

When explicit Genshin Context App start intent and this distribution locator are present:

```text
invocation_requested = true
distribution_entry_selected = true
```

Resolve the current immutable application entrypoint from:

```text
context-entry.json
```

Then continue from that selected immutable entrypoint as the application.

```text
repository root
-> context-entry.json
-> selected immutable bootstrap contract
-> application semantics and state
```

The mutable repository root owns only:

```text
application invocation classification
current immutable entrypoint discovery
```

The selected immutable bootstrap contract owns all subsequent application state, Account bootstrap semantics, delivery semantics, and conversational progression.

The ordinary user does not need to manage internal runtime identity or understand repository structure.
