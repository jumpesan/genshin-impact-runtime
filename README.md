# Genshin Context App Runtime

Public runtime resources for the chat-native Genshin Context App.

This repository contains the runtime contracts, projected data, registered tools, Account acquisition artifacts, and metadata used by a conversational model to operate the application.

## Start

A runtime session is selected with an immutable runtime tree locator, for example:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime/tree/<immutable-tag-or-full-commit-sha>
```

Runtime interpretation begins at:

```text
bootstrap/BOOTSTRAP.md
```

The active trusted-instruction order is declared by `context-manifest.json` rather than by this README.

## Repository roles

`context-manifest.json` classifies runtime resources such as:

```text
TRUSTED_CONTRACT
TRUSTED_EXECUTABLE
DATA_REFERENCE
USER_DISTRIBUTABLE
```

Account acquisition artifacts are registered under `registry.user_distributable` with their platform, locale, public path, filename, integrity metadata, output, and entrypoint metadata.

## Application model

The Context App is designed around semantic interpretation rather than fixed UI rendering.

The runtime provides state, authority, capability, and dependency information. The conversational model turns that context into natural interaction while preserving the same underlying application semantics.

High-level flow:

```text
start runtime
-> establish Account Context
-> interpret user goal
-> resolve repository capabilities / authority
-> execute registered deterministic functions when required
-> present the result conversationally
```

## Experimental status

This repository is an experimental runtime distribution surface. Existing experimental tags remain immutable historical checkpoints; exact commit SHAs may be used for iteration testing between checkpoints.
