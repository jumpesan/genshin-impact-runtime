# Genshin Context App — CNB-002 Experimental Runtime

> **EXPERIMENTAL / UNREVIEWED**
>
> This revision exists only for the context-native bootstrap manual validation spike. It is not Production, not a reviewed release, and does not change the frozen formal Runtime candidate C.

## Entry contract

The intended ordinary-user invocation remains:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

The ordinary user must not provide, choose, or guess a tag, commit SHA, tree, digest, selector, DTA, manifest path, or executable identity.

The repository root is a distribution namespace/current-index surface only. `context-entry.json` selects one immutable experimental runtime revision.

```text
user repository root
-> root context-entry.json
-> active_revision
-> exact immutable revision
-> immutable runtime-local context
```

Do not fall back to `main` as runtime content and do not change revisions inside the application session.

## CNB-1 result

Manual Free-account validation converged positively on both:

```text
thinking=false
thinking=true
```

for:

```text
root URL only
-> immutable runtime selection
-> Context App start
-> PLATFORM_REQUIRED
```

That empirical result is experimental evidence only and is not a formal Production trust decision.

## CNB-002 scope

CNB-002 extends the same selected immutable runtime through the PC / Chromium Account acquisition route.

Positive path:

```text
PLATFORM_REQUIRED
-> user selects PC / Chromium
-> platform = desktop_chrome_chromium
-> resolve exactly one manifest USER_DISTRIBUTABLE
-> exact commit-pinned artifact route or verified attachment
-> complete user-device procedure using manifest-owned entrypoint
-> PORTABLE_USER_CONTEXT_REQUIRED
```

The selected runtime revision must remain unchanged throughout this flow.

Load and follow, from this same immutable revision:

```text
context-manifest.json
bootstrap/ARTIFACT_DELIVERY_SECURITY.md
bootstrap/BOOTSTRAP.md
AGENTS.md
```

Do not inspect or validate Portable USER_DATA in CNB-002 and do not execute repository tools.

## Experimental authority hypothesis

For this spike only:

```text
explicit user choice of repository namespace
+ repository-root context-entry current selector
+ exact immutable revision retrieval
= context-native runtime selection
```

CNB-002 additionally tests whether runtime-local manifest semantics can drive exact USER_DISTRIBUTABLE selection without returning authority to the ordinary user or drifting to another revision.

A successful conversational result does not by itself authorize this design for Production.
