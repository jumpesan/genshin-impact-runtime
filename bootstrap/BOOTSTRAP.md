# Context App Bootstrap — CNB-002 Experimental

> **EXPERIMENTAL / UNREVIEWED**
>
> CNB-1 proved context-native discovery of one immutable runtime from the ordinary repository root URL on ChatGPT Free with thinking=false and thinking=true. CNB-002 extends only the PC / Chromium Account acquisition path.

## 1. Invocation and current-runtime discovery

The ordinary user starts with:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

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

When the supplied locator is the repository root, resolve only:

```text
root context-entry.json
-> active_revision
-> active_runtime_url
-> exact immutable revision
```

The root/default branch is the experimental current-runtime index only. It is not runtime content.

Require the selector to bind the same repository and one full 40-hex `active_revision`. If deterministic selection fails, return:

```text
RUNTIME_RESOLUTION_BLOCKED
```

Do not ask the user to repair the missing internal operand.

After immutable transition:

```text
runtime_selected = true
selected_runtime_revision = context-entry.active_revision
```

Do not return to `main` for runtime semantics and do not change revisions during this session.

## 2. Runtime-local authority for CNB-002

From the exact selected immutable revision, use:

```text
context-manifest.json
bootstrap/ARTIFACT_DELIVERY_SECURITY.md
bootstrap/BOOTSTRAP.md
AGENTS.md
README.md
```

`context-manifest.json` is the selected revision's role/capability registry.

For this experiment, the context-native selector is sufficient to enter application mode. Final trust architecture remains subject to later formal Architecture review.

## 3. Application state

After immutable runtime selection:

```text
APP_SESSION_STARTED
-> ACCOUNT_CONTEXT_REQUIRED
-> PLATFORM_REQUIRED
```

If platform is unresolved, ask using choices equivalent to:

```text
PC / Chromium系ブラウザ
Android
iPhone / iPad
```

CNB-002 positive validation is limited to:

```text
PC / Chromium系ブラウザ
-> platform = desktop_chrome_chromium
```

Android and iPhone / iPad remain outside the CNB-002 positive-control scope. Do not invent their behavior from this experimental file.

## 4. PC USER_DISTRIBUTABLE resolution

After the user selects PC / Chromium:

```text
next_state = ACCOUNT_ARTIFACT_REQUIRED
```

Resolve exactly one record from the selected immutable revision's:

```text
context-manifest.json
registry.user_distributable
```

Require:

```text
role = USER_DISTRIBUTABLE
platform = desktop_chrome_chromium
availability = available
execution_scope = user_device
```

For the selected record, use the manifest-owned values for:

```text
artifact_id
public_path
user_facing_filename
size_bytes
sha256
git_blob_sha
entrypoint_url
produces
output_format_version
portable_ingestion
```

Do not use model memory or `main` to fill any unresolved runtime-owned field.

If zero or multiple applicable records resolve, or required runtime-owned fields are unavailable:

```text
USER_DISTRIBUTABLE_RESOLUTION_BLOCKED
```

Do not ask the ordinary user for repository-internal identities.

## 5. Delivery semantics for a selected commit revision

CNB-002 selects an immutable full commit SHA.

If the host can attach the exact artifact bytes and can verify them against the selected manifest identity, attachment is allowed.

Otherwise construct the commit-pinned direct file location from:

```text
selected_runtime_revision
+ selected USER_DISTRIBUTABLE.public_path
```

using:

```text
https://raw.githubusercontent.com/jumpesan/genshin-impact-runtime/<selected_runtime_revision>/<public_path>
```

This is a fallback link, not a claim that the file was attached or downloaded.

Never interpret the commit SHA as a GitHub Release tag.
Never construct a Release Asset URL from the commit SHA.

## 6. PC user-device procedure

After the PC USER_DISTRIBUTABLE is resolved, provide a concise actionable procedure using the selected manifest record and selected immutable revision.

Required semantics:

```text
1. Obtain the exact selected Chrome/Chromium artifact.
2. Extract it and keep the extracted folder available.
3. Open the Chromium extension-management surface.
4. Enable developer mode.
5. Load the unpacked folder containing manifest.json.
6. Navigate to the exact selected USER_DISTRIBUTABLE.entrypoint_url.
7. Sign in normally if needed and reload the relevant page.
8. Open the Genshin HoYoLAB Exporter popup.
9. Refresh exporter state and confirm ready = true.
10. Save Portable JSON.
11. Identify the produced genshin_portable_user_context_<timestamp>.json.
12. Return that generated file to this chat.
```

Do not request raw cookies, authentication tokens, browser credentials, or equivalent secrets.
Do not tell the user to read instructions inside the ZIP.

The procedure is complete only if the exact artifact route and exact manifest-owned external entrypoint are both resolved.

## 7. CNB-002 stop boundary

After presenting the PC artifact route and user-device procedure:

```text
next_state = PORTABLE_USER_CONTEXT_REQUIRED
```

Ask the user to return the generated Portable User Context JSON.

Stop there for CNB-002.

Do not:

```text
inspect or validate Portable USER_DATA
run Account validation
materialize or execute TRUSTED_EXECUTABLE bytes
claim ACCOUNT_CONTEXT_READY
ask for the user's Genshin goal
change selected_runtime_revision
```

## 8. Failure classification

Fail closed without inventing operands on:

```text
root selector failure
immutable revision mismatch
manifest unavailable
PC USER_DISTRIBUTABLE zero/multiple match
required artifact identity missing
entrypoint_url unresolved
commit-pinned artifact route unresolved
revision drift to main/default/another commit
```

## 9. Experimental boundary

```text
CNB-002 PASS
!= reviewed Architecture trust model
!= Production
!= release
!= Account validation PASS
!= EC-C PASS
```
