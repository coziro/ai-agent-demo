# Design Decisions (設計の決定事項)

このファイルには、プロジェクトの重要な設計判断を記録します。なぜその選択をしたのか、何を比較検討したのかを残すことで、後から見返したときに理解しやすくなります。

---

## ファイル管理方針

**現在の状態:** アクティブな決定事項を記録中（~200行、2025-10-24時点）

**サイズ管理ガイドライン:**
- **300行を超えたら**: 古い決定事項をレビューし、現在も重要なものだけ残す
- **500行を超えたら**: アーカイブ化を検討（`.claude/archive/decisions-YYYY.md`に移動）
- **原則**: よく参照される決定事項のみを本ファイルに保持

**アーカイブの基準（将来の参考）:**
- 過去のプロジェクトフェーズの決定（もう変更される可能性が低い）
- 歴史的価値はあるが日常的には参照しない情報
- 完全に置き換えられた古い決定事項

**YAGNI原則の適用:**
現時点ではアーカイブ構造は作成していません。必要になってから対応します。

---

## テンプレート

新しい決定事項を追加する際は、以下のテンプレートをコピーして使用してください：

```markdown
### [決定事項のタイトル] - YYYY-MM-DD

**状況・課題:**
- どんな問題や選択肢があったか

**検討した選択肢:**
1. 選択肢A: ...
2. 選択肢B: ...
3. 選択肢C: ...

**決定内容:**
- 最終的に選んだ方法

**理由:**
- なぜこれを選んだのか
- どんなトレードオフがあったか

**影響範囲:**
- どのファイル・機能に影響するか

**参考資料:**
- 関連するドキュメント・URL
```

---

## 決定事項の記録

### Pyrightを型チェッカーとして採用し `typeCheckingMode="standard"` を基準に運用 - 2025-11-03

**状況・課題:**
- LangChain/LangGraph 実装に型チェックを導入して品質を高めたい
- Chainlit や LangGraph の API は型スタブが十分でなく、どの厳しさで運用するか判断が必要だった

**検討した選択肢:**
1. `typeCheckingMode="basic"`: 警告は少ないが Unknown が残っても気付きにくい
2. `typeCheckingMode="standard"`: Unknown を拾いつつ、過度なアノテーションを要求しない
3. `typeCheckingMode="strict"`: 最も厳格だが `TYPE_CHECKING` ブロックやスタブ整備が必須で初期コストが大きい

**決定内容:**
- Pyright を採用し、`pyproject.toml` の `[tool.pyright]` で `typeCheckingMode = "standard"` を設定
- `include = ["apps"]` を対象とし、アプリ実装から段階的に整備
- `reportMissingTypeStubs = false` にして外部ライブラリの警告ノイズを抑制

**理由:**
- `standard` により Unknown を早期検出しつつ、可読性を損なわずに実運用できる
- `cast` / `assert` / ガードで補える範囲が広く、strict より導入障壁が低い
- 将来的にスタブ整備が進めば strict への移行も視野に入る

**影響範囲:**
- `pyproject.toml`, `uv.lock`, `.devcontainer/Dockerfile`
- `apps/langchain_sync.py`, `apps/langchain_streaming.py`, `apps/langgraph_sync.py`, `apps/langgraph_streaming.py`
- 開発フローに `uv run pyright` 実行を追加

**今後のメモ:**
- CI（GitHub Actions）への組み込みや、`apps/` 以外のディレクトリへの適用拡大を検討する
- Chainlit/LangGraph 向けのスタブ作成やユーティリティ化で strict 運用へ徐々に近づける

### Chainlitフレームワークの採用 - 2025-10-23

**状況・課題:**
- 対話型AIアプリケーションを構築する必要があった

**検討した選択肢:**
1. Streamlit: データ分析・可視化向け
2. Gradio: シンプルなUI、主にML demo用
3. Chainlit: チャットUI特化、LLM統合が強力

**決定内容:**
- Chainlitを採用

**理由:**
- チャットインターフェースに最適化されている
- LangChain/LlamaIndexとの統合が容易
- ストリーミング対応が標準
- 日本語対応が良好

**影響範囲:**
- [app.py](../app.py)
- [.chainlit/config.toml](../.chainlit/config.toml)
- 依存関係: pyproject.toml

**参考資料:**
- https://docs.chainlit.io/

---

### Chainlit翻訳ファイルの管理方針 - 2025-10-23（2025-10-24更新）

**状況・課題:**
- Chainlitには多言語対応の翻訳ファイルが自動生成される
- 当初は不要な言語ファイルを削除する方針だったが、Chainlit起動時に自動再生成されることが判明

**検討した選択肢:**
1. 翻訳ファイルを削除し続ける → Chainlitが毎回自動生成するため不可能
2. .gitignoreで除外する → git statusが煩雑になる
3. **自動生成されたファイルをそのままコミットする** ✓

**決定内容:**
- **すべての翻訳ファイルをgitで管理する**（自動生成されるファイルを含む）
- **日本語(ja.json)と英語(en-US.json)のみを積極的にメンテナンス**
- その他の言語ファイルは自動生成されたものをそのままコミット

**理由:**
- Chainlitが起動時に翻訳ファイルを自動生成する仕様
- .gitignoreで除外すると、git statusにuntrackedファイルが常に表示される
- 自動生成ファイルをコミットすることで、git statusをクリーンに保つ
- 日英以外の言語は編集しないが、存在してもコストは低い
- チームメンバーが同じ環境を再現しやすい

**メンテナンス方針:**
- ja.jsonとen-US.jsonのみ手動編集対象
- その他の言語ファイルは触らない（Chainlitの自動生成に任せる）

**日本語翻訳ファイルの可読性向上:**
- ja.jsonのUnicodeエスケープシーケンス（`\u30ad\u30e3\u30f3\u30bb\u30eb`）を実際の日本語文字（`キャンセル`）に変換
- 理由: 開発者が直接編集しやすくするため、可読性を優先
- 実施日: 2025-10-23（コミット `156ad7e`）
- 注意: JSONとしては両方とも有効だが、人間が読み書きしやすい形式を採用

**影響範囲:**
- [.chainlit/translations/](../.chainlit/translations/)
- 特に [ja.json](../.chainlit/translations/ja.json) は編集対象

**変更履歴:**
- 2025-10-23: 当初は削除方針を採用（コミット `a8b04b1`）
- 2025-10-23: ja.jsonを人間が読みやすい形式に変換（コミット `156ad7e`）
- 2025-10-24: Chainlitの自動生成仕様が判明し、方針変更してコミット（コミット `f3f06db`）

---

### DevContainer + uv ベースの開発環境を採用 - 2025-10-23

**状況・課題:**
- チーム開発で環境の一貫性を保つ必要があった
- ローカル環境の差異による「私の環境では動く」問題を避けたい
- Python依存関係管理ツールの選定

**検討した選択肢:**

**開発環境:**
1. ローカル環境に直接インストール: 環境差異が発生しやすい
2. Docker Compose: 設定が複雑
3. **DevContainer**: VS Code統合、開発者体験が良い ✓

**Python依存関係管理:**
1. pip + requirements.txt: 標準だが機能が限定的
2. Poetry: 人気だが遅い
3. **uv**: 高速（Rust製）、モダン ✓

**Pythonバージョン:**
- Python 3.12: 最新の安定版、型ヒント機能の向上

**決定内容:**
- **DevContainer** (VS Code Dev Containers)を開発環境として採用
- **Docker** ベースイメージ: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- **uv** をPython依存関係管理ツールとして採用
- **Python 3.12** を使用

**理由:**
- **DevContainer**:
  - VS Codeとシームレスに統合
  - 全開発者が同一環境で作業可能
  - 環境構築が簡単（`devcontainer.json`1つで完結）
- **uv**:
  - 非常に高速（Rust製）
  - pyproject.toml標準対応
  - lockfileによる再現性の確保
  - DevContainerとの相性が良い
- **公式uvイメージ使用**:
  - uvとPythonが事前インストール済み
  - メンテナンスされている公式イメージ
- **シンプル設定の方針**:
  - 最小限の設定で開始（git、curl、vimのみ追加）
  - 複雑な設定は必要性が発生してから追加
  - 過剰な事前最適化を避ける（YAGNI原則）

**影響範囲:**
- [.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json)
- [.devcontainer/Dockerfile](../.devcontainer/Dockerfile)
- [pyproject.toml](../pyproject.toml)
- uv.lock
- VS Code拡張機能の自動インストール（Python、Jupyter、Claude Code）

**参考資料:**
- https://code.visualstudio.com/docs/devcontainers/containers
- https://github.com/astral-sh/uv
- https://github.com/astral-sh/uv/pkgs/container/uv

---

### .claude/ディレクトリのGit管理方針 - 2025-10-24

**状況・課題:**
- Claude Codeのコンテキスト管理ファイル（.claude/）をGitで管理すべきか検討
- 個人的なメモと、プロジェクトの知識ベースの使い分けが必要

**検討した選択肢:**
1. すべて.gitignore（個人メモとして使う） → 知識共有できない
2. 選択的にコミット（設計決定のみ） → 管理が複雑
3. **すべてコミット + 個人メモ用ファイルを別途用意** ✓

**決定内容:**
- **.claude/配下のファイルはすべてGitにコミットする**
- **個人的なメモは`.claude/personal.md`に記録し、.gitignoreで除外**

**理由:**
- このプロジェクトは**OSSとして公開**する
- **設計決定（decisions.md）は他の開発者にとって非常に価値がある**
  - 「なぜこの技術を選んだのか」はコードだけでは分からない
  - 過去の検討内容を知ることで、コントリビューターが参加しやすくなる
- **プロジェクトの透明性**が向上する
- 個人的なメモは`personal.md`に分離することで、公開・非公開を明確に区別

**運用ルール:**
- **コミットするファイル（公開）:**
  - decisions.md - 設計決定とその理由
  - references.md - 参考資料・リンク集
  - todo.md - プロジェクトタスク（個人的なものは除く）
  - context.md - 現在の作業状況（プロジェクトに関連するもののみ）

- **コミットしないファイル（個人用）:**
  - personal.md - 完全に個人的なメモ、一時的なメモ

**影響範囲:**
- [.claude/](../.claude/) - すべてのファイル（personal.md除く）
- [.gitignore](../.gitignore) - personal.mdを追加

**参考:**
成功しているOSSプロジェクトの多くは、設計決定やADR（Architecture Decision Records）を公開しており、これがコミュニティの成長に貢献している。

### LangChainの採用とシンプル実装の選択 - 2025-10-25

**状況・課題:**
- Chainlitアプリに実際のLLM機能を追加する必要があった
- 将来的にはLangGraphを使ったAIエージェントを実装したい

**検討した選択肢:**
1. **OpenAI API直接使用**: シンプルだが、将来の拡張性に制限
2. **LangChain使用**: 学習コストはあるが、LangGraphへの移行が容易
3. **LangChain + LCEL**: 強力だが、初学者には複雑

**決定内容:**
- **LangChain + ChatOpenAI を採用**
- **LCELは使わず、シンプルな実装から始める**
- **gpt-5-nano モデルを使用**

**理由:**
- 将来的にLangGraphを使いたいため、LangChainのエコシステムに慣れる
- OpenAI APIは過去に経験済みなので、新しい学びとしてLangChainを選択
- LCELは複雑なパイプラインで真価を発揮するため、シンプルなチャットでは不要
- まずは基礎を理解してから、必要に応じてLCELを導入する方針

**技術的な学び:**
- `ChatOpenAI` vs `OpenAI`: チャットモデル vs 補完モデル（レガシー）
- `ainvoke()` vs `invoke()`: 非同期 vs 同期（async関数内ではainvokeを使う）
- Pythonの非同期処理: `await`の必要性、イベントループ、ブロッキングの概念

**実装パターン:**
```python
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage

model = ChatOpenAI(model="gpt-5-nano")
system_msg = SystemMessage("You are a helpful assistant.")

@cl.on_message
async def main(message: cl.Message):
    human_msg = HumanMessage(message.content)
    response = await model.ainvoke([system_msg, human_msg])
    await cl.Message(content=response.content).send()
```

**影響範囲:**
- [app.py](../app.py) - メインアプリケーション
- [pyproject.toml](../pyproject.toml) - langchain, langchain-openai 依存関係追加
- .env - OPENAI_API_KEY 環境変数

**参考資料:**
- https://docs.langchain.com/oss/python/langchain/models
- https://python.langchain.com/docs/integrations/chat/openai/

**今後の展開:**
1. まずはマルチターン会話（会話履歴の保持）
2. ストリーミングレスポンス
3. LangGraphを使ったエージェント実装

### 日本語IME入力対応の技術調査 - 2025-10-25

**状況・課題:**
- Chainlitで日本語入力時、変換確定のEnterキーでメッセージが送信されてしまう
- 英語圏で開発されたアプリケーションでは、このようなIME対応の問題が頻繁に発生
- 汎用的なベストプラクティスと、Chainlit特有の対策を調査

**検討した選択肢:**
1. **Qiitaの回避策**: `public/custom.js`でグローバルにEnterキーをブロック
2. **Web標準のComposition Events**: `compositionstart/end`イベントを使った正攻法
3. **Chainlit本体への貢献**: Pull Requestで根本解決

**技術的知見:**

**Web標準のベストプラクティス（理想的な実装）:**
```javascript
// モダンブラウザ向けのシンプルな実装
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.isComposing) {
    submit(); // IME変換中でなければ送信
  }
});

// または、React等のフレームワークでの実装
const [isComposing, setIsComposing] = useState(false);

<input
  onCompositionStart={() => setIsComposing(true)}
  onCompositionEnd={() => setIsComposing(false)}
  onKeyDown={(e) => {
    if (e.key === 'Enter' && !isComposing) {
      submit();
    }
  }}
/>
```

**ブラウザ間の差異:**
- Chrome/Edge: `compositionend`後に`keyup`が発火しない
- Firefox/Safari/IE11: `compositionend`後に`keyup`が発火する
- Safari: 追加で`keydown`が`event.which`=229で発火
- 対策: `keydown`を使う（`keyup`は使わない）

**Qiitaの回避策の評価:**
- ✅ 動作する: Chainlitで確実に問題を回避できる
- ⚠️ 過剰な対策: プロトタイプパッチ、グローバルイベント傍受は侵襲的
- ❌ 保守性: Chainlitのバージョンアップで壊れる可能性が高い
- 理由: Chainlitのコードを直接編集できないため、外側から強引にブロックする必要がある

**なぜ英語圏のアプリでこの問題が多いのか:**
1. 開発者がIMEを使わず、テストが不十分
2. CI/CDにIMEテストが含まれていない
3. フレームワークが適切にComposition Eventsを処理していない場合がある

**決定内容（2段階アプローチ）:**
- **Phase 1: MVP後にQiitaの回避策を実装**（現実的な暫定対応）
- **Phase 2: Chainlit本体への貢献**（推奨される根本解決）
- 理由:
  - Phase 1で即座にユーザー体験を改善
  - Phase 2で全世界のユーザーに貢献し、暫定対応を不要にする

**OSSコントリビューションの詳細（2025年10月25日追記）:**

調査の結果、**ChainlitのGitHubに既に関連Issueが存在することを発見**:

1. **Issue #2600** (2025-10-21): 中国語IME（Pinyin）の問題
   - 状態: オープン、needs-triage
   - 問題: Enterで変換確定と同時にメッセージ送信
   - 原因: compositionstart/compositionendイベント処理の欠如
   - 回避策: Shift+Enterで確定してからEnter送信
   - URL: https://github.com/Chainlit/chainlit/issues/2600

2. **Issue #2598** (2025-10-21): 韓国語IMEの問題
   - 状態: オープン、needs-triage
   - 問題: メッセージが2回送信される
   - 原因: React.jsのIMEイベント処理のレースコンディション
   - URL: https://github.com/Chainlit/chainlit/issues/2598

**重要な発見:**
- 日本語のIssueはまだ報告されていない
- 日本語ユーザーはQiitaで回避策を共有しているため、GitHubに報告していない
- 中国語・韓国語ユーザーは直接GitHubに報告している
- 両Issueとも2025年10月21日から放置されている（PRなし）

**コントリビューションの機会:**
1. 既存Issue（#2600, #2598）に日本語でも発生すると報告
2. 両Issueに👍リアクションで優先度を上げる
3. Composition Events処理を実装したPRを作成
4. 日本語・中国語・韓国語すべてで動作確認
5. 全世界のIMEユーザーに貢献できる

**技術的アプローチ:**
- 場所: Chainlitのフロントエンド（React）の入力コンポーネント
- 修正: `onCompositionStart/End`ハンドラを追加
- 参考実装: references.mdに記載済み

**参考資料:**
- Qiita記事（回避策）: https://qiita.com/bohemian916/items/4f3e860904c24922905a
- MDN - compositionstart: https://developer.mozilla.org/en-US/docs/Web/API/Element/compositionstart_event
- Handling IME events: https://www.stum.de/2016/06/24/handling-ime-events-in-javascript/
- Square's best practices: https://developer.squareup.com/blog/understanding-composition-browser-events/
- Stack Overflow discussion: https://stackoverflow.com/questions/7316886/detecting-ime-input-before-enter-pressed-in-javascript

**影響範囲:**
- 実装時: public/custom.js（新規）、.chainlit/config.toml

**学び:**
- Web標準のComposition Eventsが存在するが、既存アプリに統合するのは難しい
- 国際化（i18n）はアプリ設計の初期段階から考慮すべき
- OSSへの貢献は、同様の問題を抱える他のユーザーにも貢献できる

### UIレイヤーとビジネスロジックの分離方針 - 2025-10-26

**状況・課題:**
- Chainlitで会話履歴管理を実装する際、`cl.user_session` や `cl.chat_context` などChainlit固有の機能を使うか検討
- 将来的にStreamlitや別のUIフレームワークに移行する可能性がある

**検討した選択肢:**
1. **Chainlitの機能を最大限活用**: `cl.chat_context.to_openai()` などで簡単に実装
2. **ビジネスロジックを分離**: ChatSessionクラスなどを作成してフレームワーク非依存に
3. **完全なレイヤー分離**: UI層、ビジネスロジック層、LLM層を明確に分ける

**決定内容:**
- **現時点では選択肢1で実装（Chainlitに依存）**
- **将来的には選択肢2-3への移行を推奨**

**理由:**
- MVP段階では開発速度を優先
- ただし、フレームワークロックインのリスクは認識しておく
- 将来の移行時には `ChatSession` クラスなどを作成してビジネスロジックを抽出する

**推奨アーキテクチャ（将来的）:**
```
UI Layer (Chainlit/Streamlit等) ← フレームワーク依存
    ↓↑
Business Logic Layer (ChatSession等) ← フレームワーク非依存
    ↓↑
LLM Layer (LangChain等) ← プロバイダー抽象化
```

**メリット:**
- テストが容易（ビジネスロジックを単体でテスト可能）
- 再利用性が高い（CLI、API、Slackボットなどでも使える）
- フレームワーク移行が簡単

**影響範囲:**
- 現在: [app.py](../app.py) - Chainlit依存の実装
- 将来: ChatSessionクラスなどを作成して分離

**参考:**
- この決定は、実装中の議論で「将来別のUIフレームワークに変更する可能性」が明らかになった際に確認された
- 現時点では技術的負債として認識しつつ、MVP完成を優先

### 会話履歴の管理方法（手動 vs 自動） - 2025-10-26

**状況・課題:**
- Chainlitには `cl.chat_context` という自動的に会話履歴を管理する機能がある
- 手動で `cl.user_session` にメッセージリストを保存する方法もある

**検討した選択肢:**
1. **cl.chat_context を使用**: Chainlitが自動的に管理、`to_openai()` で取得
2. **手動でmessagesリストを管理**: `cl.user_session` で明示的に保存

**決定内容:**
- **手動でmessagesリストを管理する方法を採用**

**理由:**
- UIフレームワーク非依存を将来的に目指すため、Chainlit固有機能への依存を最小限にする
- 明示的な管理により、どこでどうデータが保持されているか理解しやすい
- 将来のフレームワーク移行時、会話履歴管理のロジックをそのまま再利用できる可能性が高い

**技術的な学び:**
- **Pythonのリストは参照渡し**: `cl.user_session.get("messages")` で取得したリストに `append()` すると、セッション内のリストも自動的に更新される（再度 `set()` する必要なし）
- これはミュータブル（変更可能）なオブジェクトの特性による
- イミュータブル（文字列、数値など）の場合は、再度 `set()` が必要

**実装例:**
```python
@cl.on_chat_start
async def on_chat_start():
    messages = [SystemMessage("You are a helpful assistant.")]
    cl.user_session.set("messages", messages)

@cl.on_message
async def on_message(message: cl.Message):
    messages = cl.user_session.get("messages")  # リストの参照を取得
    messages.append(HumanMessage(message.content))  # 直接変更される
    response = await model.ainvoke(messages)
    messages.append(AIMessage(response.content))  # これも直接変更される
    # 再度 set() する必要なし！
```

**影響範囲:**
- [app.py](../app.py) - マルチターン会話の実装

**参考:**
- この実装中、「メッセージが消える」問題が発生したが、実際はChainlitの `user_message_autoscroll = true` によるスクロールの挙動だった
- `.chainlit/config.toml` でスクロール設定を調整して解決

### ストリーミングレスポンスの実装方針 - 2025-10-26

**状況・課題:**
- ChatGPTのようなリアルタイムなチャット体験を実装したい
- LangChainの `astream()` とChainlitの `stream_token()` を組み合わせる必要がある
- 公式ドキュメントの例と実際の動作が異なる場合の対処

**検討した選択肢:**
1. **同期的なストリーミング**: 事前に全トークンを取得してから表示（公式例のパターン）
2. **非同期ストリーミング**: LLMから逐次的にchunkを受け取りながら表示
3. **ストリーミングなし**: 完全な応答を待ってから一度に表示

**決定内容:**
- **選択肢2: 非同期ストリーミングを採用**
- `model.astream()` で非同期ジェネレーターを取得
- `async for` でchunkを逐次処理
- `.content` プロパティを使用（`.text` は非推奨）

**実装パターン:**
```python
msg = cl.Message(content="")
# 最初の send() は呼ばない（ローディング表示を維持）

full_response = ""
async for chunk in model.astream(messages):
    if chunk.content:
        await msg.stream_token(chunk.content)
        full_response += chunk.content

await msg.send()  # 最後に呼んでストリーミング完了を通知
```

**技術的な学び（実験による検証）:**
- **`send()` のタイミング**:
  - 最初に呼ぶと: 空メッセージが表示され、画面が止まったように見える（UX悪化）
  - 最初に呼ばない: ローディング表示が維持される（UX向上）
  - 最後に呼ぶ: カーソルが消え、コピーボタンが表示される（必須）
- **`stream_token()` の動作**: 初回呼び出し時に自動的にメッセージ表示が開始される
- **非同期ジェネレーター**: `astream()` の返り値には `async for` が必要（`for` だとエラー）
- **`.content` vs `.text`**: LangChainで `.text` は非推奨、`.content` を使うべき

**公式ドキュメントとの違い:**
公式例では `msg = await cl.Message(content="").send()` と最初に `send()` を呼んでいるが、非同期ストリーミングの場合は動作が異なる。実験的検証により、最初の `send()` は不要で、最後にのみ必要であることが判明。

**UX改善:**
- ユーザー入力後、ローディング表示でレスポンス待ちが明確
- ChatGPTのような文字が徐々に表示される体験
- 完了時にコピーボタンが表示され、メッセージ完了が明確

**影響範囲:**
- [app.py](../app.py) - ストリーミング対応のメッセージ処理

**参考:**
- LangChain公式ドキュメント: https://python.langchain.com/docs/how_to/streaming/
- Chainlit API リファレンス: https://docs.chainlit.io/api-reference/message
- 実装中に複数回の実験を行い、UXを確認しながら最適なパターンを決定

---

### GitHub Flowベースのブランチ戦略 - 2025-10-26

**状況・課題:**
- MVP完成後、複数の改善タスクを並行して進める必要が出てきた
- これまではmainブランチに直接コミットしていた
- 実験的な機能開発でmainブランチが不安定になるリスクがある
- 人間だけでなくClaude Codeもコードを書くため、レビュープロセスが重要

**検討した選択肢:**
1. **mainブランチ直接コミット（現状）**: シンプルだが、戻すのが難しい
2. **GitHub Flow**: 機能ブランチ + Pull Request、シンプルで効果的
3. **Git Flow**: develop/release/hotfixブランチ、大規模プロジェクト向け（過剰）
4. **GitLab Flow**: 環境別ブランチ、複数環境デプロイ向け（不要）

**決定内容:**
- **GitHub Flowを採用**
- **Pull Requestによるレビューを必須化**

**ブランチ戦略の詳細:**

1. **mainブランチ**:
   - 常にデプロイ可能な状態を保つ
   - 動作確認済みのコードのみをマージ
   - 直接コミットは禁止（緊急修正を除く）

2. **機能ブランチ**:
   - 命名規則: `feature/機能名`、`fix/バグ名`、`refactor/対象`
   - 例: `feature/japanese-ime-support`, `fix/error-handling`, `refactor/chat-session`
   - mainから作成、作業完了後にmainへマージ

3. **ワークフロー**:
   ```
   1. mainから機能ブランチを作成
      git checkout -b feature/new-feature

   2. 機能ブランチで開発・コミット
      git add .
      git commit -m "実装内容"

   3. Pull Requestを作成
      gh pr create --title "タイトル" --body "説明"

   4. レビュー・動作確認
      - Claude Codeが作成したコードを人間がレビュー
      - ローカルで動作確認

   5. 問題なければmainにマージ
      gh pr merge

   6. うまくいかない場合はブランチ削除
      git checkout main
      git branch -D feature/failed-feature
   ```

4. **Pull Requestのルール**:
   - すべてのマージはPR経由で行う
   - PR説明には以下を含める:
     - 変更の概要
     - 動作確認方法
     - スクリーンショット（UI変更の場合）
   - レビューポイント:
     - コードの品質（可読性、保守性）
     - 動作確認（実際に動くか）
     - 副作用の確認（既存機能を壊していないか）

5. **Claude Codeとの協業**:
   - Claude Codeに機能実装を依頼する際、ブランチ作成から依頼
   - PRはClaude Codeに作成してもらう
   - 最終レビュー・マージ判断は人間が行う

**理由:**
- **GitHub Flow採用**:
  - シンプルで理解しやすい（個人開発に最適）
  - mainが常に安定している安心感
  - いつでもmainに戻れる柔軟性
  - Git Flowは過剰（develop/releaseブランチは不要）
- **PR必須化**:
  - Claude Codeが書いたコードを人間がレビューできる
  - 変更履歴が明確に残る
  - GitHubの機能（CI、コードレビュー等）を活用できる
  - 将来、他の開発者が参加する際もスムーズ

**トレードオフ:**
- 手間が増える（ブランチ作成、PR作成、マージ）
- しかし、以下のメリットがコストを上回る:
  - mainブランチの安定性確保
  - 失敗した実験を簡単に破棄できる
  - コードレビューによる品質向上

**影響範囲:**
- 開発ワークフロー全体
- CLAUDE.mdに開発プロセスを追記予定
- README.mdのDevelopmentセクション更新を検討

**参考資料:**
- GitHub Flow解説: https://docs.github.com/en/get-started/using-github/github-flow
- gh CLI (Pull Request作成): https://cli.github.com/manual/gh_pr_create

**次のアクション:**
- CLAUDE.mdにブランチ戦略を記載
- 次の機能開発から実際にGitHub Flowを適用

---

### Ruffによるコード品質管理の方針 - 2025-10-26

**状況・課題:**
- コードの一貫性と品質を保つためにRuff (linter/formatter) を導入
- 自動フォーマット vs 手動フォーマットの選択
- CI/CDでの品質チェック自動化の検討

**検討した選択肢:**
1. **保存時の自動フォーマット**: VS Code設定で自動実行
2. **コミット前の手動実行**: 意識的にruffを実行
3. **pre-commitフック**: コミット時に自動実行
4. **GitHub Actions**: PR時に自動チェック

**決定内容:**
- **現時点では手動実行（選択肢2）を採用**
- **将来的にGitHub Actions（選択肢4）を導入予定**

**運用ルール:**
- コミット前に必ず以下を実行:
  ```bash
  uv run ruff check .
  uv run ruff format .
  ```
- エラーがないことを確認してからコミット

**理由:**
- **自動フォーマットをオフにする判断**:
  - 意図しない変更を防ぐ（特にAIがコードを書く場合）
  - 変更内容を意識的にレビューできる
  - シンプルさを保つ（不要な設定ファイルを避ける）
- **手動実行を選択**:
  - 何が変わったか確認してからコミットできる
  - 開発者が品質管理を意識できる
- **GitHub Actions導入は将来**:
  - 現時点では過剰な自動化を避ける（YAGNI原則）
  - PRレビュー時の自動チェックは価値が高い

**Ruff設定:**
- [pyproject.toml](../pyproject.toml) に設定を記載
- ルールセット: `E`, `F`, `I` (pycodestyle errors, pyflakes, isort)
- 行の長さ: 88文字（Blackと同じ）

**影響範囲:**
- [pyproject.toml](../pyproject.toml) - Ruff設定
- [.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json) - Ruff拡張機能
- 開発ワークフロー: コミット前のチェック

**将来の改善:**
- GitHub Actionsで自動チェック（todo.mdに記載）
- pre-commitフックの検討（必要性が出てから）

**参考資料:**
- Ruff公式ドキュメント: https://docs.astral.sh/ruff/

### GitHub CLI (gh) の導入 - 2025-10-26

**状況・課題:**
- GitHub Flowを採用し、Pull Requestベースのワークフローを実践
- PRの作成・レビュー・マージをコマンドラインから効率的に行いたい
- Claude Codeにも自動的にPRを作成してもらいたい

**検討した選択肢:**
1. **ブラウザでPR管理**: GitHub Web UIを使用、CLIツール不要
2. **GitHub CLI (gh)**: 公式CLIツール、フル機能サポート
3. **hub**: 旧世代のGitHub CLIツール（非推奨）

**決定内容:**
- **GitHub CLI (`gh`) を採用**
- **Dockerfileに追加してDevContainerにインストール**
- **Debian標準リポジトリからapt-getでインストール**

**理由:**
- **GitHub公式ツール**: Githubが公式にメンテナンス
- **Claude Codeとの相性**: Claude Codeがコマンドラインから直接PR作成可能
- **効率性**: ターミナルから離れずにPRレビュー・マージが可能
- **GitHub Flowとの親和性**: ブランチ作成→開発→PR作成の流れをCLIで完結
- **シンプルなインストール**: Debian標準リポジトリから`apt-get install gh`で完了

**インストール方法の選択:**
- ❌ **DevContainer Features**: 一貫性に欠ける、Dockerfile方式と統一すべき
- ✅ **Dockerfile (apt-get)**: git、curl、vimと同じ方式でシンプル
- ❌ **GitHub公式リポジトリ追加**: 複雑、最新版は必須ではない

**認証方法:**
- **現状**: ホストの`~/.config/gh/hosts.yml`が自動的に利用される
- **推奨**: Fine-grained Personal Access Token で特定リポジトリ(ai-agent-demo)のみに制限
- **セキュリティ**: 全リポジトリへのアクセスを避け、必要最小限の権限に制限

**実装内容:**
```dockerfile
RUN apt-get update && apt-get install -y \
    git \
    curl \
    vim \
    gh \
    && rm -rf /var/lib/apt/lists/*
```

**影響範囲:**
- [.devcontainer/Dockerfile](../.devcontainer/Dockerfile) - gh追加
- [CLAUDE.md](../CLAUDE.md) - GitHub CLIセクション追加（使用方法、認証、セキュリティ）

**参考資料:**
- GitHub CLI公式: https://cli.github.com/
- Debian packages: https://packages.debian.org/bookworm/gh
- Fine-grained Tokens: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

**成果:**
- gh version 2.23.0 がインストール済み
- 認証済み（github.com as coziro）
- CLAUDE.mdに使用方法を記載
- 次回からPRをghコマンドで作成可能

### .claude/ファイルのコミット方針 - 2025-10-26

**状況・課題:**
- .claude/ディレクトリには異なる性質のファイルが混在している
  - **context.md, todo.md**: 頻繁に更新される作業メモ（日常的なタスク管理）
  - **decisions.md**: 重要な設計決定の記録（長期的に参照される知識）
- GitHub Flowの原則では「mainに直接コミットしない」が、すべての.claude/更新でPRを作成すると開発効率が低下する
- 実用性と品質のバランスが必要

**検討した選択肢:**
1. **すべての変更をPR経由**: 一貫性はあるが、作業メモの更新が煩雑で非効率
2. **すべてmainに直接コミット**: 速いが、重要な決定もレビューなしになる
3. **ファイルの性質に応じて使い分け**: 実用的でバランスが良い ✓

**決定内容:**
- **context.md, todo.md**: mainに直接コミットOK
- **decisions.md**: PR推奨（重要な設計決定はレビューする価値あり）
- **コード変更（app.py, Dockerfileなど）**: PR必須

**理由:**
- **context.mdとtodo.mdの特性**:
  - 日常的な作業メモ、頻繁に更新される
  - アプリケーションの動作に影響しない
  - コミット失敗のリスクが極めて低い
  - PRを作成する手間が開発効率を損なう
- **decisions.mdの特性**:
  - 長期的に影響する設計判断
  - チーム全体で共有すべき知識
  - レビューによって議論が深まる価値がある
- **コード変更の特性**:
  - アプリケーションの動作に直接影響
  - バグやリグレッションのリスクあり
  - 必ずレビュー・テストが必要

**実用性と品質のバランス:**
- 低リスクの作業メモは効率優先（直接コミット）
- 重要な決定とコードは品質優先（PR経由）
- これにより、GitHub Flowの利点（mainの安定性）を保ちつつ、開発効率も維持

**コミットメッセージのルール:**
context.md, todo.mdを直接コミットする場合でも、明確なコミットメッセージを書く：
```
Add task: [タスク名]

[変更内容の簡潔な説明]
```

**影響範囲:**
- 開発ワークフロー全体
- [CLAUDE.md](../CLAUDE.md) - GitHub Flowセクションに注記追加

**参考:**
- この決定は、実際の開発で「todo.mdの軽微な更新にPRが必要か？」という疑問から生まれた
- 実用的な判断基準を設けることで、開発者の負担を減らしつつ品質も維持

### LangGraphの採用と段階的実装方針 - 2025-10-29

**状況・課題:**
- LangChainで基本的なチャット機能は実装できたが、より複雑なAIエージェント（複数ステップのタスク、条件分岐、ツール呼び出しなど）を構築したい
- LangGraphの学習を兼ねて、段階的に機能を実装していく必要がある

**検討した選択肢:**
1. **LangChainのみで実装**: シンプルだが、複雑なエージェントには限界がある
2. **LangGraphで一から実装**: 学習曲線が急で、いきなり複雑な実装は困難
3. **段階的実装（Phase 1→2→3）**: 基本機能から始めて、徐々に高度な機能を追加 ✓

**決定内容:**
- **LangGraphを採用し、3フェーズで段階的に実装**
  - Phase 1: 基本機能（システムメッセージ、会話履歴保持、非同期処理）
  - Phase 2: ストリーミング対応
  - Phase 3: 高度なエージェント（複数ノード、条件分岐、ツール呼び出し）
- **LangChain版とLangGraph版の両方を保持**（app_langchain.py と app_langgraph.py）

**理由:**
- **段階的学習**: LangGraphの概念（StateGraph、ノード、エッジ）を1つずつ理解できる
- **比較可能**: LangChain版とLangGraph版を並べて、違いを理解できる
- **実用性**: Phase 1でも実用的なチャットアプリとして機能する
- **将来の拡張性**: Phase 3で複雑なエージェントを構築する土台ができる

**Phase 1の実装内容（完了）:**
```python
# LangGraphの基本構造
from langgraph.graph import StateGraph, MessagesState, START, END

# ノード関数（非同期）
async def call_llm(state: MessagesState):
    response = await model.ainvoke(state["messages"])
    return {"messages": [response]}

# グラフ構築
graph = StateGraph(MessagesState)
graph.add_node(call_llm)
graph.add_edge(START, "call_llm")
graph.add_edge("call_llm", END)
agent = graph.compile()

# 使用
response = await agent.ainvoke({"messages": messages})
```

**技術的な学び:**
- **非同期処理の重要性**:
  - LLM呼び出しはI/O操作なので、ノード関数は`async def`で実装推奨
  - `await model.ainvoke()`を使用することで、複数ユーザーの同時実行を効率化
  - 1ユーザーでは差が見えないが、複数ユーザーではパフォーマンスが大幅に向上（30秒→3秒の事例も）
- **StateGraph**: 会話履歴を保持するStateクラスを定義
- **MessagesState**: LangGraphの組み込み状態、メッセージリストを自動管理

**Phase 2の計画（ストリーミング対応）:**
- `agent.astream()` を使用してLLMトークンを逐次取得
- `stream_mode="messages"` でストリーミング設定
- Chainlitの`msg.stream_token()`と統合

**影響範囲:**
- [app_langchain.py](../app_langchain.py) - LangChain版（既存）
- [app_langgraph.py](../app_langgraph.py) - LangGraph版（新規）
- [pyproject.toml](../pyproject.toml) - langgraph依存関係追加
- [README.md](../README.md) - 起動方法を2つ記載

**参考資料:**
- LangGraph公式ドキュメント: https://langchain-ai.github.io/langgraph/
- LangGraph v1.0リリース: context.md、references.mdに詳細記載
- 非同期処理のベストプラクティス: Web検索結果より

**ブランチ:**
- feature/add-langgraph（GitHub Flowに従う）

---

### 実験用ノートブックの命名規則 - 2025-10-29

**状況・課題:**
- Jupyter notebookで実験的なコードを書く際、どれをgitにコミットすべきか、どれをローカルのみに留めるべきか曖昧だった
- `langgraph_basic.ipynb`を誤ってPRに含めてしまった

**検討した選択肢:**
1. `*_experimental.ipynb` - 長すぎる
2. `tmp_*.ipynb` - 短く、一時ファイルとして認識しやすい ✓
3. `wip_*.ipynb` - Work In Progress、意図は明確
4. `draft_*.ipynb` - 下書きという意図が明確
5. サフィックス（`*_tmp.ipynb`など） - ファイル名の主題が前に来る

**決定内容:**
- **実験用/一時的なノートブックは `tmp_*.ipynb` という命名規則を採用**
- **.gitignoreに `notebooks/tmp_*.ipynb` を追加**
- **CLAUDE.mdに命名規則を記載**

**理由:**
- 短い（3文字）でタイプしやすい
- `tmp`は一時的なファイルとして広く認識されている
- プレフィックスなので、ディレクトリ内でソートした時に実験ファイルがまとまる
- `.gitignore`で簡単に除外できる

**運用ルール:**
- **本番用ノートブック**: `descriptive_name.ipynb` （gitにコミット）
- **実験用ノートブック**: `tmp_*.ipynb` （ローカルのみ、gitignoreで除外）

**例:**
- ✅ `langgraph_tutorial.ipynb` - 本番用（コミット）
- ✅ `tmp_test.ipynb` - 実験用（コミットしない）
- ✅ `tmp_langgraph.ipynb` - 実験用（コミットしない）

**影響範囲:**
- [.gitignore](../.gitignore) - `notebooks/tmp_*.ipynb` を追加
- [CLAUDE.md](../CLAUDE.md) - 命名規則を記載

**メリット:**
- 誤って実験用ノートブックをコミットするリスクが減る
- チーム全体で統一された規則
- ファイル名を見ただけで、コミットすべきかどうか判断できる

### アプリファイルの命名規則 - 2025-10-30

**状況・課題:**
- 複数の実装パターン（LangChain/LangGraph × sync/streaming）が混在
- ファイル名から実装方式が分かりにくい
  - `app_langchain.py` → ストリーミング版だが名前からは不明
  - `app_langgraph.py` → 同期版だが名前からは不明
- プロジェクトを「実装例集」として発展させるため、明確な命名規則が必要

**検討した選択肢:**
1. **パターンA**: `app_{framework}_{mode}.py` (例: `app_langchain_sync.py`)
2. **パターンB**: `examples/`ディレクトリに分ける (例: `examples/langchain/sync.py`)
3. **パターンC**: 番号 + 説明的な名前 (例: `app_1_langchain_sync.py`)
4. **パターンD**: ハイフン区切り (例: `app-langchain-sync.py`)

**決定内容:**
- **パターンAを採用**: `app_{framework}_{mode}.py`
- 具体的なファイル名:
  - `app_langchain_sync.py` - LangChain + 同期
  - `app_langchain_streaming.py` - LangChain + ストリーミング
  - `app_langgraph_sync.py` - LangGraph + 同期
  - `app_langgraph_streaming.py` - LangGraph + ストリーミング（将来）

**用語の定義:**
- **sync（同期版）**: 完全なレスポンスを一度に表示（`ainvoke()`使用）
- **streaming（ストリーミング版）**: トークンを逐次的に表示（`astream()`使用）
- 注意: 両方とも `async/await` を使用した非同期処理
- 「sync」は厳密には技術用語として不正確だが、ユーザー体験の観点から適切

**理由:**
- **ファイル名から一目で分かる**: フレームワークと実装方式が明確
- **簡潔**: パターンBより短く、パターンCより意味が明確
- **Pythonの慣習**: アンダースコア区切り（パターンDのハイフンではない）
- **拡張性**: 将来的に他のパターン追加も容易

**トレードオフ:**
- ファイル名が長い（平均28文字）
- しかし、明確さを優先

**影響範囲:**
- [app_langchain_sync.py](../app_langchain_sync.py) - 新規作成（git履歴から復元）
- [app_langchain_streaming.py](../app_langchain_streaming.py) - リネーム
- [app_langgraph_sync.py](../app_langgraph_sync.py) - リネーム
- [README.md](../README.md) - 2×2実装マトリックス追加
- [CLAUDE.md](../CLAUDE.md) - 起動方法更新

**実装マトリックス:**
|              | LangChain                     | LangGraph                |
|--------------|-------------------------------|--------------------------|
| **Sync**     | `app_langchain_sync.py`       | `app_langgraph_sync.py`  |
| **Streaming**| `app_langchain_streaming.py`  | (Phase 2)                |

**参考資料:**
- 実装作業: Pull Request #4（コミット 8d8a651）
- 用語に関する議論: context.mdに記録

**今後の課題:**
- docker-compose.yml の更新（どの実装をデフォルトにするか）
- ディレクトリ構成の見直し（`app_*.py`が増えた場合の整理方法）

---

### LangGraphストリーミングの実装パターン - 2025-10-31

**状況・課題:**
- LangGraphで`stream_mode="messages"`を使ったトークン単位のストリーミングを実装する必要があった
- 公式ドキュメントに実装の詳細が明記されておらず、試行錯誤が必要だった
- 当初の理解が誤っており、エラーに遭遇: `Unsupported message type: <class 'async_generator'>`

**検討した選択肢:**

**1. ノード関数で`model.astream()`を直接返す（当初の誤解）:**
```python
async def call_llm(state: MessagesState):
    response = model.astream(state["messages"])  # AsyncIterator
    return {"messages": response}  # これが間違い
```
- ❌ `AsyncIterator`は`MessagesState`で受け入れられない
- ❌ エラー: `Unsupported message type: <class 'async_generator'>`
- ❌ LangGraphはメッセージオブジェクトを期待している

**2. ノード関数内で手動でトークンを収集:**
```python
async def call_llm(state: MessagesState):
    full_content = ""
    async for chunk in model.astream(state["messages"]):
        full_content += chunk.content
    return {"messages": [AIMessage(content=full_content)]}
```
- ✅ 動作する
- ❌ `stream_mode="messages"`のトークン単位ストリーミングが機能しない
- ❌ 完全なメッセージしか返せない

**3. `streaming=True` + `ainvoke()` + コールバック機構（正解）:**
```python
model = ChatOpenAI(model="gpt-5-nano", streaming=True)

async def call_llm(state: MessagesState):
    response = await model.ainvoke(state["messages"])
    return {"messages": [response]}
```
- ✅ トークン単位のストリーミングが機能する
- ✅ LangGraphのコールバック機構が自動的にトークンをキャプチャ
- ✅ シンプルで理解しやすい

**決定内容:**

選択肢3を採用：**`streaming=True` + `ainvoke()` + LangGraphのコールバック機構**

**実装の核心部分:**

```python
# 1. モデル初期化時にstreaming=Trueを設定
model = ChatOpenAI(model="gpt-5-nano", streaming=True)

# 2. ノード関数ではainvoke()を使用（astream()ではない）
async def call_llm(state: MessagesState):
    messages = state["messages"]
    response = await model.ainvoke(messages)
    return {"messages": [response]}

# 3. stream_mode="messages"の返り値はタプル
async for message, metadata in agent.astream(
    {"messages": messages},
    stream_mode="messages"
):
    if message.content:
        await msg.stream_token(message.content)
```

**理由:**

1. **`streaming=True`が必須:**
   - これがないとLangChainがコールバックを発火しない
   - LangGraphが`StreamMessagesHandler`でトークンをキャプチャできない

2. **ノード関数では`ainvoke()`を使う:**
   - ノード関数は`BaseMessage`オブジェクトを返す必要がある
   - LangGraphが内部でコールバック経由でトークンを取得する
   - `astream()`を返すと型エラーになる

3. **LangGraphのコールバック機構:**
   - `StreamMessagesHandler`が`on_llm_new_token`イベントをキャプチャ
   - トークンごとに自動的にストリーミングに変換
   - 開発者は意識する必要がない

4. **`stream_mode="messages"`の返り値:**
   - 単一モード: `(AIMessageChunk, metadata)`のタプル
   - 複数モード: `(mode, data)`のタプル
   - タプルをアンパックして処理する必要がある

**技術的な仕組み:**

```
LangChain (streaming=True)
    ↓
ainvoke()実行中にon_llm_new_tokenコールバック発火
    ↓
LangGraph (StreamMessagesHandler)がキャプチャ
    ↓
agent.astream(stream_mode="messages")でトークン単位にストリーム
    ↓
Chainlit (stream_token())でリアルタイム表示
```

**影響範囲:**
- [app_langgraph_streaming.py](../app_langgraph_streaming.py)
- 将来のLangGraph実装（Phase 2b/3）

**調査方法:**
- LangGraphのソースコード調査（`langgraph/pregel/_messages.py`）
- 実際のエラーメッセージを元に根本原因を特定
- `MessagesState`の型定義を確認

**参考資料:**
- LangGraphソースコード: `StreamMessagesHandler`クラス
- LangChainドキュメント: Streaming概念
- context.md: 詳細な調査結果

**今後の展開:**
- Phase 2b: 複数ノード + `stream_mode="updates"`（ノード単位の進捗表示）
- Phase 3: `stream_mode=["updates", "messages"]`（両方の組み合わせ）

**重要な学び:**
- 推測ではなく実際のソースコードを調査することの重要性
- 公式ドキュメントだけでは不十分なケースがある
- エラーメッセージを丁寧に読み、根本原因を特定する姿勢

---

### エラーハンドリングの実装方針 - 2025-10-30

**状況・課題:**
- 3つのアプリファイル（`app_langchain_sync.py`、`app_langchain_streaming.py`、`app_langgraph_sync.py`）にエラーハンドリングが一切なかった
- API呼び出しやセッション管理で発生するエラーがユーザーに伝わらず、アプリがクラッシュする問題
- LangChainを使用している以上、将来的に他のLLMプロバイダー（Anthropic Claude、Google Geminiなど）に切り替える可能性がある
- プロバイダー固有の例外クラス（`from openai import APIError`）に依存すると、プロバイダー変更時にコード修正が必要になる

**検討した選択肢:**

**1. プロバイダー固有の例外を個別にキャッチ:**
```python
from openai import APIError, AuthenticationError, RateLimitError
except AuthenticationError:
    # 個別処理
except RateLimitError:
    # 個別処理
```
- ❌ OpenAIに依存
- ❌ プロバイダー変更時に全コード修正が必要
- ✅ エラータイプ別に詳細な処理が可能

**2. LangChain共通例外を使用:**
- ❌ LangChainはプロバイダーの例外をラップしていない
- ❌ LangChain独自の例外は内部機能用のみ（OutputParserExceptionなど）
- LangChainの設計思想: プロバイダーの例外をそのまま発生させる

**3. 広範な `Exception` キャッチでプロバイダー非依存に:**
```python
except Exception as e:
    await cl.ErrorMessage(content=str(e)).send()
```
- ✅ プロバイダー非依存
- ✅ シンプル
- ✅ エラーメッセージはプロバイダー提供の高品質なもの
- ⚠️ エラータイプ別の処理はできない

**4. LangChainの `with_retry()` や `with_fallbacks()` を使用:**
```python
model = ChatOpenAI(...).with_retry(...)
```
- ✅ プロバイダー非依存
- ✅ 一時的なエラーに自動対応
- ⚠️ 全ての例外をリトライするため、無駄なリトライが発生する可能性

**決定内容:**
- **選択肢3を採用**: 広範な `Exception` キャッチでプロバイダー非依存
- **リトライ機能（選択肢4）は別タスク**: 優先度は低く、後で検討
- **エラーメッセージ**: プロバイダー提供の `str(e)` をそのまま使用（自分で書かない）

**実装パターン:**
```python
@cl.on_message
async def on_message(message: cl.Message):
    try:
        messages = cl.user_session.get("messages")
        if messages is None:
            await cl.ErrorMessage(
                content="Session not initialized. Please reload the page."
            ).send()
            return

        messages.append(HumanMessage(message.content))
        response = await model.ainvoke(messages)
        messages.append(AIMessage(response.content))
        await cl.Message(content=response.content).send()

    except Exception as e:
        await cl.ErrorMessage(content=str(e)).send()
```

**理由:**

1. **プロバイダー非依存:**
   - `from openai import APIError` を使わない
   - OpenAI、Anthropic、Google、ローカルモデルなど、どのプロバイダーでも動作
   - プロバイダー変更時にエラーハンドリングコードの修正不要

2. **エラーメッセージを自分で書かない:**
   - OpenAIなどのプロバイダーが提供するエラーメッセージは既に高品質
   - 実際のメッセージ例:
     - 認証エラー: "Incorrect API key provided: sk-xxxxx. You can find your API key at https://platform.openai.com/account/api-keys."
     - レート制限: "Rate limit exceeded. Please retry after 20 seconds."
     - コンテキスト長超過: "This model's maximum context length is 4096 tokens. However, your messages resulted in 5000 tokens."
   - プロフェッショナルな品質で、具体的なアクションが含まれる
   - プロバイダーがメッセージを改善すると自動的に反映される
   - メンテナンス不要

3. **シンプルさ:**
   - コード量が最小限（約15-20行の追加）
   - 各エラータイプに対して個別のメッセージを書く必要がない
   - メンテナンスコストが低い

4. **LangChainの設計思想との整合性:**
   - LangChainはプロバイダーの例外をラップせず、そのまま発生させる設計
   - `with_retry()` や `with_fallbacks()` でアプリケーション側がエラーを吸収する
   - 今回は最低限のエラーハンドリングとし、リトライは別タスク

**技術的な発見:**
- **LangChainの例外階層**: LangChainは `LangChainException` を提供するが、これはパーサーやトレーサー用
- **モデル呼び出しの例外**: `model.ainvoke()` や `model.astream()` で発生する例外は、各プロバイダーのSDKから直接発生（ラップなし）
- **プロバイダー間の類似性**: OpenAIとAnthropicは同じクラス名（`BadRequestError`、`RateLimitError`）を使用するが、異なる名前空間で互換性なし

**影響範囲:**
- [app_langchain_sync.py](../app_langchain_sync.py) - 同期版エラーハンドリング追加
- [app_langchain_streaming.py](../app_langchain_streaming.py) - ストリーミング版エラーハンドリング追加
- [app_langgraph_sync.py](../app_langgraph_sync.py) - LangGraph版エラーハンドリング追加（レスポンス構造検証も含む）

**今後の展開:**
- **リトライ機能**: `with_retry()` の導入を別タスクとして検討（優先度: 低）
- **ログ記録**: `logging` モジュールの導入を別タスクとして検討（優先度: 中）
- **テスト**: エラーケースのテスト作成を別タスクとして検討（優先度: 中）

**参考資料:**
- LangChain例外定義: `langchain_core/exceptions.py`
- LangChainリトライ実装: `langchain_core/runnables/retry.py`
- OpenAI例外定義: `openai/_exceptions.py`
- Anthropic例外定義: `anthropic/_exceptions.py`

### セッション検証について（2025-10-31 更新）

当初、`messages is None`のチェックを実装したが、実際のテストで以下が判明:

**テスト結果:**
- Chainlitはページリロード時に自動的に`@cl.on_chat_start`を再実行する
- サーバー再起動後もエラーが発生しない（Chainlitが自動的にセッションを再確立）
- 実運用で`messages is None`は極めて発生しにくい

**決定: セッション検証コードを削除**

理由:
1. **実際には発生しない**: ユーザーテストで、リロード・サーバー再起動いずれでもエラーが発生しないことを確認
2. **学習用コードの目的**: 本質的なエラーハンドリング（API呼び出しエラー）を学ぶことが目的
3. **コードのシンプルさ優先**: 本プロジェクトは学習用であり、稀にしか発生しない例外への防御的プログラミングよりもシンプルさを優先
4. **Chainlitの仕組みを信頼**: Chainlitがセッション管理を適切に行っている

削除したコード例:
```python
# 削除前
messages = cl.user_session.get("messages")
if messages is None:
    await cl.ErrorMessage(content="Session not initialized. Please reload the page.").send()
    return

# 削除後
messages = cl.user_session.get("messages")
```

**本番運用コードの場合**: 防御的プログラミングとしてこのチェックを残すことも検討に値する。ただし、学習用コードではシンプルさを優先する。

### LangGraphレスポンス検証について（2025-10-31 更新）

当初、`app_langgraph_sync.py`に以下のレスポンス検証コードを実装していました:

```python
response = await agent.ainvoke({"messages": messages})

if not response or "messages" not in response or not response["messages"]:
    await cl.ErrorMessage(
        content="Failed to get response from the model. Please try again."
    ).send()
    return
```

しかし、LangGraphのソースコード調査により、このコードが不要であることが判明したため削除しました。

**調査結果:**

1. **LangGraphの`ainvoke()`の動作:**
   - `MessagesState`を使用している場合、常に`{"messages": [...]}`の構造を返す
   - 理論上は`None`を返す可能性もあるが、現在のグラフ実装では発生しない
   - ノードが無効な値を返しても、LangGraphは「更新なし」として前の状態を返す

2. **エラー時の動作:**
   - `model.ainvoke()`が例外を投げた場合 → 外側の`try-except`でキャッチされる
   - レスポンス構造が無効になるケースは実際には発生しない

3. **MessagesStateの保証:**
   - `MessagesState`は型システムにより`"messages"`キーの存在を保証
   - LangGraphは構造検証を行わないが、状態マージの仕組みにより構造は維持される

**決定: レスポンス検証コードを削除**

理由:
1. **実際には発生しない**: 現在のグラフ実装では、レスポンス構造は常に有効
2. **学習者を混乱させる**: LangGraphが無効な構造を返すと誤解させる可能性
3. **外側のtry-exceptで十分**: 実際のエラー（モデル失敗、ネットワークエラーなど）は既にキャッチされている
4. **テスト不可能**: この検証が役立つ状況を実際に再現できない
5. **コードのシンプルさ優先**: 学習用コードでは本質的なエラーハンドリングに集中すべき

削除後のコード:
```python
response = await agent.ainvoke({"messages": messages})
last_message = response["messages"][-1].content
```

**参考:**
- LangGraphソースコード調査: `langgraph/pregel/main.py` の`ainvoke()`実装
- `MessagesState`定義: `langgraph/graph/message.py`
- エラーコード定義: `langgraph/errors.py` (INVALID_GRAPH_NODE_RETURN_VALUEは定義されているが使用されていない)

### ディレクトリ構成の決定 (apps/ ディレクトリ) - 2025-11-01

**状況・課題:**
- プロジェクトに4つの実装ファイル（LangChain/LangGraph × sync/streaming）が存在
- ルートディレクトリに `app_*.py` が散在し、プロジェクト構造が不明瞭
- docker-compose.yml が古い `app.py` を参照していた（既に存在しないファイル）
- ユーザーが簡単にアプリを切り替えられる仕組みが必要

**検討した選択肢:**

1. **Proposal A: examples/ + 深い階層**
   ```
   examples/
   ├── langchain/
   │   ├── sync.py
   │   └── streaming.py
   ├── langgraph/
   │   ├── sync.py
   │   └── streaming.py
   └── README.md
   ```
   - ❌ 階層が深い
   - ❌ ファイル名だけではフレームワークが不明

2. **Proposal B: examples/ + フラット構造**
   ```
   examples/
   ├── langchain_sync.py
   ├── langchain_streaming.py
   ├── langgraph_sync.py
   ├── langgraph_streaming.py
   └── README.md
   ```
   - ✅ シンプル
   - ✅ ファイル名から実装パターンが一目瞭然
   - ⚠️ "examples" というディレクトリ名が実態に合わない（実際に動作するアプリ）

3. **Proposal C: src/ ベースのモジュラー構造**
   ```
   src/
   ├── apps/
   ├── core/
   └── utils/
   ```
   - ✅ 将来の拡張性が高い
   - ❌ 現時点では過剰（YAGNI原則）

4. **Proposal D: チュートリアル型**
   ```
   tutorials/
   ├── 01_langchain_basic.py
   ├── 02_langchain_streaming.py
   ...
   ```
   - ❌ 実装は学習教材ではなく、実用的なアプリケーション

**決定内容:**

**Proposal B をベースに、ディレクトリ名を `apps/` に変更**

最終的な構造:
```
apps/
├── langchain_sync.py
├── langchain_streaming.py
├── langgraph_sync.py
├── langgraph_streaming.py
└── README.md
```

ファイル移動時に `app_` プレフィックスを削除:
- `app_langchain_sync.py` → `apps/langchain_sync.py`
- `app_langchain_streaming.py` → `apps/langchain_streaming.py`
- `app_langgraph_sync.py` → `apps/langgraph_sync.py`
- `app_langgraph_streaming.py` → `apps/langgraph_streaming.py`

**理由:**

1. **ディレクトリ名を `apps/` にした理由:**
   - これらのファイルは単なる例ではなく、実際に動作するアプリケーション
   - ユーザーが `docker-compose up` で直接実行する実用的なコード
   - `examples/` だと "参考例" という印象が強く、実態に合わない

2. **フラット構造を選んだ理由:**
   - ファイル数が少ない（4ファイル + README.md）
   - ファイル名から実装パターンが一目瞭然（`{framework}_{mode}.py`）
   - 階層を深くするメリットがない（YAGNI原則）
   - README.mdの数を最小限に（1つだけ）

3. **`app_` プレフィックスを削除した理由:**
   - `apps/app_langchain_sync.py` は冗長（"app" が重複）
   - ディレクトリ名で既にアプリケーションであることが明確
   - `apps/langchain_sync.py` の方が読みやすい

4. **共通コードの分離は後回し:**
   - 現時点では4つのファイルは独立している（共通化する必然性が低い）
   - 将来的に共通コードが増えた場合は `src/` ディレクトリを検討
   - todo.mdに「共通コードの分離」タスクを記録済み

**docker-compose.yml の更新:**

環境変数 `CHAINLIT_APP` でアプリを選択可能に:

```yaml
command: uv run chainlit run ${CHAINLIT_APP:-apps/langchain_streaming.py} --host 0.0.0.0
```

**環境変数のデフォルト値を相対パスにした理由:**
- ファイル名だけ（`langchain_streaming.py`）だと、ファイルの場所が不明瞭
- フルパス（`apps/langchain_streaming.py`）の方が初めて見る人にとって分かりやすい
- docker-compose.yml のコマンドと .env の設定が対応しやすい

**影響範囲:**
- [apps/](../apps/) ディレクトリ作成
- [apps/README.md](../apps/README.md) - 実装パターンの比較表
- [docker-compose.yml](../docker-compose.yml) - 環境変数対応
- [.env.example](../.env.example) - CHAINLIT_APP 設定追加
- [README.md](../README.md) - Quick Start、Development Setup 更新
- [CLAUDE.md](../CLAUDE.md) - ファイルパス更新

**参考:**
- ユーザーフィードバック: "Simple is best", "階層を深くしない", "README を増やさない"
- Git 履歴保持: `git mv` を使用してファイル履歴を維持

**今後の展開:**
- 共通コードが増えたら `src/` ディレクトリを検討（todo.md記載済み）
- アプリ数が増えても、フラット構造を維持する方針（最大10ファイル程度まで）

---

### LangGraphコードの可読性向上（明示的な型構築と変数名の改善） - 2025-11-02

**状況・課題:**
- `langgraph_sync.py`のコードは動作するが、可読性や保守性に改善の余地があった
- 辞書リテラルを直接使用していたため、型情報が不明瞭
- 変数名が汎用的で、部分更新の意図が読み取りにくい
- 関数にドキュメントがなく、LangGraphの状態管理の仕組みが分かりにくい

**検討した選択肢:**

1. **辞書リテラルを使用（現状）:**
   ```python
   agent_response = await agent.ainvoke({"messages": chat_history})
   ```
   - ❌ 型情報が不明瞭（IDEの補完が効きにくい）
   - ❌ "messages"というキーが正しいか、コードを読まないと分からない

2. **ChatStateを明示的に構築:**
   ```python
   agent_request = ChatState(messages=chat_history)
   agent_response = await agent.ainvoke(agent_request)
   ```
   - ✅ 型情報が明確（IDEの補完が効く）
   - ✅ `ChatState`の構造を意識できる
   - ✅ 変数名で意図が明確になる

**決定内容:**

**選択肢2を採用**: `ChatState`を明示的に構築し、変数名で意図を明確化

**実装内容:**

1. **明示的な型構築:**
   ```python
   # Before
   agent_response = await agent.ainvoke({"messages": chat_history})

   # After
   agent_request = ChatState(messages=chat_history)
   agent_response = await agent.ainvoke(agent_request)
   ```

2. **変数名の改善（部分更新の意図を明確化）:**
   ```python
   # Before
   async def call_llm(state: ChatState) -> ChatState:
       ai_response = await model.ainvoke(messages)
       return {"messages": [ai_response]}

   # After
   async def call_llm(state: ChatState) -> ChatState:
       """LLMを呼び出してレスポンスを生成する。

       LangGraphは返り値の辞書を現在の状態にマージ（部分更新）する。
       messagesフィールドはリストなので、新しいメッセージが追加される。
       """
       ai_response = await model.ainvoke(messages)
       state_update = {"messages": [ai_response]}
       return state_update
   ```

3. **import文の整理:**
   - 不要な`AnyMessage`のimportを削除
   - import順序を標準化（標準ライブラリ → サードパーティ → ローカル）

**理由:**

1. **可読性の向上:**
   - `agent_request` という変数名で「LLMへのリクエスト」であることが明確
   - `state_update` という変数名で「状態の部分更新」であることが明確
   - 辞書リテラルだけでは分からない意図が、変数名で表現される

2. **型安全性の向上:**
   - `ChatState(messages=chat_history)` により、IDEの型チェックが効く
   - タイポや構造ミスを早期に発見できる
   - リファクタリング時の影響範囲が明確

3. **学習用コードとしての価値:**
   - LangGraphの状態管理の仕組み（部分更新）がdocstringで説明される
   - 初学者が「なぜ辞書を返すのか」を理解しやすい
   - ベストプラクティスを示す実装例として機能する

4. **保守性の向上:**
   - 将来的にフィールドが増えても、構造が明確
   - コードレビュー時に意図が伝わりやすい
   - バグが発生したときにデバッグしやすい

**トレードオフ:**

- コード量がわずかに増える（1-2行程度）
- しかし、可読性と保守性のメリットがコストを大きく上回る

**マジックストリング対策について:**

当初はノード名やフィールド名の定数化も検討したが、以下の理由で見送り:

1. **現状は1ノードのみ**: `call_llm.__name__` で十分
2. **YAGNI原則**: 複数ノードになってから検討
3. **学習用コードのシンプルさ優先**: 過度な抽象化を避ける

将来的に複数ノードが必要になった場合は、クラスベース実装への移行を検討（todo.md記載済み）。

**影響範囲:**
- [apps/langgraph_sync.py](../apps/langgraph_sync.py)
- Pull Request: #9（feature/refactor-langgraph-sync）

**参考資料:**
- LangGraph公式ドキュメント: 状態管理とノード実装
- Python型ヒントのベストプラクティス
- 変数名の付け方（Clean Code原則）

**学び:**
- 明示的な型構築により、コードの意図が明確になる
- 変数名で「何のための変数か」を表現することが重要
- 学習用コードでは、シンプルさと明確さのバランスが大切
- docstringは単なるドキュメントではなく、設計の意図を伝える手段

**今後の方針:**
- この改善パターンを他の3ファイルに適用するかは、必要性が出てから判断
- まずは `langgraph_sync.py` で効果を確認
- 効果が高ければ、他のファイルにも適用を検討

---

### 日本語IME入力対応 Phase 2の方針変更（OSSコントリビューション → 情報共有） - 2025-11-02

**状況・課題:**
- Phase 1で custom_js による日本語IME入力問題の解決策を実装完了（PR #11）
- 当初はPhase 2として「Chainlit本体へのPR作成」を計画（優先度: 中）
- しかし、深い技術調査（[.claude/ime-investigation.md](.claude/ime-investigation.md)）の結果、OSS貢献の現実性を再評価する必要が出てきた

**検討した選択肢:**

1. **Chainlit本体へのPR作成（当初案）:**
   - Chainlitフロントエンド（React）に`onCompositionStart/End`ハンドラを追加
   - 中国語・韓国語・日本語すべてで動作確認
   - 既存Issues #2600/#2598を解決
   - **必要な作業:**
     - React controlled componentsをuncontrolled componentsに変更
     - メッセージ履歴、コマンド機能、履歴機能との整合性確保
     - 大規模なリファクタリング
   - **見積もり:** 数週間〜数ヶ月
   - ❌ Reactの根本的な制約（async setState）により、controlled componentsでのIME対応は困難
   - ❌ Chainlit maintainersの優先度が低い（Issues #2600/#2598が2年以上オープン）
   - ❌ React team自体が8年以上IME問題を修正していない（Issues #8683/#3926）

2. **custom_jsアプローチのままで終了:**
   - Phase 1の実装で十分に動作している
   - 追加作業なし
   - ❌ 同じ問題に悩む他のユーザーを助けられない
   - ❌ 調査で得た知見が埋もれてしまう

3. **GitHub Issuesでの情報共有（新提案）:**
   - Chainlit Issues #2600（中国語IME）と#2598（韓国語IME）にコメント投稿
   - custom_jsによる解決策を共有
   - Classi技術ブログへのリンクを提供
   - ime-investigation.mdの主要な知見を要約
   - **必要な作業:**
     - GitHub Issueコメントの下書き作成
     - 英語でのコメント投稿
     - custom_jsコードとconfig.toml設定の共有
   - **見積もり:** 30分
   - ✅ 同じ問題に悩む他のユーザーを助けられる
   - ✅ Chainlit maintainersにも情報提供できる
   - ✅ OSSコミュニティへの貢献（情報共有という形）
   - ✅ 現実的な時間投資

**決定内容:**

**選択肢3を採用**: GitHub Issuesでの情報共有に変更

- **スコープ変更:**
  - FROM: "OSSコントリビューション（Chainlit本体への修正PR）"
  - TO: "コミュニティへの情報共有（GitHub Issueコメント）"
- **優先度変更:**
  - FROM: 優先度: 中
  - TO: 優先度: 低（アイデア）
- **タスク内容:**
  - Chainlit Issues #2600と#2598にコメント投稿
  - custom_jsアプローチとClassi技術ブログへのリンクを共有
  - ime-investigation.mdの主要な知見を要約
  - PRは作成しない（現実的でないため）

**理由:**

1. **React制約の根本性:**
   - React controlled componentsの async setState がIME対応の根本的な障壁
   - Reactチームが8年以上修正していない問題（Issues #8683, #3926）
   - Chainlitがuncontrolled componentsに移行するのは非現実的（大規模リファクタ必要）

2. **Chainlit既存コードの制約:**
   - Chainlitは既に`onCompositionStart/End`を実装しているが機能していない
   - React controlled componentsの制約により、イベントハンドラが効かない
   - custom_jsのような外部アプローチでしか解決できない

3. **調査の結果明らかになった事実:**
   - custom_jsが**唯一の現実的な解決策**
   - イベントキャプチャフェーズでReactより先にブロックする方法のみ有効
   - Classi開発者も同じアプローチを採用（Google Meetで実績あり）

4. **コストとベネフィットのバランス:**
   - PRアプローチ: 数週間〜数ヶ月の作業 + 大規模リファクタ + メンテナンスの複雑化
   - 情報共有アプローチ: 30分の作業 + 同じ問題に悩む他のユーザーを即座に助ける
   - 情報共有でも十分にOSSコミュニティに貢献できる

5. **実用性優先:**
   - 完璧なPRを作成するよりも、実用的な解決策を共有する方が価値が高い
   - 中国語・韓国語ユーザーも同じ問題で困っている（Issues #2600/#2598）
   - 情報共有により、他のユーザーがすぐに問題を解決できる

**影響範囲:**
- [.claude/todo.md](.claude/todo.md) - Phase 2タスクの再定義
- [.claude/ime-investigation.md](.claude/ime-investigation.md) - 包括的な技術調査ドキュメント（既存）
- 将来の情報共有アクション: GitHub Issues #2600/#2598へのコメント投稿

**参考資料:**
- [.claude/ime-investigation.md](.claude/ime-investigation.md) - 1,000行以上の技術調査
- Chainlit Issue #2600: https://github.com/Chainlit/chainlit/issues/2600
- Chainlit Issue #2598: https://github.com/Chainlit/chainlit/issues/2598
- React Issue #8683: https://github.com/facebook/react/issues/8683
- React Issue #3926: https://github.com/facebook/react/issues/3926
- Classi技術ブログ: https://tech.classi.jp/entry/2024/04/23/183000

**学び:**
- OSSコントリビューションは「PR作成」だけではない
- 情報共有、ドキュメント作成、Issue報告もコミュニティへの重要な貢献
- 現実的なアプローチを選ぶことで、より多くのユーザーを助けられる
- 深い技術調査の価値は、その知見を共有することで最大化される
- React controlled componentsとIME入力の相性問題は業界全体の課題

**今後のアクション（オプション）:**
- 時間がある時にGitHub Issues #2600/#2598にコメント投稿
- custom_jsアプローチを簡潔に説明
- Classi技術ブログと本プロジェクトのime-investigation.mdを紹介
- 他の言語（中国語・韓国語）でも同じアプローチが有効であることを示す

---

### streaming=True でsync/streaming両バージョン対応 - 2025-11-03

**状況・課題:**
- LangGraphのsync版とstreaming版で異なるmodel設定が必要
  - sync版: `ChatOpenAI(model="gpt-5-nano", streaming=False)` （デフォルト）
  - streaming版: `ChatOpenAI(model="gpt-5-nano", streaming=True)` （必須）
- ノード関数を共通化したいが、model設定が異なるため難しい
- 選択肢: ①共通化を諦める ②modelを引数で渡す ③Agentクラスパターン ④streaming=Trueで統一

**検討した選択肢:**
1. **共通化を諦める**: 各アプリに`call_llm`を直接書く
   - メリット: シンプル
   - デメリット: DRY違反（10行程度の重複）

2. **modelを引数で渡す**: `call_llm(state, model)`
   - メリット: DRY原則を守る
   - デメリット: lambdaが必要、`call_llm.__name__`が使えない

3. **Agentクラスパターン**: 依存性注入
   - メリット: エレガント、テストしやすい
   - デメリット: 複雑、将来のタスクとして検討

4. **streaming=Trueで統一**: 両バージョンで同じmodel設定
   - メリット: シンプルでDRYも達成
   - 懸念: sync版で問題が起きないか？

**決定内容:**
**選択肢4を採用**: `ChatOpenAI(streaming=True)` で統一し、両バージョンで使用

```python
# src/ai_agent_demo/node/simple_chat.py
async def call_llm(state: ChatState) -> dict:
    model = ChatOpenAI(model="gpt-5-nano", streaming=True)  # ← 常にTrue
    response = await model.ainvoke(state.messages)
    return {ChatState.MESSAGES: [response]}
```

**理由:**
1. **実験により安全性を確認**
   - sync版（`ainvoke()`）でも `streaming=True` で問題なく動作
   - コールバックは発火するが、誰も聞いていないため無視される
   - パフォーマンス影響は微小（コールバックのオーバーヘッドのみ）

2. **LangGraphの仕組み**
   - streaming版: `agent.astream(stream_mode="messages")` でLangGraphがコールバックをキャプチャ
   - sync版: `agent.ainvoke()` ではコールバックをキャプチャしない（無視される）

3. **DRY原則の達成**
   - 両バージョンで同じノード関数を使える
   - 過度な抽象化を避けつつ、コード重複を解消

4. **将来の拡張性**
   - 後でAgentクラスパターンに移行しやすい
   - シンプルな実装から始めて、必要に応じて洗練

**影響範囲:**
- `src/ai_agent_demo/node/simple_chat.py` - call_llm実装
- `apps/langgraph_sync.py` - sync版アプリ
- `apps/langgraph_streaming.py` - streaming版アプリ

**トレードオフ:**
- ✅ シンプルさとDRYの両立
- ✅ 実用上問題ないパフォーマンス
- ⚠️ sync版で不要なコールバック処理が発生（微小なオーバーヘッド）
- ⚠️ 意図が分かりにくい可能性（コメントで補足）

**検証方法:**
1. sync版で動作確認: `uv run chainlit run apps/langgraph_sync.py`
2. streaming版で動作確認: `uv run chainlit run apps/langgraph_streaming.py`
3. 両方で正常動作を確認

**学び:**
- `streaming=True` は「ストリーミング可能にする」フラグであり、必ずストリーミングするわけではない
- LangGraphのコールバック機構は柔軟で、聞き手がいない場合は無視される
- 実際に試してみることの重要性（当初は不安だったが、動作確認で安全性を確認）
- シンプルな解決策が最良であることが多い

**今後の展望:**
- 将来的にはAgentクラスパターンへの移行を検討（todo.md参照）
- 複数ノードを扱う場合は、より洗練されたアーキテクチャが必要になる可能性
- 現時点ではこのシンプルなアプローチで十分

**参考:**
- [.claude/context.md](context.md) - 技術的な学びセクション
- [.claude/todo.md](todo.md) - Agentクラスパターンへの移行タスク

---

### ディレクトリ構成: エージェント名優先 - 2025-11-03

**状況・課題:**
- `src/ai_agent_demo/` 配下のディレクトリ構成をどうするか
- 当初は機能別（`state/`, `node/`, `agent/`）で実装していた
- 将来的に複数のエージェントを実装する予定

**検討した選択肢:**
1. **機能別（当初の設計）:**
   ```
   src/ai_agent_demo/
   ├── state/
   │   └── simple_chat.py
   ├── node/
   │   └── simple_chat.py
   └── agent/
       └── simple_chat.py
   ```
2. **エージェント名優先（採用）:**
   ```
   src/ai_agent_demo/
   └── simple_chat/
       ├── state.py
       ├── node.py
       └── agent.py
   ```

**決定内容:**
- **エージェント名を最上位**に配置する構成を採用

**理由:**
1. **高い凝集度**: 1つのエージェントに関連するコード（state, node, agent）が1箇所にまとまる
2. **削除が容易**: エージェント単位でディレクトリごと削除できる
3. **依存関係が明確**: エージェント間の依存が見えやすい
4. **理解しやすい**: 「このエージェントは何をするのか」という単位で把握できる
5. **スケーラブル**: 新しいエージェントを追加する際、単に新しいディレクトリを作るだけ

**トレードオフ:**
- 共通コードの扱いが課題になる可能性があるが、現時点では `simple_chat` 専用で問題なし
- 将来的に共通コードが必要になったら `common/` ディレクトリを追加すれば良い（YAGNI原則）

**影響範囲:**
- [src/ai_agent_demo/simple_chat/](../src/ai_agent_demo/simple_chat/) - 新しいディレクトリ構成
- [apps/langgraph_sync.py](../apps/langgraph_sync.py) - インポートパス変更
- [apps/langgraph_streaming.py](../apps/langgraph_streaming.py) - インポートパス変更

**関連決定:**
- [共通コードの分離範囲](#共通コードの分離範囲--2025-11-03)（下記）

---

### 共通コードの分離範囲 - 2025-11-03

**状況・課題:**
- todo.mdでは `load_chat_history()`, エラーハンドリング, モデル初期化の共通化も計画していた
- どこまで共通化すべきか？

**検討した選択肢:**
1. **todo.mdの計画通り完全実装:**
   - `src/chat/history.py` - load_chat_history()
   - `src/chat/handlers.py` - エラーハンドリング
   - `src/chat/models.py` - モデル初期化
2. **コアのみ共通化（採用）:**
   - ChatState, call_llm, create_agent のみ
3. **すべて共通化しない:**
   - 各アプリで独自実装を維持

**決定内容:**
- **LangGraphのコア部分のみを共通化**し、以下は意図的に見送る：
  - `load_chat_history()` - 各アプリに残す
  - エラーハンドリング - 各アプリに残す
  - モデル初期化 - `call_llm` 内で実装（暫定）

**理由:**

**共通化したもの（必要性が高い）:**
- ✅ **ChatState**: LangGraphの中核、完全に共通
- ✅ **call_llm**: ビジネスロジック、`streaming=True`で両対応可能
- ✅ **create_agent**: グラフ構築ロジック、完全に共通

**共通化しなかったもの（YAGNI原則）:**
- ❌ **load_chat_history()**:
  - Chainlit依存が強い（`cl.user_session`）
  - チェックポイント機構導入後に不要になる可能性が高い
  - 各アプリで10行程度、過度な抽象化を避ける
- ❌ **エラーハンドリング**:
  - 各アプリで3-4行程度（`try-except-raise`）
  - 共通化しても削減効果が少ない
  - アプリ固有のエラー処理が必要になる可能性
- ❌ **モデル初期化**:
  - Agentクラスパターン導入時に対応予定（優先度低）
  - 現在は `call_llm` 内で実装（暫定対応）

**影響範囲:**
- [src/ai_agent_demo/simple_chat/](../src/ai_agent_demo/simple_chat/) - 共通化されたコード
- [apps/langgraph_sync.py](../apps/langgraph_sync.py) - Chainlit依存部分は残る
- [apps/langgraph_streaming.py](../apps/langgraph_streaming.py) - Chainlit依存部分は残る

**成果:**
- コード削減: 合計52行削減（各アプリ26行×2）
- DRY原則: 重複コードの完全排除
- シンプルさ維持: 学習用コードとして適切なバランス

**将来の対応:**
- チェックポイント機構導入後に `load_chat_history()` を再検討
- Agentクラスパターン導入時にモデル初期化を対応

**参考:**
- Pull Request #12: "Extract LangGraph common code and reorganize by agent"
- [.claude/todo.md](todo.md) - LangGraphチェックポイント機構、Agentクラスパターン
