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

---

## 次に決めるべきこと

このセクションには、**まだ決定していない重要な設計判断**を記録します。
決定したら上の「決定事項の記録」セクションに移動してください。

### 近いうちに決めるべきこと

- [ ] **LLMプロバイダーの選定** - ChainlitアプリにLLMを統合する際に必要
  - 選択肢: OpenAI / Anthropic / Azure OpenAI / ローカルモデル（Ollama等）
  - 検討ポイント: コスト、日本語性能、レイテンシ、プライバシー
  - 影響: app.py、環境変数、依存関係

### 将来的に決めるべきこと

- [ ] **認証・認可方式** - 本番環境でユーザー管理が必要になった場合
  - 選択肢: OAuth、JWT、Chainlit組み込み認証

- [ ] **データ永続化方式** - チャット履歴や会話データを保存する場合
  - 選択肢: PostgreSQL、SQLite、クラウドDB

- [ ] **ベクトルDBの選定** - RAG（文書検索）機能が必要になった場合
  - 選択肢: Chroma、Pinecone、Weaviate、Qdrant

- [ ] **デプロイ方法** - 本番環境への公開方法
  - 選択肢: Docker Compose、Cloud Run、Heroku、Railway
