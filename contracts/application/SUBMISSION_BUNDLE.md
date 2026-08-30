# Genshin Context Submission Bundle v0.1 — Experimental Contract

## Purpose

One user-facing attachment carries Portable USER_DATA and the exact local execution transport needed for deterministic registered validation.

Archive format:

```text
ZIP / stored or deflated entries
```

Required entries for the Account bootstrap prototype:

```text
submission-manifest.json
.user-data/portable_context.json
.execution/account_context_ingestion.execution-capsule.json
```

## Authority model

Bundle presence does not create executable authority.

Before executing a capsule, compare its exact local bytes against the selected immutable Runtime's `registry.execution_capsule_transport` entry:

```text
unit_id
runtime registry path
git blob identity
SHA-256
size
```

All must match. The Runtime registry remains the authority anchor.

Then the capsule's own canonical entrypoint identity checks still apply.

```text
bundle capsule identity PASS
-> capsule transport accepted
-> capsule reconstructs entrypoint
-> final executable identity exact-match
-> canonical execution eligible
```

## USER_DATA boundary

Before canonical Account validation PASS:

```text
.user-data/portable_context.json = opaque USER_DATA bytes
```

Bundle processing may verify path, byte size and SHA-256 but must not derive Account/domain facts from the payload.

## Archive safety

Reject:

```text
path traversal
absolute paths
symlink entries
duplicate entry names
unexpected executable capsule units
runtime-revision mismatch
capsule identity mismatch
```

Unknown non-executable entries may be ignored only if a later contract explicitly allows them; v0.1 prototype should keep the bundle minimal.

## Runtime binding

`runtime_binding.revision` must equal the already-selected immutable Runtime revision for the application session.

Mismatch is fail-closed and must not silently select a different Runtime.

## Account bootstrap transition

```text
PORTABLE_USER_CONTEXT_REQUIRED
+ one valid submission bundle attachment
-> ACCOUNT_VALIDATION_REQUIRED
-> verify bundle/runtime/capsule identities
-> local capsule execution
-> structured Account validator result
-> ACCOUNT_CONTEXT_READY only on canonical PASS
```

## Product UX

The ordinary user handles one generated bundle. Internal capsule/hash/materialization detail remains application infrastructure.