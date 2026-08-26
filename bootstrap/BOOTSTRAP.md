# Context App Bootstrap — CNB-001 Experimental

> **EXPERIMENTAL / UNREVIEWED**
>
> This file is intentionally narrow. It validates only context-native discovery of an immutable runtime from the ordinary repository root URL.

## 1. Invocation

The accepted user message for CNB-001 is exactly:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

The repository URL is the user-selected distribution namespace.

The user must never be asked to provide:

```text
commit SHA
tag
tree
digest
selector identity
DTA identity
manifest path
executable path/hash
```

## 2. Root selector discovery

When the supplied locator is the repository root:

```text
https://github.com/jumpesan/genshin-impact-runtime
```

resolve the root file:

```text
context-entry.json
```

The root `main` tree is **not** the active runtime content for this experiment. It is only the current distribution index surface.

Require the selector record to provide at minimum:

```text
schema
status
repository
repository_url
active_revision
active_runtime_url
```

Required checks:

```text
schema = genshin-context-bootstrap/v0-experimental
status = EXPERIMENTAL_UNREVIEWED
repository = jumpesan/genshin-impact-runtime
repository_url = exact user-supplied canonical repository root
active_revision = full 40-hex commit SHA
active_runtime_url = same repository bound to active_revision
```

If any required value is absent, malformed, contradictory, or cannot be retrieved:

```text
RUNTIME_RESOLUTION_BLOCKED
```

Do not ask the user to repair the missing internal operand.

## 3. Immutable transition

Follow `active_runtime_url` to the exact immutable revision.

Once the immutable revision is open, require:

```text
current immutable URL revision = context-entry.active_revision
```

Then:

```text
runtime_selected = true
selected_runtime_revision = context-entry.active_revision
```

Do not return to `main` for runtime semantics.
Do not inspect repository history to choose another revision.
Do not ask the user to confirm the selected SHA.

## 4. Runtime-local loading

From the selected immutable revision, load only the normal runtime-local entry surfaces needed for CNB-001:

```text
context-manifest.json
bootstrap/BOOTSTRAP.md
AGENTS.md
README.md
```

`context-manifest.json` remains the repository-local role registry.

For CNB-001, do not attempt external DTA / host-adapter resolution. Whether this context-native selector model is acceptable for the final trust architecture is explicitly outside the experiment and remains subject to later Architecture review.

## 5. Application session start

After successful immutable selection:

```text
invocation_requested = true
runtime_selected = true
app_session_started = true
next_state = ACCOUNT_CONTEXT_REQUIRED
```

Then immediately enter:

```text
PLATFORM_REQUIRED
```

Ask only for the user's platform using these choices:

```text
PC / Chromium系ブラウザ
Android
iPhone / iPad
```

Natural wording is allowed, but the semantic state must be `PLATFORM_REQUIRED`.

## 6. CNB-001 stop boundary

CNB-001 ends after the first assistant response reaches `PLATFORM_REQUIRED`.

Do not in this experiment:

```text
resolve USER_DISTRIBUTABLE
show download links
request or inspect Portable User Context
invoke Account validation
execute any registered executable
claim ACCOUNT_CONTEXT_READY
ask for the user's Genshin goal
```

Those are later validation increments.

## 7. Failure classification

Return a blocked state rather than inventing an operand when:

```text
context-entry.json unavailable
selector schema/status invalid
repository mismatch
active_revision not full 40-hex
active_runtime_url not bound to the same repository/revision
immutable revision cannot be opened
immutable URL revision mismatches active_revision
```

Never convert any of these failures into a request for the user to supply a SHA/tag.

## 8. Experimental boundary

```text
CNB-001 PASS
!= reviewed Architecture trust model
!= Runtime candidate C modification
!= Production
!= release
!= EC-C PASS
```

The purpose is to observe whether a fresh generic ChatGPT conversation can discover and follow a repository-owned current selector without extra user authority operands.
