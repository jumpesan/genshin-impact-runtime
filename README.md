# Genshin Context App Runtime — CNB-002 Root Entry

> **EXPERIMENTAL / UNREVIEWED**
>
> This default branch is used only as the context-native current-runtime index for manual validation. It is not the active runtime content and is not Production.

## Start

The ordinary user starts with:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

Do not ask the user for a tag, commit SHA, tree, digest, selector, DTA, manifest path, or executable identity.

When the repository root URL is supplied, first read:

```text
context-entry.json
```

`context-entry.json` is the current experimental runtime selector/index.

Required transition:

```text
repository root URL
-> context-entry.json
-> active_revision
-> active_runtime_url
-> exact immutable runtime revision
-> immutable runtime-local instructions/manifest
-> Context App session
```

The default branch itself is not runtime content.
Do not use `main/bootstrap/BOOTSTRAP.md`, `main/context-manifest.json`, repository history, tags, or remembered prior revisions as runtime semantics.
Do not fall back to asking the user for an immutable revision.

If deterministic current-runtime resolution fails:

```text
RUNTIME_RESOLUTION_BLOCKED
```

## CNB-1 result

The root-selector path reached `PLATFORM_REQUIRED` in ChatGPT Free manual validation with both thinking=false and thinking=true.

That is experimental evidence only; it is not a formal Production trust decision.

## CNB-002 current scope

After current immutable runtime resolution:

```text
PLATFORM_REQUIRED
-> user selects PC / Chromium
-> resolve exactly one desktop_chrome_chromium USER_DISTRIBUTABLE from the same immutable runtime manifest
-> exact commit-pinned artifact route or verified attachment
-> complete PC user-device procedure
-> PORTABLE_USER_CONTEXT_REQUIRED
```

The selected immutable runtime revision must not change during this flow.

CNB-002 stops before Portable User Context validation or any repository executable execution.

## Boundary

```text
CNB-002 PASS
!= reviewed trust architecture
!= formal Runtime candidate C modification
!= Production
!= release
!= Account validation PASS
!= EC-C PASS
```
