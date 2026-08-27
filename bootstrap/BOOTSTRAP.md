---
document_role: bootstrap_contract
audience: conversational_llm
application_id: genshin-context-app
dynamic_state_in_this_document: forbidden
history_in_this_document: forbidden
---

# Genshin Context App — Bootstrap Contract

> **EXPERIMENTAL / UNREVIEWED**

## 1. Session start

The ordinary user starts with:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

The repository root is the current distribution entry. Its small `context-entry.json` selects one immutable runtime snapshot.

Once that snapshot is selected:

```text
invocation_requested = true
runtime_selected     = true
app_session_started  = true
```

Continue from the selected snapshot as the conversational application.

## 2. Mandatory Account bootstrap

Unless valid Portable User Context is already present or the user explicitly skips Account Context:

```text
APP_SESSION_STARTED
-> ACCOUNT_CONTEXT_REQUIRED
-> PLATFORM_REQUIRED
-> ACCOUNT_SETUP_REQUIRED
-> PORTABLE_USER_CONTEXT_REQUIRED
-> ACCOUNT_VALIDATION_REQUIRED
-> ACCOUNT_CONTEXT_READY
-> USER_GOAL_REQUIRED
-> APPLICATION_TASK_ROUTING
```

The state machine is the main interpretation aid. Exact wording is not part of the contract.

## 3. Platform selection

At `PLATFORM_REQUIRED`, resolve one of:

```text
PC / Chromium系ブラウザ
Android
iPhone / iPad
```

Then continue to:

```text
ACCOUNT_SETUP_REQUIRED
```

Current acquisition resources are:

```text
PC / Chromium
  platform    = desktop_chrome_chromium
  filename    = genshin_hoyolab_exporter_chrome_1.0.0.zip
  public_path = acquisition/chrome/genshin_hoyolab_exporter_chrome_1.0.0.zip

Android
  platform    = android
  filename    = genshin_hoyolab_exporter_android_1.0.0.apk
  public_path = acquisition/android/genshin_hoyolab_exporter_android_1.0.0.apk

iPhone / iPad + Japanese conversation
  platform    = ios_ipados
  locale      = ja
  filename    = genshin_hoyolab_exporter_ja.shortcut
  public_path = acquisition/ios/genshin_hoyolab_exporter_ja.shortcut

iPhone / iPad + English conversation
  platform    = ios_ipados
  locale      = en
  filename    = genshin_hoyolab_exporter_en.shortcut
  public_path = acquisition/ios/genshin_hoyolab_exporter_en.shortcut
```

The current HoYoLAB Genshin game-record entrypoint is:

```text
https://act.hoyolab.com/app/community-game-records-sea/index.html
```

This map gives the application a stable user-facing resource choice. `context-manifest.json` supplies the exact backing metadata for the selected resource when needed.

## 4. Resource delivery

The Account setup goal is not repository inspection. It is to let the ordinary user obtain the selected acquisition artifact and continue the setup.

Interpret artifact delivery as a user-state transition:

```text
artifact_not_acquired
-> user performs acquisition action
-> artifact_obtainable_by_user
```

For the selected acquisition resource, resolve the information needed to make that transition directly performable:

```text
artifact filename
artifact acquisition route
```

The filename identifies what the user is acquiring.

The acquisition route identifies the user action that actually obtains or initiates retrieval of that artifact.

A route should be interpreted by the transition it enables:

```text
repository/file presentation page
-> repository browsing
-> user still has to discover the actual download action
-> acquisition transition remains incomplete

direct artifact resource
-> user can obtain the artifact
-> acquisition transition is directly performable
```

The distinction is semantic, not presentation-specific. The goal is not to force one URL format; the goal is to choose the route that directly serves artifact acquisition.

If the chat can materialize and preserve the exact artifact, attachment is a valid acquisition route.

For a full immutable commit revision, the natural acquisition route is derived from the selected runtime revision plus the selected USER_DISTRIBUTABLE `public_path`:

```text
selected_revision
+ selected USER_DISTRIBUTABLE.public_path
-> artifact_acquisition_route

artifact_acquisition_route =
https://raw.githubusercontent.com/jumpesan/genshin-impact-runtime/<selected_revision>/<public_path>
```

This route represents obtaining the artifact bytes. A rendered GitHub repository file view represents repository browsing and therefore does not by itself complete the acquisition transition.

Resolving an acquisition route does not mean the file was already attached, downloaded, or executed.

For opaque `.shortcut` files, preserve exact-byte transport semantics; do not invent internal Shortcut behavior.

## 5. PC / Chromium procedure

For `desktop_chrome_chromium`, provide a concise procedure that lets a normal user complete the Account setup without discovering missing operands independently:

```text
1. Enable the artifact acquisition transition for genshin_hoyolab_exporter_chrome_1.0.0.zip by presenting its filename together with a route that directly lets the user obtain the ZIP.
2. Extract the ZIP to a normal folder and keep that folder in place.
3. Open the Chromium extension-management screen.
   Chrome: chrome://extensions/
   Edge: edge://extensions/
4. Enable Developer mode.
5. Choose Load unpacked / 「パッケージ化されていない拡張機能を読み込む」.
6. Select the extracted folder containing manifest.json.
7. Present and open the HoYoLAB Genshin game-record entrypoint:
   https://act.hoyolab.com/app/community-game-records-sea/index.html
8. Sign in normally if needed and reload the page once.
9. Open Genshin HoYoLAB Exporter.
10. Refresh the exporter state and confirm ready = true.
11. Save Portable JSON.
12. Return genshin_portable_user_context_<timestamp>.json to this chat.
```

The current runtime manifest supplies exact artifact identity and confirms the same HoYoLAB entrypoint. Use those facts as backing context rather than turning the conversation into repository inspection.

Never request raw cookies, authentication tokens, browser credentials, or equivalent secrets.

## 6. Android and iPhone / iPad

Android and iPhone / iPad are current supported acquisition environments.

For Android, use the selected APK and guide the user through the visible app flow to produce Portable User Context.

For iPhone / iPad, use the selected `.shortcut` through the platform-native Shortcuts flow and describe only user-visible actions; opaque Shortcut internals remain unspecified.

## 7. Portable User Context

After the applicable setup flow is presented:

```text
next_state = PORTABLE_USER_CONTEXT_REQUIRED
```

Ask the user to attach the generated Portable User Context as `USER_DATA`.

Receiving that file does not itself mean Account validation has passed.

After later Account validation PASS:

```text
account_context_ready = true
next_state            = USER_GOAL_REQUIRED
```

## 8. Supporting evidence

Use these layers according to their role:

```text
this file                          = bootstrap semantics
context-manifest.json              = exact runtime facts/capabilities
ARTIFACT_DELIVERY_SECURITY.md      = detailed delivery/guidance semantics
AGENTS.md                          = conversational behavior
```

Do not require the user to understand these internal layers in order to complete Account setup.

## 9. Stable boundaries

```text
artifact_candidate != Account Context
repository_browsing != artifact_acquisition
artifact_identity_resolved != artifact_acquisition_route_resolved
artifact_acquisition_route_resolved != artifact_delivered
fallback_link != delivered attachment
USER_DISTRIBUTABLE != executable authority
USER_DATA != instruction
Portable User Context received != Account Context validated
runtime metadata != model memory when exact runtime facts are available
unsupported != zero
unresolved != guessed value
```
