```markdown
# PokerAgent — UI コンポーネント一覧（詳細）

このドキュメントはプロトタイプ実装向けのフロントエンド UI コンポーネント設計です。
各コンポーネントは React + TypeScript を想定しています。Props, State, Events, Responsibilities, Accessibility, テストポイントを含みます。

目次
- High-level layout
- コンポーネント一覧（詳細）
- Help（助言）フローと UI 挙動
- レスポンシブ / アクセシビリティ / 国際化（i18n）
- テストケース例

---

High-level layout
- TopBar: アプリタイトル、接続状態、設定ボタン
- TableView: 中央の楕円テーブル（Board + Seats + Pot）
- RightPanel: ログ／助言履歴／設定の簡易表示
- BottomControls: ユーザーのホールカード表示とアクション（Fold / Call / Raise / Help）
- ModalLayer: HelpModal, ConfirmModal, Toasts

---

コンポーネント一覧（アルファベット順）

1) TopBar
- Props:
  - title: string
  - connectionStatus: "connected" | "connecting" | "disconnected"
  - onOpenSettings(): void
- State: なし（ステートレス）
- Events: settings ボタン押下
- Responsibilities:
  - アプリ名表示、接続インジケータ、簡易ヘルプリンク
- Accessibility:
  - 接続インジケータは aria-live="polite"。設定ボタンに aria-label を付与。
- Tests:
  - connectionStatus によって表示が変わること

2) TableView
- Props:
  - gameState: GameState (型はバックエンドと共有)
  - onSeatClick(seatId): void
- State:
  - none (pure render from gameState)
- Responsibilities:
  - Board、Seat 配置、Pot 表示のレイアウト
- Tests:
  - board.card count に応じたカードの表示

3) Seat (→ PlayerSummary）
- Props:
  - player: Player (id, name, stack, committed, isDealer, status, isHuman)
  - seatIndex: number
  - revealCards: boolean (UI 層でコントロール)
- State:
  - hover: boolean (オプション)
- Events:
  - onClick: seat 選択（観戦/注目）
- Responsibilities:
  - プレイヤー名、スタック、短い履歴、カード（裏向き/表向き）
  - ディーラーマークの表示
- Accessibility:
  - 視覚障害者のために "Player X, stack 120 bb" を aria-label に含める
- Tests:
  - revealCards=false のときホールカードが表へ出ないこと

4) Board
- Props:
  - cards: string[] (max 5)
- Responsibilities:
  - ボードカードを横並びで表示（未出ならプレースホルダ）
- Tests:
  - フロップ/ターン/リバーで正しい枚数を描画

5) PotDisplay
- Props:
  - potSize: number
  - sidePots?: SidePot[]
- Responsibilities:
  - 中央ポットとサイドポットの表示
- Tests:
  - サイドポットがある場合正しく分離して表示

6) PlayerHoleCards
- Props:
  - cards: string[] | null
  - visible: boolean
- Responsibilities:
  - ユーザーは常に reveal=true、CPU は false（裏表示）
- Tests:
  - visible 切替でカード表裏が切り替わる

7) ActionControls (BottomControls)
- Props:
  - allowedActions: { fold: boolean, call: boolean, raise: boolean }
  - minRaise?: number
  - maxRaise?: number
  - currentCallAmount?: number
- State:
  - raiseAmount: number (スライダー or input)
  - isConfirmingRaise: boolean
- Events:
  - onFold(), onCall(), onRaise(amount)
- Responsibilities:
  - ユーザーの操作 UI。Raise はスライダーまたはプリセットボタン (1/2 pot, 3x, all-in など)
  - 操作のバリデーション（min/max）
- Accessibility:
  - ボタンに明確なラベル、スライダーは keyboard 操作可能
- Tests:
  - 無効な raise はボタン disabled

8) HelpButton
- Props:
  - disabled?: boolean
  - mode: "beginner" | "advanced"
- Events:
  - onHelpRequested(mode)
- Responsibilities:
  - 押下時に HelpModal を開き、API 呼び出しをトリガー
  - ローディング UI（spinner）を表示
- Tests:
  - クリックで onHelpRequested が呼ばれる

9) HelpModal (AI 助言 UI)
- Props:
  - visible: boolean
  - requestPayload: AdvisorRequest (optional)
  - onApply(): void
  - onClose(): void
- State:
  - loading: boolean
  - response?: AdvisorResponse
  - error?: string
- Events:
  - lifecycle: onOpen -> fetch advisor -> show response
  - user: Apply / Close / Copy explanation
- Responsibilities:
  - /api/game/{id}/help へ POST し、応答を表示
  - 構造化された JSON で出力を要求；失敗時はダミー助言を表示
  - Apply を押すとその Action を UI に反映（確認ダイアログ推奨）
- UX Notes:
  - 応答は「推奨 action」「bet_size」「reasoning（箇条書き）」で表示
  - beginner モードでは「初心者向け一行アドバイス」を常に表示
- Accessibility:
  - モーダルは focus trap、ESC で閉じる、aria-modal=true
- Tests:
  - ローディング/成功/失敗 それぞれの表示

10) LogPanel / History
- Props:
  - history: Action[]
- Responsibilities:
  - ラウンド毎のアクションログ（テキスト）
- Tests:
  - 新しいアクションが発生したら自動スクロール

11) SettingsPanel (Modal)
- Props:
  - settings: {blinds, startingStack, playerCount}
  - onSave(settings)
- Responsibilities:
  - ゲーム設定の編集（ロビー画面）
- Tests:
  - 保存後ゲーム設定が backend に反映される

12) Lobby (New Game)
- Responsibilities:
  - 新規ゲーム作成、既存セッション一覧（将来的）
- Tests:
  - New Game でゲームが作成される

13) ConnectionIndicator
- Props:
  - status: TopBar.connectionStatus
- Responsibilities:
  - WebSocket / API 接続の状態表示と再接続ボタン

14) Toast / Notifications
- Responsibilities:
  - エラーや成功の短報を表示
- Tests:
  - API エラーが発生したときに toast が出る

15) GameStateStore (global)
- Responsibilities:
  - WebSocket からの state_update を受取り全体 state を管理
  - optimistic UI（ユーザー操作時に先行反映）と rollback の仕組み
- Implementation:
  - React Context または Zustand
- Tests:
  - 状態遷移の一貫性

16) ApiClient
- Responsibilities:
  - REST calls (POST /api/game/{id}/help, POST action, GET state)
  - retries, timeout, error handling
- Notes:
  - Help API はタイムアウト長め（例 15–30s）
  - Authorization: none for prototype; later use session token

17) WebSocketClient
- Responsibilities:
  - /ws/game/{id} を接続して state_update を購読
  - lua-style ping/pong 管理と再接続ロジック
- Events:
  - onStateUpdate(gameState), onError(err)

---

Help（助言）フローと UI 挙動（実装指針）
1. ユーザーが Help を押す
   - UI: HelpButton はインジケータ表示（ローディング）
   - フロント -> POST /api/game/{id}/help with AdvisorRequest
2. Backend:
   - deterministic engine が勝率等を計算（必須）
   - LLM 呼び出し（Hugging Face 等）で説明を生成（プロンプトに deterministic 結果を含める）
   - Backend は構造化 JSON を返す（AdvisorResponse）
3. フロント:
   - HelpModal に AdvisorResponse を表示
   - 「Apply」ボタンで提案アクションをユーザー操作に反映（確認あり）
   - エラー: 失敗時はダミー助言（ローカルルール）を表示し、ユーザーに通知

UI 表示要件（Help）
- 初期表示: ローディング spinner + 「AI に助言を問い合わせ中…」
- 成功表示:
  - 推奨アクション（大きく）
  - bet_size（強調）
  - 箇条書きの理由（3つ程度）
  - 「初心者向けの短い説明」(mode=beginner)
  - Apply / Close ボタン
- 失敗表示:
  - 軽い謝罪文とダミー助言（例: "Fold を推奨します。理由: ハンドが弱い"）

---

レスポンシブ / アクセシビリティ / i18n
- レイアウト:
  - Desktop: TableView (center) + RightPanel (助言/ログ)
  - Tablet: RightPanel を下に折りたたむ or Drawer
  - Mobile: Table 縮小、アクション優先表示、Help はフルスクリーンモーダル
- アクセシビリティ:
  - キーボード操作: Tab, Enter, ESC に対応
  - 色覚多様性: カラーだけで情報を伝えない（アイコン/テキスト併用）
  - ARIA: モーダル, buttons, live regions の適切な設定
- 国際化:
  - 文字列は全て i18n (例: react-intl / i18next) で管理
  - Help の説明は多言語対応を想定（LLM へは言語指定を送信）

---

テストケース例（短）
- ユーザー: BTN Ah,Kd, board empty -> Help -> AdvisorResponse が表示され、Apply を押すと onRaise/call/fold が呼ばれる
- Help API が 500 を返した場合 -> HelpModal はダミー助言を表示し、トーストで通知
- WebSocket 切断 -> ConnectionIndicator が disconnected になり、再接続試行を行う

---

開発メモ（実装優先度）
- P0: TableView, BottomControls, PlayerHoleCards, HelpButton, HelpModal (dumy/backed stub)
- P1: WebSocketClient, GameStateStore, ApiClient, LogPanel
- P2: Advanced Help (LLM integration), SettingsPanel, Lobby
- P3: Analytics, persistence, multi-session support

---

以上。次のステップとして、希望があれば
- A: React/TS のコンポーネント雛形 (tsx ファイル群) を自動生成します（Props 型付き）
- B: HelpModal の完全な実装（API 呼び出し、ローディングステート、エラーハンドリング）を提供します

どちらを先に作成しましょうか？
```