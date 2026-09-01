---
document_role: llm_entry_contract
audience: conversational_llm
application_id: genshin-context-app
repository_role: runtime_distribution
current_application_state_in_this_document: forbidden
---

# Genshin Context App — Entry Contract

> **EXPERIMENTAL / A1 D1 BOUNDED PROJECTION**

Genshin Context App is a chat-native application.

Canonical start input:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

The repository URL in this start input is the application's stable distribution locator. It is not, by itself, Runtime authority and it is not a request to explain the repository.

When explicit Genshin Context App start intent and this distribution locator are present:

```text
invocation_requested = true
distribution_entry_selected = true
```

A safe conversational application session may begin, but repository or Runtime content is not yet verified distribution merely because the session exists.

Before interpreting the current release nomination, read and apply the public validation contract and schema at these fixed root paths:

```text
context-release-discovery-validation.md
context-release-discovery.schema.json
```

Then validate the raw governing descriptor at:

```text
context-entry.json
```

The validation contract/schema are not selected by `context-entry.json`; the descriptor cannot override their path, version, or rules.

The descriptor has exactly one authority role:

```text
RELEASE_CANDIDATE_NOMINATION_AUTHORITY
```

It nominates which GitHub Release must be validated. It does not by itself prove that the Release or Runtime is accepted.

Required progression:

```text
repository root
-> fixed public D1 validation contract/schema
-> validated governing context-entry.json
-> exact nominated GitHub Release
-> Immutable Release + Release attestation + exact authority/review assets
-> exact reviewed Runtime acceptance
-> authority-selected Runtime README.md / bootstrap/BOOTSTRAP.md
-> trusted application semantics and verified capabilities
```

The ordinary user does not provide or choose the Runtime tag, commit SHA, digest, authority asset, review identity, validation contract, or schema.

If the validation contract/schema, descriptor, nominated release, or downstream authority chain cannot be resolved, do not fall back to `main`, `latest`, newest-by-time, another tag, model memory, or a user-supplied identity. Verified Runtime capabilities remain unavailable.

The mutable repository root owns only:

```text
application invocation classification
current release-candidate nomination
nomination-validation semantics
```

The accepted exact Runtime owns subsequent trusted application state, Account bootstrap semantics, delivery semantics, and conversational progression.
