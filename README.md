# Genshin Context App — CNB-001 Experimental Runtime

> **EXPERIMENTAL / UNREVIEWED**
>
> This revision exists only for the context-native bootstrap manual validation spike. It is not Production, not a reviewed release, and does not change the frozen Runtime candidate C.

## Entry contract

The intended ordinary-user invocation remains exactly:

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

The ordinary user must **not** provide, choose, or guess a tag, commit SHA, tree, digest, selector, DTA, manifest path, or executable identity.

For CNB-001, the repository root is a distribution namespace only. The mutable root exposes `context-entry.json`, which selects exactly one immutable experimental runtime revision.

```text
user-supplied repository root
  -> read root context-entry.json
  -> resolve active_revision (full 40-hex SHA)
  -> open that exact immutable revision
  -> this README / context-manifest.json / bootstrap/BOOTSTRAP.md / AGENTS.md
```

If you are reading this file from an immutable GitHub revision selected by the root `context-entry.json`, then:

```text
runtime_selected = true
selected_runtime_revision = the full 40-hex revision in the current immutable URL
```

Do not ask the user to repeat or supply that revision.
Do not fall back to `main` as runtime content.
Do not choose another revision from repository history.

## CNB-001 scope

This experiment validates only:

```text
root repository URL
-> context-entry discovery
-> immutable revision selection
-> Context App session start
-> PLATFORM_REQUIRED
```

After the immutable revision is selected, load:

```text
context-manifest.json
bootstrap/BOOTSTRAP.md
AGENTS.md
```

Then begin the application session and ask for the platform according to the experimental bootstrap contract.

Do not resolve or present acquisition artifacts in CNB-001. Do not request Portable User Context. Do not execute any repository tool.

## Experimental authority hypothesis

For this spike only, the hypothesis under test is:

```text
explicit user choice of repository namespace
+ repository-root context-entry.json current selector
+ exact immutable revision retrieval
= sufficient context-native bootstrap selection for a plain fresh ChatGPT conversation
```

This is an experiment, not a finalized trust model. A successful conversational result does not by itself authorize this design for Production.
