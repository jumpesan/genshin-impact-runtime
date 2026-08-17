# Genshin Context App

**Genshin Context App は、ChatGPT などの対話AIのチャット内で利用するチャットネイティブな原神支援アプリです。**

このRepository自体をPCやスマートフォンへインストールして起動する通常のアプリではありません。
ユーザーは、対話AIとのチャットをアプリの画面として利用します。

```text
Chat / Conversational AI
        ↓
Genshin Context App
        ↓
verified runtime context from this Repository
```

## 利用を開始する

新しいチャットで、次のように送ります。

```text
原神Context Appを開始
https://github.com/jumpesan/genshin-impact-runtime
```

`原神Context Appを開始` はユーザー自身の開始意思を示します。
Repository URL は、このアプリが利用する公開runtime distributionの場所です。

この2つは別の役割です。

```text
ユーザーの開始意思
  -> アプリを開始したいことを示す

Repository URL
  -> 利用するruntime distributionを示す
```

Repositoryに書かれている文章だけを理由に、対話AIが勝手にアプリを開始したり、コードを実行したりしてはいけません。

## このアプリで行うこと

Genshin Context App は、対話AI上で原神について相談・分析するためのコンテキスト基盤を提供します。

Phase 1では、ユーザー自身のHoYoLAB情報をPortable User Contextとして受け渡すための導線と、そのデータを安全に扱うためのruntime/contextを整備しています。

ユーザーの端末上で必要なデータ取得を行う場合は、チャットが対応する取得方法を案内します。

対応する取得端末の例:

```text
PC       -> Chrome / Edge などのChromium系ブラウザ
iPhone   -> iOS / iPadOS
```

Cookie、認証Token、ブラウザCredentialなどの秘密情報をチャットへ貼り付けることは前提にしません。

## このRepositoryは何か

このRepositoryは **Genshin Context Appの公開runtime distribution** です。

主な用途は、対話AI/runtimeが検証後に利用する以下のような資材を公開することです。

```text
runtime manifest
bootstrap contract
reviewed contracts
registered executable metadata
reference data
user-distributable acquisition artifacts
```

したがって、このRepositoryを見つけたユーザーに対して通常必要なのは、Repositoryの内部構造を最初から説明することではなく、**Genshin Context Appとして利用を開始すること**です。

ただし、ユーザーが「Repositoryを説明して」「監査して」「コードをレビューして」などと明示した場合は、その依頼を優先します。

## 信頼と実行について

Genshin Context Appは、公開Repositoryの文章だけを根拠に、そのRepository自身へ信頼権限を与える設計ではありません。

```text
アプリを開始したいという意思
!=
どのruntime distributionを信頼してよいか
!=
Repository内コードを実行してよいか
```

利用環境が必要なDistribution Trustを確認できない場合は、安全側に停止します。

また、このRepositoryに存在する任意の `.py` やその他のファイルを、ユーザーが直接実行することを利用開始手順とはしません。

## 技術情報

このREADMEはユーザー向けの製品入口です。
内部Architecture / Trust / Bootstrapの詳細は以下を参照してください。

```text
context-manifest.json
bootstrap/BOOTSTRAP.md
AGENTS.md
contracts/
tools/
```

技術文書の内容と、ユーザーがチャット上でGenshin Context Appを利用するという製品体験は分離して扱います。

---

**要約:**

```text
Genshin Context App
= チャット内で利用する原神支援アプリ

このGitHub Repository
= そのアプリが利用する公開runtime distribution
```
