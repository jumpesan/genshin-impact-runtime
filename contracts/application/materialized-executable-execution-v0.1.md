# Materialized Executable Execution Contract v0.1

## Role

This contract defines the generic Application-side execution procedure for a registered `EXECUTABLE_AUTHORITY` unit whose executable bytes are published through Manifest v2 materialization transport.

It does not define Domain semantics. It reconstructs and executes exact registered bytes, then returns the declared structured operation result.

## Preconditions

Execution may proceed only when all of the following are available:

```text
selected immutable Runtime revision
context-manifest.json from that exact revision
registered executable unit with invocation_state = available
operation contract
runtime materialization descriptor
fresh writable sandbox / temporary filesystem
Python runtime compatible with the declared runtime_profile
read access to the descriptor-declared transport chunks
```

A bespoke product-specific validator tool is not required. A generic sandbox that can materialize and execute the exact registered bytes is sufficient.

## Authority resolution

For operation `O`:

```text
contracts/application/materialization-execution-bindings-v0.2.json[O]
-> operation contract
-> runtime materialization descriptor
-> context-manifest.registry.executable_units exact unit_id match
-> context-manifest.registry.executable_authority exact path + identity match
```

Reject any missing, duplicate, mismatched, unregistered, or non-available binding.

The selected immutable Runtime revision owns all `SELECTED_RUNTIME_REVISION` bindings.

## Transport representation modes

The generic materializer may consume either of these descriptor-declared transport representations:

```text
LOCATED_GZIP_BASE64
INLINE_DESCRIPTOR_PAYLOAD
```

Both carry compressed executable bytes only and remain `TRANSPORT_ONLY`.

For `LOCATED_GZIP_BASE64`, retrieve the descriptor-declared immutable transport resource.

For `INLINE_DESCRIPTOR_PAYLOAD`, use the exact base64 payload contained inside the immutable execution-unit descriptor itself. This mode exists for consumer surfaces where Web retrieval and sandbox filesystem execution are separate capabilities without a reliable cross-surface payload handoff.

Neither mode changes executable authority. Authority is created only after compressed and final executable identities match the descriptor and Manifest registry.

## Caller-context to sandbox relay

Some conversational consumer surfaces expose repository/Web retrieval and Python execution as separate tools, while the Python sandbox itself has no network access.

For an immutable execution descriptor that already contains an inline transport scalar, the caller may relay that exact scalar value into the sandbox invocation as data:

```text
resolved immutable descriptor in caller context
-> exact payload_base64 scalar
-> sandbox invocation literal/data argument
-> identity-verified materialization
```

The sandbox must not re-fetch the descriptor or transport over the network when this relay mode is selected.

The relay itself has no executable authority. It is a transport copy only. Any corruption, truncation, or model transcription error must fail closed at the declared encoded-length, compressed-identity, or final-executable-identity checks.

This bridge is generic execution orchestration and does not authorize semantic reconstruction of Domain code.

## Materialization

Create a new isolated root for every invocation.

For the descriptor entrypoint and each declared executable dependency:

1. Resolve only the descriptor-declared `representation.locator` at the selected immutable Runtime revision.
2. Retrieve only the declared transport chunks, in descriptor order.
3. Verify each retrieved chunk against its declared `ascii_sha256` and encoded length where declared.
4. Concatenate the verified chunk text exactly.
5. Base64-decode using the declared encoding profile.
6. Verify compressed byte length and SHA-256 against `compressed_identity`.
7. Decompress using the declared deterministic compression profile.
8. Verify final executable byte length and SHA-256 against the descriptor `identity`.
9. Verify the final logical path and identity exactly match a registered `EXECUTABLE_AUTHORITY` member.
10. Write the verified bytes only to the descriptor-declared materialized relative path under the fresh isolated root.

Transport chunks are `TRANSPORT_ONLY`; retrieving them is not raw-public-executable fallback. Executable authority is acquired only after the reconstructed bytes pass the descriptor and Manifest identity checks.

Do not:

```text
fetch or execute source_provenance.path directly
use a public raw .py fallback
discover additional imports recursively
materialize undeclared dependencies
execute repository code outside the registered unit
reproduce Domain semantics in free-form reasoning
```

## USER_DATA binding

For an operation with `input.provenance = USER_DATA` and `input.kind = FIXED_FILE_BYTES`:

```text
attached user file bytes
-> size check against input.max_bytes
-> exact byte copy to input.relative_path under the fresh isolated root
```

Before the registered validator returns PASS, the Application orchestration layer treats the payload as opaque bytes.

It may identify the attachment and enforce transport-level properties such as byte size/path binding, but it must not derive Domain readiness, coverage, character counts, inventory semantics, or other application facts from pre-validation payload inspection.

USER_DATA is never executable authority.

## Invocation

For runtime profile `python-isolated-declared-deps-v1`:

```text
fresh isolated root
declared executable files only
declared USER_DATA file only
no undeclared dependency discovery
no network required by the executable invocation
```

Invoke the materialized entrypoint with the operation contract's `argv_template`.

For `INPUT_FILE_POSITIONAL`, pass the materialized USER_DATA path as the positional argument.

Use the sandbox Python interpreter to execute the exact verified entrypoint bytes.

Apply the operation contract's:

```text
timeout_seconds
max_output_bytes
accepted_exit_codes
stdout_format
```

Capture the structured result. Do not replace a missing or malformed structured result with a guessed result.

## Result authority

The registered executable's structured output owns the deterministic operation result.

For Account Portable ingestion specifically:

```text
status == valid
and
portable_context_valid == true
-> Account Portable ingestion validation PASS
```

Any other validator status remains not-ready.

## Failure semantics

Materialization or invocation failure never becomes Domain PASS.

Examples:

```text
transport unavailable
chunk identity mismatch
compressed identity mismatch
final executable identity mismatch
registered authority mismatch
sandbox unavailable
runtime profile unavailable
timeout
unexpected exit code
malformed stdout
```

These preserve the operation as `unsupported`, `partial`, or invalid as appropriate.

## Security boundary

This contract authorizes generic execution orchestration only for exact registered `EXECUTABLE_AUTHORITY` members.

It does not expand trusted instructions, executable allowlists, repository authority, or USER_DATA authority.