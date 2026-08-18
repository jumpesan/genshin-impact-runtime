# Context App — Artifact Delivery Security Boundaries

## Purpose

This document defines the stable security and integrity properties of Account `USER_DISTRIBUTABLE` transport.

It is intentionally narrow. Bootstrap behavior and user guidance are defined by `bootstrap/BOOTSTRAP.md`.

## 1. Artifact identity

The selected manifest record defines the artifact identity.

A delivered artifact satisfies:

```text
filename == user_facing_filename
size     == size_bytes
sha256   == manifest sha256
revision == selected runtime revision
```

A byte mismatch changes artifact identity and therefore does not satisfy delivery of the selected `USER_DISTRIBUTABLE`.

## 2. Execution boundary

`USER_DISTRIBUTABLE` execution occurs on `user_device` according to its declared `execution_scope`.

Repository retrieval, session-local materialization, hashing, archive inspection, and chat attachment are transport or inspection operations rather than authority to execute the artifact.

## 3. Optional security scanning

A host may perform a read-only security scan when an actual scanner is available.

Scan semantics are:

```text
scanner executed -> report its observed status factually
scanner unavailable -> no scan result
scan success -> no issue reported by that scanner in that run
```

Scanning preserves artifact bytes. The final delivered bytes still satisfy the manifest identity after inspection.

A scan result does not change the artifact's trust role from `USER_DISTRIBUTABLE` to `TRUSTED_EXECUTABLE`.

## 4. Opaque artifacts

An artifact marked `opaque = true` is transported as exact registered bytes. Its runtime behavior is represented by trusted metadata/contracts and by user-visible behavior on the user's device, not by reconstructing or rewriting its binary representation.

## 5. Credential boundary

Authentication credentials stay within the user's normal device/browser session.

The Account acquisition handoff to chat is the produced Portable User Context. Raw cookies, authentication tokens, and browser credentials are outside the chat payload boundary.

## 6. Fail-closed identity

Artifact identity, authority, or required security state remains unresolved when its authoritative evidence is unresolved.

```text
unresolved evidence -> unresolved state
hash mismatch        -> delivery rejected
```
