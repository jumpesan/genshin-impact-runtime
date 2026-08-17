# Published Contracts

This directory contains only contracts intentionally projected for Context App runtime use.

Contract files are `TRUSTED_CONTRACT` only when explicitly registered by `context-manifest.json`.

A trusted contract:

```text
does not automatically become an LLM instruction
does not redefine repository trust roles
does not grant tool/action authority
must preserve the owning Domain's semantics
```

Current candidate:

```text
application/README.md  -> bootstrap/session semantics projection
account/README.md      -> pending Account ingestion contract marker
```

Research notes, review discussion, private fixtures, and development-only status files are not published contracts.
