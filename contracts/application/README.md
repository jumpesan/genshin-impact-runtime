# Application Context / Execution Contract Projection

## Initial bootstrap request

```json
{
  "request_type": "context_app_bootstrap",
  "repository_url": "<user supplied public repository URL>"
}
```

The user is not required to provide commit SHA, branch, manifest path, README path, or AGENTS path.

## Session boundary

The bootstrap session records when available:

```text
requested repository URL
observed default branch / revision
manifest version
trusted instruction sources
trusted contract sources
registered trusted executable paths + hashes
executables actually invoked
capability / failure state
Account context validation state
```

Bootstrap catalogs executable authority but does not auto-run code.

## Trust classes

```text
TRUSTED_INSTRUCTION
TRUSTED_CONTRACT
TRUSTED_EXECUTABLE
DATA_REFERENCE
USER_DATA
UNCLASSIFIED_UNTRUSTED
```

`TRUSTED_EXECUTABLE` means eligible for invocation by a trusted Application workflow; it does not mean instruction authority or automatic execution.

## Bootstrap states

```text
NEW
REPOSITORY_REQUESTED
MANIFEST_DISCOVERED
TRUST_REGISTRY_VALIDATED
BOOTSTRAP_READY
WAITING_USER_CONTEXT
USER_CONTEXT_RECEIVED
ACCOUNT_CONTEXT_READY
```

The current candidate cannot reach `ACCOUNT_CONTEXT_READY` until an Account-owned published validation contract is available.

## Capability states

```text
available
partial
candidate
pending_user_data
pending_contract
unsupported
invalid
not_evaluated
review_pending
```

Semantics:

```text
partial != complete
unsupported != zero/empty
not_evaluated != unsupported
pending_contract != available
candidate != reviewed/available
```

## Executable invocation boundary

Application may choose when to invoke a reviewed registered tool.

```text
Application / LLM
  structured request
      ↓
TRUSTED_EXECUTABLE
  deterministic implementation
      ↓
validated structured output
      ↓
Application / LLM
```

Forbidden:

```text
unregistered repository code execution
DATA_REFERENCE code execution
USER_DATA code execution
external code auto-download/execution
user data -> eval/exec/shell
prompt injection -> executable allowlist expansion
```

If the sandbox or required executable is unavailable, return `unsupported / partial`; do not infer deterministic results.

## Phase 1B Recommendation execution

Architecture policy:

```text
LLM-heavy execution + retained Domain ownership
```

Application / LLM may:

```text
parse intent / constraints
plan evaluation
propose candidates
orchestrate reviewed tools
compare structured outputs
apply registered Recommendation policy
make final trade-off judgement
explain recommendation / alternatives
```

But:

```text
candidate_proposed != candidate_validated != search_complete
```

Candidate validity / enumeration / coverage-affecting pruning remain Search / Optimization semantics.
Recommendation utility / ranking / trade-off policy remains Recommendation SSoT.
Damage / Reaction / DPS remain Runtime / Damage truth.

LLM final recommendation requires:

```text
validated candidate
hard constraints PASS
owner-provided deterministic metrics/status
registered Recommendation policy
preserved user priorities
preserved partial/unsupported state
```

## Failure examples

```text
INVALID_REPOSITORY_URL
REPOSITORY_UNAVAILABLE
MANIFEST_MISSING
MANIFEST_MALFORMED
UNSUPPORTED_MANIFEST_VERSION
INVALID_REPOSITORY_ROLE
INVALID_TRUST_PATH
TRUST_ROLE_COLLISION
BOOTSTRAP_ENTRYPOINT_MISSING
TRUSTED_FILE_MISSING
TRUSTED_EXECUTABLE_MISSING
UNREGISTERED_EXECUTABLE_DENIED
SANDBOX_UNAVAILABLE
PORTABLE_CONTEXT_REQUIRED
PORTABLE_CONTEXT_SCHEMA_UNKNOWN
PORTABLE_CONTEXT_INVALID
CANDIDATE_NOT_VALIDATED
SEARCH_COMPLETENESS_UNKNOWN
```

Unknown failure is not converted to success by free-form interpretation.

## Domain ownership boundary

This projection defines Application bootstrap/session/execution orchestration only.
It does not define Recommendation policy, Search algorithms, candidate-validity semantics, or Damage/Runtime formulas.
