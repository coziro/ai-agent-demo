# Current Work Context (現在の作業コンテキスト)

このファイルには、**今現在進行中の作業**を記録します。VS Codeを再起動したりコンテナをrebuildした後でも、ここを見れば作業を再開できます。

**最終更新:** 2025-11-01（古い完了タスク削除: 2025-10-26以前を整理）

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

現在進行中のタスクはありません。

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
