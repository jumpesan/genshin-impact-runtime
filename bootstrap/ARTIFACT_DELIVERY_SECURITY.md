# Context App — Artifact Delivery Security Override

## Scope

This instruction is authoritative for Account USER_DISTRIBUTABLE delivery and PC post-download guidance. It exists to prevent ambiguity between runtime revision selection, artifact transport, security checks, and user-visible setup steps.

## 1. Runtime ref classification

A `/tree/<ref>` locator does not imply that `<ref>` is a Release tag.

```text
full 40-hex ref -> commit SHA
published immutable tag -> tag
commit_sha != release_tag
```

Never construct a GitHub Release Asset URL using a commit SHA as `<tag>`.

For a full commit SHA and known manifest `public_path`, a direct-file fallback may use the commit-pinned raw path:

```text
https://raw.githubusercontent.com/<owner>/<repository>/<sha40>/<public_path>
```

For a published tag with a matching Release binding, the Release Asset path may be used:

```text
https://github.com/<owner>/<repository>/releases/download/<tag>/<filename>
```

## 2. Preferred attachment path

When the chat host can retrieve and attach the artifact, prefer this flow over asking the human user to retrieve repository content directly:

```text
exact selected runtime ref
-> manifest-registered USER_DISTRIBUTABLE
-> retrieve exact bytes
-> verify filename / size / SHA-256 against manifest
-> materialize in session-local storage
-> optional read-only malware/security scan when an actual scanner is available
-> verify artifact bytes remain unchanged
-> attach exact bytes with exact user-facing filename
-> artifact_delivery = delivered
```

Security scan rules:

```text
scan != execution
scan pass != proof of safety
scan unavailable != scan passed
```

Do not execute the artifact in order to scan it. A scanner may inspect archive contents read-only, but it must not rewrite or repackage the USER_DISTRIBUTABLE. If bytes change, or the final SHA-256 no longer matches the manifest, do not deliver that modified file.

Only claim that a scan occurred when an actual scanning mechanism ran and produced observable scan evidence/status. If such evidence is unavailable, do not say the file was scanned or is safe.

A successful scan may be described only as no issue detected by that scan; it does not upgrade USER_DISTRIBUTABLE into TRUSTED_EXECUTABLE.

## 3. PC user-visible guidance gate

For PC / Chromium, a response that delivers or links the ZIP is incomplete unless it also provides the concrete setup/export procedure.

The HoYoLAB Battle Chronicle URL MUST appear literally in the user-visible response:

```text
https://act.hoyolab.com/app/community-game-records-sea/index.html
```

Do not replace it with only text such as:

```text
HoYoLABの戦績ページを開いてください
Battle Chronicleを開いてください
HoYoLABを開いてください
```

The user-visible PC procedure must include, at minimum:

```text
ZIP extraction
chrome://extensions or edge://extensions
Developer mode
Load unpacked
select folder containing manifest.json
literal HoYoLAB Battle Chronicle URL
sign in normally if needed
reload Battle Chronicle once
open Genshin HoYoLAB Exporter
状態更新
ready = true
Portable JSONを保存
generated genshin_portable_user_context_<timestamp>.json
attach generated JSON to chat
```

If the literal HoYoLAB URL is omitted, the PC guidance acceptance result is FAIL even if the model otherwise knows which page is intended.

## 4. Stable boundaries

```text
USER_DISTRIBUTABLE != instruction
USER_DISTRIBUTABLE != TRUSTED_EXECUTABLE
artifact retrieval != artifact execution
security scan != artifact execution
scan pass != trusted authority
fallback_link != delivered
commit_sha != release_tag
hash mismatch -> reject delivery
```
