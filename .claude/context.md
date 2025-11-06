# Current Work Context (現在の作業コンテキスト)

このファイルには、**今現在進行中の作業**を記録します。VS Codeを再起動したりコンテナをrebuildした後でも、ここを見れば作業を再開できます。

**最終更新:** 2025-11-06（Chainlit 2.8.4アップグレード完了）

---

## ファイル管理方針

**このファイルの特性:** 短期的な作業状況を記録（頻繁に更新・削除される）

**メンテナンスガイドライン:**
- **完了したタスク**: 1-2週間程度で「最近完了したタスク」から削除してOK
- **重要な決定**: [decisions.md](decisions.md)に移動
- **長期的なタスク**: [todo.md](todo.md)に移動
- **原則**: このファイルは常にコンパクトに保つ（目安: 200行以内）

**定期クリーンアップ（推奨）:**
週に1回程度、完了したタスクを整理して、ファイルサイズを適切に保ちましょう。

---

## 現在の作業状況

### 進行中のタスク

（現在進行中のタスクはありません）

---

## 最近完了したタスク

### Chainlit 2.8.4アップグレード（IME公式修正） - 完了日: 2025-11-06

**目的:**
- Chainlit 2.8.4の公式IME修正（PR #2575）を検証
- custom.jsによる回避策が不要になるか確認

**ブランチ:** `feature/upgrade-chainlit-2.8.4`

**完了した項目:**
- ✅ pyproject.tomlで`chainlit>=2.8.4`に更新
- ✅ uv syncで依存関係更新
- ✅ custom.jsを無効化してIME動作テスト
- ✅ Chrome/Safari on macOSで完全動作確認
- ✅ custom.js完全削除（公式修正で不要と判明）
- ✅ ドキュメント更新（ime-investigation.md）

**検証結果:**
- ✅ IME変換中のEnter → 変換確定（送信されない）
- ✅ 変換確定後のEnter → メッセージ送信
- ✅ 英語入力でEnter → メッセージ送信
- ✅ Shift+Enter → 改行

**技術的な学び:**
- **根本原因の再評価**: 以前「Reactの根本的な問題」と判断したのは誤りだった
- **実際の原因**: AutoResizeTextareaが composition events を親に伝播していなかった
- **修正内容**: イベントハンドラprops追加により、イベント伝播を実装
- **調査の教訓**: コンポーネント階層全体を調査する重要性、最新PR履歴の確認

**成果:**
- custom.js削除（56行のJavaScriptコード削除）
- よりシンプルな構成（公式実装に依存）
- メンテナンス負担の軽減

**Pull Request:**
- #14 "feat: Upgrade Chainlit 2.8.3 → 2.8.4 (official IME fix)"（マージ済み）

**参考:**
- [Chainlit PR #2575](https://github.com/Chainlit/chainlit/pull/2575)
- [Chainlit Release 2.8.4](https://github.com/Chainlit/chainlit/releases/tag/2.8.4)
- [.claude/ime-investigation.md](ime-investigation.md) - 詳細な調査記録

---

### LangGraphチェックポイント機構の導入（Agent class pattern） - 完了日: 2025-11-03

**目的:**
- 会話履歴の永続化をChainlitのセッション管理から切り離す
- LangGraph標準のチェックポイント機構 (InMemorySaver) に移行
- Agent class patternの導入（依存性注入、テスタビリティ向上）
- UIフレームワークからの独立性を高める

**ブランチ:** `feature/langgraph-checkpoint` (マージ済み、削除済み)

**完了した項目:**
- ✅ Pydantic BaseModelベースの`SimpleChatState`実装
- ✅ Agent class pattern (`SimpleChatAgent`) の導入
- ✅ SYSTEM_PROMPTのパラメータ化 (DEFAULT_SYSTEM_PROMPT + 依存性注入)
- ✅ グラフ構築の分離 (`_build_graph()` メソッド)
- ✅ 適切な型ヒント追加 (冗長性を避けつつ可読性向上)
- ✅ UUID-based thread_id によるスレッド分離
- ✅ `apps/langgraph_sync.py` を checkpoint版に置き換え
- ✅ `apps/langgraph_streaming.py` は旧実装を維持（トークンストリーミング対応）
- ✅ 旧`simple_chat`パッケージの削除と新実装への置き換え
- ✅ Pull Request #13 作成・マージ

**実装の詳細:**

1. **Agent Class Pattern**
   - `SimpleChatAgent` クラスでmodel, graph, configをカプセル化
   - コンストラクタで依存性注入 (`system_prompt`, `model_name`, `streaming`)
   - UUID-based `thread_id` で各インスタンスを分離

2. **Checkpoint Mechanism**
   - `InMemorySaver` による会話履歴の永続化
   - `RunnableConfig(configurable={"thread_id": ...})` で状態管理
   - UI層は履歴管理不要、agent.graph.ainvoke() を呼ぶだけ

3. **Pydantic BaseModel State**
   - 実行時バリデーション、型安全性
   - チェックポイント機構との互換性確認済み
   - `user_request` フィールド保持（UI層のシンプル化優先）

**設計決定事項:**

1. **Pydantic BaseModel 採用** - TypedDictより型安全性とバリデーションが優れる
2. **user_request フィールド保持** - UI層の実装をシンプルに保つため
3. **ストリーミングとの両立を断念** - checkpoint機構はストリーミングと相性が悪い
   - `langgraph_sync.py`: checkpoint使用、トークンストリーミングなし
   - `langgraph_streaming.py`: 旧実装埋め込み、トークンストリーミングあり
4. **型ヒントのバランス** - 有用な箇所のみ追加、冗長性を回避

**技術的な学び:**

- **LangGraph + Checkpoint + Streaming の制約**:
  - `stream_mode="messages"` + checkpoint は全履歴を emit してしまう
  - トークンレベルストリーミングには stateless agent が必要
  - 将来的には複雑なフィルタリングが必要かもしれない

- **Pydantic と Checkpoint の相性**:
  - `BaseModel` は問題なくチェックポイント復元できる
  - `Optional[list] = None` パターンでも正常動作

- **Thread Isolation**:
  - UUID-based `thread_id` で複数ユーザー対応
  - Chainlit session とは独立した状態管理

**成果:**
- コード削減: -143行 (10ファイル変更、+157/-300)
- DRY原則達成: Agent class pattern による再利用性向上
- UI独立性: Chainlit依存を最小化

**Pull Request:**
- #13 "feat: implement LangGraph checkpoint mechanism with Agent class pattern"
- マージ済み (2025-11-03)

**Trade-offs:**
- ストリーミングとチェックポイントの両立を断念（2実装並存）
- InMemorySaver（再起動で消失）→ 将来的にPostgreSQL等へ移行可能

---

### 共通コードの分離（LangGraph対象） - 完了日: 2025-11-03

**目的:**
- LangGraphの2つの実装（langgraph_sync.py、langgraph_streaming.py）から重複コードを抽出
- `src/ai_agent_demo/` ディレクトリに共通モジュールを作成
- DRY原則、再利用性、テスタビリティの向上

**ブランチ:** `feature/extract-langgraph-common-code`

**ディレクトリ構成（計画）:**
```
src/
├── ai_agent_demo/
│   ├── __init__.py
│   ├── config.py          # SYSTEM_PROMPT, DEFAULT_MODEL
│   ├── state.py           # ChatState定義
│   ├── nodes/
│   │   ├── __init__.py
│   │   └── llm.py         # call_llm() ノード関数
│   └── graph.py           # create_chat_graph()
apps/
├── langchain_sync.py      # 対象外（LangChainは現状維持）
├── langchain_streaming.py # 対象外
├── langgraph_sync.py      # リファクタリング対象
└── langgraph_streaming.py # リファクタリング対象
```

**完了した項目:**
- [x] ブランチ作成: `feature/extract-langgraph-common-code`
- [x] ディレクトリ構成の見直し・決定
  - `src/ai_agent_demo/simple_chat/` を採用（エージェント名優先）
  - 機能別（state/, node/, agent/）からエージェント別に変更
- [x] 開発モードインストールの設定完了
  - `uv pip install -e .` で動作確認
  - `pyproject.toml` に `[build-system]` と `[tool.hatch.build.targets.wheel]` を追加
  - `devcontainer.json` に `postCreateCommand` を追加
- [x] 共通コードの抽出
  - `ChatState` - エージェントの状態定義
  - `call_llm` - LLM呼び出しノード関数（`streaming=True`で両対応）
  - `create_agent` - グラフ構築ファクトリ関数
- [x] `apps/langgraph_sync.py` のリファクタリング完了（-26行）
- [x] `apps/langgraph_streaming.py` のリファクタリング完了（-26行）
- [x] ディレクトリ構成の再編成（エージェント名優先）
- [x] ドキュメント更新（README.md, CLAUDE.md, context.md）
- [x] Ruff + Pyright チェック完了（0エラー）
- [x] Pull Request #12 作成・マージ完了

**技術的な学び:**
- **Hatchling**: uvのデフォルトビルドバックエンド、`src/` レイアウトを自動認識
- **開発モードインストール**: `uv pip install -e .` で編集可能モードに
- **インポートパス**: `from ai_agent_demo.state import ChatState`（`src.` プレフィックス不要）
- **DevContainer設定**: `postCreateCommand` で自動セットアップ
- **UV_LINK_MODE**: DevContainer環境ではハードリンクが使えないことが多い
  - `UV_LINK_MODE=copy` で警告を抑制可能
- **streaming=True の互換性（重要な発見）:**
  - `ChatOpenAI(streaming=True)` + `ainvoke()` はsync版でも動作
  - sync版: コールバックが発火するが無視される（問題なし）
  - streaming版: LangGraphがコールバック経由でトークンをキャプチャ
  - 両バージョンで同じノード関数を使える（DRY原則達成）
  - パフォーマンス影響: コールバックのオーバーヘッドは微小で実用上問題なし

**設計判断:**
- LangChainは対象外: 現状でも十分シンプル、LangGraphと構造が異なる
- ディレクトリ構成: エージェント名優先（`simple_chat/`配下にstate, node, agentを集約）
- ノード関数の共通化: `streaming=True` で統一（両バージョン対応）
- 過度な抽象化を避ける: load_chat_history, エラーハンドリングは各アプリに残す
  - load_chat_history: Chainlit依存、チェックポイント機構導入後に再検討
  - エラーハンドリング: 各アプリ3-4行程度、共通化不要
- 将来的にはAgentクラスパターンへの移行を検討（todo.md参照）

**最終的なディレクトリ構成:**
```
src/ai_agent_demo/simple_chat/
├── __init__.py    # ChatState, call_llm, create_agentをエクスポート
├── state.py       # ChatState定義
├── node.py        # call_llm ノード関数
└── agent.py       # create_agent グラフファクトリ
```

**成果:**
- コード削減: 合計52行削減（各アプリ26行×2）
- DRY原則達成: 重複コードの完全排除
- 高い凝集度: エージェント単位でコードが集約
- 将来の拡張性: 新しいエージェントの追加が容易

**Pull Request:**
- #12 "Extract LangGraph common code and reorganize by agent"
- マージ済み（2025-11-03）
- 8コミット、19ファイル変更（+389行/-119行）

---

**作業を開始したら、以下のテンプレートを使って記録してください：**

```markdown
#### [タスク名] - 開始日: YYYY-MM-DD

**目的:**
- 何を実現しようとしているか

**現在の状態:**
- どこまで進んでいるか
- 完了した項目
- 未完了の項目

**次にやること:**
1. 具体的なステップ1
2. 具体的なステップ2

**ブロッカー:**
- 進行を妨げている問題（あれば）

**関連ファイル:**
- [app.py](../app.py)
- [config.toml](../.chainlit/config.toml)

**メモ:**
- その他気づいたこと
```

---

## 最近完了したタスク

### 日本語IME入力対応 Phase 1 - 2025-11-02

**完了内容:**
- `.claude/ime-investigation.md` を作成（1,000行以上の技術調査ドキュメント）
- `public/custom.js` を作成（3重の安全装置: グローバル変数、e.isComposing、keyCode 229）
- `.chainlit/config.toml` に `custom_js = "/public/custom.js"` を追加
- Chrome on macOSで動作確認完了（IME変換中のEnterブロック成功）
- PR [#11](https://github.com/coziro/ai-agent-demo/pull/11) を作成・マージ

**技術的な学び:**
- イベントキャプチャフェーズでReactより先にイベントをブロック
- Safari特有の問題（keyCode 229が非推奨だが必要）
- 3重の安全装置でブラウザ互換性を確保
- Classi方式（IME変換中のみブロック）でシンプルかつ確実な実装

**参考資料:**
- [.claude/ime-investigation.md](.claude/ime-investigation.md) - 包括的な技術調査
- Classi技術ブログ: https://tech.classi.jp/entry/2024/04/23/183000

**フォローアップ（オプション）:**
- Safari/Firefoxでの動作確認
- 中国語/韓国語IMEでのテスト
- Phase 2: Chainlit本体へのPR（[todo.md優先度: 中](todo.md)参照）

---

### Pyright導入と型チェック修正 - 2025-11-03

**完了内容:**
- `pyproject.toml` に `[tool.pyright]` を追加し、`typeCheckingMode = "standard"` を基準に設定
- `uv.lock` を更新し、DevContainerで必要な `libatomic1` を追加インストール
- Chainlit/LangGraph の各アプリで `cast` / `assert` / ガードを追加してPyrightエラーを解消
- `uv run pyright` を標準のローカル検証ステップに組み込み
- PR [#10](https://github.com/coziro/ai-agent-demo/pull/10) を作成・マージ

**フォローアップ:**
- Pyright をCIに組み込む (GitHub Actions) - 未着手
- `.claude/settings.local.json` の取り扱いルールを検討

---

### ディレクトリ構成の見直し + docker-compose.yml更新 - 2025-11-01

**完了内容:**
- `apps/` ディレクトリを作成し、全ての実装ファイルを移動（git履歴保持）
- ファイル名から `app_` プレフィックスを削除（apps/配下なので冗長）
- docker-compose.yml を環境変数 `CHAINLIT_APP` で起動アプリを選択可能に更新
- .env.example に CHAINLIT_APP 設定を追加（4つの選択肢を記載）
- README.md の改善:
  - プロジェクト説明を "LangChain/LangGraph implementation examples with Chainlit UI" に変更
  - Quick Start セクションに docker-compose 使用方法を追加
  - Development Setup セクションを簡素化、apps/README.md への参照を追加
- apps/README.md を新規作成（実装パターンの比較、起動方法を記載）
- main.py を削除（不要になったため）

**移動したファイル:**
- `app_langchain_sync.py` → `apps/langchain_sync.py`
- `app_langchain_streaming.py` → `apps/langchain_streaming.py`
- `app_langgraph_sync.py` → `apps/langgraph_sync.py`
- `app_langgraph_streaming.py` → `apps/langgraph_streaming.py`

**docker-compose.yml の変更:**
```yaml
command: uv run chainlit run ${CHAINLIT_APP:-apps/langchain_streaming.py} --host 0.0.0.0
```

**設計判断:**
- ディレクトリ名: `apps/` (実装は単なる例ではなく実際に動作するアプリケーション)
- ファイル命名: `app_` プレフィックスを削除（ディレクトリ名で既に明確）
- 環境変数のデフォルト値: `apps/langchain_streaming.py` (フルパスで明確に)
- シンプルさ優先: 階層は浅く、READMEは最小限に

**技術的な学び:**
- `git mv` でファイル履歴を保持しながらリネーム・移動が可能
- docker-compose の `${VAR:-default}` 構文でデフォルト値を設定
- .env ファイルで環境変数を管理し、docker-compose.yml は変更不要に
- ユーザー向けドキュメントは「シングルソースの原則」で冗長性を排除

**成果物:**
- [apps/](../apps/) ディレクトリ（4つの実装ファイル + README.md）
- [docker-compose.yml](../docker-compose.yml) - 環境変数対応
- [.env.example](../.env.example) - CHAINLIT_APP 設定追加
- [README.md](../README.md) - 説明改善、docker-compose 使用方法追加
- [CLAUDE.md](../CLAUDE.md) - ファイルパス更新
- Pull Request #8（マージ済み）

**今後のタスク:**
- 共通コードの分離（src/ ディレクトリの検討）- todo.md に記載済み

---

### LangGraphストリーミング版の実装（Phase 2a） - 2025-10-31

**完了内容:**
- app_langgraph_streaming.pyを作成（トークン単位のストリーミング）
- 2×2実装マトリックス完成（LangChain/LangGraph × sync/streaming）
- README.md、CLAUDE.mdを更新
- Pull Request #6をマージ

**重要な技術的発見:**
1. **`streaming=True`が必須**
   - ChatOpenAI初期化時に`streaming=True`を設定しないとストリーミングが機能しない
   - これがないとLangChainがコールバックを発火しない

2. **ノード関数では`ainvoke()`を使用**
   - `model.astream()`ではなく、`await model.ainvoke()`を使う
   - ノード関数は`BaseMessage`オブジェクトを返す必要がある
   - `AsyncIterator`を返すとエラー: `Unsupported message type: <class 'async_generator'>`

3. **LangGraphのコールバック機構**
   - LangGraphは`StreamMessagesHandler`でコールバックをキャプチャ
   - `on_llm_new_token`イベントを通じてトークンを取得
   - 自動的にストリーミングに変換してくれる

4. **`stream_mode="messages"`の返り値**
   - `(AIMessageChunk, metadata)`のタプルを返す
   - タプルをアンパックして処理: `async for message, _ in agent.astream(...)`

**当初の誤解と修正:**
- 誤: ノード関数で`model.astream()`を返せばLangGraphが転送してくれる
- 正: `model.ainvoke()`を使い、LangGraphがコールバック経由でトークンをキャプチャ

**調査方法:**
- LangGraphのソースコード調査（`langgraph/pregel/_messages.py`）
- `MessagesState`の型定義確認
- 実際のエラーを元に推測ではなく実装を確認

**成果物:**
- [app_langgraph_streaming.py](../app_langgraph_streaming.py)
- [README.md](../README.md) - 実装マトリックス更新
- [CLAUDE.md](../CLAUDE.md) - 起動コマンド追加
- Pull Request #6（マージ済み）

**今後のタスク:**
- Phase 2b: 複数ノード + `stream_mode="updates"`
- Phase 3: `stream_mode=["updates", "messages"]`の組み合わせ
- リファクタリング（型ヒント、変数名、無駄な処理の削除）

**技術的な学び:**
- 推測ではなく実際のソースコード調査の重要性
- 公式ドキュメントだけでは不十分なケースがある
- エラーメッセージを丁寧に読み、根本原因を特定する

---

### LangChain/LangGraphハンドラのリファクタリング - 2025-11-01

**完了内容:**
- 4つのハンドラ（LangChain/LangGraph × sync/streaming）の履歴管理を `load_chat_history()` に統一
- セッションキーを `chat_history_key` に揃え、変数名・型ヒント・例外処理を整理
- LangGraph版に `ChatState` を導入し、`agent.ainvoke` のレスポンスをそのまま履歴へ反映
- `.claude/todo.md` にチェックポイント導入タスクを追加、今後の検討事項を明確化

**重要な技術的発見:**
1. Chainlitの`Message.stream_token()`が内部で`content`を蓄積しているため、ストリーミング後はそのまま履歴に保存できる
2. LangGraphでは`StateGraph(ChatState)`とすることでTypedDictベースの型情報をIDE補完に活かせる
3. LangGraphレスポンス（`agent.ainvoke`）を再ラップせずに履歴へ統合することで重複生成を防げる

**調査方法:**
- Chainlitの`message.py`を確認して`stream_token`の挙動を把握
- LangGraphの型定義を読み、StateGraphに独自TypedDictを渡す方法を検証
- 既存コードと動作を比較しながら命名や型の統一案を洗い出し

**成果物:**
- [app_langchain_sync.py](../app_langchain_sync.py)
- [app_langchain_streaming.py](../app_langchain_streaming.py)
- [app_langgraph_sync.py](../app_langgraph_sync.py)
- [app_langgraph_streaming.py](../app_langgraph_streaming.py)
- Pull Request #7（Refine Lang chat handlers、マージ済み）

**今後のタスク:**
- `.claude/todo.md` に記載した LangGraph チェックポイント機構の検討・導入
- LangGraphストリーミング版で複数メッセージ／更新ストリームに対応するか判断
- ログ出力（標準logging / loguru / cl.logger）の方針決定と実装

---

### エラーハンドリングの追加（シンプル版） - 2025-10-31

**完了内容:**
- 3つのChainlitアプリ全てにエラーハンドリングを追加（PR #5マージ済み）
- API呼び出しエラーをキャッチ（`try-except Exception`）
- プロバイダー非依存な実装（`str(e)`でエラーメッセージ表示）
- 不要な防御的コードを削除（セッション検証、LangGraphレスポンス検証）
- 学習用コードのシンプルさを優先

**実装方針:**
- **プロバイダー非依存**: `Exception`で広くキャッチし、OpenAI依存を避ける
- **エラーメッセージ**: `str(e)`でプロバイダーのメッセージを直接表示（高品質なため）
- **リトライは別タスク**: `with_retry()`の導入は低優先度で別途検討

**削除したコード:**
1. **セッション検証** (`messages is None`チェック):
   - Chainlitはページリロード/サーバー再起動時に自動的にセッションを再確立
   - 実際にはほぼ発生しない状況への防御的プログラミング
   - テスト不可能（再現方法がない）

2. **LangGraphレスポンス検証** (`response`構造チェック):
   - LangGraphのソースコード調査により不要と判明
   - `MessagesState`は型システムで構造を保証
   - LangGraphは無効な返り値を「更新なし」として扱い、エラーにならない
   - 実際のエラーは外側の`try-except`でキャッチされる

**技術的な学び:**
- **調査の重要性**: 推測ではなく、実際のテストとソースコード調査に基づいて判断
- **学習用コードの設計**: 本番運用コードとは異なり、シンプルさを優先すべき
- **本質的なエラーハンドリング**: API呼び出しエラーに集中することで、学習効果が向上

**成果物:**
- [app_langchain_sync.py](../app_langchain_sync.py) - シンプルなエラーハンドリング
- [app_langchain_streaming.py](../app_langchain_streaming.py) - シンプルなエラーハンドリング
- [app_langgraph_sync.py](../app_langgraph_sync.py) - シンプルなエラーハンドリング
- [.claude/decisions.md](decisions.md) - 詳細な調査結果と削除理由を記録
- Pull Request #5（マージ済み、コミット b5d1fd4）

**今後のタスク:**
- リトライ機能の追加（`with_retry()`）- 優先度: 低
- ログ記録の追加 - 優先度: 中
- テストの追加 - 優先度: 中

---

### ファイル整理とLangChain同期版の復元 - 2025-10-30

**完了内容:**
- ファイル名を統一命名規則に従って整理（sync/streaming）
- app_langchain.py → app_langchain_streaming.py にリネーム
- app_langgraph.py → app_langgraph_sync.py にリネーム
- app_langchain_sync.py をgit履歴（コミット a55aecf）から復元
- README.md、CLAUDE.md、.claude/todo.md を更新
- 2×2実装マトリックスを確立（LangChain/LangGraph × sync/streaming）
- Pull Request #4をマージ

**実装マトリックス（現状）:**
- ✅ LangChain + 同期（app_langchain_sync.py）
- ✅ LangChain + ストリーミング（app_langchain_streaming.py）
- ✅ LangGraph + 同期（app_langgraph_sync.py）
- ⏳ LangGraph + ストリーミング（Phase 2で実装予定）

**技術的な学び:**
- **用語の整理**: "sync"は厳密には非同期処理だが、ユーザー体験の観点から「一度に表示」を意味する
- **git履歴の活用**: 過去のコミットから必要なファイルを復元できる（`git show a55aecf:app.py`）
- **命名規則の重要性**: ファイル名からすぐに実装方式が分かることで、プロジェクトの見通しが大幅に改善

**成果物:**
- [app_langchain_sync.py](../app_langchain_sync.py) - LangChain同期版（復元）
- [app_langchain_streaming.py](../app_langchain_streaming.py) - LangChainストリーミング版（リネーム）
- [app_langgraph_sync.py](../app_langgraph_sync.py) - LangGraph同期版（リネーム）
- [README.md](../README.md) - 2×2マトリックス追加
- [CLAUDE.md](../CLAUDE.md) - 起動方法更新
- Pull Request #4（マージ済み、コミット 8d8a651）

**今後のタスク:**
- docker-compose.yml の更新（別タスクとして todo.md に記録済み）
- LangGraphストリーミング版の実装（2×2マトリックス完成のため）

---

### LangGraph Phase 1実装完了 - 2025-10-29

**完了内容:**
- LangGraphの基本実装を完了し、mainブランチにマージ（PR #3）
- app.py を app_langchain.py にリネーム
- app_langgraph.py を新規作成（StateGraph、システムメッセージ、会話履歴保持、非同期処理）
- langgraph v1.0.1 を依存関係に追加
- README.md、decisions.md、CLAUDE.md、.gitignore を更新
- 実験用ノートブックの命名規則を確立（`tmp_*.ipynb`）

**技術的な学び:**
- **非同期処理の重要性**: LLM呼び出しはI/O操作なので、ノード関数は`async def`で実装推奨
- **StateGraph**: LangGraphの基本構造、ノードとエッジでグラフを構築
- **MessagesState**: LangGraphの組み込み状態、メッセージリストを自動管理
- **複数ユーザーでのパフォーマンス**: 非同期処理により、30秒→3秒に改善する事例もある

**成果物:**
- [app_langchain.py](../app_langchain.py) - LangChain版（ストリーミング対応）
- [app_langgraph.py](../app_langgraph.py) - LangGraph版（基本実装）
- [README.md](../README.md) - 2つの実装の起動方法を記載
- [.claude/decisions.md](decisions.md) - LangGraph採用の設計決定を記録
- Pull Request #3（マージ済み）

---

## セッション引き継ぎチェックリスト

新しいセッションを開始する際は、Claude Codeに以下を伝えてください：

- [ ] 「.claude/context.mdを読んで、前回の続きをお願いします」
- [ ] 必要に応じて「.claude/todo.mdのタスクを確認してください」
- [ ] 設計の背景が必要なら「.claude/decisions.mdを参照してください」

---

## 注意事項

このファイルは**作業中の一時的な情報**を記録するためのものです。タスクが完了したら：

1. 完了したタスクを「最近完了したタスク」セクションに移動
2. 重要な決定事項があれば [decisions.md](decisions.md) に記録
3. 「進行中のタスク」セクションをクリア

長期的な情報は他のファイルに記録してください：
- 設計判断 → [decisions.md](decisions.md)
- タスク管理 → [todo.md](todo.md)
- 参考資料 → [references.md](references.md)
