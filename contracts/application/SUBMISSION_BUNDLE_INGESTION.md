# Submission Bundle Ingestion v0.1 — Experimental

## Role

This contract defines generic local ingestion for a `GENSHIN_CONTEXT_SUBMISSION_BUNDLE` attachment.

It is Application/runtime orchestration. It does not own Account semantics or any Domain validator logic.

## Input

One local ZIP attachment.

Expected Account prototype members:

```text
submission-manifest.json
.user-data/portable_context.json
.execution/account_context_ingestion.execution-capsule.json
```

## Phase 1 — Archive envelope

Open the ZIP from local attachment storage only.

Before extracting:

```text
reject absolute paths
reject `..` traversal
reject symlink entries
reject duplicate normalized entry names
reject unexpected execution-capsule member paths
```

Read `submission-manifest.json` first and validate it against:

```text
contracts/application/submission-bundle-v0.1.schema.json
```

## Phase 2 — Runtime binding

Require:

```text
submission-manifest.runtime_binding.repository
== selected Runtime repository

submission-manifest.runtime_binding.revision
== selected immutable Runtime revision
```

Never switch Runtime revision to satisfy the bundle.

Mismatch is:

```text
bundle_status = invalid
reason = RUNTIME_BINDING_MISMATCH
```

## Phase 3 — USER_DATA transport identity

Read `.user-data/portable_context.json` as opaque bytes.

Verify only transport properties before canonical Account validation:

```text
exact path
size_bytes
SHA-256
```

Do not parse the JSON for Domain semantics at this stage.

## Phase 4 — Execution capsule authorization

For each manifest execution-capsule entry:

1. Resolve exactly one matching `context-manifest.registry.execution_capsule_transport` item by `unit_id`.
2. Require manifest `runtime_registry_path` to equal registry `path`.
3. Read the local capsule bytes from the bundle.
4. Compute local capsule byte size and SHA-256.
5. Require local byte identity to equal both bundle manifest identity and Runtime registry identity.
6. Require manifest Git blob identity to equal Runtime registry Git blob identity.

Capsule self-declared fields cannot authorize the capsule.

```text
bundle capsule bytes
+ bundle manifest identity
+ selected Runtime registry identity
-> exact triple match
-> capsule transport authorized
```

Any mismatch fails closed before materialization.

## Phase 5 — Canonical execution

After capsule transport authorization, execute the capsule's declared local materialization recipe.

For the current Account unit this means:

```text
local capsule
-> verify embedded compressed payload
-> decompress
-> verify final registered executable identity
-> fresh isolated root
-> materialize exact entrypoint
-> bind opaque USER_DATA bytes
-> invoke canonical validator
-> parse structured stdout
```

The selected Runtime's `registry.executable_authority` remains the final executable authority anchor.

## Phase 6 — State transition

For Account Portable ingestion:

```text
structured status == valid
and portable_context_valid == true
-> ACCOUNT_CONTEXT_READY
```

Otherwise remain not-ready.

Bundle ingestion errors are distinct from Account validator errors.

Suggested orchestration classes:

```text
BUNDLE_INVALID
RUNTIME_BINDING_MISMATCH
USER_DATA_TRANSPORT_IDENTITY_MISMATCH
CAPSULE_UNREGISTERED
CAPSULE_IDENTITY_MISMATCH
MATERIALIZATION_FAILED
EXECUTION_UNAVAILABLE
VALIDATOR_RESULT_INVALID
VALIDATOR_RESULT_VALID
```

## No-network property

Once the bundle and selected Runtime metadata are resolved, canonical bundle execution must not require network access inside the Python sandbox.

The deterministic execution plane is local attachment storage plus the isolated sandbox.

## Privacy

Do not log or persist full USER_DATA payload in architecture/review evidence.

Record only bounded non-secret identity/status metadata needed for the gate.

## Legacy diagnostic compatibility

Two separate local attachments (Portable USER_DATA + capsule) remain useful for diagnostics but are not the ordinary-user contract.