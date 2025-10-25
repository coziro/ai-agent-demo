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

**決定内容（暫定）:**
- **MVP後にQiitaの回避策を実装**（現実的な選択）
- 理由: すぐに動作し、ユーザー体験を改善できる
- 将来的な選択肢: Chainlitに貢献、または独自UIの検討

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
