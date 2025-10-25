# References (参考資料)

このファイルには、プロジェクトに関連する重要なリンク、ドキュメント、参考資料を集約します。

**最終更新:** 2025-10-25

---

## ファイル管理方針

**このファイルの特性:** 長期的な参考資料の集約（増加傾向）

**メンテナンスガイドライン:**
- **古くなったリンク**: 定期的にリンク切れをチェックし、削除または更新
- **重複**: 同じ内容のリンクは統合
- **整理**: カテゴリが増えすぎたら、サブカテゴリを作成

**サイズ管理:**
- **500行を超えたら**: カテゴリ別にファイル分割を検討
  - 例: `.claude/references-llm.md`, `.claude/references-deployment.md`
- **原則**: よく使うリンクにすぐアクセスできる構造を保つ

**YAGNI原則の適用:**
現時点ではファイル分割は行っていません。必要になってから対応します。

---

## 公式ドキュメント

### Chainlit
- **公式ドキュメント:** https://docs.chainlit.io/
- **API リファレンス:** https://docs.chainlit.io/api-reference/overview
- **Examples:** https://docs.chainlit.io/examples/community
- **GitHub:** https://github.com/Chainlit/chainlit

### uv (Python パッケージマネージャー)
- **公式ドキュメント:** https://docs.astral.sh/uv/
- **GitHub:** https://github.com/astral-sh/uv

### Python
- **Python 3.12 ドキュメント:** https://docs.python.org/3.12/

---

## チュートリアル・ガイド

### Chainlit関連
- [Chainlit Quickstart](https://docs.chainlit.io/get-started/overview)
- [Building a Chatbot](https://docs.chainlit.io/guides/chatbot)
- [Streaming Responses](https://docs.chainlit.io/concepts/streaming)
- [File Upload](https://docs.chainlit.io/concepts/file-upload)
- [Authentication](https://docs.chainlit.io/authentication/overview)

### LLM統合
- [OpenAI API ドキュメント](https://platform.openai.com/docs/)
- [Anthropic API ドキュメント](https://docs.anthropic.com/)
- [LangChain ドキュメント](https://python.langchain.com/docs/get_started/introduction)
- [LangChain Models](https://docs.langchain.com/oss/python/langchain/models) - モデル統合のガイド
- [LlamaIndex ドキュメント](https://docs.llamaindex.ai/)

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

#### ストリーミングレスポンス
```python
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()

    for chunk in generate_response(message.content):
        await msg.stream_token(chunk)

    await msg.update()
```

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

## ツール・リソース

### 開発ツール
- **VS Code Extensions:**
  - Python (ms-python.python)
  - Jupyter (ms-toolsai.jupyter)
  - Claude Code (anthropics.claude-code)

### 便利なコマンド
```bash
# 依存関係の更新
uv lock --upgrade

# 仮想環境のアクティベート（必要な場合）
source .venv/bin/activate

# Jupyter Notebookサーバー起動
jupyter notebook
```

---

## 関連記事・ブログ

追加予定

---

## コミュニティ・サポート

### Chainlit
- **Discord:** https://discord.gg/chainlit
- **GitHub Issues:** https://github.com/Chainlit/chainlit/issues

---

## カテゴリ別インデックス

### 認証関連
- まだ実装していません

### データベース関連
- まだ実装していません

### デプロイ関連
- まだ実装していません

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
