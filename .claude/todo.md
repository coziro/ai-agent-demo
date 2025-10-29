# TODO List (タスク管理)

このファイルには、今後やるべきタスクを記録します。優先順位をつけて管理しましょう。

**最終更新:** 2025-10-29

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

🎉 **MVP完成！** 次はコード品質とUX向上、そして機能拡張に取り組みます。

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

- [ ] エラーハンドリングの追加
  - 目的: API エラー時の適切な処理
  - 見積もり: 1時間

### 機能拡張

- [ ] LangGraphのストリーミング対応（Phase 2）
  - 目的: app_langgraph.pyにストリーミングレスポンスを実装
  - 依存: Phase 1の完了（基本機能の実装とマージ）
  - 実装内容:
    - `agent.astream()` を使用してLLMトークンを逐次取得
    - `stream_mode="messages"` でストリーミング設定
    - Chainlitの`msg.stream_token()`と統合
  - 見積もり: 2-3時間
  - 参考: context.mdに記載されているストリーミング実装例
  - 影響範囲: app_langgraph.py

- [ ] LangGraphを使ったAIエージェントの高度な実装（Phase 3）
  - 目的: 複数ノード、条件分岐、ツール呼び出しなど複雑なエージェント
  - 依存: LangGraph基本版の完成（✅Phase 1完了）、ストリーミング対応（Phase 2）
  - 見積もり: 未定（学習含む）
  - メモ: これは大きな拡張機能

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
  - 検討項目: loguru vs 標準logging
  - 影響範囲: [app.py](../app.py)、設定ファイル
  - 見積もり: 1時間

- [ ] システムプロンプトのカスタマイズ
  - 目的: アシスタントの性格・役割を設定可能に
  - 見積もり: 30分

---

## 優先度: 低 (Low Priority)

- [ ] デプロイ手順のドキュメント作成
  - 目的: 本番環境への展開準備
  - 依存: デプロイ方法の決定（decisions.md参照）
  - 見積もり: 1時間

---

## アイデア・検討中 (Ideas / Backlog)

- [ ] GitHub ActionsでRuffの自動チェック
  - 目的: PR作成時に自動的にコード品質をチェック
  - 実装内容:
    - `.github/workflows/lint.yml` を作成
    - `ruff check` と `ruff format --check` を実行
    - PRがマージされる前にコード品質を保証
  - 見積もり: 30分-1時間
  - メモ: 現時点では手動運用で十分、必要性が出てから実装

- Jupyter Notebookでのプロトタイピング例を追加
- ユニットテストの追加

---

## 完了 (Completed)

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
