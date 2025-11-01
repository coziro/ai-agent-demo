# References (参考資料)

このファイルには、プロジェクトに関連する重要なリンク、ドキュメント、参考資料を集約します。

**最終更新:** 2025-11-01

---

## ファイル管理方針

**このファイルの特性:** 長期的な参考資料の集約（増加傾向）

### リンク追加の判断基準

**✅ 追加すべきリンク:**
- **外部の質の高いリソース**（Real Pythonのチュートリアルなど）
- **統合ガイド**（異なるツール間の連携方法）
- **見つけにくい重要な情報**（公式ドキュメントに埋もれている情報）
- **頻繁に参照するツールの公式ドキュメント**（開発で日常的に使うツール）

**❌ 追加すべきでないリンク:**
- **公式ドキュメント内の個別ページ**（Quickstart、Installation、API Referenceなど）
  - 理由: 公式サイトのナビゲーションから簡単にアクセスできる
- **バージョン管理されていない古いドキュメント**
  - 必ず最新バージョン（v1.0など）のドキュメントを参照する
  - 古いドキュメントへの警告は不要（公式サイトに既に表示されている）
- **頻繁に変更される情報**（リンク切れのリスクが高い）

### 公式ドキュメントセクションのルール

各ツール・フレームワークについて、以下のみを記載：
- **公式ドキュメント（トップページ）**: 必須
- **GitHub リポジトリ**: 必須
- **PyPI（該当する場合）**: オプション

個別ページ（QuickstartやAPI Referenceなど）は記載しない。

### メンテナンスガイドライン

- **古くなったリンク**: 定期的にリンク切れをチェックし、削除または更新
- **重複**: 同じ内容のリンクは統合
- **整理**: カテゴリが増えすぎたら、サブカテゴリを作成
- **最終更新日**: リンクを追加・削除したら日付を更新

### サイズ管理

- **500行を超えたら**: カテゴリ別にファイル分割を検討
  - 例: `.claude/references-llm.md`, `.claude/references-deployment.md`
- **原則**: よく使うリンクにすぐアクセスできる構造を保つ

**YAGNI原則の適用:**
現時点ではファイル分割は行っていません。必要になってから対応します。

---

## 公式ドキュメント

### Chainlit
- **公式ドキュメント:** https://docs.chainlit.io/
- **GitHub:** https://github.com/Chainlit/chainlit

### LangChain (v1.0)
- **公式ドキュメント (v1.0):** https://docs.langchain.com/oss/python/langchain/overview
- **GitHub:** https://github.com/langchain-ai/langchain

### LangGraph (v1.0)
- **公式ドキュメント (v1.0):** https://docs.langchain.com/oss/python/langgraph/overview
- **GitHub:** https://github.com/langchain-ai/langgraph
- **PyPI:** https://pypi.org/project/langgraph/

### uv (Python パッケージマネージャー)
- **公式ドキュメント:** https://docs.astral.sh/uv/
- **GitHub:** https://github.com/astral-sh/uv

### Ruff (Linter/Formatter)
- **公式ドキュメント:** https://docs.astral.sh/ruff/
- **GitHub:** https://github.com/astral-sh/ruff

### Python
- **Python 3.12 ドキュメント:** https://docs.python.org/3.12/

---

## チュートリアル・ガイド


### LLM統合
- [OpenAI API ドキュメント](https://platform.openai.com/docs/)
- [Anthropic API ドキュメント](https://docs.anthropic.com/)
- [LlamaIndex ドキュメント](https://docs.llamaindex.ai/)

### LangChain関連 (v1.0)
- [LangChain + Chainlit Integration](https://docs.chainlit.io/integrations/langchain) - Chainlitとの統合ガイド

### LangGraph関連 (v1.0)
- [Real Python: Build Stateful AI Agents](https://realpython.com/langgraph-python/) - LangGraphの詳細チュートリアル (追加日: 2025-10-27)
- [現場で活用するためのAIエージェント実践入門 (GitHub)](https://github.com/masamasa59/genai-agent-advanced-book/tree/main) - LangGraphの実装例が豊富 (追加日: 2025-10-30)
- [LangAcademy - Quickstart: LangGraph Essentials - Python](https://academy.langchain.com/courses/langgraph-essentials-python) - LangChain公式のLangGraphコース (追加日: 2025-10-30)

**v1.0の重要な変更点:**
- メッセージ履歴は `TypedDict` の `Annotated[list[AnyMessage], operator.add]` で管理
- ストリーミングは `stream_mode="updates"` または `stream_mode="messages"` を使用
- Functional APIとGraph APIの2つのアプローチが提供される

### 日本語IME対応（国際化）
- [Qiita: Chainlitの日本語入力で変換途中にEnterを押すとメッセージ送信されてしまう](https://qiita.com/bohemian916/items/4f3e860904c24922905a) - Chainlit特有の回避策 (追加日: 2025-10-25)
- [MDN: compositionstart event](https://developer.mozilla.org/en-US/docs/Web/API/Element/compositionstart_event) - Web標準のIME処理
- [Handling IME events in JavaScript](https://www.stum.de/2016/06/24/handling-ime-events-in-javascript/) - IMEイベント処理の詳細解説
- [Understanding Composition Browser Events](https://developer.squareup.com/blog/understanding-composition-browser-events/) - Squareによるベストプラクティス
- [Stack Overflow: Detecting IME input](https://stackoverflow.com/questions/7316886/detecting-ime-input-before-enter-pressed-in-javascript) - コミュニティの知見

---

## プロジェクト特有の資料

### 内部ドキュメント
- [CLAUDE.md](../CLAUDE.md) - プロジェクトの全体ガイド
- [decisions.md](decisions.md) - 設計の決定事項
- [context.md](context.md) - 現在の作業コンテキスト
- [todo.md](todo.md) - タスク管理

### 設定ファイル
- [pyproject.toml](../pyproject.toml) - Python依存関係
- [.chainlit/config.toml](../.chainlit/config.toml) - Chainlit設定
- [.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json) - DevContainer設定

---

## コード例・スニペット

### Chainlitの基本パターン

#### シンプルなメッセージハンドラ
```python
import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content=f"受信: {message.content}").send()
```

#### LangChain統合（シンプルなチャット）
```python
import chainlit as cl
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

#### ストリーミングレスポンス（LangChain + Chainlit）
```python
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    # 最初の send() は不要（ローディング表示を維持）

    full_response = ""
    async for chunk in model.astream([HumanMessage(message.content)]):
        if chunk.content:
            await msg.stream_token(chunk.content)
            full_response += chunk.content

    await msg.send()  # 最後に呼んで完了を通知（カーソル消去、コピーボタン表示）
```

**重要な注意点:**
- `astream()` は非同期ジェネレーターを返すため、`async for` が必要
- `chunk.content` を使用（`.text` は非推奨）
- 最初の `send()` は不要（`stream_token()` 初回呼び出し時に自動表示開始）
- 最後の `send()` は必須（ストリーミング完了を通知、UI状態を更新）

### LangGraph v1.0の基本パターン

#### 状態の定義（TypedDict）
```python
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
import operator

class MessagesState(TypedDict):
    """会話履歴を保持する状態クラス"""
    messages: Annotated[list[AnyMessage], operator.add]
```

**ポイント:**
- `Annotated[list[AnyMessage], operator.add]` により、新しいメッセージが既存のリストに追加される
- `operator.add` は状態の更新方法を指定（リストの結合）

#### シンプルなグラフの作成（Graph API）
```python
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI

# LLMモデルの初期化
model = ChatOpenAI(model="gpt-5-nano")

# ノード関数の定義
def call_model(state: MessagesState):
    """LLMを呼び出してレスポンスを生成"""
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# グラフの構築
graph_builder = StateGraph(MessagesState)
graph_builder.add_node("model", call_model)
graph_builder.set_entry_point("model")
graph_builder.set_finish_point("model")

# グラフのコンパイル
graph = graph_builder.compile()
```

#### ストリーミングの実装（Graph API）
```python
# stream_mode="updates" でノードごとの更新を取得
for chunk in graph.stream(
    {"messages": [{"role": "user", "content": "Hello!"}]},
    stream_mode="updates"
):
    print(chunk)
```

**利用可能なstream modes:**
- `"values"`: 各ステップ後の完全な状態
- `"updates"`: 各ノードからの更新のみ
- `"messages"`: LLMトークンの逐次ストリーミング（LangChain統合時）

### 日本語IME対応パターン

#### Web標準のComposition Events（理想的な実装）
```javascript
// モダンブラウザ向けのシンプルな実装
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.isComposing) {
    submit(); // IME変換中でなければ送信
  }
});

// React等のフレームワークでの実装
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

#### ブラウザ間の差異対応
```javascript
// ブラウザ間の差異を考慮した実装
let isComposing = false;
let hasCompositionJustEnded = false;

input.addEventListener('compositionstart', () => {
  isComposing = true;
});

input.addEventListener('compositionend', () => {
  isComposing = false;
  hasCompositionJustEnded = true;
});

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !isComposing) {
    if (hasCompositionJustEnded) {
      // Chrome/Edge: compositionend直後のkeydownは無視しない
      hasCompositionJustEnded = false;
    }
    submit();
  }
  // Safari対策: keyCode 229 は無視
  if (e.which !== 229) {
    hasCompositionJustEnded = false;
  }
});
```

---

## トラブルシューティング

### よくある問題と解決策

#### uv sync が失敗する
```bash
# キャッシュをクリアして再試行
uv cache clean
uv sync
```

#### Chainlitが起動しない
```bash
# ポート8000が使用中の場合、別のポートを指定
uv run chainlit run app.py --port 8001
```

---

## コミュニティ・サポート

### Chainlit
- **Discord:** https://discord.gg/chainlit
- **GitHub Issues:** https://github.com/Chainlit/chainlit/issues

---

## 新しい参考資料を追加する際のガイドライン

1. **適切なセクションに追加**
2. **リンクの説明を簡潔に**
3. **日付を記録**（いつ追加したか）
4. **定期的にリンク切れをチェック**

例：
```markdown
- [タイトル](URL) - 簡単な説明 (追加日: 2025-01-XX)
```
