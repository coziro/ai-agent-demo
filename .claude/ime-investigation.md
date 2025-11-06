# IME入力問題の調査報告

**調査日**: 2025-11-02
**対象**: Chainlit 2.8.3におけるIME変換中のEnterキー誤送信問題
**環境**: Chrome/Safari on macOS
**最終更新**: 2025-11-06（Chainlit 2.8.4で公式修正完了）

---

## ✅ 解決済み（2025-11-06更新）

**Chainlit 2.8.4で公式修正が入り、この問題は完全に解決しました。**

### 修正内容（PR #2575）

**根本原因**:
- PR #2393で`contentEditable` → `<textarea>`移行時、`AutoResizeTextarea`コンポーネントが composition events を親コンポーネント（Input.tsx）に伝播していなかった
- そのため、`Input.tsx`の`isComposing`状態が常に`false`のままだった

**修正方法**:
- `AutoResizeTextarea`に`onCompositionStart`/`onCompositionEnd`プロパティを追加
- 子コンポーネントから親コンポーネントへのイベント伝播を実装
- これにより、`Input.tsx`の`isComposing`状態が正しく更新されるようになった

**検証結果（2025-11-06）**:
- ✅ Chrome on macOS: IME変換中のEnter → 変換確定（送信されない）
- ✅ Safari on macOS: IME変換中のEnter → 変換確定（送信されない）
- ✅ 変換確定後のEnter → メッセージ送信
- ✅ 英語入力でEnter → メッセージ送信
- ✅ Shift+Enter → 改行

**結論**:
- Chainlit 2.8.4以降では、custom.jsによる回避策は不要
- 公式修正により、Reactコンポーネント階層内で正しく解決された
- 以前の調査で「Reactの根本的な問題」と判断したのは誤りで、実際は「AutoResizeTextareaの実装バグ」だった

**参考**:
- [Chainlit PR #2575](https://github.com/Chainlit/chainlit/pull/2575)
- [Chainlit Release 2.8.4](https://github.com/Chainlit/chainlit/releases/tag/2.8.4)

---

## 以下は2.8.3時点での調査記録（アーカイブ）

---

## 概要

### 問題の発見

Chainlitアプリケーションで日本語入力（IME使用）時、変換確定のためのEnterキー押下が意図せずメッセージ送信として処理されてしまう問題が発生。

### 調査範囲

- Chainlit内部実装の分析（Input.tsx）
- Reactの既知の問題調査（Issue #8683, #3926）
- ブラウザ・OSレベルのIME実装調査
- 解決策の技術的検証

### 使用環境

- **Chainlitバージョン**: 2.8.3
- **Python**: 3.12
- **パッケージマネージャ**: uv
- **ブラウザ**: Chrome, Safari（両方で問題発生確認済み）
- **OS**: macOS

---

## 1. 問題の詳細

### 1.1 現象

**症状**:
- 日本語入力時、IME変換中にEnterキーを押すと、変換確定ではなくメッセージが送信される
- 例: 「こんにちは」と入力したいのに、変換途中で送信されて「こんにちわ」のような中途半端な状態で送られる

**再現条件**:
1. Chainlitチャット入力欄で日本語入力モードをON
2. ローマ字入力（例: "konnichiwa"）
3. IME変換候補が表示されている状態でEnterキーを押す
4. 変換確定ではなく、メッセージ送信が実行される

### 1.2 影響範囲

#### ブラウザ別
- ✅ **Chrome on Mac**: 問題発生
- ✅ **Safari on Mac**: 問題発生
- ❓ **Firefox on Mac**: 未検証（同様の問題が発生する可能性高）
- ❓ **Windows環境**: 問題発生の報告は少ない（macOS特有の可能性）

#### 言語別
- ✅ **日本語**: 問題確認済み
- ❓ **中国語**: 未検証（同様の問題が発生する可能性高）
- ❓ **韓国語**: 未検証（同様の問題が発生する可能性高）

### 1.3 ユーザー影響

- 日本語話者がスムーズに入力できない
- UX（ユーザー体験）の著しい低下
- 欧米中心で開発されたWebサービスでよく見られる問題

#### 同様の問題が発生した主要サービス

**Google Meet**:
- チャット機能で日本語入力時にEnter誤送信が発生
- ユーザーからの報告多数
- Classi開発者ブログで対策方法が紹介された（2024年4月）

**ChatGPT**:
- メッセージ入力欄で同様の問題
- IME変換中のEnter送信により、中途半端なメッセージが送られる

**その他のWebサービス**:
- Slack、Discord、Teamsなどのメッセージングアプリ
- 多くのサービスで同様の問題が報告されている
- 欧米中心の開発チームでは、IME入力のテストが不足しがち

#### 問題の深刻さ

この問題は単なる「不便」ではなく、以下の理由から**深刻なUX問題**として認識すべき：

1. **入力の基本動作が壊れている** - ユーザーが意図した通りに入力できない
2. **回避策がない** - ユーザー側での対処が困難
3. **頻度が高い** - 日本語入力では必ずIMEを使用するため、常に問題が発生
4. **プロフェッショナルな印象の低下** - サービス全体の品質が疑われる

---

## 2. 技術的調査

### 2.1 Chainlit内部実装の分析

#### ファイル構造

Chainlitのフロントエンドは以下の構成：

```
chainlit/frontend/
└── src/
    └── components/
        └── chat/
            └── MessageComposer/
                ├── Input.tsx              ← メイン入力コンポーネント
                ├── SubmitButton.tsx
                └── index.tsx
```

**GitHub URL**: https://github.com/Chainlit/chainlit/blob/main/frontend/src/components/chat/MessageComposer/Input.tsx

#### Input.tsxの実装内容

**重要な発見**: Chainlit 2.8.3には**既にIME対応コードが実装されている**

```typescript
// frontend/src/components/chat/MessageComposer/Input.tsx（抜粋）

const [isComposing, setIsComposing] = useState(false);

// IME変換開始
const handleCompositionStart = () => {
  setIsComposing(true);
};

// IME変換終了
const handleCompositionEnd = () => {
  setIsComposing(false);
};

// Enterキー処理
const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
  if (
    e.key === 'Enter' &&
    !e.shiftKey &&
    onEnter &&
    !isComposing &&        // ← IME変換中はfalse
    !showCommands
  ) {
    e.preventDefault();
    onEnter();             // メッセージ送信
  }
};

return (
  <textarea
    onKeyDown={onKeyDown}
    onCompositionStart={handleCompositionStart}
    onCompositionEnd={handleCompositionEnd}
    // ...
  />
);
```

**実装の意図**:
- `isComposing`状態でIME変換中を追跡
- 変換中（`isComposing === true`）はEnterキー送信を抑制
- 理論上は正しい実装

#### なぜ機能しないのか？

**問題点**:
1. **Reactの状態更新の非同期性**
   - `setIsComposing(false)`は非同期で更新される
   - `onKeyDown`実行時、まだ古い値を参照している可能性

2. **ブラウザのイベント発火順序**
   - Safari: `keydown` → `compositionend`（逆順）
   - `keydown`時点で`compositionend`が未発火のため判定不能

3. **Reactの合成イベントシステム**
   - バブリングフェーズで処理される
   - ネイティブイベントとのタイミングずれ

### 2.2 Reactの既知の問題

#### React Issue #8683: Composition Events problem in controlled components

**URL**: https://github.com/facebook/react/issues/8683

**問題内容**:
- IME使用時、Reactの制御コンポーネントで`onChange`イベントが過剰に発火
- ブラウザ間でイベント発火順序が異なる（**3種類以上の異なるパターン**）
- 検索・フィルタ機能が誤作動する

**Reactチームの見解**:
- Issue #3926の重複として認識
- **現在もOPEN（未解決）**
- 「優先度が高くない」とコメント

#### React Issue #3926: Change event fires extra times before IME composition ends

**URL**: https://github.com/facebook/react/issues/3926

**問題内容**:
- IME変換中に`change`イベントが意図せず発火
- 提案: `compositionstart`と`compositionend`の間の`input`イベントを無視

**現状**:
- プルリクエスト（#8438）は作成されたが、マージされていない
- **Issue は現在もOPEN（未解決）**
- IE11/Edgeでは`compositionend`後に`input`イベントが発火しない問題あり

**重要な結論**:
> Reactフレームワーク自体が、IME入力に関する完全な解決策を持っていない

### 2.3 ブラウザ・OSレベルの問題

#### イベント発火パターンの違い（3種類）

##### パターンA: Chrome 53以降（macOS）
```
1. compositionstart
2. input (onChange発火)          ← 変換途中でも発火
3. compositionupdate
4. input (onChange発火)          ← 変換途中でも発火
5. compositionend
6. input (onChange発火)
```

##### パターンB: Safari（macOS）
```
1. compositionstart
2. keydown (Enter)               ← ここで判定！
3. compositionend                ← keydownの後（遅い）
```

**問題**: `keydown`時点で`compositionend`が未発火のため、IME状態を正確に判定できない

##### パターンC: iOS Safari
```
1. input (onChange発火)
2. compositionstart              ← inputの後（逆順）
3. compositionend
```

#### macOSのIME実装

**eyesofkids/react-compositionevent** リポジトリの調査結果より:

> "macOS（**全ブラウザ**）と Windows（IE除く）で合成イベント問題が存在"

**重要な知見**:
- macOS上では、**Chrome/Safari/Firefoxすべてで同じ問題が発生**
- これは**ブラウザの問題ではなく、macOSのIME実装の問題**
- Windowsでは比較的問題が少ない（IEを除く）

#### Chrome 53の変更

**2016年頃の変更**:
- Chrome 53でイベント発火順序が変更された
- それ以前の対策コードが動作しなくなった
- 既存のReactアプリケーションに影響

### 2.4 参考文献・リソース

#### 調査したリソース

1. **React GitHub Issues**
   - Issue #8683: https://github.com/facebook/react/issues/8683
   - Issue #3926: https://github.com/facebook/react/issues/3926

2. **eyesofkids/react-compositionevent**
   - URL: https://github.com/eyesofkids/react-compositionevent
   - 制御コンポーネントでの解決は困難との結論
   - デモサイト: https://eyesofkids.github.io/react-compositionevent/

3. **heistak.github.io - Japanese Input Guide**
   - URL: https://heistak.github.io/your-code-displays-japanese-wrong/otherthings.html
   - メッセージングアプリのベストプラクティス
   - 推奨: Enterキーのキーコードではなく改行文字を検出

4. **Chainlit Issue #1557**
   - URL: https://github.com/Chainlit/chainlit/issues/1557
   - 日本語入力でのフォーカス喪失問題

5. **Classi開発者ブログ**
   - URL: https://tech.classi.jp/entry/2024/04/23/183000
   - IME変換中のEnterキー対処法
   - `isComposing`プロパティの活用

6. **Qiita記事**
   - URL: https://qiita.com/bohemian916/items/4f3e860904c24922905a
   - ChainlitでのIME入力対応（Phase 1と同じアプローチ）

---

## 3. 根本原因の分析

### 3.1 Reactの制御コンポーネントの限界

#### 制御コンポーネントとは

```typescript
// 制御コンポーネントの例
const [value, setValue] = useState('');

<textarea
  value={value}                          // ← Reactのstateから値を供給
  onChange={(e) => setValue(e.target.value)}
  onKeyDown={onKeyDown}
/>
```

**特徴**:
- 入力値をReactのstateで管理
- すべての変更が`setState()`を経由
- 一見理想的だが、IME入力には問題がある

#### setStateの非同期性

```typescript
const handleCompositionEnd = () => {
  setIsComposing(false);  // ← この更新は非同期
};

const onKeyDown = (e) => {
  // この時点では、まだ isComposing === true の可能性
  if (e.key === 'Enter' && !isComposing) {
    onEnter();
  }
};
```

**問題**:
- `setState()`は即座に反映されない
- 次のレンダリングサイクルまで古い値が使われる
- イベントハンドラ間で状態の不整合が発生

#### Reactの合成イベント（SyntheticEvent）

**Reactのイベント処理**:
1. ブラウザのネイティブイベントを検知
2. Reactの合成イベントに変換
3. バブリングフェーズで処理

**問題**:
- ネイティブイベントとのタイミングずれ
- `compositionend`と`keydown`の順序が保証されない

### 3.2 ブラウザ間のイベント順序の違い

#### Chrome 53以降の変更（2016年）

**変更内容**:
- `compositionend`後の`input`イベント発火順序が変更
- 既存のIME対策コードが動作しなくなった

**影響**:
- 多くのWebアプリケーションで問題が再発
- Reactアプリケーションも影響を受けた

#### Safariの特殊なイベント順序

**Safari固有の問題**:
```
keydown (Enter) → compositionend
```

**他のブラウザ**:
```
compositionend → keydown (Enter)
```

**結果**:
- `keydown`実行時、`compositionend`が未発火
- `isComposing`の状態を正確に判定できない
- Reactの実装では対処不可能

### 3.3 macOS環境での特殊性

#### 全ブラウザで発生する理由

**eyesofkids/react-compositionevent**の調査結果:

> "macOS（全ブラウザ）と Windows（IE除く）で合成イベント問題が存在"

**技術的背景**:
- macOSのIME実装がブラウザに影響
- OS レベルでのイベント処理順序の問題
- ブラウザ側だけでは解決できない

#### Chrome vs Safariの違い

| ブラウザ | イベント順序 | 判定可能性 | 問題の深刻度 |
|---------|-------------|-----------|------------|
| Chrome | compositionend → keydown | 理論上可能 | 中（React状態更新の遅延） |
| Safari | keydown → compositionend | 不可能 | 高（順序が逆） |
| Firefox | compositionend → keydown | 理論上可能 | 中（未検証） |

**結論**:
- ChromeもSafariも、Reactの制御コンポーネントでは対処困難
- Safari は特に問題が深刻（イベント順序が逆）

---

## 4. 解決策の検討

### 4.1 Phase 1: custom_js による対策

#### アプローチの概要

**基本方針**:
- Reactの制御コンポーネントの問題を回避
- DOM レベルで直接イベントをハンドリング
- キャプチャフェーズでReactより先に処理

#### 技術的な仕組み

##### 1. グローバル変数で同期的に状態管理

```javascript
// custom.js
let isComposing = false;  // ← グローバル変数（Reactのstateではない）

document.addEventListener('compositionstart', function() {
  isComposing = true;  // ← 即座に反映（非同期ではない）
}, true);

document.addEventListener('compositionend', function() {
  isComposing = false;  // ← 即座に反映
}, true);
```

**利点**:
- ✅ `setState()`の非同期性を回避
- ✅ イベントハンドラ間で状態が一貫
- ✅ Reactのレンダリングサイクルに依存しない

##### 2. イベントキャプチャフェーズで処理

**JavaScriptのイベント伝播（3段階）**:

```
1. キャプチャフェーズ（上から下へ）
   document → body → div → textarea
   ↓
2. ターゲットフェーズ
   textarea（イベント発生元）
   ↓
3. バブリングフェーズ（下から上へ）
   textarea → div → body → document
```

**Reactのイベント処理**:
- Reactは**バブリングフェーズ**で処理
- `onKeyDown`などのイベントハンドラはバブリングフェーズで実行

**custom_jsの実装**:

```javascript
document.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && isComposing) {
    e.preventDefault();               // デフォルト動作を無効化
    e.stopImmediatePropagation();     // Reactへの伝播を完全停止
    return false;
  }
}, true);  // ← true = キャプチャフェーズで実行（重要！）
```

**処理順序**:

```
1. ユーザーがEnterキーを押す
   ↓
2. キャプチャフェーズ: custom.jsのリスナーが実行
   ↓ isComposingがtrueなら stopImmediatePropagation()
   ↓
3. ❌ ReactのonKeyDownには到達しない（伝播が停止）
   ↓
4. ✅ メッセージ送信されない
```

##### 3. stopImmediatePropagationの効果

**通常のstopPropagation()**:
- 親要素への伝播を停止
- **同じ要素の他のリスナーは実行される**

**stopImmediatePropagation()**:
- 親要素への伝播を停止
- **同じ要素の他のリスナーも実行されない**
- より強力なブロック

**Reactとの関係**:
- Reactのイベントリスナーも停止される
- 完全にEnterキーイベントをブロック可能

##### 4. Safari対策: keyCode 229の併用

**Safari固有の問題**:
- `isComposing`プロパティが正しく機能しないケースがある
- イベント発火順序が他のブラウザと異なる（`keydown` → `compositionend`）

**keyCode 229とは**:
- **IME入力中のキーイベントで返される特殊なコード**
- W3C仕様では非推奨（deprecated）だが、Safari対策として有効
- IME変換中は、どのキーを押しても`keyCode`が`229`になる

**Classi開発者ブログの推奨実装**:

```javascript
// isComposingとkeyCode 229を併用
document.addEventListener('keydown', function(e) {
  if ((e.key === 'Enter' && e.isComposing) || e.keyCode === 229) {
    e.preventDefault();
    e.stopImmediatePropagation();
    return false;
  }
}, true);
```

**判定条件の解説**:

| 条件 | 対象ブラウザ | 理由 |
|------|------------|------|
| `e.key === 'Enter' && e.isComposing` | Chrome, Firefox | 標準的なIME検出 |
| `e.keyCode === 229` | Safari | isComposingが機能しない場合の代替 |

**注意点**:
- ✅ `keyCode`は非推奨だが、Safari対策として必要
- ✅ 将来的にSafariが`isComposing`を正しく実装すれば不要になる可能性
- ⚠️ `keyCode === 229`だけでは、IME終了直後のEnterも誤ってブロックする可能性

**推奨される実装（両方を組み合わせ）**:

```javascript
// より堅牢な実装
let isComposing = false;

document.addEventListener('compositionstart', function() {
  isComposing = true;
}, true);

document.addEventListener('compositionend', function() {
  isComposing = false;
}, true);

document.addEventListener('keydown', function(e) {
  // 3つの条件でIME変換中を判定
  if (
    e.key === 'Enter' && (
      isComposing ||           // 独自フラグ
      e.isComposing ||         // 標準プロパティ
      e.keyCode === 229        // Safari対策
    )
  ) {
    e.preventDefault();
    e.stopImmediatePropagation();
    return false;
  }
}, true);
```

**3重の安全装置**:
1. `isComposing`（グローバル変数）- 最も確実
2. `e.isComposing`（標準プロパティ）- Chrome/Firefoxで有効
3. `e.keyCode === 229`（非推奨プロパティ）- Safari対策

#### なぜ有効なのか

| 問題点 | Reactの実装 | custom_js |
|-------|-----------|----------|
| **状態更新の非同期性** | ❌ setStateで非同期 | ✅ グローバル変数で同期 |
| **イベント処理順序** | ❌ バブリングフェーズ | ✅ キャプチャフェーズ（先） |
| **Safariの逆順問題** | ❌ 対処不可能 | ✅ isComposingフラグで判定 |
| **ブラウザ互換性** | ❌ Chrome/Safari両方で問題 | ✅ 全ブラウザで動作 |
| **実装の変更可能性** | ❌ ビルド済み変更不可 | ✅ いつでも修正可能 |

#### 実装コード例

```javascript
/**
 * Chainlit IME対応 - Phase 1: 暫定対応
 *
 * 問題: Chrome/Safari on MacでIME変換中のEnterキーがメッセージ送信される
 * 原因: Reactのイベント処理タイミングとブラウザのIMEイベント順序の不一致
 * 対策: イベントキャプチャフェーズでグローバルにEnterキーをインターセプト
 */

(function() {
  'use strict';

  console.log('[Chainlit IME Fix] カスタムJSが読み込まれました');

  // IME変換状態を追跡（グローバル変数で同期的に管理）
  let isComposing = false;

  // compositionstart: IME変換開始
  document.addEventListener('compositionstart', function(e) {
    isComposing = true;
    console.log('[IME Fix] 変換開始 - isComposing = true');
  }, true);

  // compositionend: IME変換終了
  document.addEventListener('compositionend', function(e) {
    isComposing = false;
    console.log('[IME Fix] 変換終了 - isComposing = false');
  }, true);

  // keydown: Enterキーをキャプチャフェーズでインターセプト
  document.addEventListener('keydown', function(e) {
    // 3つの条件でIME変換中を判定（3重の安全装置）
    if (
      e.key === 'Enter' && (
        isComposing ||           // 独自フラグ（最も確実）
        e.isComposing ||         // 標準プロパティ（Chrome/Firefox）
        e.keyCode === 229        // Safari対策（非推奨だが必要）
      )
    ) {
      console.log('[IME Fix] IME変換中のEnterをブロック', {
        isComposing: isComposing,
        'e.isComposing': e.isComposing,
        'e.keyCode': e.keyCode
      });
      e.preventDefault();
      e.stopImmediatePropagation();
      return false;
    }
  }, true); // ← キャプチャフェーズ（重要！）

  console.log('[Chainlit IME Fix] イベントリスナー登録完了');
})();
```

#### 設定ファイルの変更

**`.chainlit/config.toml`**:

```toml
[UI]
custom_js = "/public/custom.js"
```

**注意点**:
- `custom_js_attributes`は指定しない（デフォルトの`defer`を使用）
- パスは`/public/custom.js`（先頭のスラッシュ必須）

### 4.2 Phase 2以降の展望

#### 当初の想定

**Phase 1**: custom_jsで暫定対応
**Phase 2**: Chainlit本体にプルリクエスト、または公式対応を待つ

#### 調査後の見解（重要な方針転換）

**Phase 2の再検討が必要**:

1. **Reactフレームワーク自体が未解決**
   - Issue #8683/#3926 は現在もOPEN
   - Reactチームも「優先度が低い」として対応していない
   - Chainlit側だけでは根本解決が困難

2. **制御コンポーネントでの解決は困難**
   - eyesofkids/react-compositionevent の結論
   - 非制御コンポーネントへの変更は大規模なリファクタリングが必要
   - Chainlitのアーキテクチャ変更は非現実的

3. **custom_jsは「暫定」ではなく「現実的な解決策」**
   - React/ブラウザ/OSの問題を回避する唯一の方法
   - Googleなどの大企業でも同様のアプローチを採用
   - 長期的に安定した解決策

**新しいPhase 2の方向性**:

- ❌ ~~Chainlit本体へのプルリクエスト~~ → React自体の問題のため困難
- ❌ ~~公式対応を待つ~~ → Reactチームも対応予定なし
- ✅ **custom_jsを正式な解決策として採用**
- ✅ ドキュメント化・ベストプラクティス化
- ✅ 他のIME言語（中国語、韓国語）でもテスト
- ✅ コミュニティへの共有（GitHub Discussion, Issue）

### 4.3 他の解決アプローチの検討

#### 参考: Qiita vs Classi記事のコードの違い

本プロジェクトで参考にした2つの記事のコードには、大きなアプローチの違いがあります。

##### Qiita記事（bohemian916）: 約200行の複雑なコード

**URL**: https://qiita.com/bohemian916/items/4f3e860904c24922905a

**アプローチ**: **「Enterキー送信の完全置き換え」**

```javascript
// 主要な機能（約200行）
1. ✅ IME状態の追跡
2. ✅ Enterキーの完全ブロック（IME関係なく全てブロック）
3. ✅ 改行挿入機能の手動実装
   - contentEditable用
   - textarea用
4. ✅ MutationObserverで動的要素を監視
5. ✅ EventTarget.prototypeのパッチング
6. ✅ フォーム送信の完全ブロック
```

**設計思想**:
```
Enter → 送信（既存動作） ❌ 無効化
         ↓
Enter → 改行（新しい動作） ✅ 手動実装
```

**適用ケース**:
- Enterキー送信を望まないユーザー
- 改行のみの入力欄にしたい場合
- Chainlit専用にカスタマイズしたい場合

**欠点**:
- コードが複雑（200行）
- メンテナンスが大変
- Chainlitの既存動作を大きく変更
- 他の機能との競合リスク

---

##### Classi記事: わずか3行のシンプルなコード

**URL**: https://tech.classi.jp/entry/2024/04/23/183000

**アプローチ**: **「IME変換中のみブロック」**

```javascript
// たった3行（本質部分）
document.addEventListener('keydown', function(e) {
  if ((e.key === 'Enter' && e.isComposing) || e.keyCode === 229) {
    e.stopPropagation();
  }
}, true);
```

**設計思想**:
```
IME変換中:
  Enter → ブロック

IME変換後:
  Enter → 送信（既存動作を維持）
```

**適用ケース**:
- Enter送信機能を維持したい
- Google Meet、ChatGPTなど既存サービス向け
- シンプルで保守しやすいコード
- 汎用的なIME対策

**利点**:
- シンプル（3〜45行程度）
- 理解しやすい
- 既存機能を壊さない
- メンテナンスしやすい

---

##### Chainlitでの選択: Classi方式を採用

**理由**:

1. **Chainlitの既存動作を維持**
   - Enter → 送信
   - Shift+Enter → 改行
   - ユーザーが慣れている標準的な動作

2. **コードの保守性**
   - シンプルで理解しやすい
   - バグが入りにくい
   - 将来の変更に強い

3. **目的との一致**
   - 問題: 「IME変換中のEnterが誤って送信される」
   - 解決: 「IME変換中のEnterをブロック」
   - 完全に一致

**採用コード**: Classi方式 + 3重の安全装置（約45行）

---

#### アプローチA: 改行文字検出方式

**heistak.github.io の推奨**:

> "アプリがEnterキーのキーコードではなく、**改行文字を検出する**"

**実装イメージ**:

```typescript
// Enterキーではなく、改行文字で判定
const onChange = (e) => {
  const value = e.target.value;
  if (value.includes('\n')) {
    // 改行文字が含まれていればメッセージ送信
    const message = value.replace('\n', '');
    sendMessage(message);
  }
};
```

**利点**:
- ✅ IME変換中のEnterは改行文字を生成しない
- ✅ 変換確定後のEnterのみ送信される

**欠点**:
- ❌ Shift+Enterでの改行機能と競合
- ❌ ユーザーが意図的に改行を入力できなくなる
- ❌ UX（ユーザー体験）の変更が大きい

**結論**: Chainlitでは現実的ではない

#### アプローチB: 送信ボタン必須化

**方針**:
- Enterキーでの送信を完全に無効化
- 送信ボタンのクリックのみで送信

**利点**:
- ✅ IME問題を完全に回避
- ✅ 実装が簡単

**欠点**:
- ❌ UX（ユーザー体験）の大幅な変更
- ❌ キーボード操作の利便性が低下
- ❌ 既存ユーザーの混乱

**結論**: 最終手段として検討可能だが、優先度は低い

#### アプローチC: 非制御コンポーネントへの変更

**方針**:
- Reactの制御コンポーネントを非制御コンポーネントに変更
- `useState()`を使わず、`ref`で値を管理

**利点**:
- ✅ Reactの状態更新問題を回避

**欠点**:
- ❌ Chainlitの大規模なリファクタリングが必要
- ❌ 他の機能（コマンド機能、履歴など）との整合性
- ❌ 実装コストが高い

**結論**: 非現実的

#### アプローチD: ブックマークレット方式（ユーザー側の対策）

**方針**:
- アプリケーション側ではなく、**ユーザー側で対策**
- ブラウザのブックマークに登録して、必要時にクリック
- Classi開発者ブログで紹介された方法

**実装イメージ**:

```javascript
// ブックマークレットのコード（1行にまとめる）
javascript:(function(){document.addEventListener('keydown',function(e){if((e.key==='Enter'&&e.isComposing)||e.keyCode===229){e.stopPropagation();}},true);})();
```

**使用方法**:
1. 上記のコードをブックマークのURLとして登録
2. IME問題が発生するページで、ブックマークをクリック
3. そのページでのみ対策が有効になる

**利点**:
- ✅ アプリケーション側の変更が不要
- ✅ ユーザーが自分で対処できる
- ✅ 複数のWebサービスで使い回せる

**欠点**:
- ❌ ページをリロードすると無効になる（再クリックが必要）
- ❌ すべてのユーザーに周知する必要がある
- ❌ 技術的な知識が必要

**ブラウザ拡張機能版**:
- Classi開発者は「Google Meet Chat to Clipboard」拡張機能（v4.2.0）で実装
- 自動的にすべてのページで適用される
- より便利だが、開発・配布のコストが高い

**Chainlitでの適用可否**:
- ❌ **推奨しない** - ユーザー側に負担を強いる
- ✅ custom_jsで解決できるため、アプリ側で対応すべき
- ❓ 緊急の回避策としては有効（custom_js実装前の一時対応）

**結論**: Chainlitでは custom_js（アプローチA）を採用すべき

---

## 5. 実装プラン

### 5.1 ファイル構成

```
/workspaces/ai-agent-demo/
├── .chainlit/
│   └── config.toml          ← custom_js設定を追加
├── public/                  ← ディレクトリを作成（存在しなければ）
│   └── custom.js            ← IME対応JavaScriptを配置
├── apps/
│   └── langgraph_streaming.py
└── ...
```

### 5.2 実装手順

#### ステップ1: publicディレクトリの作成

```bash
mkdir -p public
```

#### ステップ2: custom.jsの作成

**ファイル**: `public/custom.js`

**採用アプローチ**: Classi方式（シンプル版）+ 3重の安全装置

**注意**: Qiita記事（bohemian916）の200行コードは、Enter送信を完全に無効化して改行に置き換えるアプローチです。Chainlitでは既存のEnter送信機能を維持したいため、**Classi方式**（IME変換中のみブロック）を採用します。

```javascript
/**
 * Chainlit IME対応 - Phase 1
 *
 * 問題: Chrome/Safari on MacでIME変換中のEnterキーがメッセージ送信される
 * 原因: Reactの状態更新タイミングとブラウザのIMEイベント順序の不一致
 * 対策: イベントキャプチャフェーズでIME変換中のEnterキーのみをブロック
 *
 * アプローチ: Classi方式（シンプル）+ 3重の安全装置
 * - Enter送信機能は維持（IME変換後は正常に送信）
 * - IME変換中のEnterのみブロック
 *
 * 参考: https://tech.classi.jp/entry/2024/04/23/183000
 */

(function() {
  'use strict';

  console.log('[Chainlit IME Fix] カスタムJSが読み込まれました');

  // グローバル変数でIME状態を追跡（最も確実）
  let isComposing = false;

  document.addEventListener('compositionstart', function(e) {
    isComposing = true;
    console.log('[IME Fix] 変換開始');
  }, true);

  document.addEventListener('compositionend', function(e) {
    isComposing = false;
    console.log('[IME Fix] 変換終了');
  }, true);

  document.addEventListener('keydown', function(e) {
    // 3つの条件でIME変換中を判定（3重の安全装置）
    if (
      e.key === 'Enter' && (
        isComposing ||           // 独自フラグ（最も確実）
        e.isComposing ||         // 標準プロパティ（Chrome/Firefox）
        e.keyCode === 229        // Safari対策（非推奨だが必要）
      )
    ) {
      console.log('[IME Fix] IME変換中のEnterをブロック', {
        isComposing: isComposing,
        'e.isComposing': e.isComposing,
        'e.keyCode': e.keyCode
      });
      e.preventDefault();
      e.stopImmediatePropagation();
      return false;
    }
  }, true);

  console.log('[Chainlit IME Fix] イベントリスナー登録完了');
})();
```

**コードの特徴**:
- **約45行**: シンプルで理解しやすい（Qiita方式の200行と比較）
- **3重の安全装置**: `isComposing`（グローバル）、`e.isComposing`（標準）、`e.keyCode === 229`（Safari対策）
- **Enter送信を維持**: IME変換後は正常に送信される（Chainlitの既存動作を維持）
- **デバッグログ付き**: 開発者ツールで動作を確認可能

#### ステップ3: config.tomlの編集

**ファイル**: `.chainlit/config.toml`

**変更箇所**:

```toml
[UI]
custom_js = "/public/custom.js"
```

#### ステップ4: Chainlitアプリの再起動

```bash
# 実行中のChainlitを停止（Ctrl+C）

# 再起動
uv run chainlit run apps/langgraph_streaming.py
```

### 5.3 動作確認手順

#### 1. ブラウザでアプリを開く

- URL: http://localhost:8000

#### 2. 開発者ツールを開く

**Chrome/Safari**:
- Mac: `Cmd + Option + I`
- Windows/Linux: `F12`

#### 3. Consoleタブを確認

**期待される出力**:

```
[Chainlit IME Fix] カスタムJSが読み込まれました
[Chainlit IME Fix] イベントリスナー登録完了
```

#### 4. 日本語入力テスト

**手順**:
1. チャット入力欄をクリック
2. 日本語入力モードをON
3. ローマ字入力（例: "konnichiwa"）
4. 変換候補が表示されている状態でEnterキーを押す

**期待される動作**:
- ✅ 変換が確定される（送信されない）
- ✅ Consoleに以下が表示される:
  ```
  [IME Fix] 変換開始
  [IME Fix] IME変換中のEnterをブロック
  [IME Fix] 変換終了
  ```

#### 5. 正常動作の確認

**テストケース**:

| 操作 | 期待される動作 |
|------|--------------|
| IME変換中にEnter | ✅ 変換確定（送信されない） |
| 変換確定後にEnter | ✅ メッセージ送信 |
| 英語入力でEnter | ✅ メッセージ送信 |
| Shift+Enter | ✅ 改行 |

#### 6. ブラウザ別テスト

- ✅ Chrome on Mac
- ✅ Safari on Mac
- ❓ Firefox on Mac（オプション）

### 5.4 トラブルシューティング

#### custom.jsが読み込まれない場合

**確認1: ファイルの存在**

```bash
ls -la public/custom.js
```

**確認2: config.tomlの設定**

```bash
cat .chainlit/config.toml | grep custom_js
```

**確認3: ブラウザで直接アクセス**

- URL: http://localhost:8000/public/custom.js
- JavaScriptコードが表示されればOK

**確認4: Chainlitの再起動**

```bash
# 必ずアプリを再起動
uv run chainlit run apps/langgraph_streaming.py
```

#### 依然として問題が発生する場合

**より強力なブロック処理**:

```javascript
// keypress, keyupイベントも併せてブロック
['keydown', 'keypress', 'keyup'].forEach(function(eventType) {
  document.addEventListener(eventType, function(e) {
    if (e.key === 'Enter' && (isComposing || e.isComposing)) {
      e.preventDefault();
      e.stopImmediatePropagation();
      return false;
    }
  }, true);
});
```

---

## 6. 結論

### 6.1 問題の本質

今回調査した「ChainlitでのIME変換中のEnterキー誤送信問題」は、以下の複合的な要因によるものであることが判明：

1. **Reactフレームワーク自体の未解決問題**
   - Issue #8683/#3926 は現在もOPEN
   - 制御コンポーネントでの完全な解決は困難
   - Reactチームも「優先度が低い」として対応していない

2. **ブラウザ間のイベント順序の不統一**
   - Chrome 53以降の変更
   - Safariの特殊なイベント順序（`keydown` → `compositionend`）
   - 3種類以上の異なるパターンが存在

3. **macOSのIME実装**
   - OS レベルの問題
   - すべてのブラウザ（Chrome/Safari/Firefox）で影響

4. **Reactの状態管理の非同期性**
   - `setState()`の更新タイミング
   - 合成イベントとネイティブイベントのずれ

### 6.2 custom_jsは暫定ではなく現実的な解決策

**当初の想定**:
- Phase 1: custom_jsで暫定対応
- Phase 2: Chainlit本体へのプルリクエスト

**調査後の結論**:
- ✅ **custom_jsは「暫定」ではなく「現実的な解決策」**
- ✅ React/ブラウザ/OSの問題を回避する唯一の方法
- ✅ 長期的に安定した解決策として採用すべき

**理由**:
1. Reactフレームワーク自体が未解決（修正予定なし）
2. Chainlit側だけでは根本解決が不可能
3. 制御コンポーネントでの解決は技術的に困難
4. 大企業（Google等）も同様のアプローチを採用

### 6.3 推奨アプローチ

**短期（Phase 1）**:
- ✅ `custom.js`でIME対応を実装
- ✅ Chrome/Safari on Macで動作確認
- ✅ ドキュメント化（本調査報告書）

**中期（Phase 2）**:
- ✅ 他のIME言語（中国語、韓国語）でテスト
- ✅ Windows/Linux環境での動作確認
- ✅ コミュニティへの共有（GitHub Discussion）
- ✅ ベストプラクティスとしてドキュメント化

**長期（Phase 3以降）**:
- ❓ Reactフレームワークの改善を待つ（期待薄）
- ❓ 非制御コンポーネントへの移行（大規模リファクタリング）
- ❓ 送信方法の見直し（改行文字検出、ボタン必須化）

### 6.4 今後のメンテナンス方針

#### custom.jsの管理

1. **バージョン管理**
   - `public/custom.js`をGitで管理
   - 変更履歴を記録

2. **テスト**
   - Chainlitバージョンアップ時に動作確認
   - ブラウザアップデート時に再テスト

3. **ドキュメント**
   - 本調査報告書を参照
   - `.claude/decisions.md`に設計判断を記録

#### Chainlitアップデート時の対応

**確認事項**:
1. Chainlit本体でIME対応が改善されたか
2. `custom.js`が依然として必要か
3. 新しいバージョンで動作するか

**対応方針**:
- Chainlit本体で解決されるまで`custom.js`を継続使用
- 定期的にGitHub Issueを確認

---

## 付録

### A. 関連Issue・PR

#### React

- **Issue #8683**: Composition Events(Chinese, Japanese IME) problem in controlled components
  - URL: https://github.com/facebook/react/issues/8683
  - ステータス: OPEN（未解決）

- **Issue #3926**: Change event fires extra times before IME composition ends
  - URL: https://github.com/facebook/react/issues/3926
  - ステータス: OPEN（未解決）

- **PR #8438**: Fix IME composition events
  - ステータス: マージされていない

#### Chainlit

- **Issue #1557**: MIME type error when inputting Japanese causes focus loss in iframe
  - URL: https://github.com/Chainlit/chainlit/issues/1557
  - 関連: iFrame内での日本語入力問題

### B. 参考リンク

#### 技術記事

1. **Classi開発者ブログ**
   - タイトル: IME変換中のエンターキーで送信される！への対処法
   - URL: https://tech.classi.jp/entry/2024/04/23/183000
   - 内容: `isComposing`プロパティの活用、ブックマークレット実装

2. **Qiita**
   - タイトル: Chainlitの日本語入力で変換途中にEnterを押すとメッセージ送信されてしまう
   - URL: https://qiita.com/bohemian916/items/4f3e860904c24922905a
   - 内容: custom_jsによる解決方法（Phase 1と同じアプローチ）

3. **heistak.github.io**
   - タイトル: Your Code Displays Japanese Wrong - Messaging Apps
   - URL: https://heistak.github.io/your-code-displays-japanese-wrong/otherthings.html
   - 内容: IME入力のベストプラクティス、改行文字検出の推奨

#### リポジトリ

1. **eyesofkids/react-compositionevent**
   - URL: https://github.com/eyesofkids/react-compositionevent
   - デモサイト: https://eyesofkids.github.io/react-compositionevent/
   - 内容: Reactでのcomposition event問題の包括的な調査

2. **Chainlit公式リポジトリ**
   - URL: https://github.com/Chainlit/chainlit
   - Input.tsx: https://github.com/Chainlit/chainlit/blob/main/frontend/src/components/chat/MessageComposer/Input.tsx

#### 公式ドキュメント

1. **MDN Web Docs**
   - compositionstart event: https://developer.mozilla.org/en-US/docs/Web/API/Element/compositionstart_event
   - CompositionEvent: https://developer.mozilla.org/en-US/docs/Web/API/CompositionEvent

2. **Chainlit Documentation**
   - UI Customization: https://docs.chainlit.io/backend/config/ui

### C. 用語集

#### IME (Input Method Editor)
- **日本語**: 入力メソッドエディタ
- **説明**: 日本語、中国語、韓国語など、キーボードに直接対応しない文字を入力するためのソフトウェア
- **例**: macOSの日本語入力、Google日本語入力、Microsoft IME

#### Composition Events
- **説明**: IME入力時に発火するブラウザイベント
- **種類**: `compositionstart`, `compositionupdate`, `compositionend`
- **用途**: IME変換中の状態を検知

#### 制御コンポーネント (Controlled Component)
- **説明**: Reactのstateで入力値を管理するコンポーネント
- **特徴**: `value`プロパティと`onChange`イベントを使用
- **問題**: IME入力との相性が悪い

#### 非制御コンポーネント (Uncontrolled Component)
- **説明**: DOM自身が入力値を管理するコンポーネント
- **特徴**: `ref`で値を取得
- **利点**: IME入力に対応しやすい

#### keyCode 229
- **説明**: IME入力中のキーイベントで返される特殊なキーコード
- **技術的背景**: IME変換中は、どのキーを押しても`keyCode`が`229`になる
- **W3C仕様**: 非推奨（deprecated）だが、Safari対策として有効
- **用途**: `isComposing`プロパティが機能しない環境での代替判定
- **注意**: 将来的にブラウザがサポートを終了する可能性あり

#### キャプチャフェーズ (Capture Phase)
- **説明**: イベント伝播の最初の段階（上から下へ）
- **用途**: 親要素がイベントを先に処理できる
- **実装**: `addEventListener(..., true)`

#### バブリングフェーズ (Bubbling Phase)
- **説明**: イベント伝播の最後の段階（下から上へ）
- **用途**: 子要素のイベントが親要素に伝播
- **実装**: `addEventListener(..., false)`（デフォルト）

#### stopImmediatePropagation()
- **説明**: イベント伝播を完全に停止するメソッド
- **効果**: 同じ要素の他のリスナーも実行されない
- **用途**: Reactのイベントハンドラを完全にブロック

#### isComposing
- **説明**: IME変換中かどうかを示すプロパティ
- **型**: Boolean
- **値**: 変換中は`true`、それ以外は`false`

---

## 更新履歴

- **2025-11-02 (v1.1)**: Classi技術ブログの詳細情報を追加
  - Google Meet/ChatGPTでの事例を詳述
  - keyCode 229によるSafari対策を追加
  - ブックマークレット方式（アプローチD）を追加
  - 実装コード例を更新（3重の安全装置）
  - 用語集にkeyCode 229を追加

- **2025-11-02 (v1.0)**: 初版作成
  - 問題の詳細調査
  - Reactの既知問題の分析（Issue #8683/#3926）
  - Chainlit内部実装の分析（Input.tsx）
  - ブラウザ・OSレベルの問題調査
  - custom_jsによる解決策の検討
  - 実装プランの策定
  - 包括的な参考文献リスト作成
