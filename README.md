# Genshin Context App Runtime — CNB-001 Root Entry

> **EXPERIMENTAL / UNREVIEWED**
>
> This default branch is currently used only as a context-native bootstrap index for manual validation. It is not the active runtime content and is not Production.

## Start

The ordinary user starts the Context App with exactly:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

Do **not** ask the user for a tag, commit SHA, tree, digest, selector, DTA, manifest path, or executable identity.

When the repository root URL is supplied, the first runtime-discovery action is:

```text
read context-entry.json from this repository root
```

`context-entry.json` is the current runtime selector/index for CNB-001.

Required flow:

```text
repository root URL
-> context-entry.json
-> active_revision (full 40-hex SHA)
-> active_runtime_url
-> exact immutable runtime revision
-> immutable context-manifest.json
-> immutable bootstrap/BOOTSTRAP.md
-> immutable AGENTS.md
-> Context App session
-> PLATFORM_REQUIRED
```

The default branch itself is **not** runtime content.
Do not use `main/bootstrap/BOOTSTRAP.md`, `main/context-manifest.json`, repository history, tags, or remembered prior revisions to choose the active runtime.
Do not fall back to the old rule that the user must provide an immutable tree URL.

If `context-entry.json` cannot be retrieved or does not deterministically resolve exactly one immutable full-SHA revision, return:

```text
RUNTIME_RESOLUTION_BLOCKED
```

Do not repair that failure by asking the ordinary user for the missing internal revision.

## CNB-001 success condition

This experiment tests only whether a fresh generic ChatGPT conversation can perform:

```text
root URL only
-> repository-owned current selector
-> exact immutable revision
-> app start
-> platform question
```

The expected first user-visible application state is `PLATFORM_REQUIRED`, with choices equivalent to:

```text
PC / Chromium系ブラウザ
Android
iPhone / iPad
```

Do not proceed to artifact resolution, Portable User Context, Account validation, or normal Genshin task routing during CNB-001.

## Boundary

```text
CNB-001 PASS
!= reviewed trust architecture
!= frozen Runtime candidate C modification
!= Production
!= release
!= EC-C PASS
```

The experiment exists to determine whether context design alone can preserve the original product concept: the user supplies only the public Runtime repository URL and the Context App resolves its own current immutable runtime.
