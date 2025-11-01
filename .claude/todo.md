# TODO List (タスク管理)

このファイルには、今後やるべきタスクを記録します。優先順位をつけて管理しましょう。

**最終更新:** 2025-10-31（todo.md整理: LangGraph拡張タスクをアイデアセクションに移動）

---

## ファイル管理方針

**このファイルの特性:** タスクのライフサイクル管理（追加→進行中→完了→削除）

**メンテナンスガイドライン:**
- **完了タスク**: 月に1回程度、古い完了タスクを削除
- **不要になったタスク**: すぐに削除またはアイデアセクションに移動
- **原則**: 完了セクションに溜め込みすぎない（直近1-2ヶ月分のみ）

**サイズ管理:**
- **300行を超えたら**: 完了タスクの整理を検討
- **500行を超えたら**: 完了タスクを別ファイル（`.claude/archive/completed-YYYY-MM.md`）に移動

**YAGNI原則の適用:**
現時点ではアーカイブ構造は作成していません。必要になってから対応します。

---

## 進行中 (In Progress)

現在進行中のタスクはありません。

---

## 優先度: 高 (High Priority)

🎉 **MVP完成！Phase 1完了！**

**プロジェクトの方向性（2025-10-29更新）:**
このプロジェクトは、LangChain/LangGraphの**実装例集**として発展させます。
- 様々な実装パターン（同期/ストリーミング、LangChain/LangGraph）を網羅的に示す
- 学習者が参考にできるベストプラクティスを提供

### 品質向上・開発環境改善

- [ ] 日本語IME入力対応（Enterキー問題の修正）
  - 問題: 日本語変換確定のEnterでメッセージが送信されてしまう
  - 目的: 日本語ユーザーの使いやすさ向上
  - 実装: 2段階アプローチ
    1. **暫定対応（Qiita回避策）**: すぐに使えるようにする
    2. **根本解決（OSSコントリビューション）**: Chainlit本体を修正

  **Phase 1: 暫定対応（優先）**
  - 解決策: `public/custom.js` を作成してIME状態を追跡
  - 手順:
    1. `public/custom.js` ファイルを作成
    2. `.chainlit/config.toml` に `custom_js = "/public/custom.js"` を追加
    3. JavaScriptでIME compositionイベントをハンドリング
  - 参考: Qiita記事 https://qiita.com/bohemian916/items/4f3e860904c24922905a
  - 見積もり: 1-2時間
  - 影響範囲: public/custom.js（新規）、.chainlit/config.toml

  **Phase 2: OSSコントリビューション（推奨）**
  - 目的: 日本語・中国語・韓国語すべてのユーザーのために根本解決
  - 関連Issue:
    - Issue #2600: 中国語IME（Pinyin）の問題
    - Issue #2598: 韓国語IMEの問題
    - 日本語の報告はまだない → 追加する
  - タスク:
    1. Issue #2600と#2598に日本語でも同じ問題があるとコメント
    2. 両方のIssueに👍リアクション（優先度を上げるため）
    3. Chainlitのフロントエンドコードを調査（React）
    4. Composition Events処理を追加するPRを作成
    5. テスト: 日本語・中国語・韓国語すべてで動作確認
  - 技術詳細:
    - 場所: フロントエンドのReactコンポーネント（入力フィールド）
    - 修正内容: `onCompositionStart/End`イベントハンドラを追加
    - 実装例は decisions.md と references.md に記載済み
  - 参考資料:
    - Issue #2600: https://github.com/Chainlit/chainlit/issues/2600
    - Issue #2598: https://github.com/Chainlit/chainlit/issues/2598
    - Web標準: MDN Composition Events
  - 見積もり: 3-5時間（コード調査+実装+テスト+PR作成）
  - 影響範囲: Chainlitリポジトリ（フロントエンド）
  - メリット:
    - 自分のアプリだけでなく、全世界のユーザーに貢献
    - 暫定回避策が不要になる
    - メンテナンス負担が減る

### コード品質・信頼性の向上

- [x] 既存実装のリファクタリング（コード品質向上） - 2025-11-01
  - 目的: 無駄な処理の削除、型ヒントの追加、変数名の整理
  - 対象ファイル:
    - [app_langchain_sync.py](../app_langchain_sync.py)
    - [app_langchain_streaming.py](../app_langchain_streaming.py)
    - [app_langgraph_sync.py](../app_langgraph_sync.py)
    - [app_langgraph_streaming.py](../app_langgraph_streaming.py)（実装後）
  - 具体的な改善項目:
    1. **無駄な処理の削除**:
       - `AIMessage(last_message.content)` の再作成を削除（LangGraph版）
       - `response["messages"]` をそのまま使う（LangGraphが管理した履歴を活用）
    2. **型ヒントの追加**:
       - 関数の引数・返り値に型ヒントを追加
       - 変数にも適切な型アノテーションを追加
       - 例: `messages: list[BaseMessage]`, `response: dict[str, Any]`
    3. **変数名の整理**:
       - 似たような変数名（`response`, `msg`, `message`, `messages`など）を整理
       - より明確で区別しやすい名前に変更
  - 見積もり: 2-3時間
  - 依存: Phase 2a（LangGraphストリーミング実装）の完了
  - メモ: 型チェック導入前に実施すると効果的
  - 影響範囲: 4つの実装ファイル全て
  - 完了内容:
    - `load_chat_history()` の共通化とセッションキー統一
    - LangGraph版に `ChatState` を導入し `agent.ainvoke` のレスポンスを直接保存
    - ストリーミング時は `Message.stream_token()` の蓄積をそのまま履歴に反映
    - Pull Request #7（Refine Lang chat handlers）でマージ済み

### アーキテクチャ・構成

- [ ] docker-compose.ymlの更新（app.pyから新ファイル名への変更）
  - 目的: docker-compose upで起動するアプリを明確にする
  - 現状の問題: docker-compose.ymlが`app.py`を参照しているが、このファイルは存在しない
  - 検討事項:
    - どの実装をデフォルトにするか（app_langchain_streaming.py推奨）
    - または環境変数で選択可能にする
  - 影響範囲: [docker-compose.yml](../docker-compose.yml)
  - 見積もり: 30分
  - メモ: ファイル整理後に対応（別タスク）

- [ ] ディレクトリ構成の見直し
  - 目的: 複数の実装例を整理された形で提供
  - 現状の問題: `app_*.py`がトップディレクトリに散らばると見通しが悪い
  - 検討事項:
    - 実装パターン別のディレクトリ構成（examples/, src/, など）
    - 各実装の説明用README配置
    - Chainlit起動方法の統一
  - 影響範囲: プロジェクト全体
  - 見積もり: 2-3時間（設計+実装+ドキュメント更新）
  - メモ: 将来的な検討課題

### 機能拡張

- [ ] LangSmithの導入
  - 目的: LLM呼び出しのトレーシング、デバッグ、パフォーマンスモニタリング
  - 実装内容:
    - LangSmith環境変数設定（LANGCHAIN_API_KEY等）
    - 各実装にトレーシング追加
    - ドキュメント更新（セットアップ手順）
  - 見積もり: 2-3時間
  - 参考: https://docs.smith.langchain.com/

---

## 優先度: 中 (Medium Priority)

### 開発環境・運用改善

- [ ] Static type check (型チェック) の導入
  - 目的: 型エラーを事前に検出し、コードの安全性を向上
  - 検討ツール:
    - **mypy**: 最もポピュラーな型チェッカー、厳格なチェック
    - **pyright**: Microsoft製、高速、VS Code統合が優れている
    - **pytype**: Google製、型ヒント不要でも推論可能
  - 実装内容:
    1. ツール選定（mypyまたはpyright推奨）
    2. `uv add --dev mypy` または `uv add --dev pyright`
    3. pyproject.tomlに設定を追加
    4. 既存コードに型ヒントを追加（段階的に）
    5. DevContainerに型チェッカー拡張機能を追加（VS Code）
  - 運用ルール案:
    - コミット前に `uv run mypy .` または `uv run pyright` を実行
    - Ruffと同様に手動実行（将来的にGitHub Actionsで自動化）
  - 影響範囲: pyproject.toml、app.py、.devcontainer/devcontainer.json
  - 見積もり: 1-2時間
  - メモ: Ruffと組み合わせることで、コード品質が大幅に向上


- [ ] GitHub CLI (gh) の認証方法の見直し
  - 目的: セキュリティと利便性の向上
  - 現状の課題:
    - ホストの `~/.config/gh/hosts.yml` に依存している
    - 認証トークンのスコープが広すぎる可能性
  - 検討項目:
    1. **Fine-grained Personal Access Token**: 特定リポジトリ(ai-agent-demo)のみに制限
    2. **認証の永続化方法**:
       - オプションA: ホストの認証情報をマウント（現状）
       - オプションB: 環境変数 `GH_TOKEN` を使用
       - オプションC: DevContainer内で `gh auth login` を実行
    3. **Branch Protection Rules**: mainブランチへの直接pushを防ぐ
  - 実装内容:
    - Fine-grained PATの作成と設定（必要な権限のみ）
    - 認証方法の最適化（必要に応じて）
  - 影響範囲: [.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json)（認証設定）
  - 見積もり: 1時間
  - 参考: [decisions.md](decisions.md) - GitHub CLI採用の決定に記載済み
  - メモ: 実際の運用で不便が出てから対応でOK

- [ ] Loggingの仕組み導入
  - 目的: デバッグ・運用時のトラブルシューティング
  - 検討項目:
    1. loguru
    2. 標準logging
    3. Chainlit既定の `cl.logger`
  - 影響範囲: [app_langchain_sync.py](../app_langchain_sync.py), [app_langchain_streaming.py](../app_langchain_streaming.py), [app_langgraph_sync.py](../app_langgraph_sync.py)、設定ファイル
  - 見積もり: 1時間

---

## 優先度: 低 (Low Priority)

- [ ] リトライ機能の追加（with_retry()）
  - 目的: 一時的なネットワークエラーやレート制限に自動対応
  - 実装内容:
    - LangChainの `with_retry()` を使用してリトライ機構を追加
    - 最大試行回数、バックオフ戦略の設定
    - リトライ対象の例外タイプの選択
  - 実装例:
    ```python
    model = ChatOpenAI(model="gpt-5-nano").with_retry(
        retry_if_exception_type=(Exception,),
        stop_after_attempt=3,
        wait_exponential_jitter=True
    )
    ```
  - 影響範囲: すべての実装ファイル
  - 見積もり: 1-2時間
  - メモ: まずは基本的なエラーハンドリングで様子を見る
  - 参考: [decisions.md](decisions.md) - エラーハンドリングの実装方針

- [ ] GitHub ActionsでRuffの自動チェック
  - 目的: PR作成時に自動的にコード品質をチェック
  - 実装内容:
    - `.github/workflows/lint.yml` を作成
    - `ruff check` と `ruff format --check` を実行
    - PRがマージされる前にコード品質を保証
  - 見積もり: 30分-1時間
  - メリット: 手動実行忘れを防止、PRレビュー時の品質保証

- [ ] デプロイ手順のドキュメント作成
  - 目的: 本番環境への展開準備
  - 依存: デプロイ方法の決定（decisions.md参照）
  - 見積もり: 1時間

---

## アイデア・検討中 (Ideas / Backlog)

### LangGraph機能拡張（まだアイデア段階）

これらのタスクは、現状のシンプルな1ノード実装から複数ノードへの拡張アイデアです。まだ具体的な要求がないため、アイデアセクションに配置しています。

- [ ] LangGraph複数ノードの実装
  - 目的: より複雑なワークフローの実現（research → analysis → generation など）
  - 前提: 現状は1ノードのシンプルな実装のみ。複数ノードが必要になるユースケースが出てから検討
  - 実装内容:
    - 複数ノードのグラフ構造を作成
    - ノード間の状態遷移・データフロー
    - 条件分岐やループなどの制御構造
  - 見積もり: 3-4時間
  - メモ: 具体的なユースケース（例: RAG、エージェント）が決まってから実装

- [ ] LangGraph進捗表示の実装
  - 目的: 複数ノードの処理状況をリアルタイムで可視化
  - 前提: 複数ノードの実装が先
  - 実装内容:
    - `stream_mode="updates"` でノード単位の進捗を取得
    - Chainlitで「🔍 リサーチ中...」「📊 分析中...」などの進捗メッセージを表示
  - 見積もり: 2-3時間
  - メモ: 1ノードでは進捗表示の意味がない

- [ ] LangGraph高度なストリーミング（進捗表示 + トークンストリーミング）
  - 目的: ノード単位の進捗表示とトークン単位のストリーミングを組み合わせる
  - 前提: 複数ノード実装 + 進捗表示実装が先
  - 実装内容:
    - `stream_mode=["updates", "messages"]` で両方を同時に使用
    - 進捗表示とリアルタイムレスポンスの両立
    - タプル形式で返されるchunkを適切に処理
  - 見積もり: 3-4時間
  - メモ: 実装パターンはcontext.mdに記録済み。実際のニーズが出てから検討

- [ ] LangGraphチェックポイント機構の検討・導入
  - 目的: Chainlitセッションに依存せずに会話履歴を永続化し、LangGraph内で状態を復元できるようにする
  - 参考: LangGraphのcheckpointドキュメント、現在の`app_langgraph_sync.py`実装
  - 実装内容:
    - チェックポイントストア（ローカルファイルまたはインメモリ）を設定
    - `agent.ainvoke` 呼び出し時にcheckpointを活用する形へ変更
    - Chainlitセッションとの役割分担を再検討し、どちらを正本にするか整理
  - 見積もり: 2-3時間
  - メモ: 現状のシンプル実装ではChainlitセッションに履歴を保存している。置き換えメリットを検証してから着手

- [ ] LangGraphツール呼び出しの実装
  - 目的: 外部APIやデータベースとの連携
  - 前提: 具体的な統合先（Webサーチ、データベース、APIなど）が決まってから
  - 見積もり: 未定（統合先による）
  - メモ: まずは何を統合したいか決める

### その他のアイデア

- [ ] Chainlit以外のUIフレームワークの検討
  - 目的: 実装例集として、様々なUIフレームワークでの使用例を提供
  - 候補:
    - CLI（シンプルなコマンドライン実装）
    - Streamlit（データサイエンス向け）
    - Gradio（ML demo向け）
    - FastAPI（REST API）
  - メリット: ユースケース別の実装例を示せる
  - デメリット: メンテナンスコストが増える
  - メモ: 実装例集としての価値を考慮して判断

- [ ] システムプロンプトのカスタマイズ
  - 目的: アシスタントの性格・役割を設定可能に
  - 検討ポイント: どのシステムプロンプトをカスタマイズするか（app_langchain.py? app_langgraph.py? 両方?）
  - 見積もり: 30分
  - メモ: 必要性が明確になってから実装

- Jupyter Notebookでのプロトタイピング例を追加
- ユニットテストの追加

---

## 完了 (Completed)

### 2025-10-31

- [x] 2×2実装マトリックスの完成
  - 🎉 LangChain/LangGraph × sync/streaming の全4パターンを実装完了
  - 完成状態:
    - ✅ LangChain + 同期（app_langchain_sync.py）
    - ✅ LangChain + ストリーミング（app_langchain_streaming.py）
    - ✅ LangGraph + 同期（app_langgraph_sync.py）
    - ✅ LangGraph + ストリーミング（app_langgraph_streaming.py）
  - プロジェクトの方向性「実装例集」の基盤が完成

- [x] LangGraphストリーミング版の実装（Phase 2a: シンプル版）
  - app_langgraph_streaming.pyを作成（トークン単位のストリーミング）
  - 重要な技術的発見:
    - `streaming=True`がChatOpenAI初期化時に必須
    - ノード関数では`ainvoke()`を使用（`astream()`ではない）
    - LangGraphはコールバック機構でトークンをキャプチャ
    - `stream_mode="messages"`は`(AIMessageChunk, metadata)`のタプルを返す
  - 徹底的な調査により、当初の理解の誤りを発見・修正
  - 関連ファイル: [app_langgraph_streaming.py](../app_langgraph_streaming.py), [README.md](../README.md), [CLAUDE.md](../CLAUDE.md), [.claude/context.md](context.md), [.claude/decisions.md](decisions.md)
  - Pull Request #6（マージ済み、コミット 32f4a76）
  - 学び: 推測ではなく実際のソースコード調査の重要性、公式ドキュメントだけでは不十分なケースがある

- [x] エラーハンドリングの追加（シンプル版）
  - 3つのChainlitアプリ全てにエラーハンドリングを追加（PR #5マージ済み）
  - API呼び出しエラーをキャッチ（`try-except Exception`）
  - プロバイダー非依存な実装（`str(e)`でエラーメッセージ表示）
  - 不要な防御的コードを削除（セッション検証、LangGraphレスポンス検証）
  - 学習用コードのシンプルさを優先
  - 関連ファイル: [app_langchain_sync.py](../app_langchain_sync.py), [app_langchain_streaming.py](../app_langchain_streaming.py), [app_langgraph_sync.py](../app_langgraph_sync.py), [.claude/decisions.md](decisions.md)
  - 学び: 調査の重要性（推測ではなく実際のテストとソースコード調査）、学習用コードではシンプルさを優先、本質的なエラーハンドリングに集中

### 2025-10-30

- [x] プロジェクト目的の明確化とREADME更新
  - README.mdに2×2実装マトリックスを追加
  - 用語の定義（sync/streaming）を明記
  - 各実装の起動方法を記載
  - プロジェクトの方向性を「実装例集」として明確化

- [x] ファイル整理とLangChain同期版の復元
  - ファイル名を統一命名規則に従って整理（`app_{framework}_{mode}.py`）
  - app_langchain.py → app_langchain_streaming.py にリネーム
  - app_langgraph.py → app_langgraph_sync.py にリネーム
  - app_langchain_sync.py をgit履歴（コミット a55aecf）から復元
  - README.md、CLAUDE.md、.claude/todo.md を更新
  - 2×2実装マトリックスを確立（LangChain/LangGraph × sync/streaming）
  - Pull Request #4をマージ
  - 関連ファイル: [app_langchain_sync.py](../app_langchain_sync.py), [app_langchain_streaming.py](../app_langchain_streaming.py), [app_langgraph_sync.py](../app_langgraph_sync.py), [README.md](../README.md)
  - 学び: git履歴の活用、命名規則の重要性、用語の整理（"sync" vs "streaming"）

### 2025-10-29

- [x] LangGraph Phase 1実装（基本機能）
  - LangGraphの基本実装を完了し、mainブランチにマージ（PR #3）
  - app.py を app_langchain.py にリネーム
  - app_langgraph.py を新規作成（StateGraph、システムメッセージ、会話履歴保持、非同期処理）
  - langgraph v1.0.1 を依存関係に追加
  - README.md、decisions.md、CLAUDE.md、.gitignore を更新
  - 実験用ノートブックの命名規則を確立（`tmp_*.ipynb`）
  - 関連ファイル: [app_langchain.py](../app_langchain.py), [app_langgraph.py](../app_langgraph.py), [README.md](../README.md)
  - 学び: 非同期処理の重要性、StateGraphの基本構造、段階的実装の有効性

### 2025-10-26

- [x] GitHub CLI (gh) のインストールとドキュメント整備
  - GitHub CLI (`gh`) をDevContainerにインストール（Dockerfile編集）
  - バージョン確認: gh version 2.23.0
  - 認証確認: 既に認証済み（github.com as coziro）
  - CLAUDE.mdにGitHub CLIセクションを追加（Common Commands、Authentication）
  - feature/add-github-cliブランチで実装
  - 関連ファイル: [.devcontainer/Dockerfile](../.devcontainer/Dockerfile), [CLAUDE.md](../CLAUDE.md)
  - 学び: DevContainerが既に再ビルド済み、認証情報はホストから引き継がれる

- [x] Ruff (linter/formatter) の導入
  - Ruffをdev依存関係としてインストール
  - pyproject.tomlに設定追加、DevContainerにRuff拡張機能追加
  - 既存コードにRuffを適用
  - GitHub Flow初実践（feature/add-ruff → PR #1 → マージ）
  - 運用ルール確立: コミット前に手動実行
  - 関連ファイル: [pyproject.toml](../pyproject.toml), [.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json), [.claude/decisions.md](../.claude/decisions.md)
  - 学び: YAGNI原則、GitHub Flowの実践、`gh`コマンド不要（ブラウザで代替可能）

- [x] MVP完成: README.md、.env.example、docker-compose.yml、LICENSE の作成
  - シンプルなREADMEを作成（Quick Start、Development Setup、Project Structure）
  - .env.exampleファイルを作成（OpenAI API Keyテンプレート）
  - docker-compose.ymlを作成（既存Dockerfileを再利用、簡単にアプリ起動）
  - LICENSEファイルを作成（MIT License、Copyright (c) 2025 coziro）
  - 不要なセクションを削除してシンプルに（Features, Configuration, Troubleshootingなど）
  - 🎉 MVPが完成！実用的なチャットアプリとして機能

- [x] references.mdの更新
  - LangChain公式ドキュメントのリンクを追加
  - ストリーミングレスポンスのコード例を更新

- [x] ストリーミングレスポンスの実装
  - LangChainの `astream()` を使ってリアルタイム表示を実装
  - `async for` と `.content` を正しく使用
  - `send()` のタイミングを実験的に検証（最初は不要、最後は必要）
  - UX改善: ローディング表示、ChatGPTのような体験、コピーボタン表示
  - 関連ファイル: [app.py](../app.py)
  - 学び: 非同期ジェネレーター、LangChainのdeprecated属性、Chainlitのストリーミング仕様

- [x] マルチターン会話機能の実装
  - 会話履歴を保持して、文脈を理解した対話を実現
  - `cl.user_session` でユーザーごとに独立したセッション管理
  - LangChainのメッセージ形式で履歴保存（SystemMessage、HumanMessage、AIMessage）
  - モデルをグローバル変数として最適化
  - 関連ファイル: [app.py](../app.py), [.chainlit/config.toml](../.chainlit/config.toml)
  - 学び: Pythonのリストは参照渡し、Chainlitのスクロール挙動、UIとビジネスロジックの分離の重要性

### 2025-10-25

- [x] シンプルなチャット機能の実装（単発会話）
  - LangChain + ChatOpenAI (gpt-5-nano) を使用
  - 非同期処理（ainvoke）を正しく実装
  - 関連ファイル: [app.py](../app.py), .env
  - 技術選択理由: 将来のLangGraph統合を見据えてLangChainを採用

- [x] Chainlitアプリのロゴ表示を修正
  - Chainlit公式ロゴURL（light.svg）を設定
  - デフォルトテーマをlightに変更してロゴと統一

### 2025-10-24

- [x] .claude/ディレクトリ構造の作成
- [x] コンテキスト保存の仕組みを構築（decisions.md、context.md、todo.md、references.md）
- [x] CLAUDE.mdにClaude Code Context Managementセクション追加
- [x] decisions.mdとtodo.mdの整理・役割分担の明確化

### 2025-10-23

- [x] DevContainer環境の構築
- [x] Chainlitの基本セットアップ
- [x] 翻訳ファイルを日本語と英語のみに整理
- [x] uvを使った依存関係管理の導入

---

## タスクテンプレート

新しいタスクを追加する際は、以下の形式を使うと便利です：

```markdown
- [ ] [タスク名]
  - 目的: なぜこれをやるのか
  - 関連ファイル: [app.py](../app.py)
  - 見積もり: 30分 / 2時間 / 1日
  - 依存: このタスクの前に完了すべきこと
  - メモ: その他の情報
```

### 例

- [ ] Chainlitアプリにストリーミング機能を追加
  - 目的: ユーザー体験の向上、リアルタイムな応答
  - 関連ファイル: [app.py](../app.py)
  - 見積もり: 1時間
  - 依存: LLMプロバイダーの選定
  - メモ: Chainlit公式ドキュメント参照 https://docs.chainlit.io/concepts/streaming

---

## タスクの状態管理

1. **新しいタスク** → 優先度別セクションに追加
2. **作業開始** → "進行中"セクションに移動
3. **完了** → "完了"セクションに移動（日付付き）
4. **不要になった** → 削除またはアイデアセクションに移動

---

## 定期的なメンテナンス

週に1回程度、以下を実施することをおすすめします：

- [ ] 完了タスクが溜まりすぎていないか確認
- [ ] 優先度の見直し
- [ ] 古いタスクの削除または再検討
