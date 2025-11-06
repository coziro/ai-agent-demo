# TODO List (タスク管理)

このファイルには、今後やるべきタスクを記録します。優先順位をつけて管理しましょう。

**最終更新:** 2025-11-02（todo.md優先順位見直し: 共通コード分離を最優先に）

---

## プロジェクトの現状と方向性

🎉 **MVP完成！Phase 1完了！**

**プロジェクトの方向性（2025-10-29更新）:**
このプロジェクトは、LangChain/LangGraphの**実装例集**として発展させます。
- 様々な実装パターン（同期/ストリーミング、LangChain/LangGraph）を網羅的に示す
- 学習者が参考にできるベストプラクティスを提供

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

- [ ] メール作成エージェントの実装
  - 目的: State管理の学習、複数フィールドを持つStateの実践的な使い方を習得
  - 背景:
    - 現在のシンプルチャットは `messages` フィールドのみ
    - より複雑なStateを扱う練習として最適
    - シンプルながら実用的なユースケース
  - 実装内容:
    ```python
    class EmailState(TypedDict):
        messages: list[AnyMessage]  # 会話履歴
        email_subject: str          # メールタイトル
        email_body: str             # メール本文
        status: str                 # "drafting" | "reviewing" | "completed"
    ```
  - ワークフロー案:
    1. ユーザーとの対話を通じて要件をヒアリング
    2. メールタイトルと本文を段階的に作成・更新
    3. ユーザーにレビューを依頼、フィードバックを反映
    4. 最終的なメールを完成させる
  - 技術的な学び:
    - 複数フィールドを持つStateの設計
    - State更新の部分的な上書き vs 完全な置き換え
    - 条件分岐（status による処理の切り替え）
    - ユーザーフィードバックループの実装
  - 実装ファイル:
    - `apps/email_agent_sync.py` - まずsync版で実装
    - `apps/email_agent_streaming.py` - 動作確認後にstreaming版
    - `src/ai_agent_demo/email_agent/` - EmailState, ノード関数, グラフ構築
  - 見積もり: 3-4時間
  - メモ: 複雑すぎず、Stateの使い方を学ぶのに最適な題材

---

## 優先度: 中 (Medium Priority)

- [ ] LangSmithの導入
  - 目的: LLM呼び出しのトレーシング、デバッグ、パフォーマンスモニタリング
  - 背景: LangGraphを使った複雑なエージェント実装後に必要になるツール
  - 実装内容:
    - LangSmith環境変数設定（LANGCHAIN_API_KEY等）
    - 各実装にトレーシング追加
    - ドキュメント更新（セットアップ手順）
  - 見積もり: 2-3時間
  - 参考: https://docs.smith.langchain.com/
  - メモ: 現時点では優先度低、複雑なエージェント実装後に再検討


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
  - 影響範囲: [apps/langchain_sync.py](../apps/langchain_sync.py), [apps/langchain_streaming.py](../apps/langchain_streaming.py), [apps/langgraph_sync.py](../apps/langgraph_sync.py), [apps/langgraph_streaming.py](../apps/langgraph_streaming.py)、設定ファイル
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

- [ ] LangGraph Checkpoint + Token-level Streamingの両立（技術的課題）
  - 目的: チェックポイント機構を使いながらトークン単位のストリーミングを実現する
  - 背景:
    - PR #13で `langgraph_sync.py` はcheckpoint版に移行完了
    - `langgraph_streaming.py` は旧実装を埋め込んで対応（2実装並存状態）
    - 理想は1つの実装でcheckpoint + streamingの両立
  - 現在の問題点:
    - `stream_mode="messages"` + checkpoint + `config` parameter → **全履歴をemitしてしまう**
    - 理由: LangGraphがcheckpointから復元した履歴もすべてストリームに流す
    - 結果: 過去のメッセージが毎回画面に表示される（ユーザー体験が悪い）
  - 検証済みの事実:
    - 旧実装（checkpointなし）: `agent.astream()` は新規メッセージのみemit → 正常動作
    - 新実装（checkpoint + config）: `agent.graph.astream()` は全メッセージemit → バグ発生
    - checkpoint復元の有無が `config` parameter の存在で決まる
  - 考えられる解決策（未検証）:
    1. **メッセージ数カウント方式**:
       - 事前に `agent.graph.get_state(config)` で現在の履歴件数を取得
       - ストリーミング中、履歴件数以降のメッセージのみ表示
       - 課題: 状態取得のオーバーヘッド、複雑な実装
    2. **タイムスタンプ/ID方式**:
       - 各メッセージにタイムスタンプやIDを付与
       - ストリーミング開始前のメッセージをフィルタリング
       - 課題: メッセージ構造の拡張が必要、LangGraph標準から逸脱
    3. **stream_mode="updates" 使用**:
       - ノード単位の更新のみ取得、トークンレベルではない
       - 課題: トークン単位のストリーミングができない（意味がない）
    4. **カスタムストリーミングロジック**:
       - LangGraphの内部実装を深く理解し、独自のフィルタリング実装
       - 課題: 複雑すぎる、メンテナンス困難、LangGraphアップデートで壊れる可能性
  - 現在の暫定対応（PR #13で実装済み）:
    - `langgraph_sync.py`: Checkpoint使用、トークンストリーミングなし
    - `langgraph_streaming.py`: 旧実装埋め込み（stateless agent）、トークンストリーミングあり
    - 理由: 実装のシンプルさと動作の確実性を優先
  - 実装優先度: 低（現状の2実装並存で実用上問題なし）
  - 再検討のタイミング:
    - LangGraph公式で解決策が提示された場合
    - 複雑な実装を許容できる明確なビジネス要求がある場合
    - コミュニティで標準的なパターンが確立された場合
  - 見積もり: 未定（解決策次第で4-8時間、または実現不可能）
  - 参考:
    - [apps/langgraph_streaming.py](../apps/langgraph_streaming.py) - 現在の暫定実装
    - [.claude/context.md](context.md) - 問題発覚と対応の経緯
    - [.claude/decisions.md](decisions.md) - ストリーミングとの両立を断念した設計判断
  - メモ: この問題はLangGraphの設計上の制約である可能性が高い。無理に解決しようとすると複雑性が増すだけかもしれない。

- [ ] LangGraph複数ノードの実装（汎用的なパターン）
  - 目的: より複雑なワークフローの実現（research → analysis → generation など）
  - 前提: 現状は1ノードのシンプルな実装のみ。複数ノードが必要になるユースケースが出てから検討
  - 実装内容:
    - 複数ノードのグラフ構造を作成
    - ノード間の状態遷移・データフロー
    - 条件分岐やループなどの制御構造
  - 見積もり: 3-4時間
  - メモ: 具体的なユースケース（例: RAG、エージェント）が決まってから実装。メール作成エージェントで基礎を学んだ後に検討

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

### 2025-11-06

- [x] Chainlit 2.8.4へのアップグレード（IME公式修正）
  - 目的: Chainlit 2.8.4の公式IME修正（PR #2575）を検証し、custom.jsが不要になるか確認
  - 完了内容:
    - pyproject.tomlで`chainlit>=2.8.4`に更新
    - uv syncで依存関係更新
    - custom.jsを無効化してIME動作テスト（Chrome/Safari on macOS）
    - custom.js完全削除（公式修正で不要と判明）
    - ドキュメント更新（ime-investigation.md, context.md）
  - 検証結果:
    - ✅ IME変換中のEnter → 変換確定（送信されない）
    - ✅ 変換確定後のEnter → メッセージ送信
    - ✅ 英語入力でEnter → メッセージ送信
    - ✅ Shift+Enter → 改行
  - 技術的な学び:
    - 根本原因: AutoResizeTextareaがcomposition eventsを親に伝播していなかった
    - 以前「Reactの根本的な問題」と判断したのは誤り
    - 調査の教訓: コンポーネント階層全体の調査、最新PR履歴の確認の重要性
  - 成果: custom.js削除（56行）、よりシンプルな構成
  - 影響範囲: pyproject.toml, uv.lock, public/custom.js（削除）, .chainlit/config.toml, .claude/ime-investigation.md, .claude/context.md
  - Pull Request: #14（feature/upgrade-chainlit-2.8.4、マージ済み）
  - 参考:
    - [Chainlit PR #2575](https://github.com/Chainlit/chainlit/pull/2575)
    - [Chainlit Release 2.8.4](https://github.com/Chainlit/chainlit/releases/tag/2.8.4)
    - [.claude/ime-investigation.md](.claude/ime-investigation.md)

### 2025-11-03

- [x] LangGraphチェックポイント機構の導入（Agent class pattern）
  - 目的: Chainlitセッション管理から脱却し、LangGraph標準のチェックポイント機構に移行
  - 完了内容:
    - InMemorySaverによる会話履歴の永続化
    - Agent class pattern (SimpleChatAgent) の導入
    - Pydantic BaseModelベースのSimpleChatState実装
    - SYSTEM_PROMPTのパラメータ化（依存性注入）
    - グラフ構築の分離（_build_graph メソッド）
    - UUID-based thread_id によるスレッド分離
    - apps/langgraph_sync.pyをcheckpoint版に置き換え
    - apps/langgraph_streaming.pyは旧実装維持（トークンストリーミング対応）
    - 旧simple_chatパッケージの削除と新実装への置き換え
  - 設計決定:
    - Pydantic BaseModel採用（TypedDictより型安全性が高い）
    - user_requestフィールド保持（UI層のシンプル化優先）
    - ストリーミングとの両立を断念（2実装並存）
    - 型ヒントのバランス（有用な箇所のみ追加、冗長性回避）
  - 技術的な学び:
    - LangGraph + Checkpoint + Streamingの制約（stream_mode="messages"は全履歴emit）
    - Pydantic BaseModelとCheckpointの相性は良好
    - UUID-based thread_idで複数ユーザー対応
  - 成果: コード削減-143行（10ファイル変更、+157/-300）
  - 影響範囲: apps/langgraph_sync.py, apps/langgraph_streaming.py, src/ai_agent_demo/simple_chat/
  - Pull Request: #13（feature/langgraph-checkpoint、マージ済み）
  - 参考: [.claude/context.md](context.md), [.claude/decisions.md](decisions.md)

- [x] 共通コードの分離（LangGraph対象）
  - 目的: DRY原則、コードの再利用性向上、テスタビリティ向上
  - 完了内容:
    - `src/ai_agent_demo/simple_chat/` ディレクトリ作成（エージェント名優先）
    - `ChatState`, `call_llm`, `create_agent` を共通モジュールとして抽出
    - `apps/langgraph_sync.py` リファクタリング（-26行）
    - `apps/langgraph_streaming.py` リファクタリング（-26行）
    - ディレクトリ構成を機能別からエージェント別に変更
    - ドキュメント更新（README.md, CLAUDE.md, context.md）
  - 重要な発見:
    - `ChatOpenAI(streaming=True)` はsync/streaming両方で動作
    - sync版: コールバック発火するが無視される（問題なし）
    - streaming版: LangGraphがコールバック経由でトークンキャプチャ
    - 両バージョンで同じノード関数を使用可能
  - 設計判断:
    - load_chat_history(), エラーハンドリング, モデル初期化は共通化しない
    - YAGNI原則: 過度な抽象化を避け、必要になってから対応
    - チェックポイント機構導入後に再検討
  - 成果:
    - コード削減: 合計52行削減
    - DRY原則達成: 重複コード完全排除
    - 高い凝集度: エージェント単位でコード集約
    - 将来の拡張性: 新しいエージェント追加が容易
  - 影響範囲: 19ファイル変更（+389行/-119行）
  - Pull Request: #12（feature/extract-langgraph-common-code）
  - 参考: [.claude/decisions.md](decisions.md#ディレクトリ構成-エージェント名優先---2025-11-03)

### 2025-11-02

- [x] 日本語IME入力対応 Phase 1: 暫定対応
  - 完了内容:
    - `public/custom.js` を作成（3重の安全装置: グローバル変数、e.isComposing、keyCode 229）
    - `.chainlit/config.toml` に `custom_js = "/public/custom.js"` を追加
    - Chrome/Safari on macOSで動作確認完了（IME変換中のEnterブロック成功）
    - コメント・ログメッセージは英語で記述
  - 影響範囲: [public/custom.js](../public/custom.js)（新規、56行）、[.chainlit/config.toml](../.chainlit/config.toml)
  - Pull Request: #11（feature/ime-phase1）
  - 参考資料:
    - [.claude/ime-investigation.md](.claude/ime-investigation.md)（1,000行以上の技術調査）
    - Classi技術ブログ: https://tech.classi.jp/entry/2024/04/23/183000
  - 学び:
    - イベントキャプチャフェーズでReactより先にイベントをブロック
    - Safari特有の問題（keyCode 229の必要性）
    - 3重の安全装置でブラウザ互換性を確保
    - Classi方式（IME変換中のみブロック）でシンプルかつ確実な実装

- [x] `langgraph_sync.py`のリファクタリング（可読性向上）
  - 完了内容:
    - `ChatState`を明示的に構築（`agent_request = ChatState(messages=chat_history)`）
    - 変数名の改善（`agent_request`, `state_update`で部分更新の意図を明確化）
    - `call_llm()`関数にdocstringを追加
    - 不要な`AnyMessage`のimportを削除、import順序の標準化
  - 影響範囲: [apps/langgraph_sync.py](../apps/langgraph_sync.py)
  - Pull Request: #9（feature/refactor-langgraph-sync）
  - 学び: 明示的な型構築により可読性が向上、変数名で意図を明確に表現する重要性

### 2025-11-01

- [x] ディレクトリ構成の見直し + docker-compose.yml更新
  - 目的: 複数の実装例を整理された形で提供、docker-composeで起動するアプリを選択可能にする
  - 完了内容:
    - `apps/` ディレクトリを作成し、全ての実装ファイルを移動（git履歴保持）
    - ファイル名から `app_` プレフィックスを削除（`langchain_sync.py` など）
    - `main.py` を削除（不要と判断）
    - `apps/README.md` を作成（4つの実装の比較説明）
    - docker-compose.yml を更新（環境変数 `CHAINLIT_APP` で起動アプリを選択可能に）
    - .env.example に `CHAINLIT_APP` の設定を追加（デフォルト: `apps/langchain_streaming.py`）
    - README.md を更新（プロジェクト説明、docker-compose使用方法、簡素化）
    - CLAUDE.md を更新（起動コマンド、プロジェクト構造）
  - 設計判断:
    - ディレクトリ名: `apps/` (実装は単なる例ではなく実際に動作するアプリ)
    - フラット構造を選択（階層は浅く、README最小限）
    - 環境変数のパス: フルパス `apps/langchain_streaming.py` (明確性優先)
  - 影響範囲: プロジェクト全体
  - Pull Request: #8（feature/restructure-directory）
  - 学び: `git mv`でファイル履歴保持、docker-compose環境変数、シングルソースの原則

- [x] 既存実装のリファクタリング（コード品質向上）
  - 目的: 無駄な処理の削除、型ヒントの追加、変数名の整理
  - 対象ファイル:
    - [app_langchain_sync.py](../app_langchain_sync.py)
    - [app_langchain_streaming.py](../app_langchain_streaming.py)
    - [app_langgraph_sync.py](../app_langgraph_sync.py)
    - [app_langgraph_streaming.py](../app_langgraph_streaming.py)
  - 完了内容:
    - `load_chat_history()` の共通化とセッションキー統一
    - LangGraph版に `ChatState` を導入し `agent.ainvoke` のレスポンスを直接保存
    - ストリーミング時は `Message.stream_token()` の蓄積をそのまま履歴に反映
    - Pull Request #7（Refine Lang chat handlers）でマージ済み
  - 学び:
    - ChainlitのストリーミングAPI実装（`stream_token`）の内部動作を理解
    - LangGraphのStateGraphにTypedDictを渡すと型補完が効きやすい
    - LangGraphレスポンスを再ラップせず履歴へ統合すると二重生成を防げる

### 2025-11-03

- [x] Static type check (型チェック) の導入
  - Pyright を採用し、`pyproject.toml` へ `[tool.pyright]` を追加 (`typeCheckingMode = "standard"`, `include = ["apps"]`)
  - Chainlit/LangGraph 各アプリで `cast`/`assert`/ガードを追加して Unknown を解消
  - DevContainer に `libatomic1` を追加して Pyright の `nodeenv` 依存をサポート
  - 運用ルール: コミット前に `uv run pyright` を実行（Ruff と同列の手動チェック）
  - PR #10 にてマージ済み

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
